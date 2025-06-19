# Komorebi Floating Workspace Indicator - Task List

**Note**: This project is Windows-only as Komorebi window manager is only available for Windows.

## Development Phases

### Phase 1: Core Functionality ✅ COMPLETED

- [x] Multi-monitor detection and management
- [x] Basic floating window creation
- [x] Workspace state detection per monitor
- [x] Simple indicator display (number/name)
- [x] Top-center positioning system
- [x] Always-on-top behavior
- [x] Transparency setting
- [x] Real-time polling and updates
- [x] Komorebi IPC integration
- [x] Error handling and logging

### Phase 2: Configuration & Polish ✅ COMPLETED

- [x] Display format configuration (template system)
- [x] Command-line interface with arguments
- [x] Template system with placeholders
- [x] Color customization (blue theme)
- [x] Size customization (auto-sizing)
- [x] Transparency customization (semi-transparent background)
- [x] Context menu functionality
- [x] Workspace switching via context menu
- [x] Draggable windows with repositioning
- [x] Position reset functionality
- [x] Template testing utility

### Phase 3: Advanced Features 🚧 IN PROGRESS

- [ ] Settings persistence for user preferences
- [ ] Window position saving and restoration
- [ ] Template persistence across sessions
- [ ] Advanced styling options
- [ ] Multiple color schemes
- [ ] Custom font selection
- [ ] Opacity adjustment controls

### Phase 4: Future Enhancements 📋 PLANNED

- [ ] Click-through functionality (left click passes through to content underneath)
- [ ] Edge selection (top, bottom, left, right)
- [ ] System tray integration
- [ ] Minimize to system tray
- [ ] Tray icon with status
- [ ] Global hotkeys for workspace switching
- [ ] Configuration GUI
- [ ] Visual settings interface
- [ ] Plugin system for extensibility
- [ ] Multi-language support
- [ ] Performance optimization
- [ ] Reduced polling frequency when idle
- [ ] Workspace switching via direct click
- [ ] Advanced monitor detection
- [ ] Hot-plugging support
- [ ] DPI scaling improvements

## Current Status

### Completed Features ✅

**Core Application**

- Multi-monitor workspace indicator
- Real-time workspace state updates
- Floating overlay windows
- Always-on-top behavior
- Context menu with workspace switching
- Draggable window repositioning

**Template System**

- Customizable display formats
- Placeholder support: `{monitor}`, `{workspace}`, `{name}`
- Command-line template configuration
- Template testing utility

**User Interface**

- Blue color scheme with semi-transparent background
- Rounded corners and modern styling
- Position reset functionality
- Comprehensive error handling

**Technical Implementation**

- PyQt6-based GUI
- Modular architecture
- Comprehensive logging
- Graceful error handling
- Build system with PyInstaller

### In Progress 🚧

**Settings Persistence**

- User preferences storage
- Window position saving
- Template persistence

### Planned 📋

**Advanced Features**

- Click-through mode
- Edge selection
- System tray integration
- Configuration GUI
- Performance optimizations

---

_This task list tracks the development progress for the Komorebi Floating Workspace Indicator project. Phase 1 and 2 are complete with a fully functional application._
