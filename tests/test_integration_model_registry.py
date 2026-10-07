import pytest
from pydantic import ValidationError

from src.integration.model_registry import MODEL_NAMES, ModelRegistry, ModelRegistryError
from src.integration.models import ModelLoadRequest


def config(mode="synthetic_demo"):
    return {"mode": mode, "models": {"allow_real_model_loading": False, "configured_artifacts": {}}}


def test_synthetic_registry_is_deterministic_and_idempotent():
    registry = ModelRegistry(config())
    assert set(registry.states.values()) == {"not_loaded"}
    first = registry.load()
    second = registry.load()
    assert first.action == "loaded"
    assert second.action == "already_loaded"
    assert first.real_models_loaded is False
    assert set(first.models.model_dump().values()) == {"synthetic"}


def test_model_request_cannot_accept_path():
    with pytest.raises(ValidationError):
        ModelLoadRequest.model_validate({"load": True, "model_path": "anything"})


def test_private_local_requires_all_explicit_opt_ins(monkeypatch):
    monkeypatch.delenv("WAYLOOM_INTEGRATION_MODE", raising=False)
    monkeypatch.delenv("WAYLOOM_ALLOW_REAL_MODELS", raising=False)
    registry = ModelRegistry(config("private_local"))
    with pytest.raises(ModelRegistryError, match="disabled"):
        registry.load()


def test_missing_configured_models_has_sanitized_error(monkeypatch):
    private = config("private_local")
    private["models"]["allow_real_model_loading"] = True
    private["models"]["configured_artifacts"] = {name: "missing-artifact" for name in MODEL_NAMES}
    monkeypatch.setenv("WAYLOOM_INTEGRATION_MODE", "private_local")
    monkeypatch.setenv("WAYLOOM_ALLOW_REAL_MODELS", "1")
    with pytest.raises(ModelRegistryError) as caught:
        ModelRegistry(private).load()
    assert "missing-artifact" not in str(caught.value)
