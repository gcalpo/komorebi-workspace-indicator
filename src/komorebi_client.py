"""
Komorebi Client Module

Handles communication with the komorebic command line tool to query
workspace and monitor state information.
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Windows-specific subprocess flags
if sys.platform == "win32":
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0


@dataclass
class KomorebiMonitorInfo:
    """Information about a monitor from Komorebi."""

    id: int
    name: str
    device: str
    device_id: str
    size: Dict[str, int]  # left, top, right, bottom


@dataclass
class WorkspaceState:
    """Represents the current workspace state for a monitor."""

    monitor_index: int
    workspace_index: int
    workspace_name: Optional[str] = None
    workspace_layout: Optional[str] = None


class KomorebiClient:
    """Client for interacting with the komorebic command line tool."""

    def __init__(self, komorebic_path: str = "komorebic.exe"):
        """
        Initialize the Komorebi client.

        Args:
            komorebic_path: Path to the komorebic executable
        """
        self.komorebic_path = komorebic_path
        self._cached_state: Optional[WorkspaceState] = None

    def is_komorebi_running(self) -> bool:
        """
        Check if Komorebi is running and accessible.

        Returns:
            True if komorebic is accessible, False otherwise
        """
        try:
            result = self._execute_query("version")
            return result is not None and result.strip() != ""
        except Exception as e:
            logger.warning(f"Failed to check if Komorebi is running: {e}")
            return False

    def get_focused_monitor_index(self) -> Optional[int]:
        """
        Get the index of the currently focused monitor.

        Returns:
            Monitor index (0-based) or None if query fails
        """
        try:
            result = self._execute_query("focused-monitor-index")
            if result:
                return int(result.strip())
        except (ValueError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to get focused monitor index: {e}")
        return None

    def get_focused_workspace_index(self) -> Optional[int]:
        """
        Get the index of the currently focused workspace.

        Returns:
            Workspace index (0-based) or None if query fails
        """
        try:
            result = self._execute_query("focused-workspace-index")
            if result:
                return int(result.strip())
        except (ValueError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to get focused workspace index: {e}")
        return None

    def get_focused_workspace_name(self) -> Optional[str]:
        """
        Get the name of the currently focused workspace.

        Returns:
            Workspace name or None if not set or query fails
        """
        try:
            result = self._execute_query("focused-workspace-name")
            if result and result.strip():
                return result.strip()
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to get focused workspace name: {e}")
        return None

    def get_focused_workspace_layout(self) -> Optional[str]:
        """
        Get the layout of the currently focused workspace.

        Returns:
            Workspace layout or None if query fails
        """
        try:
            result = self._execute_query("focused-workspace-layout")
            if result and result.strip():
                return result.strip()
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to get focused workspace layout: {e}")
        return None

    def get_current_workspace_state(self) -> Optional[WorkspaceState]:
        """
        Get the complete current workspace state.

        Returns:
            WorkspaceState object or None if any query fails
        """
        try:
            monitor_index = self.get_focused_monitor_index()
            workspace_index = self.get_focused_workspace_index()

            if monitor_index is None or workspace_index is None:
                return None

            # Get the original unfiltered monitor list to map index to ID correctly
            result = self._execute_monitor_info_command()
            if not result:
                return None

            monitors_data = json.loads(result)
            if monitor_index >= len(monitors_data):
                logger.error(f"Monitor index {monitor_index} out of range")
                return None

            monitor_id = monitors_data[monitor_index]["id"]

            workspace_name = self.get_focused_workspace_name()
            workspace_layout = self.get_focused_workspace_layout()

            state = WorkspaceState(
                monitor_index=monitor_id,  # Store actual monitor ID, not 0-based index
                workspace_index=workspace_index,
                workspace_name=workspace_name,
                workspace_layout=workspace_layout,
            )

            # Cache the state for comparison
            self._cached_state = state
            return state

        except Exception as e:
            logger.error(f"Failed to get current workspace state: {e}")
            return None

    def has_workspace_changed(self) -> bool:
        """
        Check if the workspace state has changed since last query.

        Returns:
            True if workspace state has changed, False otherwise
        """
        current_state = self.get_current_workspace_state()
        if current_state is None:
            return False

        if self._cached_state is None:
            return True

        return (
            current_state.monitor_index != self._cached_state.monitor_index
            or current_state.workspace_index != self._cached_state.workspace_index
        )

    def _execute_query(self, query_type: str) -> Optional[str]:
        """
        Execute a komorebic query command.

        Args:
            query_type: The type of query to execute

        Returns:
            Query result as string or None if failed
        """
        try:
            result = subprocess.run(
                [self.komorebic_path, "query", query_type],
                capture_output=True,
                text=True,
                timeout=5.0,  # 5 second timeout
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"komorebic query failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"komorebic query timed out for: {query_type}")
            return None
        except FileNotFoundError:
            logger.error(f"komorebic executable not found at: {self.komorebic_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing komorebic query: {e}")
            return None

    def get_monitor_information(self) -> List[KomorebiMonitorInfo]:
        """
        Get monitor information from Komorebi.

        Returns:
            List of KomorebiMonitorInfo objects, excluding UNKNOWN entries
        """
        try:
            result = self._execute_monitor_info_command()
            if not result:
                return []

            # Parse JSON response
            monitors_data = json.loads(result)
            monitors = []

            for i, monitor_data in enumerate(monitors_data):
                # Skip UNKNOWN monitors
                if monitor_data.get("device") == "UNKNOWN":
                    logger.info(f"Skipping UNKNOWN monitor {i}")
                    continue

                monitor_info = KomorebiMonitorInfo(
                    id=monitor_data["id"],
                    name=monitor_data["name"],
                    device=monitor_data["device"],
                    device_id=monitor_data["device_id"],
                    size=monitor_data["size"],
                )
                monitors.append(monitor_info)
                logger.info(
                    f"Found Komorebi monitor {i}: {monitor_info.name} "
                    f"({monitor_info.size['right'] - monitor_info.size['left']}x"
                    f"{monitor_info.size['bottom'] - monitor_info.size['top']})"
                )

            return monitors

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse monitor information JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get monitor information: {e}")
            return []

    def _execute_monitor_info_command(self) -> Optional[str]:
        """
        Execute the komorebic monitor-information command.

        Returns:
            Command result as string or None if failed
        """
        try:
            result = subprocess.run(
                [self.komorebic_path, "monitor-information"],
                capture_output=True,
                text=True,
                timeout=5.0,  # 5 second timeout
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"komorebic monitor-information failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("komorebic monitor-information timed out")
            return None
        except FileNotFoundError:
            logger.error(f"komorebic executable not found at: {self.komorebic_path}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error executing komorebic monitor-information: {e}"
            )
            return None

    def get_workspace_index_for_monitor(self, monitor_index: int) -> Optional[int]:
        """
        Get the current workspace index for a specific monitor without focusing on it.

        Args:
            monitor_index: The monitor index to query

        Returns:
            Workspace index (0-based) or None if query fails
        """
        try:
            result = self._execute_query(f"workspace-index {monitor_index}")
            if result:
                return int(result.strip())
        except (ValueError, subprocess.SubprocessError) as e:
            logger.error(
                f"Failed to get workspace index for monitor {monitor_index}: {e}"
            )
        return None

    def get_workspace_name_for_monitor(self, monitor_index: int) -> Optional[str]:
        """
        Get the current workspace name for a specific monitor without focusing on it.

        Args:
            monitor_index: The monitor index to query

        Returns:
            Workspace name or None if not set or query fails
        """
        try:
            result = self._execute_query(f"workspace-name {monitor_index}")
            if result and result.strip():
                return result.strip()
        except subprocess.SubprocessError as e:
            logger.error(
                f"Failed to get workspace name for monitor {monitor_index}: {e}"
            )
        return None

    def get_all_monitors_workspace_state(self) -> List[WorkspaceState]:
        """
        Get workspace state for all monitors without focusing on any of them.

        Returns:
            List of WorkspaceState objects for all monitors
        """
        try:
            # Get the current state from komorebic
            result = subprocess.run(
                [self.komorebic_path, "state"],
                capture_output=True,
                text=True,
                timeout=5.0,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode != 0:
                logger.error(f"Failed to get komorebi state: {result.stderr}")
                return []

            # Parse JSON state
            state_data = json.loads(result.stdout)
            monitors_data = state_data.get("monitors", {}).get("elements", [])

            states = []

            for monitor_index, monitor_data in enumerate(monitors_data):
                # Skip UNKNOWN monitors
                if monitor_data.get("device") == "UNKNOWN":
                    logger.info(f"Skipping UNKNOWN monitor {monitor_index}")
                    continue

                monitor_id = monitor_data["id"]
                workspaces = monitor_data.get("workspaces", {})
                focused_workspace = workspaces.get("focused", 0)

                # Get workspace name if available
                workspace_names = monitor_data.get("workspace_names", {})
                workspace_name = workspace_names.get(str(focused_workspace))

                state = WorkspaceState(
                    monitor_index=monitor_id,  # Store actual monitor ID
                    workspace_index=focused_workspace,
                    workspace_name=workspace_name,
                )
                states.append(state)

                logger.info(
                    f"Found monitor {monitor_id} on workspace {focused_workspace}"
                )

            return states

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse komorebi state JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get all monitors workspace state: {e}")
            return []

    def get_monitor_index_from_id(self, monitor_id: int) -> Optional[int]:
        """
        Get the 0-based monitor index from a Komorebi monitor ID.

        Args:
            monitor_id: The Komorebi monitor ID

        Returns:
            0-based monitor index or None if not found
        """
        try:
            monitors = self.get_monitor_information()
            for i, monitor in enumerate(monitors):
                if monitor.id == monitor_id:
                    return i
            return None
        except Exception as e:
            logger.error(f"Failed to get monitor index from ID {monitor_id}: {e}")
            return None

    def get_workspaces_with_windows_for_monitor(
        self, monitor_identifier: int
    ) -> List[int]:
        """
        Get list of workspace indices that have windows on the specified monitor.

        Args:
            monitor_identifier: The monitor index (0-based) or Komorebi monitor ID

        Returns:
            List of workspace indices (0-based) that have windows
        """
        try:
            # Determine if this is a monitor ID or index
            # If it's a large number, it's likely a monitor ID
            if monitor_identifier > 1000:  # Monitor IDs are typically large numbers
                monitor_index = self.get_monitor_index_from_id(monitor_identifier)
                if monitor_index is None:
                    logger.warning(f"Monitor ID {monitor_identifier} not found")
                    return []
            else:
                monitor_index = monitor_identifier

            logger.debug(
                f"Looking for workspaces with windows on monitor {monitor_identifier} (index: {monitor_index})"
            )

            # Get the current state
            result = subprocess.run(
                [self.komorebic_path, "state"],
                capture_output=True,
                text=True,
                timeout=5.0,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode != 0:
                logger.error(f"Failed to get komorebi state: {result.stderr}")
                return []

            # Parse JSON state
            state_data = json.loads(result.stdout)

            # Find the monitor by index
            monitors = state_data.get("monitors", {}).get("elements", [])
            if monitor_index >= len(monitors):
                logger.warning(
                    f"Monitor index {monitor_index} not found in state (total monitors: {len(monitors)})"
                )
                return []

            monitor = monitors[monitor_index]
            workspaces = monitor.get("workspaces", {}).get("elements", [])

            logger.debug(
                f"Found {len(workspaces)} workspaces on monitor {monitor_identifier}"
            )

            workspaces_with_windows = []

            # Check each workspace for windows
            for workspace_index, workspace in enumerate(workspaces):
                containers = workspace.get("containers", {}).get("elements", [])
                floating_windows = workspace.get("floating_windows", {}).get(
                    "elements", []
                )
                maximized_window = workspace.get("maximized_window")

                # Check if workspace has any windows
                has_windows = (
                    len(containers) > 0
                    or len(floating_windows) > 0
                    or maximized_window is not None
                )

                logger.debug(
                    f"Workspace {workspace_index}: containers={len(containers)}, floating={len(floating_windows)}, maximized={maximized_window is not None}, has_windows={has_windows}"
                )

                if has_windows:
                    workspaces_with_windows.append(workspace_index)

            logger.debug(
                f"Found {len(workspaces_with_windows)} workspaces with windows on monitor {monitor_identifier}: {workspaces_with_windows}"
            )

            # If no workspaces with windows found, but we know there should be some,
            # return all workspaces as a fallback (this allows cycling through all workspaces)
            if not workspaces_with_windows and len(workspaces) > 0:
                logger.info(
                    f"No workspaces with windows detected on monitor {monitor_identifier}, falling back to all {len(workspaces)} workspaces"
                )
                return list(range(len(workspaces)))

            return workspaces_with_windows

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse komorebi state JSON: {e}")
            return []
        except Exception as e:
            logger.error(
                f"Failed to get workspaces with windows for monitor {monitor_identifier}: {e}"
            )
            return []

    def _workspace_has_windows(self, monitor_index: int, workspace_index: int) -> bool:
        """
        Check if a specific workspace has any windows.

        Args:
            monitor_index: The monitor index
            workspace_index: The workspace index

        Returns:
            True if the workspace has windows, False otherwise
        """
        try:
            # Get the current state
            result = subprocess.run(
                [self.komorebic_path, "state"],
                capture_output=True,
                text=True,
                timeout=5.0,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode != 0:
                logger.error(f"Failed to get komorebi state: {result.stderr}")
                return False

            # Parse JSON state
            state_data = json.loads(result.stdout)

            # Find the monitor by index
            monitors = state_data.get("monitors", {}).get("elements", [])
            if monitor_index >= len(monitors):
                return False

            monitor = monitors[monitor_index]
            workspaces = monitor.get("workspaces", {}).get("elements", [])

            if workspace_index >= len(workspaces):
                return False

            workspace = workspaces[workspace_index]
            containers = workspace.get("containers", {}).get("elements", [])
            floating_windows = workspace.get("floating_windows", {}).get("elements", [])
            maximized_window = workspace.get("maximized_window")

            # Check if workspace has any windows
            return (
                len(containers) > 0
                or len(floating_windows) > 0
                or maximized_window is not None
            )

        except Exception as e:
            logger.error(
                f"Failed to check if workspace {workspace_index} on monitor {monitor_index} has windows: {e}"
            )
            return False

    def switch_to_workspace_on_monitor(
        self, monitor_identifier: int, workspace_index: int
    ) -> bool:
        """
        Switch to a specific workspace on a specific monitor.

        Args:
            monitor_identifier: The monitor index (0-based) or Komorebi monitor ID
            workspace_index: The workspace index to switch to (0-based)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine if this is a monitor ID or index
            # If it's a large number, it's likely a monitor ID
            if monitor_identifier > 1000:  # Monitor IDs are typically large numbers
                monitor_index = self.get_monitor_index_from_id(monitor_identifier)
                if monitor_index is None:
                    logger.error(f"Monitor ID {monitor_identifier} not found")
                    return False
            else:
                monitor_index = monitor_identifier

            # Use the single focus-monitor-workspace command for efficiency
            result = subprocess.run(
                [
                    self.komorebic_path,
                    "focus-monitor-workspace",
                    str(monitor_index),
                    str(workspace_index),
                ],
                capture_output=True,
                text=True,
                timeout=5.0,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode != 0:
                logger.error(
                    f"Failed to focus monitor {monitor_index} workspace {workspace_index}: {result.stderr}"
                )
                return False

            logger.info(
                f"Successfully switched to workspace {workspace_index} on monitor {monitor_identifier}"
            )
            return True

        except subprocess.TimeoutExpired:
            logger.error(
                f"Timeout switching to workspace {workspace_index} on monitor {monitor_identifier}"
            )
            return False
        except FileNotFoundError:
            logger.error(f"komorebic executable not found at: {self.komorebic_path}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error switching to workspace {workspace_index} on monitor {monitor_identifier}: {e}"
            )
            return False
