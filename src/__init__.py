"""
Komorebi Floating Workspace Indicator Package

A Windows utility that displays workspace information as floating indicators
on each monitor, integrated with the Komorebi window manager.
"""

__version__ = "1.0.0"
__author__ = "Komorebi Indicator Team"

from .floating_window_manager import FloatingWindowManager, WorkspaceIndicator
from .komorebi_client import KomorebiClient, WorkspaceState
from .main import KomorebiIndicatorApp, main
from .monitor_manager import MonitorInfo, MonitorManager

__all__ = [
    "KomorebiClient",
    "WorkspaceState",
    "MonitorManager",
    "MonitorInfo",
    "FloatingWindowManager",
    "WorkspaceIndicator",
    "KomorebiIndicatorApp",
    "main",
]
