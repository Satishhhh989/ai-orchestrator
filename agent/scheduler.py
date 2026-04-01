import logging
import sys
import os
import subprocess
import threading
from typing import Callable, Optional
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

logger = logging.getLogger(__name__)


class CronManager:

    def __init__(self, alert_callback: Optional[Callable] = None) -> None:
        self.alert_callback = alert_callback
        self.scheduler = BackgroundScheduler(
            job_defaults={"misfire_grace_time": 30},
            timezone="UTC"
        )
        self.scheduler.start()
        logger.info("[CronManager] Background scheduler started.")

    def _execute_python_payload(self, job_id: str, code: str) -> None:
        logger.info(f"[CronManager] Firing job: {job_id}")
        try:
            script_path = os.path.join(os.getcwd(), f"cron_{job_id}.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120
            )

            output = (result.stdout + result.stderr).strip()

            try:
                os.remove(script_path)
            except Exception:
                pass

            if output and self.alert_callback:
                self.alert_callback(job_id, output)

        except subprocess.TimeoutExpired:
            if self.alert_callback:
                self.alert_callback(job_id, f"Job `{job_id}` timed out after 120 seconds.")
        except Exception as e:
            logger.error(f"[CronManager] Job {job_id} failed: {e}")
            if self.alert_callback:
                self.alert_callback(job_id, f"Job `{job_id}` crashed: {e}")

    def schedule_interval(
        self, job_id: str, code: str, seconds: int = 0, minutes: int = 0, hours: int = 0
    ) -> str:
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"[CronManager] Replaced existing job: {job_id}")

        self.scheduler.add_job(
            func=self._execute_python_payload,
            trigger=IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours),
            args=[job_id, code],
            id=job_id,
            name=job_id,
            replace_existing=True
        )
        total_secs = hours * 3600 + minutes * 60 + seconds
        msg = f"Cron job `{job_id}` scheduled — runs every {total_secs}s."
        logger.info(f"[CronManager] {msg}")
        return msg

    def schedule_cron(
        self, job_id: str, code: str,
        hour: str = "*", minute: str = "*", second: str = "0",
        day_of_week: str = "*"
    ) -> str:
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            func=self._execute_python_payload,
            trigger=CronTrigger(
                hour=hour, minute=minute, second=second, day_of_week=day_of_week
            ),
            args=[job_id, code],
            id=job_id,
            name=job_id,
            replace_existing=True
        )
        msg = f"Cron job `{job_id}` scheduled — {hour}h {minute}m {second}s {day_of_week}."
        logger.info(f"[CronManager] {msg}")
        return msg

    def cancel_job(self, job_id: str) -> str:
        job = self.scheduler.get_job(job_id)
        if job:
            self.scheduler.remove_job(job_id)
            msg = f"Job `{job_id}` cancelled and removed."
        else:
            msg = f"Job `{job_id}` not found."
        logger.info(f"[CronManager] {msg}")
        return msg

    def list_jobs(self) -> str:
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return "No scheduled jobs currently active."

        lines = ["**Active Scheduled Jobs:**\n"]
        for job in jobs:
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "N/A"
            lines.append(f"• `{job.id}` — Next run: `{next_run}`")
        return "\n".join(lines)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("[CronManager] Scheduler stopped.")
