import time
import os
import sys
import logging
from typing import Callable, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

FLAG_FILE_PATH = "task_done.flag"
POLL_INTERVAL = 3.0
COOLDOWN_PERIOD = 2.0


class NotificationListener:

    def __init__(self, on_task_complete_callback: Callable[[], None], workflow_logger=None) -> None:
        self.on_task_complete_callback = on_task_complete_callback
        self.workflow_logger = workflow_logger
        self.is_listening = False
        self.last_modified_time: Optional[float] = None

    def check_flag_file(self) -> bool:
        if not os.path.exists(FLAG_FILE_PATH):
            return False

        try:
            current_mtime = os.path.getmtime(FLAG_FILE_PATH)

            if self.last_modified_time is None:
                self.last_modified_time = current_mtime
                return False

            if current_mtime > self.last_modified_time:
                self.last_modified_time = current_mtime
                return True

        except OSError as e:
            logger.error(f"Error accessing flag file: {e}")

        return False

    def reset_flag(self) -> None:
        if os.path.exists(FLAG_FILE_PATH):
            try:
                os.remove(FLAG_FILE_PATH)
                self.last_modified_time = None
                logger.debug("Flag file reset.")
            except OSError:
                pass

    def start_listening(self) -> None:
        self.is_listening = True

        if os.path.exists(FLAG_FILE_PATH):
            self.last_modified_time = os.path.getmtime(FLAG_FILE_PATH)
        else:
            self.last_modified_time = None

        logger.info(f"Listening for task completion... (Update '{FLAG_FILE_PATH}')")

        if self.workflow_logger:
            self.workflow_logger.log("Waiting for task completion")

        try:
            while self.is_listening:
                if self.check_flag_file():
                    logger.info("Task completion detected!")

                    if self.workflow_logger:
                        self.workflow_logger.log("Task completed detected")

                    try:
                        self.on_task_complete_callback()
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")

                    time.sleep(COOLDOWN_PERIOD)
                    logger.info("Waiting for next task...")

                    if self.workflow_logger:
                        self.workflow_logger.log("Waiting for task completion")

                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Listener stopped by user.")
            self.stop_listening()

    def stop_listening(self) -> None:
        self.is_listening = False
