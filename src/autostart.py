"""
Autostart functionality for Komorebi Workspace Indicator

Handles creating and removing Windows startup shortcuts.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

try:
    import win32com.client
    import win32api
    import win32con
    from win32com.shell import shell, shellcon
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logger = logging.getLogger(__name__)


class AutostartManager:
    """Manages Windows autostart functionality for the application."""
    
    def __init__(self):
        """Initialize the autostart manager."""
        self.app_name = "komorebi-workspace-indicator"
        self.shortcut_name = f"{self.app_name}.lnk"
        
    def get_startup_folder(self) -> Optional[Path]:
        """
        Get the Windows startup folder path.
        
        Returns:
            Path to the startup folder, or None if unavailable
        """
        if not WIN32_AVAILABLE:
            logger.error("Win32 libraries not available")
            return None
            
        try:
            # Get the startup folder path using shell folders
            startup_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, None, 0)
            return Path(startup_folder)
        except Exception as e:
            logger.error(f"Failed to get startup folder: {e}")
            return None
    
    def get_shortcut_path(self) -> Optional[Path]:
        """
        Get the full path to the shortcut file.
        
        Returns:
            Path to the shortcut file, or None if startup folder unavailable
        """
        startup_folder = self.get_startup_folder()
        if startup_folder is None:
            return None
        return startup_folder / self.shortcut_name
    
    def get_executable_path(self) -> Path:
        """
        Get the path to the executable or script to run.
        
        Returns:
            Path to the executable or script
        """
        # Check if we're running as a PyInstaller executable
        if getattr(sys, 'frozen', False):
            return Path(sys.executable)
        else:
            # Running as a Python script - point to run.py
            script_dir = Path(__file__).parent.parent
            return script_dir / "run.py"
    
    def is_autostart_enabled(self) -> bool:
        """
        Check if autostart is currently enabled.
        
        Returns:
            True if autostart shortcut exists, False otherwise
        """
        shortcut_path = self.get_shortcut_path()
        if shortcut_path is None:
            return False
        return shortcut_path.exists()
    
    def enable_autostart(self) -> bool:
        """
        Enable autostart by creating a shortcut in the startup folder.
        
        Returns:
            True if successful, False otherwise
        """
        if not WIN32_AVAILABLE:
            logger.error("Cannot enable autostart: Win32 libraries not available")
            return False
            
        try:
            shortcut_path = self.get_shortcut_path()
            if shortcut_path is None:
                logger.error("Cannot get startup folder path")
                return False
                
            executable_path = self.get_executable_path()
            
            # Create the shortcut using COM
            shell_obj = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell_obj.CreateShortCut(str(shortcut_path))
            
            if getattr(sys, 'frozen', False):
                # Running as executable
                shortcut.Targetpath = str(executable_path)
                shortcut.WorkingDirectory = str(executable_path.parent)
            else:
                # Running as Python script
                python_exe = sys.executable
                shortcut.Targetpath = python_exe
                shortcut.Arguments = f'"{executable_path}"'
                shortcut.WorkingDirectory = str(executable_path.parent)
            
            shortcut.Description = "Komorebi Workspace Indicator"
            shortcut.save()
            
            logger.info(f"Autostart enabled: Created shortcut at {shortcut_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable autostart: {e}")
            return False
    
    def disable_autostart(self) -> bool:
        """
        Disable autostart by removing the shortcut from the startup folder.
        
        Returns:
            True if successful or shortcut doesn't exist, False on error
        """
        try:
            shortcut_path = self.get_shortcut_path()
            if shortcut_path is None:
                logger.error("Cannot get startup folder path")
                return False
                
            if shortcut_path.exists():
                shortcut_path.unlink()
                logger.info(f"Autostart disabled: Removed shortcut at {shortcut_path}")
            else:
                logger.info("Autostart was not enabled (shortcut not found)")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable autostart: {e}")
            return False
    
    def get_status(self) -> str:
        """
        Get a human-readable status of autostart configuration.
        
        Returns:
            Status string
        """
        if not WIN32_AVAILABLE:
            return "Autostart unavailable (Win32 libraries missing)"
            
        shortcut_path = self.get_shortcut_path()
        if shortcut_path is None:
            return "Autostart unavailable (cannot access startup folder)"
            
        if self.is_autostart_enabled():
            return f"Autostart enabled (shortcut: {shortcut_path})"
        else:
            return "Autostart disabled"


def enable_autostart() -> bool:
    """Enable autostart functionality."""
    manager = AutostartManager()
    return manager.enable_autostart()


def disable_autostart() -> bool:
    """Disable autostart functionality."""
    manager = AutostartManager()
    return manager.disable_autostart()


def is_autostart_enabled() -> bool:
    """Check if autostart is enabled."""
    manager = AutostartManager()
    return manager.is_autostart_enabled()


def get_autostart_status() -> str:
    """Get autostart status string."""
    manager = AutostartManager()
    return manager.get_status() 