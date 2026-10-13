"""
Firebase integration — projects, usage tracking, future billing.

Works in two modes:
- Connected: FIREBASE_CREDENTIALS + FIREBASE_PROJECT_ID set → Firestore.
- Local: falls back to a JSON file so the Studio runs without Firebase.
"""
import json
import os
import threading
import time

_lock = threading.Lock()
_local_file = os.path.join(os.path.dirname(__file__), "studio_local.json")

_db = None
_project_id = os.environ.get("FIREBASE_PROJECT_ID")
_creds_json = os.environ.get("FIREBASE_CREDENTIALS")
if _project_id and _creds_json:
    import firebase_admin
    from firebase_admin import credentials, firestore

    firebase_admin.initialize_app(
        credentials.Certificate(json.loads(_creds_json)),
        {"projectId": _project_id},
    )
    _db = firestore.client()


def save_project(title: str, idea: str, video_path: str, meta: dict) -> str:
    record = {
        "title": title,
        "idea": idea,
        "created_at": int(time.time()),
        "meta": meta,
    }
    if _db is not None:
        ref = _db.collection("shorts").document()
        ref.set(record)
        return ref.id
    with _lock:
        try:
            data = json.load(open(_local_file))
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        rid = f"local-{len(data)}"
        record["id"] = rid
        data.append(record)
        json.dump(data, open(_local_file, "w"))
        return rid


def is_connected() -> bool:
    return _db is not None
