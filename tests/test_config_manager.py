from anki.collection import CsvMetadata

import kind2anki.config_manager as config_manager


def test_import_mode_round_trip(fake_config):
    assert config_manager.get_import_mode() == CsvMetadata.DupeResolution.PRESERVE
    config_manager.set_import_mode(CsvMetadata.DupeResolution.DUPLICATE)
    assert config_manager.get_import_mode() == CsvMetadata.DupeResolution.DUPLICATE


def test_last_run_round_trip(fake_config):
    assert config_manager.get_last_run() is None
    config_manager.set_last_run(123456)
    assert config_manager.get_last_run() == 123456
