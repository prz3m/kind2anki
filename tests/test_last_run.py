from freezegun import freeze_time

import kind2anki.last_run as last_run


def test_write_then_read_last_run(fake_config):
    with freeze_time("2026-06-25"):
        last_run.save_days_since_last_run()
    with freeze_time("2026-06-28"):
        assert last_run.get_days_since_last_run() == 4
