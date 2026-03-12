"""
Main Application Module

Main entry point for the Komorebi Floating Workspace Indicator.
Orchestrates all components and provides the main application loop.
"""

import logging
import sys
import time
from typing import Optional

# Add these imports for fullscreen detection
import win32gui
import win32con
import win32api
import win32process
import ctypes

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from .floating_window_manager import FloatingWindowManager
from .komorebi_client import KomorebiClient, WorkspaceState
from .monitor_manager import MonitorManager

# Configure logging


def configure_logging(log_level: str = None):
    """
    Configure logging based on the specified level.
    
    Args:
        log_level: Logging level ('debug', 'info', 'warning', 'error', 'critical')
                  If None, logging is effectively disabled (level 100)
    """
    if log_level is None:
        # Set to level 100 to effectively disable all logging
        level = 100
    else:
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        level = level_map.get(log_level.lower(), 100)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("komorebi_indicator.log")],
        force=True  # Reconfigure existing loggers
    )



logger = logging.getLogger(__name__)


class KomorebiIndicatorApp:
    """Main application class for the Komorebi Floating Workspace Indicator."""

    def __init__(
        self, 
        template: Optional[str] = None, 
        show_monitor: bool = False, 
        show_name: bool = False, 
        show_layout: bool = False,
        opacity: Optional[float] = None,
        poll_interval_ms: int = 1000,
    ):
        """
        Initialize the application.

        Args:
            template: Custom template string for workspace indicators
            show_monitor: Whether to show monitor indices
            show_name: Whether to show workspace names
            show_layout: Whether to show workspace layout
            opacity: Window opacity (0.0 to 1.0)
            poll_interval_ms: Polling interval in milliseconds
        """
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Komorebi Floating Workspace Indicator")
        self.app.setApplicationVersion("1.0.0")

        # Initialize components
        self.komorebi_client = KomorebiClient()
        self.monitor_manager = MonitorManager(self.komorebi_client)
        self.window_manager = FloatingWindowManager(
            self.monitor_manager,
            template=template if template is not None else "",
            show_monitor=show_monitor,
            show_name=show_name,
            show_layout=show_layout,
            komorebi_client=self.komorebi_client,
            opacity=opacity,
        )

        # Setup polling timer
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_workspace_state)
        self.poll_interval = poll_interval_ms

        # State tracking - track (workspace_index, workspace_name, workspace_layout, workspace_layout_flip) per monitor
        self.monitor_workspace_states = {}  # monitor_id -> (workspace_index, workspace_name, workspace_layout, workspace_layout_flip)
        self.last_update_time = {}  # monitor_id -> timestamp (for log throttling only)
        self.is_running = False

        logger.info("Komorebi Floating Workspace Indicator initialized")
        if template:
            logger.info(f"Using custom template: '{template}'")

    def start(self):
        """Start the application."""
        try:
            # Check if Komorebi is running
            if not self.komorebi_client.is_komorebi_running():
                logger.error("Komorebi is not running or not accessible!")
                logger.error("Please ensure Komorebi is installed and running.")
                return False

            logger.info("Komorebi detected and accessible")

            # Log monitor configuration
            logger.info(self.monitor_manager.get_monitor_summary())

            # Initialize workspace state for all monitors
            self._initialize_workspace_states()

            # Show workspace indicators
            self.window_manager.show_all_indicators()

            # Start polling for workspace changes
            self.poll_timer.start(self.poll_interval)
            self.is_running = True

            logger.info(
                f"Started polling for workspace changes every {self.poll_interval}ms"
            )
            logger.info(
                f"Created {self.window_manager.get_indicator_count()} workspace indicators"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            return False

    def _initialize_workspace_states(self):
        """Initialize workspace state for all detected monitors."""
        try:
            # Get workspace state for all monitors individually
            all_states = self.komorebi_client.get_all_monitors_workspace_state()
            if all_states:
                for state in all_states:
                    self.monitor_workspace_states[state.monitor_index] = (
                        state.workspace_index,
                        state.workspace_name,
                        state.workspace_layout,
                        getattr(state, "workspace_layout_flip", None),
                    )
                    logger.info(
                        f"Initialized monitor {state.monitor_index} with workspace {state.workspace_index}"
                    )
                    # Update the specific indicator for this monitor
                    self.window_manager.update_workspace_state(state)
            else:
                # Fallback to old method if get_all_monitors_workspace_state fails
                current_state = self.komorebi_client.get_current_workspace_state()
                if current_state:
                    for monitor in self.monitor_manager.get_monitors():
                        self.monitor_workspace_states[monitor.id] = (
                            current_state.workspace_index,
                            getattr(current_state, "workspace_name", None),
                            getattr(current_state, "workspace_layout", None),
                            getattr(current_state, "workspace_layout_flip", None),
                        )
                        logger.info(
                            f"Initialized monitor {monitor.id} with workspace {current_state.workspace_index}"
                        )
                    self.window_manager.initialize_all_indicators(
                        current_state.workspace_index
                    )
        except Exception as e:
            logger.error(f"Failed to initialize workspace states: {e}")

    def stop(self):
        """Stop the application."""
        logger.info("Stopping Komorebi Floating Workspace Indicator...")

        self.is_running = False
        self.poll_timer.stop()
        self.window_manager.hide_all_indicators()

        logger.info("Application stopped")

    def _is_focused_window_fullscreen(self, monitor_rects=None):
        """
        Check if the currently focused window is running fullscreen on any monitor.
        Args:
            monitor_rects: Optional list of monitor rects (left, top, right, bottom)
        Returns:
            True if a fullscreen window is detected, False otherwise
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return False
            # Ignore our own indicator windows
            title = win32gui.GetWindowText(hwnd)
            if "KomorebiWorkspaceIndicator" in title:
                return False
            rect = win32gui.GetWindowRect(hwnd)
            l, t, r, b = rect
            # Get all monitor rects if not provided
            if monitor_rects is None:
                monitor_rects = [m.rect for m in self.monitor_manager.get_monitors()]
            for mon_l, mon_t, mon_r, mon_b in monitor_rects:
                # Allow a small tolerance for borders
                if abs(l - mon_l) <= 2 and abs(t - mon_t) <= 2 and abs(r - mon_r) <= 2 and abs(b - mon_b) <= 2:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking fullscreen window: {e}")
            return False

    def _poll_workspace_state(self):
        """Poll for workspace state changes and hide indicator if fullscreen app is focused."""
        if not self.is_running:
            return

        try:
            # Hide indicators if fullscreen app is focused
            if self._is_focused_window_fullscreen():
                self.window_manager.hide_all_indicators()
                return
            else:
                self.window_manager.show_all_indicators()

            # Get workspace state for all monitors
            all_states = self.komorebi_client.get_all_monitors_workspace_state()

            if not all_states:
                logger.warning("Failed to get workspace states for all monitors")
                return

            current_time = time.time()

            # Always push current state to indicators every poll so every displayed
            # property (workspace, name, layout) updates when it changes.
            for current_state in all_states:
                self.window_manager.update_workspace_state(current_state)

                # Log only when something changed (throttle log spam)
                monitor_id = current_state.monitor_index
                last_update = self.last_update_time.get(monitor_id, 0)
                if current_time - last_update >= 0.5 and self._has_state_changed(
                    current_state
                ):
                    logger.info(
                        f"Workspace changed: Monitor {monitor_id} -> "
                        f"W{current_state.workspace_index} "
                        f"name={current_state.workspace_name!r} layout={current_state.workspace_layout!r}"
                    )
                    self.monitor_workspace_states[monitor_id] = (
                        current_state.workspace_index,
                        current_state.workspace_name,
                        current_state.workspace_layout,
                        getattr(current_state, "workspace_layout_flip", None),
                    )
                    self.last_update_time[monitor_id] = current_time

            # Ensure we have stored state for all monitors (for next poll's change detection)
            for current_state in all_states:
                monitor_id = current_state.monitor_index
                if monitor_id not in self.monitor_workspace_states:
                    self.monitor_workspace_states[monitor_id] = (
                        current_state.workspace_index,
                        current_state.workspace_name,
                        current_state.workspace_layout,
                        getattr(current_state, "workspace_layout_flip", None),
                    )

        except Exception as e:
            logger.error(f"Error during workspace polling: {e}")

    def _has_state_changed(self, current_state: WorkspaceState) -> bool:
        """True if any displayed property (workspace, name, layout, layout_flip) changed."""
        monitor_id = current_state.monitor_index
        if monitor_id not in self.monitor_workspace_states:
            return True
        prev = self.monitor_workspace_states[monitor_id]
        # Unpack: (workspace_index, workspace_name, workspace_layout, workspace_layout_flip) or legacy
        if isinstance(prev, tuple):
            prev_idx = prev[0] if len(prev) > 0 else None
            prev_name = prev[1] if len(prev) > 2 else None
            prev_layout = prev[2] if len(prev) > 2 else (prev[1] if len(prev) == 2 else None)
            prev_flip = prev[3] if len(prev) > 3 else None
            if len(prev) == 2:
                prev_name = None  # (idx, layout) legacy
        else:
            prev_idx, prev_name, prev_layout, prev_flip = prev, None, None, None
        current_flip = getattr(current_state, "workspace_layout_flip", None)
        return (
            prev_idx != current_state.workspace_index
            or prev_name != current_state.workspace_name
            or prev_layout != current_state.workspace_layout
            or prev_flip != current_flip
        )

    def run(self):
        """Run the application main loop."""
        if not self.start():
            return 1

        try:
            logger.info("Starting main application loop...")
            return self.app.exec()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.stop()
            return 0
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.stop()
            return 1
        finally:
            self.stop()


def main(
    template: Optional[str] = None, 
    show_monitor: bool = False, 
    show_name: bool = False, 
    show_layout: bool = False, 
    log_level: str = None,
    opacity: Optional[float] = None,
    poll_interval_ms: int = 1000,
):
    """
    Main entry point.

    Args:
        template: Custom template string for workspace indicators
        show_monitor: Whether to show monitor indices
        show_name: Whether to show workspace names
        show_layout: Whether to show workspace layout
        log_level: Logging level ('debug', 'info', 'warning', 'error', 'critical')
                  If None, logging is effectively disabled
        opacity: Window opacity (0.0 to 1.0)
        poll_interval_ms: Polling interval in milliseconds
    """
    # Configure logging first
    configure_logging(log_level)
    
    try:
        app = KomorebiIndicatorApp(
            template=template if template is not None else "",
            show_monitor=show_monitor,
            show_name=show_name,
            show_layout=show_layout,
            opacity=opacity,
            poll_interval_ms=poll_interval_ms,
        )
        return app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
