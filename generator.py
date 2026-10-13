"""
Step 1+2: Gemini writes the script AND generates the scene images.

Uses the free Gemini API (AI Studio). One call for the script (JSON),
then one Imagen call per scene.
"""
import json
import os

import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SCRIPT_MODEL = "gemini-2.0-flash"

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


def generate_script(idea: str) -> dict:
    model = genai.GenerativeModel(SCRIPT_MODEL)
    resp = model.generate_content(_SCRIPT_PROMPT.format(idea=idea.strip()))
    text = resp.text.strip()
    # strip accidental code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    assert len(data["scenes"]) == 4, "expected exactly 4 scenes"
    return data


def generate_scene_image(image_prompt: str, out_path: str) -> str:
    """Generate one animated scene image with Gemini/Imagen. Returns out_path."""
    model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
    full_prompt = f"{_STYLE}. {image_prompt}"
    resp = model.generate_image(full_prompt) if hasattr(model, "generate_image") \
        else model.generate_content(
            f"Generate an image: {full_prompt}",
            generation_config={"response_modalities": ["IMAGE"]},
        )
    # extract image bytes from the response parts
    for part in resp.parts:
        blob = getattr(part, "inline_data", None)
        if blob and blob.data:
            with open(out_path, "wb") as f:
                f.write(blob.data)
            return out_path
    raise RuntimeError("Gemini returned no image for prompt: " + image_prompt[:80])
