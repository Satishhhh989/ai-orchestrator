import os
import sys
import io
import logging
import subprocess
import tempfile
from datetime import datetime
from typing import Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logger = logging.getLogger(__name__)


def is_authorized(update: Update) -> bool:
    authorized_id = int(os.getenv("USER_ID", "0"))
    sender_id = update.effective_user.id
    sender_name = update.effective_user.full_name

    if sender_id != authorized_id:
        logger.warning(
            f"[BLOCKED] Unauthorized access attempt | "
            f"User: {sender_name} (ID: {sender_id}) | "
            f"Message: {update.message.text if update.message else 'N/A'}"
        )
        return False

    return True


class TelegramController:

    def __init__(self, workflow_logger=None, engine=None, executor=None, ai_controller=None, cron_manager=None) -> None:
        load_dotenv()

        self.workflow_logger = workflow_logger
        self.engine = engine
        self.executor = executor
        self.ai_controller = ai_controller
        self.cron_manager = cron_manager

        self.token: str = os.getenv("TELEGRAM_TOKEN", "")
        self.user_id: int = int(os.getenv("USER_ID", "0"))
        self._application: Optional[Application] = None

        self.transfer_dir = os.path.join(os.getcwd(), "transfer")
        os.makedirs(self.transfer_dir, exist_ok=True)

        if not self.token:
            logger.error("[ERROR] TELEGRAM_TOKEN is not set. Bot cannot start.")
            raise ValueError("TELEGRAM_TOKEN environment variable is required. Set it in your .env file.")

        if self.user_id == 0:
            logger.error("[ERROR] USER_ID is not set. Bot cannot start.")
            raise ValueError("USER_ID environment variable is required. Set it in your .env file.")

        logger.info(f"[OK] TelegramController initialized | Authorized user ID: {self.user_id}")

    async def send_message(self, text: str) -> None:
        if self._application and self.user_id:
            try:
                await self._application.bot.send_message(
                    chat_id=self.user_id,
                    text=text,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"[ERROR] Failed to send message: {e}")

    async def _flush_transfer_folder(self, update: Update) -> None:
        if not os.path.exists(self.transfer_dir):
            return

        files = [f for f in os.listdir(self.transfer_dir) if os.path.isfile(os.path.join(self.transfer_dir, f))]
        if not files:
            return

        logger.info(f"[OUTBOX] Flushing {len(files)} files to user...")
        for filename in files:
            file_path = os.path.join(self.transfer_dir, filename)
            try:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    with open(file_path, "rb") as f:
                        await update.message.reply_photo(photo=f, caption=f"Generated: `{filename}`", parse_mode="Markdown")
                else:
                    with open(file_path, "rb") as f:
                        await update.message.reply_document(document=f, caption=f"Generated: `{filename}`", parse_mode="Markdown")
                os.remove(file_path)
            except Exception as e:
                logger.error(f"[ERROR] Failed to send {filename}: {e}")

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /start received from {update.effective_user.full_name}")
        await update.message.reply_text("System is online")

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /status received from {update.effective_user.full_name}")

        if not self.engine:
            await update.message.reply_text("System running. Engine not connected.")
            return

        status = self.engine.get_status()
        running = status.get("running", False)
        paused = status.get("paused", False)
        current = status.get("current_step", 0) + 1
        total = status.get("total_steps", 0)

        reply_text = f"Step {current}/{total} | Running: {running} | Paused: {paused}"
        await update.message.reply_text(reply_text)

    async def _cmd_startflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /startflow received from {update.effective_user.full_name}")

        if not self.engine or not self.executor:
            await update.message.reply_text("Engine or Executor not connected")
            return

        prompts = ["Step 1", "Step 2", "Step 3"]
        self.engine.start_workflow(prompts)

        first_prompt = self.engine.get_current_prompt()
        if first_prompt:
            success = self.executor.send_prompt(first_prompt)
            if success:
                if self.workflow_logger:
                    self.workflow_logger.log(f"Started flow and executed: {first_prompt}")
                await update.message.reply_text("Workflow started and first step executed")
            else:
                await update.message.reply_text("Workflow started but failed to send first step")
        else:
            await update.message.reply_text("Workflow started but no prompts available.")

    async def _cmd_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /pause received from {update.effective_user.full_name}")

        if self.engine:
            self.engine.pause()
            if self.workflow_logger:
                self.workflow_logger.log("Paused via Telegram")

        await update.message.reply_text("Workflow paused")

    async def _cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /resume received from {update.effective_user.full_name}")

        if self.engine:
            self.engine.resume()
            if self.workflow_logger:
                self.workflow_logger.log("Resumed via Telegram")

        await update.message.reply_text("Workflow resumed")

    async def _cmd_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /logs received from {update.effective_user.full_name}")

        if not self.workflow_logger:
            await update.message.reply_text("Logger is not configured.")
            return

        log_file = self.workflow_logger.get_log_file_path()

        if log_file and os.path.exists(log_file):
            try:
                with open(log_file, "rb") as f:
                    await update.message.reply_document(f)
            except IOError as e:
                logger.error(f"[ERROR] Failed to read log file: {e}")
                await update.message.reply_text("Failed to read log file. Check console.")
        else:
            await update.message.reply_text("No logs available")

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return

        help_text = (
            "**AI Workflow Orchestrator — Help**\n\n"
            "**Natural Language**\n"
            "Just type anything! I will interpret it as a system command, "
            "Python script, or web scraping task.\n\n"
            "**Commands**\n"
            "- `/status` - Check engine status\n"
            "- `/startflow` - Start a workflow\n"
            "- `/pause` / `/resume` - Control workflow\n"
            "- `/logs` - Get current execution logs\n"
            "- `/desktop` - Start interactive Remote Desktop\n"
            "- `/type <text>` - Type text remotely\n"
            "- `/enter` - Press Enter key\n"
            "- `/copy` - Copy clipboard from remote\n"
            "- `/paste <text>` - Paste text remotely\n"
            "- `/jobs` - List background scheduled tasks\n"
            "- `/workflows` - List defined workflows\n"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def _cmd_workflows(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return

        if not self.engine:
            await update.message.reply_text("Engine not connected.")
            return

        workflows = self.engine.list_workflows() if hasattr(self.engine, "list_workflows") else ["No workflows discovered"]
        text = "**Available Workflows:**\n" + "\n".join([f"- `{w}`" for w in workflows])
        await update.message.reply_text(text, parse_mode="Markdown")

    def _make_desktop_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Up", callback_data="rd_up")],
            [
                InlineKeyboardButton("Left", callback_data="rd_left"),
                InlineKeyboardButton("Click", callback_data="rd_click"),
                InlineKeyboardButton("Right", callback_data="rd_right"),
            ],
            [InlineKeyboardButton("Down", callback_data="rd_down")],
            [
                InlineKeyboardButton("Refresh", callback_data="rd_refresh"),
                InlineKeyboardButton("Close", callback_data="rd_close"),
            ],
        ])

    def _capture_screen_bytes(self) -> bytes:
        try:
            import mss
            import pyautogui
            from PIL import Image, ImageDraw

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX").convert("RGB")

                draw = ImageDraw.Draw(img)
                mx, my = pyautogui.position()
                rx = mx - monitor["left"]
                ry = my - monitor["top"]

                r = 10
                draw.ellipse((rx - r - 1, ry - r - 1, rx + r + 1, ry + r + 1), fill="black")
                draw.ellipse((rx - r, ry - r, rx + r, ry + r), fill="#FFF000", outline="black", width=2)
                draw.line((rx - r*2, ry, rx + r*2, ry), fill="black", width=3)
                draw.line((rx - r*2 + 1, ry, rx + r*2 - 1, ry), fill="#FFF000", width=1)
                draw.line((rx, ry - r*2, rx, ry + r*2), fill="black", width=3)
                draw.line((rx, ry - r*2 + 1, rx, ry + r*2 - 1), fill="#FFF000", width=1)

                label = f"Cursor: {mx}, {my}"
                draw.text((rx + 15, ry + 15), label, fill="white", stroke_fill="black", stroke_width=2)

                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return buf.getvalue()
        except Exception as e:
            logger.error(f"[Desktop] Synthetic cursor capture failed: {e}")
            return b""

    async def _cmd_desktop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return

        logger.info(f"[CMD] /desktop initiated by {update.effective_user.full_name}")
        await update.message.reply_text("Initiating Remote Desktop stream...")

        screen_bytes = self._capture_screen_bytes()
        if not screen_bytes:
            await update.message.reply_text("Failed to capture screen. Is mss installed?")
            return

        await update.message.reply_photo(
            photo=screen_bytes,
            caption="**Remote Desktop Active** — Use controls to navigate.",
            parse_mode="Markdown",
            reply_markup=self._make_desktop_keyboard()
        )

    async def _handle_desktop_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        action = query.data
        STEP = 50

        if action == "rd_close":
            await query.edit_message_caption(caption="Remote Desktop session closed.")
            return

        try:
            import pyautogui
            pyautogui.FAILSAFE = False

            if action == "rd_up":
                pyautogui.moveRel(0, -STEP)
            elif action == "rd_down":
                pyautogui.moveRel(0, STEP)
            elif action == "rd_left":
                pyautogui.moveRel(-STEP, 0)
            elif action == "rd_right":
                pyautogui.moveRel(STEP, 0)
            elif action == "rd_click":
                pyautogui.click()
        except Exception as e:
            await query.edit_message_caption(caption=f"Control error: {e}")
            return

        screen_bytes = self._capture_screen_bytes()
        if screen_bytes:
            try:
                await query.edit_message_media(
                    media=InputMediaPhoto(
                        media=screen_bytes,
                        caption="**Remote Desktop Active** — Use controls to navigate.",
                        parse_mode="Markdown",
                    ),
                    reply_markup=self._make_desktop_keyboard()
                )
            except Exception as e:
                logger.warning(f"[Desktop] Frame refresh skipped: {e}")

    async def _cmd_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return

        args = context.args
        if not args:
            await update.message.reply_text("Usage: /type <text to type>")
            return

        text_to_type = " ".join(args)
        try:
            import pyautogui
            pyautogui.write(text_to_type, interval=0.01)
            await update.message.reply_text(f"Typed: `{text_to_type}`", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Typing error: {e}")

    async def _cmd_enter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        try:
            import pyautogui
            pyautogui.press('enter')
            await update.message.reply_text("Pressed `Enter`", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Keyboard error: {e}")

    async def _cmd_copy(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        try:
            import pyautogui
            import pyperclip
            import time
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            clip_text = pyperclip.paste()
            if clip_text:
                await update.message.reply_text(f"Copied text:\n`{clip_text}`", parse_mode="Markdown")
            else:
                await update.message.reply_text("Clipboard is empty.")
        except Exception as e:
            await update.message.reply_text(f"Copy error: {e}")

    async def _cmd_paste(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return

        args = context.args
        try:
            import pyautogui
            import pyperclip
            import time

            if args:
                text_to_paste = " ".join(args)
                pyperclip.copy(text_to_paste)
                time.sleep(0.2)

            pyautogui.hotkey('ctrl', 'v')
            await update.message.reply_text("Pasted!", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Paste error: {e}")

    async def _cmd_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return
        logger.info(f"[CMD] /jobs received from {update.effective_user.full_name}")

        if not self.cron_manager:
            await update.message.reply_text("Scheduler is not connected.")
            return

        result = self.cron_manager.list_jobs()
        await update.message.reply_text(result, parse_mode="Markdown")

    async def _handle_unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_authorized(update):
            return

        user_text = update.message.text
        logger.info(f"[MSG] AI processing: {user_text[:80]}")

        if not self.ai_controller:
            await update.message.reply_text("My AI core is not connected. Use command buttons.")
            return

        try:
            await update.message.chat.send_action(action="typing")
        except:
            pass

        intent = self.ai_controller.process_message(user_text)

        reply_msg = intent.get("reply", "Understood.")
        action = intent.get("action", "none")
        command = intent.get("command", "")
        job_id = intent.get("job_id", "")
        interval_seconds = int(intent.get("interval_seconds", 0))
        interval_minutes = int(intent.get("interval_minutes", 0))
        interval_hours = int(intent.get("interval_hours", 0))

        await update.message.reply_text(reply_msg)

        if action == "screenshot":
            if not self.executor:
                await update.message.reply_text("Executor module is missing. Cannot take screenshot.")
            else:
                img_path = self.executor.take_screenshot()
                if img_path and os.path.exists(img_path):
                    with open(img_path, "rb") as f:
                        await update.message.reply_photo(photo=f)
                else:
                    await update.message.reply_text("Failed to capture screenshot")

        elif action == "execute_powershell" and command:
            logger.warning("[UNRESTRICTED] Executing PowerShell")
            if self.workflow_logger:
                self.workflow_logger.log(f"AI PowerShell: {command}")
            try:
                process = subprocess.run(
                    ["powershell.exe", "-Command", command],
                    capture_output=True, text=True, timeout=120
                )
                output = process.stdout + process.stderr
                if output.strip():
                    truncated = output[:4000] + "\n...[truncated]" if len(output) > 4000 else output
                    await update.message.reply_text(f"```\n{truncated}\n```", parse_mode="Markdown")
                else:
                    await update.message.reply_text("PowerShell executed. (No output)")
            except subprocess.TimeoutExpired:
                await update.message.reply_text("PowerShell timed out after 120s.")
            except Exception as e:
                await update.message.reply_text(f"PowerShell failed: {e}")

        elif action in ("execute_python", "web_scrape") and command:
            label = "Web Scrape" if action == "web_scrape" else "Python Script"
            logger.warning(f"[UNRESTRICTED] Executing {label}")
            if self.workflow_logger:
                self.workflow_logger.log(f"AI {label} requested.")
            try:
                script_path = os.path.join(os.getcwd(), "agent_payload.py")
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(command)
                process = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True, text=True, timeout=180
                )
                output = process.stdout + process.stderr
                if output.strip():
                    truncated = output[:4000] + "\n...[truncated]" if len(output) > 4000 else output
                    await update.message.reply_text(f"```\n{truncated}\n```", parse_mode="Markdown")
                else:
                    await update.message.reply_text(f"{label} executed. (No console output)")
                try:
                    os.remove(script_path)
                except Exception:
                    pass
            except subprocess.TimeoutExpired:
                await update.message.reply_text(f"{label} timed out after 180s.")
            except Exception as e:
                await update.message.reply_text(f"{label} failed: {e}")

        elif action == "schedule_task" and command and job_id:
            if not self.cron_manager:
                await update.message.reply_text("Scheduler not connected.")
            else:
                result = self.cron_manager.schedule_interval(
                    job_id=job_id, code=command,
                    seconds=interval_seconds, minutes=interval_minutes, hours=interval_hours
                )
                await update.message.reply_text(result, parse_mode="Markdown")

        elif action == "cancel_job" and job_id:
            if not self.cron_manager:
                await update.message.reply_text("Scheduler not connected.")
            else:
                result = self.cron_manager.cancel_job(job_id)
                await update.message.reply_text(result, parse_mode="Markdown")

        elif action == "list_jobs":
            if not self.cron_manager:
                await update.message.reply_text("Scheduler not connected.")
            else:
                result = self.cron_manager.list_jobs()
                await update.message.reply_text(result, parse_mode="Markdown")

        elif action == "start_workflow":
            await self._cmd_startflow(update, context)

        elif action == "none":
            pass

        else:
            logger.warning(f"AI returned unknown action: {action}")

        await self._flush_transfer_folder(update)

    def _register_handlers(self, app: Application) -> None:
        app.add_handler(CommandHandler("start", self._cmd_start))
        app.add_handler(CommandHandler("status", self._cmd_status))
        app.add_handler(CommandHandler("startflow", self._cmd_startflow))
        app.add_handler(CommandHandler("pause", self._cmd_pause))
        app.add_handler(CommandHandler("resume", self._cmd_resume))
        app.add_handler(CommandHandler("logs", self._cmd_logs))
        app.add_handler(CommandHandler("desktop", self._cmd_desktop))
        app.add_handler(CommandHandler("type", self._cmd_type))
        app.add_handler(CommandHandler("enter", self._cmd_enter))
        app.add_handler(CommandHandler("copy", self._cmd_copy))
        app.add_handler(CommandHandler("paste", self._cmd_paste))
        app.add_handler(CommandHandler("jobs", self._cmd_jobs))
        app.add_handler(CommandHandler("help", self._cmd_help))
        app.add_handler(CommandHandler("workflows", self._cmd_workflows))

        app.add_handler(CallbackQueryHandler(
            self._handle_desktop_callback, pattern="^rd_"
        ))

        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_unknown)
        )

        logger.info("[OK] All command handlers registered")

    async def start(self) -> None:
        logger.info("Building Telegram bot application...")

        self._application = Application.builder().token(self.token).build()
        self._register_handlers(self._application)

        logger.info("Telegram bot starting -- polling for updates...")
        print()
        print("=" * 50)
        print("  Telegram Bot is LIVE")
        print(f"  Listening for commands...")
        print(f"  Authorized user: {self.user_id}")
        print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print()

        await self._application.initialize()
        await self._application.start()
        await self._application.updater.start_polling(drop_pending_updates=True)

        await self.send_message("System is online and ready.")

    async def stop(self) -> None:
        if self._application:
            logger.info("Stopping Telegram bot...")
            await self._application.updater.stop()
            await self._application.stop()
            await self._application.shutdown()
            logger.info("Telegram bot stopped.")
