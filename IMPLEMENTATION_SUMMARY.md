# Configuration File Support - Implementation Summary

## Overview

Successfully implemented configuration file support for the Komorebi Workspace Indicator application. Users can now set default preferences in a TOML configuration file, with command-line arguments overriding config file values.

## Changes Made

### 1. New Files Created

#### `src/config.py`
- **Settings dataclass**: Holds all configurable settings with defaults
- **Validation**: Automatic validation of opacity (0.0-1.0), log_level, and poll_interval_ms (≥100ms)
- **Path functions**: 
  - `get_config_dir()`: Returns platform-specific config directory
  - `get_default_config_path()`: Returns default config file path
- **Config loading**: `load_config(path)` loads and parses TOML files
- **CLI merging**: `merge_cli_args(settings, args)` merges CLI args with config

#### `config.example.toml`
- Complete example configuration file with all available options
- Includes comments explaining each setting
- Shows example values and valid ranges

#### `tests/test_config.py`
- Comprehensive test suite with 17 tests
- Tests default settings, validation, path resolution, and config loading
- All tests pass successfully

### 2. Modified Files

#### `pyproject.toml`
- Added `tomli>=2.0.0` dependency for Python < 3.11
- Python 3.11+ uses built-in `tomllib`

#### `run.py`
- Added `--config` argument to specify custom config file path
- Loads config file at startup
- Merges CLI arguments with config (CLI takes precedence)
- Passes all settings (including opacity and poll_interval_ms) to main()
- Updated detached process spawning to pass config path

#### `src/main.py`
- Extended `main()` to accept `opacity` and `poll_interval_ms` parameters
- Updated `KomorebiIndicatorApp.__init__()` to accept and use these parameters
- Passes opacity to FloatingWindowManager
- Uses poll_interval_ms for polling timer

#### `src/floating_window_manager.py`
- `FloatingWindowManager.__init__()` now accepts optional `opacity` parameter
- Stores and passes opacity to each WorkspaceIndicator
- `WorkspaceIndicator.__init__()` now accepts optional `opacity` parameter
- Uses provided opacity or falls back to DEFAULT_OPACITY

#### `README.md`
- Added comprehensive "Configuration" section
- Documents config file location for each platform
- Table of all configuration keys with types, defaults, and descriptions
- Example configuration file snippet
- Notes about CLI arguments overriding config

### 3. Configuration Settings

| Setting          | Type   | Default         | Description                                    |
| ---------------- | ------ | --------------- | ---------------------------------------------- |
| template         | string | `"{workspace}"` | Display template with placeholders             |
| show_monitor     | bool   | false           | Show monitor index (1-based)                   |
| show_name        | bool   | false           | Show workspace name                            |
| show_layout      | bool   | false           | Show workspace layout (e.g., VerticalStack)    |
| log_level        | string | null            | Logging level or null for no logging           |
| opacity          | float  | 0.7             | Window opacity (0.0 to 1.0)                    |
| poll_interval_ms | int    | 1000            | Polling interval in milliseconds (minimum 100) |

### 4. Configuration File Locations

- **Windows**: `%APPDATA%\komorebi-workspace-indicator\config.toml`
- **macOS**: `~/Library/Application Support/komorebi-workspace-indicator/config.toml`
- **Linux**: `~/.config/komorebi-workspace-indicator/config.toml`

## Usage Examples

### Using Default Config Location

1. Copy `config.example.toml` to the config directory
2. Edit values as desired
3. Run the application: `py run.py`

### Using Custom Config File

```cmd
py run.py --config path\to\custom\config.toml
```

### Overriding Config with CLI

```cmd
# Config file sets opacity=0.8, but CLI overrides it
py run.py --template "M{monitor} W{workspace}"
```

## Testing

All tests pass successfully:

```
============================= 17 passed in 0.05s ==============================
```

Test coverage includes:
- Default settings creation
- Validation of opacity, log_level, and poll_interval_ms
- Config directory path resolution (Windows, macOS, Linux)
- Loading missing config files (returns defaults)
- Loading valid TOML files
- Loading partial TOML files (missing keys use defaults)
- Handling invalid values (corrected to defaults)
- Handling malformed TOML (returns defaults)

## Backward Compatibility

The implementation is fully backward compatible:
- If no config file exists, the application uses hardcoded defaults
- All existing CLI arguments work exactly as before
- CLI arguments always override config file values
- No breaking changes to existing functionality

## Dependencies

- Added `tomli>=2.0.0` for Python < 3.11 (conditional dependency)
- Python 3.11+ uses built-in `tomllib` (no extra dependency)

## Future Enhancements (Not Implemented)

The following were identified as optional enhancements but not implemented in this version:
- Creating config directory and file if they don't exist
- Watching config file for changes and reloading
- GUI settings dialog (already planned in PROJECT.md)
