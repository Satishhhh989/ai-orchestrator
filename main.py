import asyncio
import os
import signal
import sys
import logging
import threading

if sys.platform == "win32":
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr is not None:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from bot.telegram_bot import TelegramController
from memory.state_manager import WorkflowLogger
from orchestrator.workflow_engine import WorkflowEngine
from agent.executor import Executor
from listener.notification_listener import NotificationListener
from agent.ai_controller import AIController
from agent.scheduler import CronManager


def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/system.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handlers = []

    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    logging.basicConfig(level=logging.INFO, handlers=handlers)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)


async def main() -> None:
    print()
    print("=" * 50)
    print("  AI Workflow Orchestrator Starting...")
    print("=" * 50)
    print()

    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Environment variables loaded")

    workflow_logger = WorkflowLogger()
    logger.info("WorkflowLogger initialized")

    engine = WorkflowEngine(workflow_logger=workflow_logger)
    executor = Executor(workflow_logger=workflow_logger)
    ai_controller = AIController(workflow_logger=workflow_logger)
    logger.info("Core modules initialized")

    cron_manager = CronManager()
    logger.info("CronManager started")

    try:
        controller = TelegramController(
            workflow_logger=workflow_logger,
            engine=engine,
            executor=executor,
            ai_controller=ai_controller,
            cron_manager=cron_manager
        )
    except ValueError as e:
        print(f"\n[ERROR] Configuration error: {e}")
        print("   Please check your .env file and try again.\n")
        sys.exit(1)

    main_loop = asyncio.get_running_loop()

    def cron_alert_callback(job_id: str, output: str) -> None:
        msg = f"**Cron Job `{job_id}` fired:**\n```\n{output[:3500]}\n```"
        asyncio.run_coroutine_threadsafe(
            controller.send_message(msg), main_loop
        )

    cron_manager.alert_callback = cron_alert_callback
    logger.info("CronManager alert callback wired to Telegram")

    def on_task_complete() -> None:
        if not engine.is_running or engine.is_paused:
            return

        next_prompt = engine.next_step()

        if next_prompt is None:
            workflow_logger.log("Workflow fully completed")
            asyncio.run_coroutine_threadsafe(
                controller.send_message("Workflow completed"), main_loop
            )
            return

        success = executor.send_prompt(next_prompt)
        if success:
            workflow_logger.log(f"Next step executed: {next_prompt}")
            asyncio.run_coroutine_threadsafe(
                controller.send_message("Next step executed"), main_loop
            )
        else:
            workflow_logger.log("Failed to execute next step")
            asyncio.run_coroutine_threadsafe(
                controller.send_message("Failed to execute next step"), main_loop
            )

    listener = NotificationListener(
        on_task_complete_callback=on_task_complete,
        workflow_logger=workflow_logger
    )
    listener_thread = threading.Thread(target=listener.start_listening, daemon=True)
    listener_thread.start()
    logger.info("Listener background thread started")

    shutdown_event = asyncio.Event()

    def handle_signal(signum, frame):
        print("\n[!] Received shutdown signal...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        await controller.start()
        await shutdown_event.wait()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        cron_manager.shutdown()
        await controller.stop()
        print("\nAI Workflow Orchestrator stopped. Goodbye!\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
        sys.exit(0)
