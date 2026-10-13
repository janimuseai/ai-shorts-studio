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

st.set_page_config(
    page_title="🎬 AI Shorts Studio",
    page_icon="🎬",
    layout="wide",
)

# ---------- Premium styling ----------
st.markdown("""
<style>
  .hero { text-align:center; padding: 1.2rem 0 .4rem; }
  .hero h1 { font-size: 2.6rem; margin-bottom:.2rem; }
  .hero p { color:#9aa0a6; font-size:1.05rem; }
  .badge { display:inline-block; background:#1a73e8; color:#fff; border-radius:999px;
           padding:.25rem .8rem; font-size:.8rem; margin:.15rem; }
  .stButton>button[kind="primary"] { font-size:1.15rem; padding:.7rem 1rem; border-radius:12px; }
  .idea-card { background:#f8f9fa; border:1px solid #e8eaed; border-radius:14px;
               padding:1rem; margin-bottom:.6rem; }
  .step-done { color:#188038; font-weight:600; }
  footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
  <h1>🎬 AI Shorts Studio</h1>
  <p>Type a story idea → get a ready-to-upload YouTube Short.</p>
  <span class="badge">🎨 Animated scenes</span>
  <span class="badge">🎙️ English voiceover</span>
  <span class="badge">💬 Single-line captions</span>
  <span class="badge">📱 1080×1920 vertical</span>
</div>
""", unsafe_allow_html=True)

# ---------- Input ----------
col1, col2 = st.columns([3, 1])
with col1:
    idea = st.text_area(
        "✍️ Story idea",
        placeholder="A clever rabbit who learns to share…",
        height=90,
    )
with col2:
    st.markdown("**✨ Try one:**")
    for ex in [
        "🐦 The thirsty crow",
        "🐢 The tortoise and the hare",
        "⭐ A little star afraid of the dark",
    ]:
        if st.button(ex, use_container_width=True, key=ex):
            idea = ex.split(" ", 1)[1]
            st.rerun()

# ---------- Generate ----------
if st.button("🎬 MAKE MY SHORT", type="primary", use_container_width=True):
    if not idea or not idea.strip():
        st.warning("👆 Pehle story idea likho!")
    else:
        workdir = tempfile.mkdtemp(prefix="shorts-studio-")
        prog = st.progress(0, text="Starting…")
        with st.status("🎬 Building your Short…", expanded=True) as status:
            try:
                st.write("✍️ **Step 1/4** — Gemini is writing your script…")
                prog.progress(10, text="Writing script…")
                script = generate_script(idea)
                scenes = script["scenes"]
                narrations = [s["narration"] for s in scenes]

                st.write("🎨 **Step 2/4** — Painting 4 animated scenes…")
                images = []
                for i, s in enumerate(scenes):
                    prog.progress(15 + i * 15, text=f"Painting scene {i + 1}/4…")
                    st.write(f"&nbsp;&nbsp;&nbsp;🖼️ Scene {i + 1}/4…")
                    images.append(generate_scene_image(
                        s["image"], os.path.join(workdir, f"scene_{i}.png")))

                st.write("🎙️ **Step 3/4** — Recording English voiceover…")
                prog.progress(80, text="Recording voiceover…")
                voices = narrate_scenes(scenes, workdir)

                st.write("🎞️ **Step 4/4** — Assembling your Short…")
                prog.progress(90, text="Assembling video…")
                out_path = os.path.join(workdir, "short.mp4")
                build_short(images, voices, narrations, out_path, workdir)

                st.write("💾 Saving project…")
                pid = save_project(script["title"], idea, out_path,
                                   {"moral": script["moral"],
                                    "scenes": len(scenes)})
                prog.progress(100, text="Done!")
                status.update(label="✅ Done!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Failed", state="error")
                st.error(f"Oops! {e}")
                st.stop()

        st.success(f"### ✅ **{script['title']}**\n*{script['moral']}*")
        st.video(out_path)
        with open(out_path, "rb") as f:
            st.download_button("⬇️ Download Short", f, file_name="short.mp4",
                               mime="video/mp4", use_container_width=True,
                               type="primary")
        st.caption(f"🆔 `{pid}`"
                   + (" · 🔥 synced to Firebase" if is_connected()
                      else " · 💾 saved locally"))

st.divider()
c1, c2, c3 = st.columns(3)
c1.markdown("**🎨 Step 1**\n\nGemini writes your script")
c2.markdown("**🎙️ Step 2**\n\nScenes + voiceover generated")
c3.markdown("**📱 Step 3**\n\nVertical Short, ready to upload")
st.caption("Built with ❤️ by **Jani Muse Ai** 🤖 · https://www.youtube.com/@JaniMuseAi")
