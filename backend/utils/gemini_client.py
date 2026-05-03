# backend/utils/gemini_client.py
# Central Gemini API client — used by all agents

import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger("vera.gemini")

_configured = False

def _configure():
    global _configured
    if not _configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file.\n"
                "Get a FREE key at: https://aistudio.google.com → 'Get API Key'"
            )
        genai.configure(api_key=api_key)
        _configured = True


def get_model(model_name: str = "gemini-1.5-flash"):
    """
    Returns a configured Gemini GenerativeModel.
    
    Models available on the FREE tier:
      - gemini-1.5-flash  (fast, great for most tasks)
      - gemini-1.5-pro    (smarter, slower — use for verification)
      - gemini-1.0-pro    (older but stable)
    """
    _configure()
    return genai.GenerativeModel(model_name)


def generate(prompt: str, model_name: str = "gemini-1.5-flash", temperature: float = 0.3) -> str:
    """Simple single-turn text generation. Returns response string."""
    _configure()
    model = genai.GenerativeModel(
        model_name,
        generation_config=genai.types.GenerationConfig(temperature=temperature),
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini generate error: {e}")
        raise


def generate_json(prompt: str, model_name: str = "gemini-1.5-flash") -> dict:
    """
    Generate a response and parse it as JSON.
    Strips markdown code fences automatically.
    """
    _configure()
    model = genai.GenerativeModel(
        model_name,
        generation_config=genai.types.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw: {text[:200]}")
        return {}
    except Exception as e:
        logger.error(f"Gemini JSON generate error: {e}")
        raise
