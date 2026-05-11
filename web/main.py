import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from scheduler import SchedulerManager
from audio_manager import AudioManager
from timetable_manager import TimetableManager
from config import Config

logger = logging.getLogger(__name__)

app = FastAPI(title="SwiftBell Web Dashboard")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

config = Config()
audio = AudioManager(config)
timetable = TimetableManager(config)
scheduler = SchedulerManager(config, audio, timetable)

scheduler_thread: Optional[threading.Thread] = None
scheduler_running = False


class SchedulerLoop(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = False

    def run(self):
        self.running = True
        last_check = time.time()
        interval = config.get("timetable_check_interval", 300)
        while self.running:
            try:
                scheduler.check_schedule()
                now = time.time()
                if now - last_check > interval:
                    if timetable.has_timetable_changed():
                        timetable.load_timetable()
                        scheduler.load_schedule(timetable.get_events())
                    last_check = now
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(5)

    def stop(self):
        self.running = False


@app.on_event("startup")
def startup():
    try:
        timetable.load_timetable()
        scheduler.load_schedule(timetable.get_events())
        logger.info("Timetable loaded on startup")
    except Exception as e:
        logger.warning(f"Could not load timetable on startup: {e}")


@app.get("/")
def dashboard(request: Request):
    now = datetime.now()
    today = now.strftime("%A").lower()
    all_events = timetable.get_events()
    upcoming = []
    for e in all_events:
        day = e.get("day", "everyday").lower()
        if day not in ("everyday", today):
            continue
        upcoming.append(e)
    upcoming.sort(key=lambda x: x["time"])

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "running": scheduler_running,
            "events": upcoming,
            "current_time": now.strftime("%H:%M:%S"),
            "today": now.strftime("%A"),
        },
    )


@app.get("/api/status")
def api_status():
    now = datetime.now()
    today = now.strftime("%A").lower()
    all_events = timetable.get_events()
    upcoming = []
    for e in all_events:
        day = e.get("day", "everyday").lower()
        if day not in ("everyday", today):
            continue
        upcoming.append(
            {"time": e["time"], "event": e["event"], "type": e.get("type", "announcement")}
        )
    upcoming.sort(key=lambda x: x["time"])

    return {
        "running": scheduler_running,
        "current_time": now.strftime("%H:%M:%S"),
        "today": now.strftime("%A"),
        "upcoming_events": upcoming[:10],
        "audio_playing": audio.current_audio_thread is not None
        and audio.current_audio_thread.is_alive(),
    }


@app.post("/api/start")
def api_start():
    global scheduler_thread, scheduler_running
    if scheduler_running:
        return JSONResponse({"status": "already_running"})
    try:
        timetable.load_timetable()
        scheduler.load_schedule(timetable.get_events())
        loop = SchedulerLoop()
        loop.start()
        scheduler_thread = loop
        scheduler_running = True
        logger.info("Scheduler started via web")
        return JSONResponse({"status": "started"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/api/stop")
def api_stop():
    global scheduler_thread, scheduler_running
    if scheduler_thread:
        scheduler_thread.stop()
        scheduler_thread = None
    scheduler_running = False
    audio.stop_all()
    logger.info("Scheduler stopped via web")
    return JSONResponse({"status": "stopped"})


@app.post("/api/emergency")
def api_emergency():
    logger.warning("Emergency triggered via web")
    siren = config.get("evacuation_siren", "sounds/evacuation.wav")
    msg = config.get(
        "emergency_message",
        "EMERGENCY! Please evacuate the building immediately.",
    )
    audio.play_siren_then_speak(siren, msg, repeat_count=3)
    return JSONResponse({"status": "emergency_triggered"})


@app.post("/api/reload")
def api_reload():
    try:
        timetable.load_timetable()
        scheduler.load_schedule(timetable.get_events())
        return JSONResponse({"status": "reloaded", "count": len(timetable.get_events())})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
