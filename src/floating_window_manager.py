"""
Floating Window Manager Module

Handles creation and management of floating workspace indicator windows
using PyQt6. Provides always-on-top windows positioned at monitor top-center.
"""

import logging
from typing import Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QMenu, QVBoxLayout, QWidget

from .komorebi_client import WorkspaceState
from .monitor_manager import MonitorInfo

logger = logging.getLogger(__name__)


class WorkspaceIndicator(QWidget):
    """Individual workspace indicator widget for a single monitor."""

    DEFAULT_OPACITY = 0.7
    DEFAULT_TEMPLATE = "{workspace}"

    def __init__(
        self,
        monitor_info: MonitorInfo,
        monitor_id: int,
        parent=None,
        template: str = None,
        show_monitor: bool = False,
        show_name: bool = False,
        komorebi_client=None,
        window_manager=None,
    ):
        """
        Initialize the workspace indicator.

        Args:
            monitor_info: Information about the monitor this indicator belongs to
            monitor_id: The Komorebi monitor ID (not 1-based index)
            parent: Parent widget
            template: Custom template string. Available placeholders:
                     {monitor} - Monitor index (1-based for display)
                     {workspace} - Workspace number (1-based for display)
                     {name} - Workspace name
            show_monitor: Whether to show monitor index (overrides template)
            show_name: Whether to show workspace name (overrides template)
            komorebi_client: KomorebiClient instance for workspace switching
            window_manager: Reference to FloatingWindowManager for refresh operations
        """
        super().__init__(parent)
        self.monitor_info = monitor_info
        self.monitor_id = monitor_id  # Store the actual Komorebi monitor ID
        self.current_workspace = 0  # 0-based internally
        self.current_workspace_name = None
        self.komorebi_client = komorebi_client
        self.window_manager = window_manager  # Store reference to window manager

        # Dragging state
        self.user_moved = False  # Track if user has manually moved the window

        # Set up template
        if template:
            self.template = template
        else:
            self.template = self.DEFAULT_TEMPLATE

        # Set window class name to help Komorebi ignore this window
        self.setWindowTitle("KomorebiWorkspaceIndicator")
        
        self._setup_ui()
        self._setup_window_properties()
        self.set_opacity(self.DEFAULT_OPACITY)

    def _setup_ui(self):
        """Setup the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        # Set styling for the main widget to remove any borders
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
            QMenu {
                background-color: #222;
                color: #fff;
                border-radius: 6px;
                border: 1px solid #444;
            }
            QMenu::item:selected {
                background-color: #444;
            }
        """)

        # Monitor and workspace label
        initial_text = self._format_display_text(self.current_workspace, None)
        self.workspace_label = QLabel(initial_text)
        self.workspace_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.workspace_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.workspace_label.setStyleSheet(
            """
            QLabel {
                color: #2196F3;
                background-color: rgba(0, 0, 0, 0.8);
                border-radius: 4px;
                padding: 8px 12px;
            }
        """
        )

        # Make the label draggable
        self.workspace_label.mousePressEvent = self._label_mouse_press
        self.workspace_label.mouseMoveEvent = self._label_mouse_move
        self.workspace_label.mouseReleaseEvent = self._label_mouse_release
        self.workspace_label.setCursor(Qt.CursorShape.OpenHandCursor)

        layout.addWidget(self.workspace_label)

        # Let the widget size itself to fit content
        self.adjustSize()

        # Position the window after sizing
        self._position_window()

    def _format_display_text(
        self, workspace_index: int, workspace_name: Optional[str]
    ) -> str:
        """Format the display text according to the template."""
        # Convert to 1-based for display only
        display_workspace = workspace_index + 1

        # For monitor display, convert Komorebi monitor ID to a display-friendly number
        # We'll use the monitor ID directly, but if it's too large, we'll map it
        display_monitor = self.monitor_id
        if display_monitor > 100:  # If monitor ID is very large, use a simpler mapping
            # Try to get a simpler display number based on monitor position
            monitors = sorted(
                self.komorebi_client.get_monitor_information() if self.komorebi_client else [],
                key=lambda m: (m.size["left"], m.size["top"])
            )
            for i, monitor in enumerate(monitors):
                if monitor.id == self.monitor_id:
                    display_monitor = i + 1  # 1-based for display
                    break

        return (
            self.template.format(
                monitor=display_monitor,
                workspace=display_workspace,
                name=workspace_name if workspace_name else "",
            )
            .strip()
            .rstrip(":")
        )  # Remove trailing colon if no name

    def _setup_window_properties(self):
        """Setup window properties for floating behavior."""
        # Make window always on top and frameless
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint 
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool  # This prevents it from appearing in taskbar
            | Qt.WindowType.WindowDoesNotAcceptFocus  # This prevents focus stealing
        )

        # Make window semi-transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Prevent the window from being managed by window managers
        self.setAttribute(Qt.WidgetAttribute.WA_X11DoNotAcceptFocus, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Make sure the widget can receive mouse events
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

    def _position_window(self):
        """Position the window at the top-center of its monitor."""
        left, top, right, bottom = self.monitor_info.rect
        center_x = (left + right) // 2

        # Position at top-center with slight offset
        x = center_x - (self.width() // 2)
        y = top + 10  # 10px from top

        self.move(x, y)
        self.user_moved = False  # Reset user_moved flag when repositioning
        logger.info(f"Positioned indicator for monitor {self.monitor_id} at ({x}, {y})")

    def reset_position(self):
        """Reset the window position to default top-center."""
        self.user_moved = False
        self._position_window()

    def _label_mouse_press(self, event):
        """Handle mouse press on the label for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Use window dragging method
            self.windowHandle().startSystemMove()
            self.user_moved = True
            logger.debug("Started dragging via window handle")
            event.accept()

    def _label_mouse_move(self, event):
        """Handle mouse move on the label for dragging."""
        # This method is not needed when using startSystemMove()
        pass

    def _label_mouse_release(self, event):
        """Handle mouse release on the label for dragging."""
        # This method is not needed when using startSystemMove()
        pass

    def update_workspace(
        self, workspace_index: int, workspace_name: Optional[str] = None
    ):
        """
        Update the displayed workspace information.

        Args:
            workspace_index: New workspace index (0-based)
            workspace_name: New workspace name (optional)
        """
        if (
            workspace_index != self.current_workspace
            or workspace_name != self.current_workspace_name
        ):
            self.current_workspace = workspace_index
            self.current_workspace_name = workspace_name

            # Update display text
            display_text = self._format_display_text(workspace_index, workspace_name)
            self.workspace_label.setText(display_text)

            # Always use blue color
            self.workspace_label.setStyleSheet(
                """
                QLabel {
                    color: #2196F3;
                    background-color: rgba(0, 0, 0, 0.8);
                    border-radius: 4px;
                    padding: 8px 12px;
                }
            """
            )

            # Resize to fit new content
            self.adjustSize()

            # Only reposition if user hasn't moved the window manually
            if not self.user_moved:
                self._position_window()

            logger.debug(
                f"Updated workspace indicator for monitor {self.monitor_id} "
                f"to workspace {workspace_index}"
            )

    def _get_workspace_color(self, workspace_index: int) -> str:
        """
        Get color for a workspace index.

        Args:
            workspace_index: Workspace index (0-based)

        Returns:
            Color string for the workspace
        """
        colors = [
            "#4CAF50",  # Green
            "#2196F3",  # Blue
            "#FF9800",  # Orange
            "#9C27B0",  # Purple
            "#F44336",  # Red
            "#00BCD4",  # Cyan
            "#FFEB3B",  # Yellow
            "#795548",  # Brown
            "#607D8B",  # Blue Grey
            "#E91E63",  # Pink
        ]

        return colors[workspace_index % len(colors)]

    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        menu = QMenu(self)

        # Add Reset Position option
        reset_action = menu.addAction("Reset Position")
        reset_action.triggered.connect(self.reset_position)

        # Add Refresh Monitors option
        if self.window_manager:
            refresh_action = menu.addAction("Refresh Monitors")
            refresh_action.triggered.connect(self._refresh_monitors)

        menu.addSeparator()

        # Add Quit option
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit_application)

        # Show the menu at the cursor position
        menu.exec(event.globalPos())

    def _refresh_monitors(self):
        """Refresh monitor configuration."""
        if self.window_manager:
            logger.info("Manual monitor refresh requested")
            self.window_manager.refresh_monitors()

    def _switch_to_workspace(self, workspace_index: int):
        """Switch to the specified workspace."""
        # This would integrate with komorebic to switch workspaces
        # workspace_index is 0-based internally, but we display it as 1-based
        display_number = workspace_index + 1
        logger.info(
            f"Switching to workspace {display_number} (internal index {workspace_index}) on monitor {self.monitor_id}"
        )
        # TODO: Implement workspace switching

    def _show_settings(self):
        """Show settings dialog."""
        logger.info("Show settings requested")
        # TODO: Implement settings dialog

    def _quit_application(self):
        """Quit the application."""
        logger.info("Quit requested")
        QApplication.quit()

    def set_opacity(self, opacity: float):
        """Set the window opacity (0.0 to 1.0)."""
        self.setWindowOpacity(opacity)


class FloatingWindowManager:
    """Manages floating workspace indicator windows for all monitors."""

    def __init__(
        self,
        monitor_manager,
        template: str = None,
        show_monitor: bool = False,
        show_name: bool = False,
        komorebi_client=None,
    ):
        """
        Initialize the floating window manager.

        Args:
            monitor_manager: MonitorManager instance
            template: Custom template for workspace indicators
            show_monitor: Whether to show monitor indices
            show_name: Whether to show workspace names
            komorebi_client: KomorebiClient instance for workspace switching
        """
        self.monitor_manager = monitor_manager
        self.indicators: Dict[int, WorkspaceIndicator] = (
            {}
        )  # key: monitor_id (Komorebi monitor ID)
        self.template = template
        self.show_monitor = show_monitor
        self.show_name = show_name
        self.komorebi_client = komorebi_client
        self.app = None

        # Create indicators for all monitors
        self._create_indicators()

    def _create_indicators(self):
        """Create workspace indicators for all monitors."""
        # Sort monitors by their position to ensure consistent indexing
        monitors = sorted(
            self.monitor_manager.get_monitors(), key=lambda m: (m.rect[0], m.rect[1])
        )  # Sort by x, then y

        # Create indicators with actual Komorebi monitor IDs
        for monitor in monitors:
            indicator = WorkspaceIndicator(
                monitor,
                monitor_id=monitor.id,  # Use actual Komorebi monitor ID
                parent=None,
                template=self.template,
                show_monitor=self.show_monitor,
                show_name=self.show_name,
                komorebi_client=self.komorebi_client,
                window_manager=self,
            )
            self.indicators[monitor.id] = indicator  # Use Komorebi monitor ID as key
            logger.info(f"Created indicator for monitor {monitor.id}")

    def show_all_indicators(self):
        """Show all workspace indicators."""
        for indicator in self.indicators.values():
            indicator.show()
        logger.info(f"Showing {len(self.indicators)} workspace indicators")

    def initialize_all_indicators(self, workspace_index: int):
        """Initialize all indicators with the given workspace index."""
        for monitor_id, indicator in self.indicators.items():
            indicator.update_workspace(workspace_index)
            logger.info(
                f"Initialized indicator for monitor {monitor_id} with workspace {workspace_index}"
            )

    def hide_all_indicators(self):
        """Hide all workspace indicators."""
        for indicator in self.indicators.values():
            indicator.hide()
        logger.info("Hiding all workspace indicators")

    def update_workspace_state(self, workspace_state: WorkspaceState):
        """
        Update workspace state for the appropriate monitor.

        Args:
            workspace_state: Current workspace state
        """
        # Komorebi uses 1-based monitor indices
        monitor_id = workspace_state.monitor_index
        indicator = self.indicators.get(monitor_id)

        if indicator:
            indicator.update_workspace(
                workspace_state.workspace_index, workspace_state.workspace_name
            )
        else:
            logger.warning(f"No indicator found for monitor {monitor_id}")

    def refresh_monitors(self):
        """Refresh indicators when monitor configuration changes."""
        logger.info("Refreshing monitor configuration...")
        
        # First refresh the monitor manager to get updated monitor information
        self.monitor_manager.refresh()
        
        # Hide existing indicators
        self.hide_all_indicators()

        # Clear existing indicators
        for indicator in self.indicators.values():
            indicator.close()
        self.indicators.clear()

        # Create new indicators
        self._create_indicators()

        # Show new indicators
        self.show_all_indicators()

        logger.info("Refreshed workspace indicators for new monitor configuration")

    def get_indicator_count(self) -> int:
        """
        Get the number of active indicators.

        Returns:
            Number of indicators
        """
        return len(self.indicators)
