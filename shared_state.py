# shared_state.py
import threading
from collections import deque
from datetime    import datetime


class SharedState:
    def __init__(self, max_log_entries: int = 100):
        self._lock           = threading.Lock()
        self.latest_frame    = None
        self.survivor_count  = 0
        self.total_survivors = 0
        self.fps             = 0.0
        self.detection_log   = deque(maxlen=max_log_entries)
        self.gps_points      = []
        self.mission_start   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.is_active       = False
        self.map_html        = None   # Folium map stored as HTML string in memory

    # ── Frame ─────────────────────────────────
    def update_frame(self, frame):
        with self._lock:
            self.latest_frame = frame.copy()

    def get_frame(self):
        with self._lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    # ── Count ─────────────────────────────────
    def update_count(self, count: int):
        with self._lock:
            self.survivor_count = count
            if count > 0:
                self.total_survivors += count

    def get_count(self) -> int:
        with self._lock:
            return self.survivor_count

    # ── FPS ───────────────────────────────────
    def update_fps(self, fps: float):
        with self._lock:
            self.fps = fps

    # ── Detection Log ─────────────────────────
    def add_log_entry(self, entry: dict):
        with self._lock:
            self.detection_log.appendleft(entry)

    def get_log(self) -> list:
        with self._lock:
            return list(self.detection_log)

    # ── GPS Points ────────────────────────────
    def add_gps_point(self, lat: float, lon: float, meta: dict):
        with self._lock:
            self.gps_points.append({"lat": lat, "lon": lon, **meta})

    def get_gps_points(self) -> list:
        with self._lock:
            return list(self.gps_points)

    # ── Map HTML (in-memory) ──────────────────
    def update_map_html(self, html: str):
        with self._lock:
            self.map_html = html

    def get_map_html(self) -> str:
        with self._lock:
            return self.map_html

    # ── Stats Snapshot ────────────────────────
    def get_stats(self) -> dict:
        with self._lock:
            return {
                "survivor_count" : self.survivor_count,
                "total_survivors": self.total_survivors,
                "fps"            : self.fps,
                "mission_start"  : self.mission_start,
                "total_events"   : len(self.detection_log),
                "is_active"      : self.is_active,
            }


# Global shared instance
state = SharedState()
