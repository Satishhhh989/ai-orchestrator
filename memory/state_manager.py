import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class StateManager:

    def __init__(self, state_file: str = "data/state.json") -> None:
        self._state_file = Path(state_file)
        self._state: Dict[str, Any] = {}
        self._metadata: Dict[str, str] = {
            "created_at": datetime.now().isoformat(),
            "last_saved": "",
            "version": "1.0.0",
        }
        logger.info(f"StateManager created (file: {self._state_file})")

    async def initialize(self) -> None:
        if self._state_file.exists():
            try:
                with open(self._state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self._state = data.get("state", {})
                self._metadata = data.get("metadata", self._metadata)

                logger.info(f"Loaded state from {self._state_file} ({len(self._state)} keys)")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load state file: {e}. Starting fresh.")
                self._state = {}
        else:
            logger.info("No existing state file found. Starting with empty state.")

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    async def update(self, key: str, value: Any) -> None:
        self._state[key] = value
        logger.debug(f"State updated: {key}")

    async def delete(self, key: str) -> bool:
        if key in self._state:
            del self._state[key]
            logger.debug(f"State deleted: {key}")
            return True
        return False

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        if prefix:
            return [k for k in self._state.keys() if k.startswith(prefix)]
        return list(self._state.keys())

    async def save_state(self) -> None:
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            self._metadata["last_saved"] = datetime.now().isoformat()

            data = {
                "metadata": self._metadata,
                "state": self._state,
            }

            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"State saved to {self._state_file} ({len(self._state)} keys)")

        except IOError as e:
            logger.error(f"Failed to save state: {e}")

    async def clear(self) -> None:
        self._state.clear()
        logger.info("State cleared.")

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_keys": len(self._state),
            "namespaces": list(
                set(k.split(":")[0] for k in self._state.keys() if ":" in k)
            ),
            "metadata": self._metadata,
        }


class WorkflowLogger:

    def __init__(self, logs_dir: str = "logs") -> None:
        self.logs_dir = Path(logs_dir)
        self.current_log_file: Optional[Path] = None
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def start_new_workflow(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_{timestamp}.log"
        self.current_log_file = self.logs_dir / filename
        logger.info(f"New workflow log created: {self.current_log_file}")

    def log(self, message: str) -> None:
        if not self.current_log_file:
            logger.warning("Attempted to write to WorkflowLogger without an active log file.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        try:
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(formatted_message)
        except OSError as e:
            logger.error(f"Failed to write to workflow log {self.current_log_file}: {e}")

    def get_log_file_path(self) -> Optional[str]:
        if self.current_log_file:
            return str(self.current_log_file.absolute())
        return None
