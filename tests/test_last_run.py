from freezegun import freeze_time

import kind2anki.last_run


def test_write_then_read_last_run(tmp_path, monkeypatch):
    monkeypatch.setattr(kind2anki.last_run, "ROOT_FOLDER", tmp_path)
    with freeze_time("2026-06-25"):
        kind2anki.last_run.save_days_since_last_run()
    with freeze_time("2026-06-28"):
        assert kind2anki.last_run.get_days_since_last_run() == 4
