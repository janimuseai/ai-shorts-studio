"""
Step 1+2: Gemini writes the script AND generates the scene images.

Uses the free Gemini API (AI Studio). One call for the script (JSON),
then one Imagen call per scene.
"""
import json
import os

import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SCRIPT_MODELS = [
    "gemini-3.8-flash",      # current flagship (API-recommended)
    "gemini-3.5-flash",      # stable fallback
    "gemini-3-flash-preview", # preview fallback
    "gemini-flash-latest",   # alias fallback
]
IMAGE_MODELS = [
    "gemini-3.1-flash-image", # current image model
    "gemini-2.5-flash-image", # nano banana fallback
    "gemini-nano-banana-2.1", # alt fallback
]

_STYLE = (
    "Animated cartoon illustration, vibrant colors, 9:16 vertical composition, "
    "no text, no words, no letters in the image"
)

_SCRIPT_PROMPT = """You write scripts for 30-second animated YouTube Shorts (moral stories for kids).

Given the story idea below, return ONLY valid JSON — no markdown, no backticks:
{{
  "title": "short catchy title with one emoji",
  "moral": "one-line moral",
  "scenes": [
    {{"narration": "one or two short sentences (~6 sec spoken)",
      "image": "detailed visual description of this scene, cartoon style"}},
    ... exactly 4 scenes ...
  ]
}}

Story idea: {idea}"""


def _try_models(models, call):
    """Try each model in order; return the first successful response."""
    last_err = None
    for name in models:
        try:
            return call(genai.GenerativeModel(name)), name
        except Exception as e:
            last_err = e
    raise RuntimeError(f"All models failed: {models}. Last error: {last_err}")


def generate_script(idea: str) -> dict:
    def call(model):
        return model.generate_content(_SCRIPT_PROMPT.format(idea=idea.strip()))
    resp, used = _try_models(SCRIPT_MODELS, call)
    text = resp.text.strip()
    # strip accidental code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    assert len(data["scenes"]) == 4, "expected exactly 4 scenes"
    return data


def generate_scene_image(image_prompt: str, out_path: str) -> str:
    """Generate one animated scene image with Gemini/Imagen. Returns out_path."""
    full_prompt = f"{_STYLE}. {image_prompt}"

    def call(model):
        if hasattr(model, "generate_image"):
            return model.generate_image(full_prompt)
        return model.generate_content(
            f"Generate an image: {full_prompt}",
            generation_config={"response_modalities": ["IMAGE"]},
        )
    resp, used = _try_models(IMAGE_MODELS, call)
    # extract image bytes from the response parts
    for part in resp.parts:
        blob = getattr(part, "inline_data", None)
        if blob and blob.data:
            with open(out_path, "wb") as f:
                f.write(blob.data)
            return out_path
    raise RuntimeError("Gemini returned no image for prompt: " + image_prompt[:80])
