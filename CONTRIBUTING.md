# Contributing to Komorebi Workspace Indicator

Thank you for your interest in contributing to this Windows-only project!

**Note**: This project is Windows-only as Komorebi window manager is only available for Windows.

## How to Contribute

### Reporting Bugs

- Use the GitHub issue tracker
- Include detailed steps to reproduce
- Specify your Windows version and Python version
- Attach relevant log files

### Suggesting Features

- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Consider implementation complexity

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Prerequisites

- **Windows 10/11** (64-bit)
- Python 3.8 or higher
- Git
- Komorebi window manager (for testing)

### Installation

1. Clone your fork
2. Create and activate a virtual environment (Windows):
   ```cmd
   py -3 -m venv venv
   venv\Scripts\activate
   ```
3. Install the project with development dependencies:
   ```cmd
   pip install -e ".[dev]"
   ```

### Development Workflow

#### Code Quality Checks

The project uses simple, fast Python development tools:

- **Ruff**: Fast Python linter and formatter (replaces flake8 + black)
- **Black**: Code formatter (backup to Ruff)

#### Running Tests

```cmd
# Run all tests
pytest

# Run tests with verbose output
pytest -v
```

#### Code Formatting and Linting

```cmd
# Format and lint all code (recommended)
ruff check --fix src/
ruff format src/

# Or use black directly
black src/
```

## Code Style

- Follow PEP 8 guidelines (enforced by Ruff)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small (< 50 lines)
- Use meaningful commit messages

## Testing Guidelines

- Write tests for new functionality when possible
- Focus on testing the core workspace indicator logic
- Mock external dependencies (Qt, Komorebi client) in tests
- Test both success and error cases
