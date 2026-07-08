const BACKEND_URL = "http://localhost:8000";

let observationsList = [];
let selectedObservationId = null;

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
  fetchHistory();
  
  // Set up refresh timer
  setInterval(fetchHistory, 5000);

  // Bind simulate button
  document.getElementById("btn-trigger-scan").addEventListener("click", triggerMockScan);
});

// Fetch History and Heatmap
async function fetchHistory() {
  try {
    const response = await fetch(`${BACKEND_URL}/history`);
    if (!response.ok) throw new Error("Backend history fetch failed");
    
    const data = await response.json();
    observationsList = data;
    
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
    container.innerHTML = `<div class="feed-empty">No observations scanned yet. Click "Simulate Device Scan" to trigger the Snapdragon local pipeline.</div>`;
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

// Render Pins on Map Canvas
function renderHeatmap() {
  const container = document.getElementById("pins-container");
  container.innerHTML = "";

  if (observationsList.length === 0) return;

  // Find map min/max boundaries dynamically or use relative bounds
  // Center is 12.9716, 77.7500. We will map a +-0.02 range to 0-100% of container size
  const centerLat = 12.9716;
  const centerLng = 77.7500;
  const range = 0.02; // Roughly 2km grid bounds

  observationsList.forEach(obs => {
    // Convert GPS coordinates to grid percentages
    // X axis (Longitude)
    let pctX = 50 + ((obs.longitude - centerLng) / range) * 50;
    // Y axis (Latitude - inverse since CSS top increases downwards)
    let pctY = 50 - ((obs.latitude - centerLat) / range) * 50;

    // Constrain inside map bounds
    pctX = Math.max(5, Math.min(95, pctX));
    pctY = Math.max(5, Math.min(95, pctY));

    const pin = document.createElement("div");
    pin.className = `map-pin ${getPinClass(obs.development_score)}`;
    pin.style.left = `${pctX}%`;
    pin.style.top = `${pctY}%`;
    pin.title = `${obs.construction_stage || "Observation"} (Score: ${obs.development_score})`;
    
    pin.onclick = (e) => {
      e.stopPropagation();
      selectObservation(obs.observation_id);
    };

    container.appendChild(pin);
  });
}

function getPinClass(score) {
  if (score >= 80) return "completed-site";
  if (score >= 50) return "normal-site";
  return "active-site";
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
  document.getElementById("det-pm25").innerText = hasSensors ? `${obs.dust_pm25} µg/m³` : "-- µg/m³";
  
  const statusBadge = document.getElementById("det-sensor-status");
  statusBadge.className = `badge-status ${obs.sensor_status}`;
  statusBadge.innerText = obs.sensor_status.toUpperCase();

  // RERA permits
  const reraContainer = document.getElementById("det-rera-list");
  if (obs.rera_projects.length === 0) {
    reraContainer.innerHTML = `<div class="feed-empty">No RERA projects found within 500m search radius.</div>`;
  } else {
    reraContainer.innerHTML = obs.rera_projects.map(p => {
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
  if (obs.summary.toLowerCase().includes("unauthorized") || obs.summary.toLowerCase().includes("disputed")) return "HIGH";
  if (obs.sensor_status === "degraded" || obs.rera_projects.length === 0) return "MEDIUM";
  return "LOW";
}

// Trigger Simulated Scan
async function triggerMockScan() {
  const btn = document.getElementById("btn-trigger-scan");
  btn.disabled = true;
  btn.innerHTML = `<span class="btn-icon">⏳</span> Processing...`;

  // Alternate locations near Whitefield to test correlation logic:
  // 1. Exact center Whitefield (triggers successful correlation)
  // 2. Outlying Whitefield (fails correlation)
  const isCorrelated = Math.random() > 0.4;
  const latOffset = isCorrelated ? (Math.random() - 0.5) * 0.0003 : (Math.random() - 0.5) * 0.009;
  const lngOffset = isCorrelated ? (Math.random() - 0.5) * 0.0003 : (Math.random() - 0.5) * 0.009;

  const mockPayload = {
    timestamp: new Date().toISOString(),
    latitude: 12.9716 + latOffset,
    longitude: 77.7500 + lngOffset,
    images: ["base64_visual_frame_captured_by_oneplus15_camera_stream_data"],
    voice_query: "Show construction legality and safety score."
  };

  try {
    const response = await fetch(`${BACKEND_URL}/observation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mockPayload)
    });

    if (!response.ok) throw new Error("Failed to post mock scan");

    const result = await response.json();
    console.log("Mock Scan pipeline response:", result);
    
    // Auto-select the newly created observation
    selectedObservationId = result.observation_id;
    await fetchHistory();
  } catch (error) {
    console.error("Simulation failed:", error);
    alert("Connection error: Ensure Backend server (Port 8000) is running!");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">⚡</span> Simulate Device Scan`;
  }
}
