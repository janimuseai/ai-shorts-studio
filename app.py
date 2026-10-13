"""
🎬 AI SHORTS STUDIO — Gradio UI.

Type a story idea → get a ready-to-upload YouTube Short:
animated scenes, English voiceover, single-line captions at the bottom.
"""
import os
import tempfile

import gradio as gr

from generator import generate_script, generate_scene_image
from voiceover import narrate_scenes
from assembler import build_short
from firebase_db import save_project, is_connected


def make_short(idea: str, progress=gr.Progress(track_tqdm=True)):
    if not idea.strip():
        return None, "Type a story idea first! 👆"
    workdir = tempfile.mkdtemp(prefix="shorts-studio-")

    progress(0.05, desc="✍️ Gemini is writing your script…")
    script = generate_script(idea)
    scenes = script["scenes"]
    narrations = [s["narration"] for s in scenes]

    progress(0.25, desc="🎨 Gemini is painting 4 animated scenes…")
    images = []
    for i, s in enumerate(scenes):
        out = os.path.join(workdir, f"scene_{i}.png")
        images.append(generate_scene_image(s["image"], out))
        progress(0.25 + 0.15 * (i + 1), desc=f"🎨 Scene {i + 1}/4 painted…")

    progress(0.7, desc="🎙️ Recording voiceover…")
    voices = narrate_scenes(scenes, workdir)

    progress(0.85, desc="🎬 Assembling your Short…")
    out_path = os.path.join(workdir, "short.mp4")
    build_short(images, voices, narrations, out_path, workdir)

    progress(0.95, desc="💾 Saving project…")
    pid = save_project(script["title"], idea, out_path,
                       {"moral": script["moral"], "scenes": len(scenes)})

    done = (
        f"✅ **{script['title']}**\n\n"
        f"*{script['moral']}*\n\n"
        f"Project id: `{pid}`"
        + (" · 🔥 synced to Firebase" if is_connected() else " · 💾 saved locally")
    )
    return out_path, done


with gr.Blocks(title="🎬 AI Shorts Studio", theme=gr.themes.Monochrome()) as app:
    gr.Markdown(
        "# 🎬 AI SHORTS STUDIO\n"
        "### Type a story idea → get a ready-to-upload YouTube Short.\n"
        "Animated scenes · English voiceover · single-line captions · vertical 1080×1920"
    )
    idea = gr.Textbox(
        label="Story idea",
        placeholder="A clever rabbit who learns to share…",
        lines=2,
    )
    btn = gr.Button("🎬 MAKE MY SHORT", variant="primary")
    with gr.Row():
        video = gr.Video(label="Your Short")
        status = gr.Markdown()
    gr.Examples(
        ["The thirsty crow", "The tortoise and the hare", "A little star who was afraid of the dark"],
        inputs=idea,
    )
    btn.click(make_short, inputs=idea, outputs=[video, status])
    gr.Markdown("Built by **Jani Muse Ai** 🤖 · https://www.youtube.com/@JaniMuseAi")

if __name__ == "__main__":
    app.launch()
