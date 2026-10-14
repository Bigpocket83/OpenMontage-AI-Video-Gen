"""Explicit model routing stays strict unless a provider opts in by field."""

from types import SimpleNamespace

import pytest

from tools.audio.elevenlabs_tts import ElevenLabsTTS
from tools.audio.mlx_audio_tts import MLXAudioTTS
from tools.provider_routing import filter_explicit_route


@pytest.mark.parametrize(
    "route",
    [
        {"preferred_provider": "mlx_audio"},
        {"preferred_tool": "mlx_audio_tts"},
        {"hosting_provider": "mlx_audio"},
        {"allowed_providers": ["mlx_audio"]},
    ],
)
def test_open_model_field_requires_an_explicit_provider_route(route):
    tool = MLXAudioTTS()
    assert filter_explicit_route(
        {**route, "model_id": "org/arbitrary-model"}, [tool]
    ) == [tool]


@pytest.mark.parametrize(
    "route",
    [
        {},
        {"preferred_provider": "auto"},
        {"preferred_provider": "elevenlabs"},
        {"allowed_providers": ["mlx_audio", "elevenlabs"]},
        {"preferred_provider": "mlx_audio", "preferred_tool": "elevenlabs_tts"},
        {"preferred_provider": "mlx_audio", "hosting_provider": "fal.ai"},
    ],
)
def test_unknown_model_cannot_silently_route_to_open_model_provider(route):
    assert filter_explicit_route(
        {**route, "model_id": "unknown-cloud-model"}, [MLXAudioTTS()]
    ) == []


@pytest.mark.parametrize("field", ["model", "model_name"])
def test_open_model_contract_does_not_accept_unsupported_aliases(field):
    assert filter_explicit_route(
        {"preferred_provider": "mlx_audio", field: "org/arbitrary-model"},
        [MLXAudioTTS()],
    ) == []


def test_catalogued_provider_still_rejects_unknown_model():
    tool = ElevenLabsTTS()
    assert filter_explicit_route(
        {"preferred_provider": "elevenlabs", "model_id": "eleven_v4"}, [tool]
    ) == [tool]
    assert filter_explicit_route(
        {"preferred_provider": "elevenlabs", "model_id": "unknown-model"}, [tool]
    ) == []


@pytest.mark.parametrize(
    "catalog_source", ["schema", "_MODELS", "_MODEL_ALIASES", "model_catalog"]
)
@pytest.mark.parametrize("field", ["model", "model_id", "model_name"])
def test_existing_model_catalog_sources_remain_strict(catalog_source, field):
    tool = SimpleNamespace(
        name="catalogued_tts",
        capability="tts",
        provider="catalogued",
        input_schema={"properties": {field: {"type": "string"}}},
        supports={},
        get_info=lambda: {},
    )
    if catalog_source == "schema":
        tool.input_schema["properties"][field]["enum"] = ["known-model"]
    elif catalog_source == "model_catalog":
        tool.get_info = lambda: {"model_catalog": {"known-model": {}}}
    else:
        setattr(tool, catalog_source, {"known-model": {}})

    assert filter_explicit_route({field: "known-model"}, [tool]) == [tool]
    assert filter_explicit_route({field: "unknown-model"}, [tool]) == []


def test_uncatalogued_model_field_alone_does_not_opt_in():
    tool = SimpleNamespace(
        name="uncatalogued_tts",
        capability="tts",
        provider="uncatalogued",
        input_schema={"properties": {"model_id": {"type": "string"}}},
        supports={},
        get_info=lambda: {},
    )
    assert filter_explicit_route(
        {"preferred_provider": "uncatalogued", "model_id": "unknown-model"},
        [tool],
    ) == []


@pytest.mark.parametrize(
    "properties",
    [{}, {"model_id": {"type": "string", "enum": ["known-model"]}}],
    ids=["undeclared-field", "enumerated-field"],
)
def test_open_model_opt_in_does_not_override_schema_constraints(properties):
    tool = SimpleNamespace(
        name="schema_constrained_tts",
        capability="tts",
        provider="schema_constrained",
        input_schema={"properties": properties},
        supports={"open_model_fields": ["model_id"]},
        get_info=lambda: {},
    )
    assert filter_explicit_route(
        {"preferred_provider": tool.provider, "model_id": "unknown-model"}, [tool]
    ) == []


@pytest.mark.parametrize("open_fields", [None, True, "model_id", {"model_id": True}])
def test_malformed_open_model_contract_does_not_opt_in(open_fields):
    tool = SimpleNamespace(
        name="malformed_tts",
        capability="tts",
        provider="malformed",
        input_schema={"properties": {"model_id": {"type": "string"}}},
        supports={"open_model_fields": open_fields},
        get_info=lambda: {},
    )
    assert filter_explicit_route(
        {"preferred_provider": tool.provider, "model_id": "unknown-model"}, [tool]
    ) == []


@pytest.mark.parametrize("supports", [{}, {"open_model_fields": ["model_id"]}])
def test_unrelated_candidate_without_provider_is_rejected_by_model(supports):
    tool = SimpleNamespace(
        input_schema={"properties": {"model_id": {"type": "string"}}},
        supports=supports,
        get_info=lambda: {},
    )
    assert filter_explicit_route({"model_id": "unknown-model"}, [tool]) == []
