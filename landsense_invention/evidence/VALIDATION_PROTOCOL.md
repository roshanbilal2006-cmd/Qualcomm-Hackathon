# LandSense AI: Physical Hardware Validation Protocol

**Document Version:** 1.0.0  
**Target Invention:** Dual-Rate Information-Theoretic Directed Observation Engine (DIT-DOE)  
**Location:** `/landsense_invention/evidence/VALIDATION_PROTOCOL.md`

---

## 1. Objective & Hardware Scope

This document defines the physical hardware-software interface contract between the software controller and the IoT hardware node being constructed by team members.

**Core Principle:** Teammates do **NOT** need to redesign their microcontroller hardware. The existing Arduino Uno / Nano setup with an analog sound sensor (KY-037) and an optical particulate sensor (GP2Y1010 / PM2.5) satisfies all requirements for TRL 4 bench validation.

---

## 2. Hardware Interface Specification

The hardware exposes communication over a standard USB CDC serial connection (default: `COM3` on Windows, `/dev/ttyUSB0` on Linux, baud rate: `9600` or `115200`).

### Standard Telemetry Frame (ASCII CRLF-delimited):
```
<noise_db>,<dust_pm25>,<dust_pm10>,<device_status>\r\n
```
*Example:* `74.2,38.5,65.1,OK\r\n`

---

## 3. Separation of Hardware Capabilities

### A. REQUIRED Capabilities (Must Have for TRL 4 Bench Testing)
1. **Continuous Telemetry Stream:**
   - Transmit valid reading at $1.0\,\text{Hz} \pm 10\%$.
   - Format: 3 numeric float tokens (`noise_db`, `pm25`, `pm10`).
2. **Deterministic Range Limits:**
   - Acoustic noise: $[40.0, 110.0]\,\text{dBA}$.
   - PM2.5 particulate: $[0.0, 500.0]\,\mu\text{g/m}^3$.
   - PM10 particulate: $[0.0, 1000.0]\,\mu\text{g/m}^3$.
3. **Fixed Perimeter Mounting:**
   - Sensor node must be stationary during observation runs at known GPS/cartesian coordinates $(x_{\text{sensor}}, y_{\text{sensor}})$.
4. **Serial Connection Stability:**
   - Survive continuous 30-minute streaming without buffer overflow or MCU crash.

### B. OPTIONAL Capabilities (Improves System Resilience)
1. **Dynamic Sampling Rate Control (Serial Command Ingestion):**
   - Software can send `SET_RATE <Hz>\n` (e.g., `SET_RATE 5` or `SET_RATE 0.2`) to conserve power during steady-state.
2. **On-Board Timestamping:**
   - Arduino tracks relative millisecond tick counter (`millis()`) in serial frame: `<timestamp_ms>,<noise>,<pm25>,<pm10>`.
3. **Hardware Health Ping:**
   - Software sends `PING\n`, hardware replies `PONG,UNO-Q,UPTIME_SEC\n`.

### C. NICE-TO-HAVE Capabilities (Future TRL 5 Deployment)
1. **Micro-SD Offline Blackbox Logging:**
   - Log readings locally in case USB/RF connection drops.
2. **Ambient Weather Ingestion:**
   - Onboard DHT22 or BME280 sensor reporting ambient temperature ($^\circ\text{C}$) and relative humidity ($\%$) for dynamic air absorption correction.
3. **Pneumatic Self-Cleaning Micro-Fan:**
   - Micro-blower pulse to purge dust accumulation from optical chamber.

---

## 4. Software Adapter Interface (`mcp/adapters/sensor/arduino_sensor_adapter.py`)

The existing software adapter already implements the required interface methods:

```python
class SensorProvider(ABC):
    @abstractmethod
    def read(self) -> dict:
        """
        Returns:
            {
                "device_id": str,
                "timestamp": str,  # ISO 8601 UTC
                "noise_db": float,
                "pm25": float,
                "pm10": float
            }
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Returns 'connected' or 'disconnected'."""
        pass
```

---

## 5. Laboratory Bench Test Protocol (TRL 4 Step-by-Step)

```
[Audio Speaker (Test Tones)] ──┐
                               ▼
[Aerosol / Incense Plume]   ──► [Arduino IoT Node (KY-037 + GP2Y1010)]
                                               │
                                               │ USB Serial (9600 baud)
                                               ▼
                               [Snapdragon Laptop (DIT-DOE Controller)]
                                               │
                                               │ Web / LAN Dispatch
                                               ▼
                               [Android Mobile Phone (Directed View)]
```

1. **Step 1: Noise Floor & Zero Calibration:**
   - Place sensor node in quiet room ($<45\,\text{dBA}$).
   - Verify reported `noise_db` matches calibrated sound level meter within $\pm 3\,\text{dBA}$.
2. **Step 2: Step-Response Acoustic Excitation:**
   - Play a 1 kHz sinusoidal tone burst at $85\,\text{dBA}$ from a nearby speaker.
   - Verify software EKF detects innovation anomaly ($|r_t| > 16.0$) within $2.0\,\text{seconds}$.
3. **Step 3: Particulate Response:**
   - Introduce controlled incense or aerosol smoke near the optical sensor.
   - Verify PM2.5 rises above $50\,\mu\text{g/m}^3$.
4. **Step 4: End-to-End Closed-Loop Trigger:**
   - Verify laptop controller triggers `DISPATCH_DIRECTED_INSPECTION` with optimal $(x^*, y^*, \theta^*)$ waypoint.
   - Upload mock photo from Android client.
   - Verify laptop controller successfully logs covariance reduction $>60\%$.
