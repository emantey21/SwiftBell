import json
import pytest
from config import Config


@pytest.fixture
def fresh_config():
    return Config(config_file="")


class TestConfig:
    def test_default_values(self, fresh_config):
        assert fresh_config.get("timetable_file") == "timetable.json"
        assert fresh_config.get("tts_rate") == 200
        assert fresh_config.get("tts_volume") == 1.0
        assert fresh_config.get("tts_voice") == "female"

    def test_get_with_default(self, fresh_config):
        assert fresh_config.get("nonexistent_key", "fallback") == "fallback"
        assert fresh_config.get("nonexistent_key") is None

    def test_set_and_get(self, fresh_config):
        fresh_config.set("custom_key", "custom_value")
        assert fresh_config.get("custom_key") == "custom_value"

    def test_update_multiple(self, fresh_config):
        fresh_config.update({"tts_rate": 300, "tts_volume": 0.5})
        assert fresh_config.get("tts_rate") == 300
        assert fresh_config.get("tts_volume") == 0.5

    def test_get_all_returns_copy(self, fresh_config):
        all_settings = fresh_config.get_all()
        assert isinstance(all_settings, dict)
        assert all_settings["tts_rate"] == 200
        all_settings["tts_rate"] = 999
        assert fresh_config.get("tts_rate") == 200

    def test_load_from_json_overrides_defaults(self, tmp_path):
        cfg_file = tmp_path / "test_config.json"
        cfg_file.write_text(json.dumps({"tts_rate": 300, "tts_voice": "male"}), encoding="utf-8")
        cfg = Config(config_file="")
        cfg.load_from_file(str(cfg_file))
        assert cfg.get("tts_rate") == 300
        assert cfg.get("tts_voice") == "male"
        assert cfg.get("tts_volume") == 1.0
