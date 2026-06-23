"""Unit tests for the pure transcript logic. Run: python test_transcribe.py"""

from transcribe import fmt_ts, build_transcript


def check(name, cond):
    print(("PASS" if cond else "FAIL") + " - " + name)
    return cond


def main():
    ok = True

    # fmt_ts
    ok &= check("fmt_ts 0   -> 0:00", fmt_ts(0) == "0:00")
    ok &= check("fmt_ts 65  -> 1:05", fmt_ts(65) == "1:05")
    ok &= check("fmt_ts 300 -> 5:00", fmt_ts(300) == "5:00")

    meta = {"source": "demo.mp4", "language": "en",
            "duration": 300, "created": "2026-06-22 10:00:00"}
    segs = [(0.0, " Hello world. "), (5.2, "Second line.")]

    ts = build_transcript(meta, segs, True, False)
    ok &= check("timestamps on  -> [0:00]", "[0:00] Hello world." in ts)
    ok &= check("timestamps on  -> [0:05]", "[0:05] Second line." in ts)
    ok &= check("header carries source",    "demo.mp4" in ts)

    plain = build_transcript(meta, segs, False, False)
    ok &= check("timestamps off -> no tag", "[0:00]" not in plain and "Hello world." in plain)

    spk = build_transcript(meta, segs, True, True)
    ok &= check("speaker note present", "diarization not enabled" in spk)

    print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
