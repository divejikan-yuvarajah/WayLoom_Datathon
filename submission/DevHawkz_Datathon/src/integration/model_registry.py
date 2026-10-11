"""Idempotent registry that never accepts caller-controlled artifact paths."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.integration.models import ModelLoadResponse
from src.integration.privacy import PrivacyError, assert_not_protected_path


MODEL_NAMES = ("task1_service", "task1_late", "task2a_total", "task2a_chilled_or_pipeline")


class ModelRegistryError(RuntimeError):
    """A configured registry operation failed without exposing its path."""


class ModelRegistry:
    def __init__(self, config: dict[str, Any]):
        self.mode = str(config.get("mode", "synthetic_demo"))
        self._model_config = dict(config.get("models") or {})
        self._states = {name: "not_loaded" for name in MODEL_NAMES}
        self._loaded = False

    @property
    def states(self) -> dict[str, str]:
        return dict(self._states)

    def load(self) -> ModelLoadResponse:
        if self._loaded:
            return self._response("already_loaded")
        if self.mode == "synthetic_demo":
            self._states = {name: "synthetic" for name in MODEL_NAMES}
            self._loaded = True
            return self._response("loaded")
        if self.mode != "private_local":
            raise ModelRegistryError("Unsupported integration mode.")
        if not self._private_local_opted_in():
            raise ModelRegistryError("Private-local model loading is disabled.")
        configured = self._model_config.get("configured_artifacts") or {}
        if set(configured) != set(MODEL_NAMES):
            self._states = {name: "error" for name in MODEL_NAMES}
            raise ModelRegistryError("Preconfigured model artifacts are unavailable.")
        try:
            for name in MODEL_NAMES:
                path = assert_not_protected_path(Path(str(configured[name])))
                if not path.exists():
                    raise FileNotFoundError
        except (OSError, PrivacyError):
            self._states = {name: "error" for name in MODEL_NAMES}
            raise ModelRegistryError("Preconfigured model artifacts are unavailable.") from None
        self._states = {name: "loaded" for name in MODEL_NAMES}
        self._loaded = True
        return self._response("loaded")

    def _private_local_opted_in(self) -> bool:
        return (
            self._model_config.get("allow_real_model_loading") is True
            and os.environ.get("WAYLOOM_INTEGRATION_MODE") == "private_local"
            and os.environ.get("WAYLOOM_ALLOW_REAL_MODELS") == "1"
        )

    def _response(self, action: str) -> ModelLoadResponse:
        return ModelLoadResponse(
            mode=self.mode,
            action=action,
            real_models_loaded=self.mode == "private_local" and self._loaded,
            models=self._states,
        )
