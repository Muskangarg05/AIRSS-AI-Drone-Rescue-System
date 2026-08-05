# main_v2.py — Phase 2 Entry Point (GPS Fixed)
import threading
import time
import cv2

import config
from detector     import SurvivorDetector
from alert        import trigger_alert
from gps_mapper   import GPSMapper
from dashboard    import run_dashboard
from shared_state import state
from main         import StreamReader, SessionLogger, FPSTracker, draw_fps


def detection_loop(stream, detector, mapper, logger):
    fps_tracker     = FPSTracker(window=30)
    frame_number    = 0
    state.is_active = True
    print("[Detection] 🔴 Detection loop started.")

    try:
        while stream.is_running():
            frame = stream.read()
            if frame is None:
                time.sleep(0.01)
                continue

            frame_number += 1
            fps_tracker.tick()
            fps = fps_tracker.get_fps()

            # ── Run Detection ─────────────────
            result = detector.process_frame(frame)

            # ── Push to SharedState ───────────
            state.update_frame(draw_fps(result.annotated_frame, fps))
            state.update_count(result.survivor_count)
            state.update_fps(fps)

            # ── On Survivor Detection ─────────
            if result.was_yolo_run and result.survivor_count > 0:

                # ── Fetch REAL GPS ────────────
                # get_real_gps() tries: Phone GPS → IP Geolocation → Fallback
                lat, lon, address, gps_source = mapper.get_real_gps()

                print(
                    f"[Main] 🔴 ALERT | Frame {frame_number:05d} | "
                    f"Survivors: {result.survivor_count} | "
                    f"GPS: ({lat}, {lon}) | "
                    f"Source: {gps_source} | "
                    f"Time: {result.timestamp}"
                )

                # ── Add Marker to GPS Map ─────
                mapper.add_survivor_marker(
                    lat         = lat,
                    lon         = lon,
                    count       = result.survivor_count,
                    screenshot  = result.screenshot_path,
                    timestamp   = result.timestamp,
                    address     = address,
                    source      = gps_source,
                    confidences = result.confidences,
                )

                # ── Log Entry ─────────────────
                log_entry = {
                    "timestamp"     : result.timestamp,
                    "survivor_count": result.survivor_count,
                    "confidences"   : result.confidences,
                    "screenshot"    : result.screenshot_path,
                    "lat"           : lat,
                    "lon"           : lon,
                    "address"       : address,
                    "gps_source"    : gps_source,
                }
                state.add_log_entry(log_entry)
                state.add_gps_point(lat, lon, log_entry)

                logger.log(
                    timestamp       = result.timestamp,
                    frame_num       = frame_number,
                    survivor_count  = result.survivor_count,
                    confidences     = result.confidences,
                    screenshot_path = result.screenshot_path,
                )

                # ── Fire Voice + Email Alert ──
                # Email now includes GPS coords + Google Maps link
                trigger_alert(
                    survivor_count  = result.survivor_count,
                    screenshot_path = result.screenshot_path,
                    lat             = lat,
                    lon             = lon,
                    address         = address,
                    gps_source      = gps_source,
                )

            # ── Local OpenCV Window ───────────
            cv2.imshow("Drone Feed", result.annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[Main] Q pressed — shutting down...")
                break

    except KeyboardInterrupt:
        print("\n[Detection] Interrupted by user.")

    finally:
        state.is_active = False
        stream.stop()
        cv2.destroyAllWindows()
        print("[Detection] Loop ended.")


def main():
    print("=" * 55)
    print("  AI RESCUE DRONE — PHASE 2 MISSION DASHBOARD")
    print("=" * 55)
    print(f"  Dashboard  → http://localhost:{config.DASHBOARD_PORT}")
    print(f"  Stream URL → {config.STREAM_URL}")
    print("=" * 55)

    # ── Init Components ───────────────────────
    stream   = StreamReader(config.STREAM_URL)
    detector = SurvivorDetector(
        model_path        = config.MODEL_PATH,
        confidence_thresh = config.CONFIDENCE_THRESHOLD,
        frame_skip        = config.FRAME_SKIP,
        input_width       = config.INPUT_WIDTH,
        input_height      = config.INPUT_HEIGHT,
    )
    mapper = GPSMapper()
    logger = SessionLogger(log_dir="logs")

    # ── Start Stream ──────────────────────────
    if not stream.start():
        print("[Main] ❌ Stream failed.")
        print("[Main]    → Set STREAM_URL=0 in .env for laptop webcam")
        print("[Main]    → Set STREAM_URL=http://[phone-ip]:8080/video for phone")
        return

    # ── Launch Flask Dashboard (background) ──
    flask_thread = threading.Thread(
        target = run_dashboard,
        kwargs = {"host": "0.0.0.0", "port": config.DASHBOARD_PORT},
        daemon = True,
    )
    flask_thread.start()
    print(f"[Dashboard] ✅ Open → http://localhost:{config.DASHBOARD_PORT}")

    # ── Run Detection Loop (main thread) ──────
    detection_loop(stream, detector, mapper, logger)


if __name__ == "__main__":
    main()
