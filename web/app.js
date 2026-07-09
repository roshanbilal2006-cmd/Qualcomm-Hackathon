const BACKEND_URL = "http://localhost:8000";
const OWNER_STORAGE_KEY = "landsense_owner_id";

let observationsList = [];
let heatmapPoints = [];
let selectedObservationId = null;
let ownerId = getOwnerId();
let osmMap = null;
let heatmapLayer = null;

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
  initializeOpenStreetMap();
  fetchHistory();
  
  // Set up refresh timer
  setInterval(fetchHistory, 5000);

  // Bind capture controls
  document.getElementById("btn-trigger-scan").addEventListener("click", triggerMockScan);
  document.getElementById("btn-upload-photo").addEventListener("click", openUploadModal);
  document.getElementById("btn-close-upload").addEventListener("click", closeUploadModal);
  document.getElementById("btn-use-location").addEventListener("click", fillCurrentLocation);
  document.getElementById("upload-form").addEventListener("submit", handlePhotoUpload);
});

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Unable to read selected image"));
    reader.readAsDataURL(file);
  });
}

function createMockConstructionImageDataUrl() {
  const canvas = document.createElement("canvas");
  canvas.width = 640;
  canvas.height = 420;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = "#9fb7c9";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#b98552";
  ctx.fillRect(0, 300, canvas.width, 120);

  ctx.fillStyle = "#6f7680";
  for (let x = 120; x <= 500; x += 95) {
    ctx.fillRect(x, 120, 16, 190);
  }
  for (let y = 145; y <= 255; y += 55) {
    ctx.fillRect(90, y, 450, 14);
  }

  ctx.strokeStyle = "#d6b35a";
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.moveTo(90, 105);
  ctx.lineTo(540, 285);
  ctx.moveTo(540, 105);
  ctx.lineTo(90, 285);
  ctx.stroke();

  ctx.fillStyle = "#c84d32";
  ctx.fillRect(420, 250, 85, 55);
  ctx.fillStyle = "#f3c24d";
  ctx.fillRect(445, 225, 34, 25);

  return canvas.toDataURL("image/jpeg", 0.86);
}

// Fetch History and Heatmap
async function fetchHistory() {
  try {
    const [historyResponse, heatmapResponse] = await Promise.all([
      fetch(`${BACKEND_URL}/history?owner_id=${encodeURIComponent(ownerId)}`),
      fetch(`${BACKEND_URL}/heatmap`)
    ]);

    if (!historyResponse.ok) throw new Error("Backend history fetch failed");
    if (!heatmapResponse.ok) throw new Error("Backend heatmap fetch failed");
    
    observationsList = await historyResponse.json();
    heatmapPoints = await heatmapResponse.json();
    
    // Update counter
    document.getElementById("history-count").innerText = observationsList.length;
    
    renderFeed();
    renderHeatmap();
    
    if (selectedObservationId) {
      showObservationDetails(selectedObservationId);
    }
  } catch (error) {
    console.error("Error fetching system history:", error);
  }
}

