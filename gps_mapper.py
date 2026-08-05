# gps_mapper.py — COMPLETE UPDATED VERSION
# Real GPS: IP Webcam API → IP Geolocation → Fallback
# Coordinates shown on map + email + detection frame

import io
import time
import random
import requests
import folium
from folium.plugins import MarkerCluster, Fullscreen, MiniMap
from datetime import datetime

import config
from shared_state import state


class GPSMapper:

    def __init__(self):
        self._marker_count   = 0
        self._map            = self._build_base_map()
        self._cluster        = MarkerCluster(name="Survivors").add_to(self._map)
        self._last_known_lat = config.BASE_LOCATION[0]
        self._last_known_lon = config.BASE_LOCATION[1]
        self._last_known_address = "Unknown"
        print(f"[GPSMapper] ✅ Map initialized. Base: {config.BASE_LOCATION}")
        self._render_to_state()

    # ══════════════════════════════════════════
    # REAL GPS — 3-Tier Fetch
    # ══════════════════════════════════════════

    def get_real_gps(self) -> tuple:
        """
        Fetches real GPS coordinates using 3-tier fallback:
          1. IP Webcam Android app GPS sensor API (most accurate)
          2. IP-based geolocation via ip-api.com (city-level, free)
          3. config.BASE_LOCATION (hardcoded fallback)

        Returns:
            (lat, lon, address, source) tuple
        """

        # ── Tier 1: IP Webcam GPS Sensor ─────
        if isinstance(config.STREAM_URL, str) and config.STREAM_URL.startswith("http"):
            lat, lon, address = self._fetch_ipwebcam_gps()
            if lat is not None:
                self._last_known_lat     = lat
                self._last_known_lon     = lon
                self._last_known_address = address
                return lat, lon, address, "Phone GPS"

        # ── Tier 2: IP Geolocation ────────────
        lat, lon, address = self._fetch_ip_geolocation()
        if lat is not None:
            self._last_known_lat     = lat
            self._last_known_lon     = lon
            self._last_known_address = address
            return lat, lon, address, "IP Geolocation"

        # ── Tier 3: Hardcoded Fallback ────────
        print("[GPSMapper] ⚠️  Using BASE_LOCATION fallback.")
        return (
            self._last_known_lat,
            self._last_known_lon,
            self._last_known_address or "Base Location",
            "Fallback"
        )

    def _fetch_ipwebcam_gps(self):
        """
        Fetches GPS from IP Webcam app sensor API.
        Endpoint: http://[IP]:8080/sensors.json?sense=gps

        IP Webcam GPS JSON format:
        {
          "gps": {
            "data": [[timestamp, [lat, lon, altitude, accuracy, bearing, speed]]]
          }
        }
        """
        try:
            base = config.STREAM_URL.rsplit("/", 1)[0]   # Remove /video
            url  = f"{base}/sensors.json?sense=gps"
            resp = requests.get(url, timeout=3)

            if resp.status_code == 200:
                data     = resp.json()
                gps_data = data.get("gps", {}).get("data", [])

                if gps_data:
                    latest  = gps_data[-1][1]   # Last GPS reading values
                    lat     = round(float(latest[0]), 6)
                    lon     = round(float(latest[1]), 6)
                    address = self._reverse_geocode(lat, lon)
                    print(f"[GPSMapper] 📡 Phone GPS → ({lat}, {lon})")
                    return lat, lon, address

        except requests.exceptions.ConnectionError:
            print("[GPSMapper] ⚠️  IP Webcam GPS not reachable.")
        except Exception as e:
            print(f"[GPSMapper] ⚠️  IP Webcam GPS error: {e}")

        return None, None, None

    def _fetch_ip_geolocation(self):
        """
        Fetches approximate location from ip-api.com (free, no API key).
        Accuracy: city-level (~1–5 km radius).
        """
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=5)

            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    lat     = round(float(data["lat"]), 6)
                    lon     = round(float(data["lon"]), 6)
                    address = (
                        f"{data.get('city', '')}, "
                        f"{data.get('regionName', '')}, "
                        f"{data.get('country', '')}"
                    ).strip(", ")
                    print(f"[GPSMapper] 🌐 IP Geolocation → ({lat}, {lon}) — {address}")
                    return lat, lon, address

        except Exception as e:
            print(f"[GPSMapper] ⚠️  IP Geolocation error: {e}")

        return None, None, None

    def _reverse_geocode(self, lat: float, lon: float) -> str:
        """
        Converts lat/lon to human-readable address using Nominatim (free).
        """
        try:
            url  = (
                f"https://nominatim.openstreetmap.org/reverse"
                f"?lat={lat}&lon={lon}&format=json"
            )
            headers = {"User-Agent": "DroneRescueSystem/1.0"}
            resp    = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("display_name", f"{lat}, {lon}")
        except Exception:
            pass
        return f"{lat}, {lon}"

    # ══════════════════════════════════════════
    # MAP MARKER
    # ══════════════════════════════════════════

    def add_survivor_marker(
        self,
        lat        : float,
        lon        : float,
        count      : int,
        screenshot : str,
        timestamp  : str,
        address    : str   = "",
        source     : str   = "",
        confidences: list  = None,
    ):
        self._marker_count += 1
        conf_str = ", ".join(
            str(round(c, 2)) for c in (confidences or [])
        ) or "N/A"
        address_display = address or f"{lat}, {lon}"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif;width:250px;">
            <div style="background:#e74c3c;color:white;padding:8px;
                        border-radius:6px 6px 0 0;text-align:center;">
                <b>🚨 SURVIVOR ALERT #{self._marker_count}</b>
            </div>
            <div style="padding:10px;border:1px solid #ddd;
                        border-radius:0 0 6px 6px;font-size:12px;">
                <p><b>👥 Survivors:</b> {count}</p>
                <p><b>🕒 Time:</b> {timestamp}</p>
                <p><b>📍 Lat:</b> {lat}</p>
                <p><b>📍 Lon:</b> {lon}</p>
                <p><b>🏠 Address:</b> {address_display[:60]}...</p>
                <p><b>🛰️ Source:</b> {source}</p>
                <p><b>🎯 Confidence:</b> {conf_str}</p>
            </div>
        </div>
        """

        folium.Marker(
            location = [lat, lon],
            popup    = folium.Popup(popup_html, max_width=260),
            tooltip  = f"⚠️ {count} Survivor(s) — {timestamp}",
            icon     = folium.Icon(color="red", icon="user", prefix="fa"),
        ).add_to(self._cluster)

        folium.Circle(
            location     = [lat, lon],
            radius       = 15,
            color        = "#e74c3c",
            fill         = True,
            fill_opacity = 0.15,
            tooltip      = f"Detection Zone #{self._marker_count}",
        ).add_to(self._map)

        print(
            f"[GPSMapper] 📍 Marker #{self._marker_count} → "
            f"({lat}, {lon}) | {count} survivor(s) | {source}"
        )
        self._render_to_state()

    def _build_base_map(self) -> folium.Map:
        m = folium.Map(
            location   = config.BASE_LOCATION,
            zoom_start = 15,
            tiles      = "OpenStreetMap",
        )
        folium.TileLayer(
            tiles   = (
                "https://server.arcgisonline.com/ArcGIS/rest/"
                "services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            ),
            attr    = "Esri",
            name    = "Satellite View",
            overlay = False,
            control = True,
        ).add_to(m)
        Fullscreen(position="topright").add_to(m)
        MiniMap(toggle_display=True).add_to(m)
        folium.LayerControl().add_to(m)
        folium.Marker(
            location = config.BASE_LOCATION,
            popup    = folium.Popup("<b>🚁 Operation HQ</b>", max_width=200),
            tooltip  = "Operation HQ",
            icon     = folium.Icon(color="blue", icon="home", prefix="fa"),
        ).add_to(m)
        return m

    def _render_to_state(self):
        try:
            buf      = io.BytesIO()
            self._map.save(buf, close_file=False)
            html_str = buf.getvalue().decode("utf-8")
            state.update_map_html(html_str)
        except Exception as e:
            print(f"[GPSMapper] ⚠️  Map render error: {e}")

    def get_marker_count(self) -> int:
        return self._marker_count
