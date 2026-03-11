r"""
Configuration Module

Handles loading and validation of configuration settings from TOML files.

Configuration File Location:
- Windows: %APPDATA%\komorebi-workspace-indicator\config.toml
- macOS: ~/Library/Application Support/komorebi-workspace-indicator/config.toml

Configuration Keys:
- template (str): Display template with placeholders {monitor}, {workspace}, {name}, {layout}
- show_monitor (bool): Show monitor index in display
- show_name (bool): Show workspace name in display
- show_layout (bool): Show workspace layout in display
- log_level (str): Logging level (debug, info, warning, error, critical, or null)
- opacity (float): Window opacity (0.0 to 1.0)
- poll_interval_ms (int): Polling interval in milliseconds

CLI arguments override config file values.
"""

import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Try to import tomllib (Python 3.11+) or tomli (fallback)
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """Application settings with defaults."""
    
    template: str = "{workspace}"
    show_monitor: bool = False
    show_name: bool = False
    show_layout: bool = False
    log_level: Optional[str] = None
    opacity: float = 0.7
    poll_interval_ms: int = 1000
    
    def __post_init__(self):
        """Validate settings after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate settings values."""
        # Validate opacity
        if not 0.0 <= self.opacity <= 1.0:
            logger.warning(f"Invalid opacity {self.opacity}, must be between 0.0 and 1.0. Using default 0.7")
            self.opacity = 0.7
        
        # Validate log_level
        valid_log_levels = ['debug', 'info', 'warning', 'error', 'critical', None]
        if self.log_level is not None and self.log_level.lower() not in [lvl for lvl in valid_log_levels if lvl]:
            logger.warning(f"Invalid log_level '{self.log_level}'. Using default (no logging)")
            self.log_level = None
        elif self.log_level is not None:
            self.log_level = self.log_level.lower()
        
        # Validate poll_interval_ms
        if self.poll_interval_ms < 100:
            logger.warning(f"Invalid poll_interval_ms {self.poll_interval_ms}, must be >= 100. Using default 1000")
            self.poll_interval_ms = 1000


def get_config_dir() -> Path:
    """
    Get the application configuration directory.
    
    Returns:
        Path to the config directory
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%\komorebi-workspace-indicator
        appdata = os.environ.get("APPDATA", ".")
        return Path(appdata) / "komorebi-workspace-indicator"
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/komorebi-workspace-indicator
        return Path.home() / "Library" / "Application Support" / "komorebi-workspace-indicator"
    else:
        # Linux/other: ~/.config/komorebi-workspace-indicator
        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(xdg_config) / "komorebi-workspace-indicator"


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.
    
    Returns:
        Path to config.toml in the config directory
    """
    return get_config_dir() / "config.toml"


def load_config(path: Optional[Path] = None) -> Settings:
    """
    Load configuration from a TOML file.
    
    Args:
        path: Path to config file. If None, uses default path.
    
    Returns:
        Settings object with loaded or default values
    """
    if path is None:
        path = get_default_config_path()
    
    # If file doesn't exist, return defaults
    if not path.exists():
        logger.debug(f"Config file not found at {path}, using defaults")
        return Settings()
    
    # Check if TOML library is available
    if tomllib is None:
        logger.warning("TOML library not available (tomli/tomllib). Cannot load config file. Using defaults.")
        logger.warning("Install tomli for Python < 3.11: pip install tomli")
        return Settings()
    
    try:
        # Load and parse TOML file
        with open(path, "rb") as f:
            config_data = tomllib.load(f)
        
        logger.info(f"Loaded configuration from {path}")
        
        # Extract settings with defaults
        settings = Settings(
            template=config_data.get("template", Settings.template),
            show_monitor=config_data.get("show_monitor", Settings.show_monitor),
            show_name=config_data.get("show_name", Settings.show_name),
            show_layout=config_data.get("show_layout", Settings.show_layout),
            log_level=config_data.get("log_level", Settings.log_level),
            opacity=config_data.get("opacity", Settings.opacity),
            poll_interval_ms=config_data.get("poll_interval_ms", Settings.poll_interval_ms),
        )
        
        return settings
        
    except Exception as e:
        logger.warning(f"Failed to load config from {path}: {e}")
        logger.warning("Using default settings")
        return Settings()


def merge_cli_args(settings: Settings, args) -> Settings:
    """
    Merge CLI arguments into settings, with CLI taking precedence.
    
    Args:
        settings: Settings loaded from config file
        args: Parsed command line arguments
    
    Returns:
        Merged Settings object
    """
    # Create a new Settings object with merged values
    merged = Settings(
        template=settings.template,
        show_monitor=settings.show_monitor,
        show_name=settings.show_name,
        show_layout=settings.show_layout,
        log_level=settings.log_level,
        opacity=settings.opacity,
        poll_interval_ms=settings.poll_interval_ms,
    )
    
    # Override with CLI args if provided
    # For template, check if it's not the default (meaning user explicitly set it)
    if hasattr(args, 'template') and args.template != "{workspace}":
        merged.template = args.template
    
    # For boolean flags, True means user explicitly set them
    if hasattr(args, 'show_monitor') and args.show_monitor:
        merged.show_monitor = True
    
    if hasattr(args, 'show_name') and args.show_name:
        merged.show_name = True
    
    if hasattr(args, 'show_layout') and args.show_layout:
        merged.show_layout = True
    
    # For log level, check various CLI options
    if hasattr(args, 'debug') and args.debug:
        merged.log_level = 'debug'
    elif hasattr(args, 'verbose') and args.verbose:
        merged.log_level = 'info'
    elif hasattr(args, 'log_level') and args.log_level:
        merged.log_level = args.log_level
    
    return merged
