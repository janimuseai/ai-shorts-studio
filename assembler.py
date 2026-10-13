"""
Step 4: assemble the Short with ffmpeg.

- Each scene image → 1080x1920 segment with slow zoom (Ken Burns)
- Scene voiceover laid under its segment
- Single-line captions, bottom-center, burned in
- Output: vertical MP4 ready for YouTube Shorts
"""
import os
import subprocess

W, H = 1080, 1920
FPS = 30

_CAPTION_STYLE = (
    "FontSize=26,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,"
    "BorderStyle=1,Outline=2,Shadow=1,MarginV=45,Alignment=2"
)


def _run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def _probe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip().split("=")[1])


def _single_line_srt(narration: str, start: float, end: float, srt_path: str, idx: int):
    """Split narration into short single-line captions across the scene window."""
    words = narration.replace("—", "-").split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 38 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    span = (end - start) / max(len(lines), 1)
    with open(srt_path, "w") as f:
        for j, line in enumerate(lines):
            s = start + j * span
            e = start + (j + 1) * span
            f.write(f"{idx + j}\n{_ts(s)} --> {_ts(e)}\n{line}\n\n")
    return len(lines)


def _ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def build_short(scene_images: list, voice_paths: list, narrations: list,
                out_path: str, workdir: str) -> str:
    durations = [_probe_duration(p) for p in voice_paths]
    total = sum(durations)

    seg_paths, srt_path = [], os.path.join(workdir, "captions.srt")
    t, cap_idx = 0.0, 1
    open(srt_path, "w").close()
    for i, (img, dur) in enumerate(zip(scene_images, durations)):
        frames = max(int(dur * FPS), 1)
        seg = os.path.join(workdir, f"seg_{i}.mp4")
        _run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", img,
              "-vf",
              f"scale=1296:2304:force_original_aspect_ratio=increase,"
              f"crop=1296:2304,scale={W}:{H},"
              f"zoompan=z='min(zoom+0.0015,1.15)':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
              "-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p",
              "-preset", "veryfast", seg])
        seg_paths.append(seg)
        # append this scene's captions (single line each)
        tmp_srt = os.path.join(workdir, f"cap_{i}.srt")
        n = _single_line_srt(narrations[i], t, t + dur, tmp_srt, cap_idx)
        cap_idx += n
        with open(tmp_srt) as src, open(srt_path, "a") as dst:
            dst.write(src.read())
        t += dur

    concat_list = os.path.join(workdir, "concat.txt")
    with open(concat_list, "w") as f:
        for seg in seg_paths:
            f.write(f"file '{seg}'\n")
    audio_concat = os.path.join(workdir, "audio.txt")
    with open(audio_concat, "w") as f:
        for vp in voice_paths:
            f.write(f"file '{vp}'\n")
    full_audio = os.path.join(workdir, "full_audio.mp3")
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", audio_concat, "-c", "copy", full_audio])

    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", concat_list, "-i", full_audio,
          "-vf", f"subtitles={srt_path}:force_style='{_CAPTION_STYLE}'",
          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
          "-c:a", "aac", "-b:a", "128k", "-shortest",
          "-movflags", "+faststart", out_path])
    return out_path
