"""
🎬 AI SHORTS STUDIO — Streamlit edition (free deploy on Streamlit Cloud).

Type a story idea → get a ready-to-upload YouTube Short:
animated scenes, English voiceover, single-line captions at the bottom.
"""
import os
import tempfile

import streamlit as st

from generator import generate_script, generate_scene_image
from voiceover import narrate_scenes
from assembler import build_short
from firebase_db import save_project, is_connected

st.set_page_config(page_title="🎬 AI Shorts Studio", layout="wide")
st.title("🎬 AI Shorts Studio")
st.subheader("Type a story idea → get a ready-to-upload YouTube Short.")
st.caption("Animated scenes · English voiceover · single-line captions · vertical 1080×1920")

idea = st.text_area(
    "Story idea",
    placeholder="A clever rabbit who learns to share…",
    height=80,
)

examples = st.columns(3)
for col, ex in zip(examples, [
    "The thirsty crow",
    "The tortoise and the hare",
    "A little star who was afraid of the dark",
]):
    if col.button(ex, use_container_width=True):
        idea = ex

if st.button("🎬 MAKE MY SHORT", type="primary", use_container_width=True):
    if not idea.strip():
        st.warning("Type a story idea first! 👆")
    else:
        workdir = tempfile.mkdtemp(prefix="shorts-studio-")
        with st.status("Building your Short…", expanded=True) as status:
            st.write("✍️ Gemini is writing your script…")
            script = generate_script(idea)
            scenes = script["scenes"]
            narrations = [s["narration"] for s in scenes]

            images = []
            for i, s in enumerate(scenes):
                st.write(f"🎨 Painting scene {i + 1}/4…")
                out = os.path.join(workdir, f"scene_{i}.png")
                images.append(generate_scene_image(s["image"], out))

            st.write("🎙️ Recording voiceover…")
            voices = narrate_scenes(scenes, workdir)

            st.write("🎬 Assembling your Short…")
            out_path = os.path.join(workdir, "short.mp4")
            build_short(images, voices, narrations, out_path, workdir)

            st.write("💾 Saving project…")
            pid = save_project(script["title"], idea, out_path,
                               {"moral": script["moral"], "scenes": len(scenes)})
            status.update(label="Done!", state="complete")

        st.success(f"✅ **{script['title']}** — *{script['moral']}*")
        st.video(out_path)
        with open(out_path, "rb") as f:
            st.download_button("⬇️ Download Short", f, file_name="short.mp4",
                               mime="video/mp4", use_container_width=True)
        st.caption(f"Project id: `{pid}`"
                   + (" · 🔥 synced to Firebase" if is_connected() else " · 💾 saved locally"))

st.divider()
st.caption("Built by **Jani Muse Ai** 🤖 · https://www.youtube.com/@JaniMuseAi")
