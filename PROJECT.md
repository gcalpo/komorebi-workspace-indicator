# Komorebi Floating Workspace Indicator

A lightweight Windows-only utility that displays the current workspace information as floating indicators pinned to the top-center of each monitor, providing quick visual feedback about the active workspace on each connected display.

**Note**: This utility is Windows-only as Komorebi window manager is only available for Windows.

## Project Overview

The Komorebi Floating Workspace Indicator is a Windows-only application that integrates with Komorebi window manager to show the current workspace status as floating overlays on each monitor. This utility provides quick visual feedback about the active workspace with customizable display formats and real-time updates.

## Core Features

### Primary Functionality

- **Floating Overlay**: Displays workspace information as floating indicators on each monitor
- **Multi-Monitor Support**: Shows workspace status for each connected monitor independently
- **Top-Center Positioning**: Pins to the top-center of each monitor for consistent placement
- **Real-time Updates**: Automatically updates when workspace changes occur (1-second polling)
- **Custom Templates**: Flexible display format using template strings with placeholders
- **Draggable Windows**: Click and drag to reposition indicators
- **Context Menu**: Right-click for workspace switching and application control

### Configuration Options

- **Template System**: Customize display format using `{monitor}`, `{workspace}`, and `{name}` placeholders
- **Command Line Arguments**: `--template`, `--show-monitor`, `--show-name` options
- **Visual Customization**: Blue color scheme with semi-transparent background
- **Always-on-Top**: Stays visible above other applications
- **Position Reset**: Context menu option to return to default top-center position

## Technical Requirements

### Platform & Dependencies

- **Operating System**: Windows 10/11 (64-bit)
- **Language**: Python 3.8+ (use `py` command on Windows if `python` points to Python 2.7)
- **Framework**: PyQt6 for GUI components
- **System Integration**: Windows API for multi-monitor support via Komorebi
- **Window Manager Integration**: Komorebi IPC through `komorebic.exe`

### Core Libraries

- `PyQt6` - GUI framework for floating windows and event handling
- `subprocess` - Execute komorebic commands and parse responses
- `json` - Parse Komorebi monitor information
- `logging` - Application logging and debugging
- `dataclasses` - Data structures for monitor and workspace information

## Architecture

### Component Structure

1. **KomorebiClient** (`src/komorebi_client.py`): Executes and parses `komorebic query` responses
2. **MonitorManager** (`src/monitor_manager.py`): Detects and manages multiple monitor configurations
3. **FloatingWindowManager** (`src/floating_window_manager.py`): Handles floating window creation and positioning
4. **Main Application** (`src/main.py`): Orchestrates components and provides polling loop

### Data Flow

1. **Initialization**: MonitorManager detects available monitors using Komorebi
2. **Window Creation**: FloatingWindowManager creates indicators for each monitor
3. **Polling Loop**: Main application polls Komorebi every 1 second for workspace changes
4. **State Updates**: KomorebiClient queries current workspace state
5. **UI Updates**: FloatingWindowManager updates corresponding indicators
6. **User Interaction**: Context menu and drag-and-drop functionality

### Komorebi Integration

The application uses the `komorebic query` command to retrieve workspace state:

```cmd
komorebic query focused-monitor-index
komorebic query focused-workspace-index
komorebic query focused-workspace-name
komorebic query focused-workspace-layout
komorebic query monitor-info
```

### Template System

The template system allows users to customize display formats:

- `{monitor}` - Monitor index (1-based for display)
- `{workspace}` - Workspace number (1-based for display)
- `{name}` - Workspace name (if available)

**Example Templates:**

- `"{workspace}"` - Just workspace number
- `"M{monitor} W{workspace}"` - Monitor and workspace
- `"M{monitor}:W{workspace} {name}"` - All info with separator

## User Experience

### Visual Design

- **Clean, Minimal Design**: Simple template-based display
- **Always-On-Top**: Stays visible above other applications
- **High Contrast**: Blue text (`#2196F3`) on dark background for visibility
- **Semi-transparent**: `rgba(0, 0, 0, 0.8)` background for non-intrusive appearance
- **Rounded Corners**: 4px border radius with padding for modern look
- **Bold Typography**: 14pt Arial Bold for readability

### Interaction Design

- **Drag and Drop**: Left-click and drag to reposition indicators
- **Context Menu**: Right-click for workspace switching and controls
- **Position Reset**: Context menu option to return to default position
- **Workspace Switching**: Direct workspace switching via context menu

### Configuration

- **Command Line Interface**: Template and display options via CLI arguments
- **Runtime Customization**: Template changes without restart
- **Monitor Detection**: Automatic detection of connected monitors
- **Error Handling**: Graceful handling of Komorebi connection issues

## Implementation Details

### Monitor Detection

- Uses Komorebi's `monitor-info` query to detect monitors
- Filters out "UNKNOWN" monitors for reliability
- Handles zero-width/height monitors with fallback dimensions
- Maps Komorebi monitor IDs to display indices

### Workspace State Management

- Tracks workspace state per monitor using Komorebi monitor IDs
- Caches state for change detection
- Handles workspace name and layout information
- Provides workspace switching functionality

### Window Management

- Creates always-on-top, frameless windows
- Positions at top-center of each monitor
- Handles user repositioning with drag-and-drop
- Provides position reset functionality

### Error Handling

- Graceful degradation when Komorebi is not available
- Logging to file (`komorebi_indicator.log`) for debugging
- Timeout handling for komorebic commands (5-second timeout)
- Fallback behavior for monitor detection issues

## Future Enhancements

### Planned Features

- **Settings Persistence**: Save user preferences and window positions
- **Advanced Styling**: More color schemes and visual customization
- **Edge Selection**: Choose which edge of the monitor to display on
- **Click-through Mode**: Option to make windows click-through
- **Workspace Switching**: Click to switch workspaces directly
- **Hotkey Support**: Global hotkeys for workspace switching

### Potential Improvements

- **Performance Optimization**: Reduce polling frequency when idle
- **Multi-language Support**: Internationalization for templates
- **Plugin System**: Extensible architecture for custom features
- **System Tray Integration**: Minimize to system tray
- **Configuration GUI**: Visual settings interface

## Installation & Distribution

### Distribution Method

- **Executable**: PyInstaller for standalone .exe files
- **Portable**: Single executable file for portable use
- **Source**: Python package with requirements.txt

### Build Process

- **Local Build**: `py build.py` for testing
- **Automated Builds**: GitHub Actions for Windows builds
- **Release Process**: Tag-based releases with automated executables

### Installation Requirements

- Windows 10/11 (64-bit)
- Python 3.8+ (for source installation)
- Komorebi window manager (for full functionality)
- PyQt6 and dependencies (automatically installed)

## Success Metrics

### Technical Metrics

- **Response Time**: < 1 second for workspace state updates (configurable)
- **Memory Usage**: < 50MB RAM usage
- **CPU Usage**: < 2% average CPU usage during polling
- **Reliability**: Stable operation with graceful error handling

### User Experience Metrics

- **Simplicity**: Easy to understand and use with template system
- **Performance**: Smooth operation without lag or stuttering
- **Visibility**: Clear workspace status display with high contrast
- **Customization**: Flexible display options via templates

### Code Quality Metrics

- **Modularity**: Clean separation of concerns across modules
- **Error Handling**: Comprehensive error handling and logging
- **Documentation**: Well-documented code with type hints
- **Testing**: Template testing utility and future test coverage

---

_This project provides a simple, lightweight Windows-only solution for workspace status indication across multiple monitors with modern Python and PyQt6 technologies._
