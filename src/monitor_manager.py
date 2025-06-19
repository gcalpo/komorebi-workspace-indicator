"""
Monitor Manager Module

Handles detection and management of multiple monitors using Komorebi's monitor information.
Provides information about monitor geometry, positioning, and properties.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .komorebi_client import KomorebiClient

logger = logging.getLogger(__name__)


@dataclass
class MonitorInfo:
    """Information about a monitor."""

    id: int  # Komorebi monitor ID
    name: str
    is_primary: bool
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    work_rect: Tuple[int, int, int, int]  # Work area (excluding taskbar)
    width: int
    height: int
    dpi: int


class MonitorManager:
    """Manages detection and information about multiple monitors using Komorebi."""

    def __init__(self, komorebi_client: KomorebiClient):
        """
        Initialize the monitor manager.

        Args:
            komorebi_client: KomorebiClient instance
        """
        self.komorebi_client = komorebi_client
        self._monitors: Dict[int, MonitorInfo] = {}  # key: monitor_id
        self._refresh_monitors()

    def _refresh_monitors(self):
        """Refresh the list of available monitors using Komorebi."""
        try:
            self._monitors.clear()

            # Get monitors from Komorebi
            komorebi_monitors = self.komorebi_client.get_monitor_information()

            # Filter out UNKNOWN monitors first
            valid_monitors = []
            for komorebi_monitor in komorebi_monitors:
                if komorebi_monitor.device != "UNKNOWN":
                    valid_monitors.append(komorebi_monitor)
                else:
                    logger.info(f"Skipping UNKNOWN monitor {komorebi_monitor.id}")

            # Calculate the narrowest monitor width for fallback (only from valid monitors)
            min_width = 10000
            for komorebi_monitor in valid_monitors:
                size = komorebi_monitor.size
                left = size["left"]
                right = size["right"]

                # Only consider monitors with valid width for min_width calculation
                if right != left:
                    width = right - left
                    min_width = min(min_width, width)

            # If no valid monitors found, keep default min_width
            if not valid_monitors:
                min_width = 1920
                logger.warning("No valid monitors found, using default width")

            # Create monitor info objects for valid monitors only
            for i, komorebi_monitor in enumerate(valid_monitors):
                size = komorebi_monitor.size
                left = size["left"]
                top = size["top"]
                right = size["right"]
                bottom = size["bottom"]

                # Fix for zero width/height using narrowest monitor width
                if right == left:
                    right = left + min_width
                    logger.info(
                        f"Using fallback width {min_width} for monitor {komorebi_monitor.id}"
                    )
                if bottom == top:
                    bottom = top + 1080  # fallback height

                rect = (left, top, right, bottom)
                width = right - left
                height = bottom - top

                # Assume work area is same as monitor area for now
                work_rect = rect

                monitor_info = MonitorInfo(
                    id=komorebi_monitor.id,
                    name=komorebi_monitor.name or f"Monitor {komorebi_monitor.id}",
                    is_primary=(i == 0),  # Assume first monitor is primary
                    rect=rect,
                    work_rect=work_rect,
                    width=width,
                    height=height,
                    dpi=96,  # Default DPI
                )

                self._monitors[komorebi_monitor.id] = monitor_info
                logger.info(
                    f"Detected monitor {komorebi_monitor.id}: {monitor_info.name} "
                    f"({monitor_info.width}x{monitor_info.height}) at {rect}"
                )

        except Exception as e:
            logger.error(f"Failed to refresh monitors: {e}")

    def get_monitors(self) -> List[MonitorInfo]:
        """
        Get list of all available monitors.

        Returns:
            List of MonitorInfo objects
        """
        return list(self._monitors.values())

    def get_monitor_count(self) -> int:
        """
        Get the number of available monitors.

        Returns:
            Number of monitors
        """
        return len(self._monitors)

    def get_monitor_by_id(self, monitor_id: int) -> Optional[MonitorInfo]:
        """
        Get monitor information by ID.

        Args:
            monitor_id: Komorebi monitor ID

        Returns:
            MonitorInfo object or None if not found
        """
        return self._monitors.get(monitor_id)

    def get_primary_monitor(self) -> Optional[MonitorInfo]:
        """
        Get the primary monitor information.

        Returns:
            MonitorInfo object for primary monitor or None if not found
        """
        for monitor in self._monitors.values():
            if monitor.is_primary:
                return monitor
        return None

    def get_monitor_at_position(self, x: int, y: int) -> Optional[MonitorInfo]:
        """
        Get the monitor that contains the specified position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            MonitorInfo object or None if position is not on any monitor
        """
        for monitor in self._monitors.values():
            left, top, right, bottom = monitor.rect
            if left <= x <= right and top <= y <= bottom:
                return monitor
        return None

    def get_top_center_position(self, monitor_id: int) -> Optional[Tuple[int, int]]:
        """
        Get the top-center position for a monitor.

        Args:
            monitor_id: Komorebi monitor ID

        Returns:
            (x, y) coordinates for top-center position or None if monitor not found
        """
        monitor = self.get_monitor_by_id(monitor_id)
        if monitor is None:
            return None

        left, top, right, bottom = monitor.rect
        center_x = (left + right) // 2
        return (center_x, top)

    def refresh(self):
        """Refresh monitor information (useful for hot-plugging)."""
        logger.info("Refreshing monitor information...")
        self._refresh_monitors()

    def get_monitor_summary(self) -> str:
        """
        Get a summary of all monitors for logging/debugging.

        Returns:
            Formatted string with monitor information
        """
        if not self._monitors:
            return "No monitors detected"

        summary = f"Monitor Configuration ({len(self._monitors)} monitors):"
        for monitor in self._monitors.values():
            primary_marker = " [PRIMARY]" if monitor.is_primary else ""
            summary += f"\n  Monitor {monitor.id}: {monitor.name} "
            summary += f"({monitor.width}x{monitor.height}) at "
            summary += f"({monitor.rect[0]},{monitor.rect[1]}) DPI: {monitor.dpi}{primary_marker}"

        return summary
