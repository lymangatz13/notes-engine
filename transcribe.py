"""
Simple Notes Generator -- local offline backend.
mp4 in -> txt out. Transcribes the first N seconds with faster-whisper.

Run:  python transcribe.py   (serves http://localhost:5000)
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify

# ---- config ----
MODEL_SIZE = "base"          # tiny | base | small | medium | large-v3
SAMPLE_RATE = 16000

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)

# faster-whisper is loaded lazily on first request (keeps tests import-light).
_model = None


# ---- pure helpers (unit-tested) ----
def fmt_ts(seconds):
    """Seconds -> 'm:ss'."""
    s = int(seconds)
    return "%d:%02d" % (s // 60, s % 60)


def build_transcript(meta, segments, want_ts, want_speaker):
    """Assemble the .txt document. segments = list of (start_seconds, text)."""
    out = []
    out.append("SIMPLE NOTES GENERATOR -- TRANSCRIPT")
    out.append("Source   : " + meta["source"])
    out.append("Language : " + meta["language"])
    out.append("Segment  : first " + fmt_ts(meta["duration"]))
    out.append("Created  : " + meta["created"])
    if want_speaker:
        out.append("Note     : speaker labels requested; diarization not enabled in offline build")
    out.append("=" * 52)
    out.append("")
    for start, text in segments:
        line = text.strip()
        out.append(("[" + fmt_ts(start) + "] " + line) if want_ts else line)
    return "\n".join(out) + "\n"


# ---- whisper ----
def get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def run_whisper(path, duration, language):
    """Decode the file, keep the first `duration` seconds, transcribe."""
    from faster_whisper.audio import decode_audio
    audio = decode_audio(path, sampling_rate=SAMPLE_RATE)
    clip = audio[: int(duration * SAMPLE_RATE)]
    segs, _info = get_model().transcribe(clip, language=language, beam_size=1)
    return [(s.start, s.text) for s in segs]


# ---- CORS (page is opened from file://) ----
@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


# ---- routes ----
@app.route("/", methods=["GET"])
def health():
    return jsonify(status="ok", model=MODEL_SIZE, service="notes-engine")


@app.route("/transcribe", methods=["POST", "OPTIONS"])
def transcribe():
    if request.method == "OPTIONS":
        return ("", 204)

    f = request.files.get("file")
    if f is None or f.filename == "":
        return jsonify(error="No .mp4 file received."), 400

    duration = int(float(request.form.get("duration", 300)))
    language = request.form.get("language", "en")
    want_ts  = request.form.get("timestamps", "true").lower() == "true"
    want_spk = request.form.get("speaker", "false").lower() == "true"

    in_path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(in_path)

    try:
        segments = run_whisper(in_path, duration, language)
    except Exception as e:
        return jsonify(error="Transcription failed: " + str(e)), 500

    meta = {"source": f.filename, "language": language,
            "duration": duration, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    text = build_transcript(meta, segments, want_ts, want_spk)

    stem = os.path.splitext(f.filename)[0]
    out_name = stem + "-notes-" + datetime.now().strftime("%m%d%y-%H%M%S") + ".txt"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)

    return jsonify(output=out_path.replace("\\", "/"),
                   text=text,
                   segments=len(segments), language=language)


if __name__ == "__main__":
    print("Notes Engine backend -> http://localhost:5000  (model: %s)" % MODEL_SIZE)
    app.run(host="127.0.0.1", port=5000)