// Render Left Feed List
function renderFeed() {
  const container = document.getElementById("observation-list");
  if (observationsList.length === 0) {
    container.innerHTML = `<div class="feed-empty">No private observations uploaded from this browser session yet.</div>`;
    return;
  }

  container.innerHTML = observationsList.map(obs => {
    const isSelected = obs.observation_id === selectedObservationId ? "selected" : "";
    const timeStr = new Date(obs.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    return `
      <div class="feed-item ${isSelected}" onclick="selectObservation('${obs.observation_id}')">
        <div class="feed-item-header">
          <span class="feed-stage">${obs.construction_stage || "Unknown"}</span>
          <span class="feed-score">${obs.development_score} / 100</span>
        </div>
        <div class="feed-details">
          <span>ID: ${obs.observation_id.substring(0, 8)}</span>
          <span>${timeStr}</span>
        </div>
      </div>
    `;
  }).join("");
}

function initializeOpenStreetMap() {
  if (!window.L) {
    document.getElementById("coord-info").innerText = "OpenStreetMap library unavailable";
    return;
  }

  osmMap = L.map("osm-map", {
    zoomControl: true,
    attributionControl: true
  }).setView([19.82817, 77.29378], 15);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(osmMap);

  heatmapLayer = L.layerGroup().addTo(osmMap);
}

// Render heatmap hotspots on OpenStreetMap
function renderHeatmap() {
  const emptyState = document.getElementById("map-empty-state");

  if (!osmMap || !heatmapLayer) {
    document.getElementById("coord-info").innerText = "OpenStreetMap not loaded";
    return;
  }

  heatmapLayer.clearLayers();

  if (heatmapPoints.length === 0) {
    document.getElementById("coord-info").innerText = "No public heatmap points yet";
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");
  const bounds = L.latLngBounds(heatmapPoints.map(point => [point.latitude, point.longitude]));
  const center = bounds.getCenter();
  document.getElementById("coord-info").innerText = `Center: ${center.lat.toFixed(5)}, ${center.lng.toFixed(5)}`;

  heatmapPoints.forEach(point => {
    const color = getPinColor(point.development_score);
    const marker = L.circleMarker([point.latitude, point.longitude], {
      radius: getHeatRadius(point.development_score),
      color,
      fillColor: color,
      fillOpacity: 0.38,
      weight: 2,
      className: `osm-hotspot ${getPinClass(point.development_score)}`
    }).bindTooltip(`${point.stage || "Observation"} | Score: ${point.development_score}`, {
      direction: "top",
      opacity: 0.92
    });

    marker.on("click", () => {
      const localObservation = observationsList.find(obs => obs.observation_id === point.observation_id);
      if (localObservation) {
        selectObservation(point.observation_id);
      }
    });

    marker.addTo(heatmapLayer);
  });

  osmMap.fitBounds(bounds.pad(0.25), { maxZoom: 16, animate: false });
  setTimeout(() => osmMap.invalidateSize(), 0);
}

function getPinClass(score) {
  if (score >= 80) return "completed-site";
  if (score >= 50) return "normal-site";
  return "active-site";
}

function getPinColor(score) {
  if (score >= 80) return "#06b6d4";
  if (score >= 50) return "#f97316";
  return "#ef4444";
}

function getHeatRadius(score) {
  return Math.max(10, Math.min(28, 10 + Number(score || 0) * 0.18));
}

// Selection handler
function selectObservation(id) {
  selectedObservationId = id;
  renderFeed();
  showObservationDetails(id);
}

// Render Detail Panel
function showObservationDetails(id) {
  const obs = observationsList.find(o => o.observation_id === id);
  if (!obs) return;

  document.getElementById("details-empty").classList.add("hidden");
  const content = document.getElementById("details-content");
  content.classList.remove("hidden");

  // Title & ID
  document.getElementById("det-stage").innerText = `${obs.construction_stage || "Processing"} Stage`;
  document.getElementById("det-id").innerText = `OBS-${obs.observation_id.substring(0, 8).toUpperCase()}`;
  document.getElementById("details-score-badge").innerText = `${obs.development_score}`;

  // Progress Bar
  const progressVal = obs.progress !== null ? obs.progress : 0;
  document.getElementById("det-progress-bar").style.width = `${progressVal}%`;
  document.getElementById("det-progress-label").innerText = `${progressVal}% Progress`;

  // Confidence & Timestamp
  const confPct = obs.confidence !== null ? Math.round(obs.confidence * 100) : "--";
  document.getElementById("det-confidence").innerText = `${confPct}%`;
  document.getElementById("det-time").innerText = new Date(obs.timestamp).toLocaleTimeString();

  // Sensors
  const hasSensors = obs.sensor_status === "connected";
  document.getElementById("det-noise").innerText = hasSensors ? `${obs.noise_db} dB` : "-- dB";
  document.getElementById("det-pm25").innerText = hasSensors ? `${obs.dust_pm25} ug/m3` : "-- ug/m3";
  
  const statusBadge = document.getElementById("det-sensor-status");
  statusBadge.className = `badge-status ${obs.sensor_status}`;
  statusBadge.innerText = obs.sensor_status.toUpperCase();

  // RERA permits
  const reraContainer = document.getElementById("det-rera-list");
  const reraProjects = obs.rera_projects || [];
  if (reraProjects.length === 0) {
    reraContainer.innerHTML = `<div class="feed-empty">No RERA projects found within 500m search radius.</div>`;
  } else {
    reraContainer.innerHTML = reraProjects.map(p => {
      const statusClass = p.status.toLowerCase().includes("approved") ? "approved" : 
                          p.status.toLowerCase().includes("disputed") ? "disputed" : "pending";
      return `
        <div class="rera-card">
          <div class="rera-name">${p.name}</div>
          <div class="rera-meta">
            <span>Builder: ${p.builder}</span>
            <span>Dist: ${p.distance}m</span>
            <span class="rera-status ${statusClass}">${p.status}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  // Summary
  document.getElementById("det-summary").innerText = obs.summary || "No reasoning summary provided.";
  
  // Risk Rating
  const riskValEl = document.getElementById("det-risk-val");
  const riskVal = getRiskRating(obs);
  riskValEl.innerText = riskVal;
  riskValEl.className = `risk-value ${riskVal.toLowerCase()}`;
}

function getRiskRating(obs) {
  const summary = (obs.summary || "").toLowerCase();
  const reraProjects = obs.rera_projects || [];
  if (summary.includes("unauthorized") || summary.includes("disputed")) return "HIGH";
  if (obs.sensor_status === "degraded" || reraProjects.length === 0) return "MEDIUM";
  return "LOW";
}

async function submitObservation(payload) {
  const response = await fetch(`${BACKEND_URL}/observation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to process observation");
  }

  const result = await response.json();
  selectedObservationId = result.observation_id;
  await fetchHistory();
  return result;
}

function optionalNumber(id) {
  const value = document.getElementById(id).value.trim();
  return value === "" ? null : Number(value);
}

function createObservationPayload(images, voiceQuery, latitude, longitude, sensorValues = {}) {
  return {
    timestamp: new Date().toISOString(),
    owner_id: ownerId,
    latitude,
    longitude,
    images,
    voice_query: voiceQuery,
    ...sensorValues
  };
}

function getOwnerId() {
  const existingOwnerId = localStorage.getItem(OWNER_STORAGE_KEY);
  if (existingOwnerId) return existingOwnerId;

  const newOwnerId = crypto.randomUUID ? crypto.randomUUID() : `web_${Date.now()}_${Math.random().toString(16).slice(2)}`;
  localStorage.setItem(OWNER_STORAGE_KEY, newOwnerId);
  return newOwnerId;
}

async function handlePhotoUpload(event) {
  event.preventDefault();
  const input = document.getElementById("photo-upload-input");
  const files = Array.from(input.files || []);
  if (files.length === 0) {
    alert("Upload at least one land-side site photo.");
    return;
  }
  if (files.length > 4) {
    alert("Upload a maximum of four photos: North, East, South, and West sides.");
    return;
  }

  const latitude = Number(document.getElementById("upload-latitude").value);
  const longitude = Number(document.getElementById("upload-longitude").value);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    alert("Please provide valid GPS latitude and longitude.");
    return;
  }

  const btn = document.getElementById("btn-submit-upload");
  btn.disabled = true;
  btn.innerHTML = `<span class="btn-icon">...</span> Processing...`;

  try {
    const imageDataUrls = await Promise.all(files.map(fileToDataUrl));
    const noiseDb = optionalNumber("upload-noise");
    const dustPm25 = optionalNumber("upload-pm25");
    const dustPm10 = optionalNumber("upload-pm10");
    const sensorValues = {};

    if (noiseDb !== null) sensorValues.noise_db = noiseDb;
    if (dustPm25 !== null) sensorValues.dust_pm25 = dustPm25;
    if (dustPm10 !== null) sensorValues.dust_pm10 = dustPm10;
    if (Object.keys(sensorValues).length > 0) sensorValues.sensor_timestamp = new Date().toISOString();

    const sideNames = ["North", "East", "South", "West"].slice(0, files.length).join(", ");
    const voiceQuery = document.getElementById("upload-query").value.trim() || `Analyze ${files.length} land-side construction photo(s): ${sideNames}.`;
    await submitObservation(createObservationPayload(
      imageDataUrls,
      voiceQuery,
      latitude,
      longitude,
      sensorValues
    ));
    closeUploadModal();
  } catch (error) {
    console.error("Photo upload failed:", error);
    alert("Photo upload failed. Ensure Backend server (Port 8000) and AI service (Port 8001) are running.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">AI</span> Process Upload`;
  }
}

function openUploadModal() {
  document.getElementById("upload-modal").classList.remove("hidden");
}

function closeUploadModal() {
  document.getElementById("upload-modal").classList.add("hidden");
  document.getElementById("upload-form").reset();
}

function fillCurrentLocation() {
  if (!navigator.geolocation) {
    alert("GPS is not available in this browser. Enter latitude and longitude manually.");
    return;
  }

  const btn = document.getElementById("btn-use-location");
  btn.disabled = true;
  btn.innerText = "Reading GPS...";

  readCurrentPosition().then(
    (position) => {
      document.getElementById("upload-latitude").value = position.coords.latitude.toFixed(7);
      document.getElementById("upload-longitude").value = position.coords.longitude.toFixed(7);
      btn.disabled = false;
      btn.innerText = "Use Phone/Browser GPS";
    }
  ).catch(
    () => {
      alert("Unable to read GPS. Please allow location access or enter coordinates manually.");
      btn.disabled = false;
      btn.innerText = "Use Phone/Browser GPS";
    }
  );
}

function readCurrentPosition() {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      resolve,
      reject,
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  });
}

// Trigger Simulated Scan
async function triggerMockScan() {
  const btn = document.getElementById("btn-trigger-scan");
  btn.disabled = true;
  btn.innerHTML = `<span class="btn-icon">...</span> Processing...`;

  let position;
  try {
    if (!navigator.geolocation) throw new Error("GPS unavailable");
    position = await readCurrentPosition();
  } catch (error) {
    alert("Simulation now needs your device GPS. Use Upload Photo to enter GPS manually if location access is unavailable.");
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">AI</span> Simulate Device Scan`;
    return;
  }

  const latOffset = (Math.random() - 0.5) * 0.0003;
  const lngOffset = (Math.random() - 0.5) * 0.0003;

  const mockPayload = createObservationPayload(
    [createMockConstructionImageDataUrl()],
    "Show construction legality and safety score.",
    position.coords.latitude + latOffset,
    position.coords.longitude + lngOffset
  );

  try {
    const result = await submitObservation(mockPayload);
    console.log("Mock Scan pipeline response:", result);
  } catch (error) {
    console.error("Simulation failed:", error);
    alert("Connection error: Ensure Backend server (Port 8000) is running!");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">AI</span> Simulate Device Scan`;
  }
}

