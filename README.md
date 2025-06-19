# Komorebi Floating Workspace Indicator

A Windows-only utility that displays the current workspace information as floating indicators pinned to the top-center of each monitor, providing quick visual feedback about the active workspace on each connected display.

**Note**: This utility is Windows-only as Komorebi window manager is only available for Windows.

## Features

- **Multi-Monitor Support**: Shows workspace status for each connected monitor independently
- **Floating Overlay**: Always-on-top indicators positioned at the top-center of each monitor
- **Real-time Updates**: Automatically updates when workspace changes occur
- **Custom Templates**: Flexible display format using template strings with placeholders
- **Context Menu**: Right-click for workspace switching and application control
- **Draggable Windows**: Click and drag to reposition indicators
- **Visual Customization**: Color-coded workspace numbers with optional custom names

## Requirements

- **Windows 10/11** (64-bit)
- Python 3.8+ (use `py` command on Windows if `python` points to Python 2.7)
- [Komorebi](https://github.com/LGUG2Z/komorebi) window manager installed and running
- `komorebic.exe` available in PATH

## Installation

### Option 1: Download Pre-built Executable (Recommended)

1. **Download from GitHub Releases**

   - Go to the [Releases page](https://github.com/yourusername/komorebi-workspace-indicator/releases)
   - Download the Windows executable: `komorebi-indicator-windows-latest.exe`

2. **Run the executable**

   ```cmd
   komorebi-indicator-windows-latest.exe
   ```

### Option 2: Build from Source

1. **Clone or download this repository**

   ```cmd
   git clone <repository-url>
   cd komorebi-workspace-indicator
   ```

2. **Install Python dependencies**

   ```cmd
   # On Windows, use py instead of python if python points to Python 2.7
   py -m pip install -r requirements.txt
   ```

3. **Ensure Komorebi is running**
   - Install Komorebi from [https://github.com/LGUG2Z/komorebi](https://github.com/LGUG2Z/komorebi)
   - Make sure `komorebic.exe` is available in your system PATH
   - Start Komorebi window manager

## Usage

### Quick Start

Run the application using the launcher script:

```cmd
# On Windows, use py instead of python if python points to Python 2.7
py run.py
```

### Command Line Options

The application supports various command-line arguments for customization:

```cmd
# Basic usage
py run.py

# Custom template
py run.py --template "M{monitor} W{workspace}"

# Show monitor index
py run.py --show-monitor

# Show workspace name
py run.py --show-name

# Combined options
py run.py --template "M{monitor}:W{workspace} {name}" --show-name
```

### Template System

The `--template` argument allows you to customize the display format using placeholders:

- `{monitor}` - Monitor index (1-based for display)
- `{workspace}` - Workspace number (1-based for display)
- `{name}` - Workspace name (if available)

**Template Examples:**

```cmd
--template "{workspace}"                    # Just workspace number
--template "M{monitor} W{workspace}"        # Monitor and workspace
--template "M{monitor}:W{workspace} {name}" # All info with separator
--template "Monitor {monitor}\\nW{workspace}\\n{name}" # Multi-line
```

### What You'll See

- Floating indicators will appear at the top-center of each monitor
- Each indicator shows the current workspace information based on your template
- Indicators are color-coded for easy identification
- Workspace names will appear if configured in Komorebi and enabled

### Controls

- **Left-click and drag** to reposition indicators
- **Right-click** on any indicator to access the context menu
- **Context menu options**:
  - Switch to specific workspace (0-9)
  - Reset position (returns to top-center)
  - Quit application

## Configuration

### Display Options

- **Template Customization**: Use `--template` to define custom display formats
- **Monitor Display**: Use `--show-monitor` to include monitor indices
- **Name Display**: Use `--show-name` to include workspace names

### Visual Settings

The application currently uses default visual settings:

- Blue color scheme (`#2196F3`)
- Semi-transparent background (`rgba(0, 0, 0, 0.8)`)
- Bold Arial font (14pt)
- Rounded corners with padding

Future versions will include:

- Custom indicator positioning
- Color scheme customization
- Indicator size adjustment
- Opacity settings

## Troubleshooting

### Python Version Issues

If you encounter syntax errors, ensure you're using Python 3.8+:

```cmd
# Check Python version
py --version

# Use py instead of python on Windows
py run.py
```

### Komorebi Not Detected

If you see "Komorebi is not running or not accessible":

1. Ensure Komorebi is installed and running
2. Verify `komorebic.exe` is in your system PATH
3. Test manually: `komorebic query version`

### No Indicators Appear

1. Check the log file `komorebi_indicator.log` for errors
2. Ensure you have at least one monitor connected
3. Verify PyQt6 is properly installed: `py -m pip install PyQt6`

### Performance Issues

1. The application polls Komorebi every 1 second by default
2. Adjust polling interval in `src/main.py` if needed
3. Monitor resource usage in Task Manager

## Development

### Project Structure

```
komorebi-workspace-indicator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main application and polling logic
│   ├── komorebi_client.py      # Komorebi integration and IPC
│   ├── monitor_manager.py      # Multi-monitor detection and management
│   └── floating_window_manager.py  # GUI components and window management
├── requirements.txt
├── run.py                      # Launcher script with CLI arguments
├── build.py                    # Local build script
├── test_templates.py           # Template testing utility
├── PROJECT.md                  # Detailed project documentation
└── README.md                   # This file
```

### Running Tests

```cmd
# Test template functionality
py test_templates.py

# Install development dependencies
py -m pip install pytest

# Run tests (when implemented)
py -m pytest tests/
```

### Building Executable

#### Local Build

For testing builds locally:

```cmd
# Use the automated build script
py build.py

# Or manually with PyInstaller
py -m pip install pyinstaller
pyinstaller --onefile --windowed run.py
```

#### Automated Builds

This project uses GitHub Actions for automated builds. Executables are automatically created when:

1. **Creating a Release**: Go to GitHub → Releases → Create a new release
2. **Pushing a Tag**: `git tag v1.0.0 && git push origin v1.0.0`
3. **Manual Trigger**: Go to Actions tab and manually trigger the workflow

The build process creates Windows executables (`.exe`).

**Build Artifacts**: After a successful build, you can download the executables from:

- The Actions tab → Select workflow run → Artifacts
- The Releases page (if triggered by a release)

### Release Process

1. **Update version** in your code if needed
2. **Create a new tag**:
   ```cmd
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **Create a GitHub Release** (optional but recommended):
   - Go to GitHub → Releases → Create a new release
   - Use the same tag name

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Check the [PROJECT.md](PROJECT.md) file for detailed technical documentation
- Open an issue on GitHub for bugs or feature requests
- Ensure Komorebi is working correctly before reporting issues

---

**Note**: This application requires Komorebi to be running to function properly. Make sure you have Komorebi installed and configured before using this indicator. This utility is Windows-only as Komorebi window manager is only available for Windows.
