import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class WorkflowEngine:

    def __init__(self, workflow_logger=None) -> None:
        self.workflow_logger = workflow_logger
        self.prompts: List[str] = []
        self.current_index: int = 0
        self.is_running: bool = False
        self.is_paused: bool = False

    def start_workflow(self, prompts: List[str]) -> None:
        self.prompts = prompts
        self.current_index = 0
        self.is_running = True
        self.is_paused = False

        if self.workflow_logger:
            self.workflow_logger.start_new_workflow()
            self.workflow_logger.log("Workflow started")

        logger.info(f"Workflow started with {len(self.prompts)} steps.")

    def get_current_prompt(self) -> Optional[str]:
        if not self.is_running or self.is_finished():
            return None
        return self.prompts[self.current_index]

    def next_step(self) -> Optional[str]:
        if not self.is_running:
            return None

        if self.is_paused:
            logger.info("Workflow is paused. Cannot advance to next step.")
            return None

        self.current_index += 1

        if self.is_finished():
            self.is_running = False
            logger.info("Workflow completed.")
            if self.workflow_logger:
                self.workflow_logger.log("Workflow completed")
            return None

        logger.info(f"Advanced to step {self.current_index + 1}/{len(self.prompts)}")

        prompt = self.prompts[self.current_index]
        if self.workflow_logger:
            self.workflow_logger.log(f"Step {self.current_index}: {prompt}")

        return prompt

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_index,
            "total_steps": len(self.prompts),
            "running": self.is_running,
            "paused": self.is_paused
        }

    def pause(self) -> None:
        if self.is_running and not self.is_paused:
            self.is_paused = True
            logger.info("Workflow paused")
            if self.workflow_logger:
                self.workflow_logger.log("Paused")

    def resume(self) -> None:
        if self.is_running and self.is_paused:
            self.is_paused = False
            logger.info("Workflow resumed")
            if self.workflow_logger:
                self.workflow_logger.log("Resumed")

    def is_finished(self) -> bool:
        return self.current_index >= len(self.prompts)
