"""
Tests for configuration module
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Settings, get_config_dir, get_default_config_path, load_config


class TestSettings:
    """Test Settings dataclass and validation."""
    
    def test_default_settings(self):
        """Test that default settings are created correctly."""
        settings = Settings()
        assert settings.template == "{workspace}"
        assert settings.show_monitor is False
        assert settings.show_name is False
        assert settings.show_layout is False
        assert settings.log_level is None
        assert settings.opacity == 0.7
        assert settings.poll_interval_ms == 1000
    
    def test_opacity_validation_too_high(self):
        """Test that opacity > 1.0 is clamped to default."""
        settings = Settings(opacity=1.5)
        assert settings.opacity == 0.7
    
    def test_opacity_validation_too_low(self):
        """Test that opacity < 0.0 is clamped to default."""
        settings = Settings(opacity=-0.5)
        assert settings.opacity == 0.7
    
    def test_opacity_validation_valid(self):
        """Test that valid opacity values are accepted."""
        settings = Settings(opacity=0.5)
        assert settings.opacity == 0.5
        
        settings = Settings(opacity=0.0)
        assert settings.opacity == 0.0
        
        settings = Settings(opacity=1.0)
        assert settings.opacity == 1.0
    
    def test_log_level_validation_invalid(self):
        """Test that invalid log levels are set to None."""
        settings = Settings(log_level="invalid")
        assert settings.log_level is None
    
    def test_log_level_validation_valid(self):
        """Test that valid log levels are accepted and lowercased."""
        for level in ["debug", "info", "warning", "error", "critical"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level
            
            settings = Settings(log_level=level.upper())
            assert settings.log_level == level
    
    def test_poll_interval_validation_too_low(self):
        """Test that poll_interval_ms < 100 is set to default."""
        settings = Settings(poll_interval_ms=50)
        assert settings.poll_interval_ms == 1000
    
    def test_poll_interval_validation_valid(self):
        """Test that valid poll intervals are accepted."""
        settings = Settings(poll_interval_ms=500)
        assert settings.poll_interval_ms == 500


class TestConfigPaths:
    """Test configuration path functions."""
    
    def test_get_config_dir_windows(self, monkeypatch):
        """Test config directory on Windows."""
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")
        
        config_dir = get_config_dir()
        assert config_dir == Path("C:\\Users\\Test\\AppData\\Roaming\\komorebi-workspace-indicator")
    
    def test_get_config_dir_macos(self, monkeypatch):
        """Test config directory on macOS."""
        monkeypatch.setattr(sys, "platform", "darwin")
        
        config_dir = get_config_dir()
        expected = Path.home() / "Library" / "Application Support" / "komorebi-workspace-indicator"
        assert config_dir == expected
    
    def test_get_config_dir_linux(self, monkeypatch):
        """Test config directory on Linux."""
        monkeypatch.setattr(sys, "platform", "linux")
        
        config_dir = get_config_dir()
        expected = Path.home() / ".config" / "komorebi-workspace-indicator"
        assert config_dir == expected
    
    def test_get_default_config_path(self, monkeypatch):
        """Test default config file path."""
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")
        
        config_path = get_default_config_path()
        assert config_path == Path("C:\\Users\\Test\\AppData\\Roaming\\komorebi-workspace-indicator\\config.toml")


class TestLoadConfig:
    """Test configuration file loading."""
    
    def test_load_config_missing_file(self):
        """Test that missing config file returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.toml"
            settings = load_config(config_path)
            
            # Should return default settings
            assert settings.template == "{workspace}"
            assert settings.opacity == 0.7
    
    def test_load_config_valid_toml(self):
        """Test loading a valid TOML config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text("""
template = "M{monitor} W{workspace}"
show_monitor = true
show_name = true
show_layout = false
log_level = "debug"
opacity = 0.5
poll_interval_ms = 500
""")
            
            settings = load_config(config_path)
            
            assert settings.template == "M{monitor} W{workspace}"
            assert settings.show_monitor is True
            assert settings.show_name is True
            assert settings.show_layout is False
            assert settings.log_level == "debug"
            assert settings.opacity == 0.5
            assert settings.poll_interval_ms == 500
    
    def test_load_config_partial_toml(self):
        """Test loading a TOML file with only some keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text("""
template = "Custom"
opacity = 0.9
""")
            
            settings = load_config(config_path)
            
            # Specified values
            assert settings.template == "Custom"
            assert settings.opacity == 0.9
            
            # Default values for unspecified keys
            assert settings.show_monitor is False
            assert settings.poll_interval_ms == 1000
    
    def test_load_config_invalid_values(self):
        """Test that invalid values in config are corrected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text("""
opacity = 2.0
log_level = "invalid"
poll_interval_ms = 50
""")
            
            settings = load_config(config_path)
            
            # Invalid values should be corrected to defaults
            assert settings.opacity == 0.7
            assert settings.log_level is None
            assert settings.poll_interval_ms == 1000
    
    def test_load_config_malformed_toml(self):
        """Test that malformed TOML returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text("this is not valid toml {{{")
            
            settings = load_config(config_path)
            
            # Should return defaults on parse error
            assert settings.template == "{workspace}"
            assert settings.opacity == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
