# 🎬 AI Shorts Studio

Type a story idea → get a **ready-to-upload YouTube Short**: 4 animated scenes,
English voiceover, single-line captions at the bottom, vertical 1080×1920.

## How it works

| Step | What | Cost |
|---|---|---|
| ✍️ Script | Gemini writes a 4-scene script (narration + image prompts) | Free |
| 🎨 Scenes | Gemini generates 4 animated images | Free |
| 🎙️ Voice | gTTS narrates each scene | Free |
| 🎬 Build | ffmpeg: zoom motion + burned-in captions + audio | Free |
| 💾 Save | Firebase Firestore (or local JSON fallback) | Free tier |

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env   # then put your Gemini key in .env
python app.py
```

Needs `ffmpeg` on PATH.

## Deploy on Hugging Face Spaces

1. Create a Space (Gradio, Python)
2. Add a `GEMINI_API_KEY` Secret in the Space settings
3. Push this repo — `app.py` is the entry point

## Roadmap to $

- [x] MVP: idea → Short in one click
- [ ] User accounts + usage limits (Firebase Auth)
- [ ] Stripe billing: $19/mo Hobby, $49/mo Pro
- [ ] Direct YouTube upload via API
- [ ] Claude script-writing as a Pro upsell

Built by **Jani Muse Ai** 🤖 — https://www.youtube.com/@JaniMuseAi
