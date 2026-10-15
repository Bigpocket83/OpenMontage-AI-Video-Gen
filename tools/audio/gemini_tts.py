"""Gemini native text-to-speech provider tool.

Uses the Gemini API (google-genai SDK) speech-generation models, which accept a
natural-language style instruction ("Say this deadpan and fast: ...") instead of
SSML. Output is 24 kHz 16-bit mono PCM, written as WAV.
"""

from __future__ import annotations

import os
import time
import wave
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

_DEFAULT_MODEL = "gemini-2.5-flash-preview-tts"
_SAMPLE_RATE = 24000


class GeminiTTS(BaseTool):
    name = "gemini_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "gemini_tts"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set GEMINI_API_KEY (or GOOGLE_API_KEY) to a Gemini API key.\n"
        "  Get one at https://aistudio.google.com/\n"
        "  Requires the 'google-genai' package (pip install google-genai).\n"
        "  Optionally set GEMINI_TTS_MODEL to override the default model."
    )
    fallback = "google_tts"
    fallback_tools = ["google_tts", "openai_tts", "piper_tts"]
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "style_prompting",
        "multilingual",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
        "ssml": False,
    }
    best_for = [
        "expressive narration steered by natural-language style prompts",
        "comedic or character-driven delivery",
        "Gemini API users without a Cloud TTS setup",
    ]
    not_good_for = [
        "voice cloning",
        "fully offline production",
        "very long single requests — synthesize per scene",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to speak"},
            "style": {
                "type": "string",
                "default": "",
                "description": (
                    "Natural-language delivery instruction prepended to the text, "
                    "e.g. 'Read in a brisk, dry, comedic documentary tone'."
                ),
            },
            "voice": {
                "type": "string",
                "default": "Charon",
                "description": "Gemini prebuilt voice name (e.g. Charon, Puck, Kore, Fenrir, Orus, Aoede).",
            },
            "model": {
                "type": "string",
                "description": "Gemini TTS model id. Defaults to GEMINI_TTS_MODEL or " + _DEFAULT_MODEL,
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(
        max_retries=2, retryable_errors=["rate_limit", "timeout", "unavailable"]
    )
    idempotency_key_fields = ["text", "style", "voice", "model"]
    side_effects = ["writes audio file to output_path", "calls Gemini API"]
    user_visible_verification = ["Listen to generated audio for natural delivery and pacing"]

    def _get_api_key(self) -> str | None:
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def get_status(self) -> ToolStatus:
        if not self._get_api_key():
            return ToolStatus.UNAVAILABLE
        try:
            import google.genai  # noqa: F401
        except ImportError:
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # Approximate: ~15 chars of English per second of speech, ~32 audio
        # tokens per second, output billed at ~$10 / 1M audio tokens.
        # Verify against https://ai.google.dev/gemini-api/docs/pricing.
        seconds = len(inputs.get("text", "")) / 15
        return round(seconds * 32 * 10 / 1_000_000, 4)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._get_api_key()
        if not api_key:
            return ToolResult(success=False, error="No Gemini API key found. " + self.install_instructions)

        start = time.time()
        try:
            result = self._generate(inputs, api_key)
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Gemini TTS failed: {str(exc).replace(api_key, '[REDACTED]')}",
            )
        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = self.estimate_cost(inputs)
        return result

    def _generate(self, inputs: dict[str, Any], api_key: str) -> ToolResult:
        from google import genai
        from google.genai import types

        text = inputs["text"]
        style = inputs.get("style", "").strip()
        voice = inputs.get("voice", "Charon")
        model = inputs.get("model") or os.environ.get("GEMINI_TTS_MODEL") or _DEFAULT_MODEL
        prompt = f"{style}:\n{text}" if style else text

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                    )
                ),
            ),
        )
        pcm = response.candidates[0].content.parts[0].inline_data.data

        output_path = Path(inputs.get("output_path", "tts_output.wav")).with_suffix(".wav")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(_SAMPLE_RATE)
            wf.writeframes(pcm)

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "voice": voice,
                "model": model,
                "text_length": len(text),
                "output": str(output_path),
                "format": "wav",
                "audio_seconds": round(len(pcm) / (2 * _SAMPLE_RATE), 2),
            },
            artifacts=[str(output_path)],
            model=f"gemini-tts/{model}/{voice}",
        )
