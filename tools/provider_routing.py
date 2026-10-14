"""Explicit tool/host/model constraints shared by capability selectors."""

from __future__ import annotations


def filter_explicit_route(inputs, candidates):
    tool_name = inputs.get("preferred_tool")
    host = inputs.get("hosting_provider")
    model_field = next(
        (field for field in ("model", "model_id", "model_name") if inputs.get(field)),
        None,
    )
    model = inputs.get(model_field) if model_field else None
    allowed = set(inputs.get("allowed_providers") or [])
    selected = []
    for tool in candidates:
        if tool_name and tool.name != tool_name:
            continue
        if host and getattr(tool, "hosting_provider", tool.provider) != host:
            continue
        if model:
            props = tool.input_schema.get("properties", {})
            # Open-model providers opt in for specific canonical schema fields.
            # They must also be explicitly targeted: otherwise an unknown cloud
            # model could silently route to a local loader during auto-selection.
            open_fields = getattr(tool, "supports", {}).get("open_model_fields", [])
            accepts_open_model = (
                isinstance(open_fields, (list, tuple))
                and model_field in open_fields
                and model_field in props
                and "enum" not in props[model_field]
            )
            if accepts_open_model:
                provider = getattr(tool, "provider", None)
                accepts_open_model = bool(
                    tool_name
                    or host
                    or provider
                    and (
                        inputs.get("preferred_provider") == provider
                        or allowed == {provider}
                    )
                )
            if not accepts_open_model:
                models = set()
                for field in ("model", "model_id", "model_name"):
                    models.update(props.get(field, {}).get("enum", []))
                models.update(getattr(tool, "_MODELS", {}))
                models.update(getattr(tool, "_MODEL_ALIASES", {}))
                models.update(tool.get_info().get("model_catalog", {}))
                if model not in models:
                    continue
        operation = inputs.get("generation_mode") or inputs.get("operation")
        routes = getattr(tool, "routes", None) or getattr(tool, "models", None)
        if isinstance(routes, dict) and operation and operation != "rank":
            model_routes = (
                routes.get(model, {}) if model else next(iter(routes.values()), {})
            )
            normalized = (
                "text_to_video"
                if operation == "generate" and tool.capability == "video_generation"
                else operation
            )
            if normalized not in model_routes:
                continue
        if tool.capability == "image_generation":
            props = tool.input_schema.get("properties", {})
            if any(inputs.get(k) and k not in props for k in ("mask_path", "mask_url")):
                continue
            if any(
                inputs.get(k) and k not in props and "images" not in props
                for k in ("image_path", "image_paths", "image_url", "image_urls")
            ):
                continue
            if operation == "precise_edit" and not (
                getattr(tool, "supports", {}).get("precise_edit")
                or isinstance(routes, dict)
                and any("precise_edit" in r for r in routes.values())
            ):
                continue
        selected.append(tool)
    return selected
