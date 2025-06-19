# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Planned

- Settings persistence for user preferences
- Advanced styling options and color schemes
- Click-through mode for indicators
- System tray integration
- Configuration GUI

## [1.0.0] - 2025-06-19

### Added

- **Core Functionality**

  - Multi-monitor workspace indicator support
  - Floating overlay windows with always-on-top behavior
  - Real-time workspace state updates (1-second polling)
  - Automatic monitor detection and management

- **Template System**

  - Customizable display format using template strings
  - Placeholder support: `{monitor}`, `{workspace}`, `{name}`
  - Command-line template configuration via `--template` argument
  - Template testing utility (`test_templates.py`)

- **User Interface**

  - Context menu for workspace switching and application control
  - Draggable windows with click-and-drag repositioning
  - Position reset functionality via context menu
  - Blue color scheme with semi-transparent background

- **Command Line Interface**

  - `--template` argument for custom display formats
  - `--show-monitor` flag to include monitor indices
  - `--show-name` flag to include workspace names
  - Comprehensive help and usage examples

- **Technical Features**
  - PyQt6-based GUI with modern styling
  - Windows API integration for monitor detection via Komorebi
  - Komorebi IPC integration with timeout handling
  - Comprehensive error handling and logging
  - Graceful degradation when Komorebi is unavailable

### Technical Implementation

- **Architecture**

  - Modular design with clean separation of concerns
  - `KomorebiClient` for Komorebi integration and IPC
  - `MonitorManager` for multi-monitor detection and management
  - `FloatingWindowManager` for GUI components and window management
  - `Main Application` for orchestration and polling logic

- **Data Structures**

  - `WorkspaceState` dataclass for workspace information
  - `KomorebiMonitorInfo` for monitor data from Komorebi
  - `MonitorInfo` for internal monitor representation

- **Build System**
  - Local build script (`build.py`) for testing
  - PyInstaller configuration for standalone Windows executables
  - GitHub Actions for automated Windows builds

### Dependencies

- PyQt6>=6.4.0 - GUI framework
- Pillow>=9.0.0 - Image processing (for future features)
- psutil>=5.8.0 - System utilities
- pywin32>=305 - Windows API integration

### Documentation

- Comprehensive README with usage examples
- Detailed PROJECT.md with architecture overview
- Template testing utility with examples
- Build and installation instructions
- Troubleshooting guide for common issues

### Platform Support

- **Windows 10/11** (64-bit) - Primary and only supported platform
- Komorebi window manager integration (Windows-only)
- Windows API integration for multi-monitor support
