import os
import time
import logging
import pyautogui
from typing import Optional

logger = logging.getLogger(__name__)

INPUT_BOX_X = 500
INPUT_BOX_Y = 500
TYPE_DELAY = 0.02
CLICK_DELAY = 1.0


class Executor:

    def __init__(self, workflow_logger=None) -> None:
        self.workflow_logger = workflow_logger

    def focus_window(self) -> bool:
        try:
            logger.info(f"Targeting input box at ({INPUT_BOX_X}, {INPUT_BOX_Y})")
            pyautogui.click(x=INPUT_BOX_X, y=INPUT_BOX_Y)
            time.sleep(CLICK_DELAY)
            return True
        except Exception as e:
            logger.error(f"Error focusing window: {e}")
            return False

    def clear_input(self) -> bool:
        try:
            logger.info("Clearing input box")
            if not self.focus_window():
                return False
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)
            pyautogui.press("backspace")
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Error clearing input box: {e}")
            return False

    def send_prompt(self, prompt: str) -> bool:
        if not prompt or not prompt.strip():
            logger.warning("Prompt is empty. Doing nothing.")
            return False

        try:
            msg = f"Sending prompt: {prompt[:50]}..."
            logger.info(msg)

            if self.workflow_logger:
                self.workflow_logger.log(f"Sending prompt: {prompt[:50]}...")

            if not self.focus_window():
                return False

            time.sleep(0.5)
            pyautogui.typewrite(prompt, interval=TYPE_DELAY)
            pyautogui.press("enter")

            logger.info("Prompt sent successfully [OK]")

            if self.workflow_logger:
                self.workflow_logger.log("Prompt sent successfully")

            return True

        except Exception as e:
            logger.error(f"Error sending prompt: {e} [FAIL]")
            if self.workflow_logger:
                self.workflow_logger.log(f"Error: {e}")
            return False

    def take_screenshot(self) -> Optional[str]:
        filename = "screenshot.png"
        try:
            logger.info("Taking full screen screenshot...")
            if self.workflow_logger:
                self.workflow_logger.log("Action: Taking screenshot")

            try:
                import mss
                with mss.mss() as sct:
                    sct.shot(output=filename)
            except ImportError:
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)

            logger.info(f"Screenshot saved to {filename} [OK]")
            return filename

        except OSError as e:
            logger.error(f"Failed to save screenshot: {e} [FAIL]")
            if self.workflow_logger:
                self.workflow_logger.log(f"Error saving screenshot: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error taking screenshot: {e} [FAIL]")
            return None
