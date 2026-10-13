"""
Step 3: free English voiceover (gTTS) — one MP3 per scene.
"""
import os

from gtts import gTTS


def narrate(text: str, out_path: str) -> str:
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(out_path)
    return out_path


def narrate_scenes(scenes: list, workdir: str) -> list:
    paths = []
    for i, scene in enumerate(scenes, 1):
        out = os.path.join(workdir, f"voice_{i}.mp3")
        paths.append(narrate(scene["narration"], out))
    return paths
