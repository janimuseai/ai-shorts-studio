"""
🎬 AI SHORTS STUDIO — turn any story idea into a ready-to-upload YouTube Short.

Pipeline (Gemini-only, zero API cost on the free tier):
  1. Idea  → Gemini writes a 4-scene script (narration + image prompt per scene)
  2. Scenes → Gemini (Imagen) generates animated-style images
  3. Voice  → free TTS narrates each scene
  4. Build  → ffmpeg assembles: zoom motion + single-line captions at bottom
  5. Ship   → vertical MP4, ready for YouTube Shorts

Built by Jani Muse Ai 🤖 — https://www.youtube.com/@JaniMuseAi
"""
