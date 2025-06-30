"""
Process management functionality for Komorebi Workspace Indicator

Handles finding and stopping running instances of the application.
"""

import os
import sys
import logging
import psutil
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages processes for the Komorebi Workspace Indicator application."""
    
    def __init__(self):
        """Initialize the process manager."""
        self.app_name = "komorebi-workspace-indicator"
        self.script_names = ["run.py", "komorebi-indicator.exe", "main.py"]
        
    def get_current_process_info(self) -> dict:
        """
        Get information about the current process.
        
        Returns:
            Dictionary with process information
        """
        current_process = psutil.Process(os.getpid())
        return {
            'pid': current_process.pid,
            'name': current_process.name(),
            'exe': current_process.exe() if hasattr(current_process, 'exe') else None,
            'cmdline': current_process.cmdline() if hasattr(current_process, 'cmdline') else []
        }
    
    def find_app_processes(self, exclude_current: bool = True) -> List[psutil.Process]:
        """
        Find all running processes related to this application.
        
        Args:
            exclude_current: Whether to exclude the current process from results
        
        Returns:
            List of psutil.Process objects
        """
        found_processes = []
        current_pid = os.getpid()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    # Skip current process if requested
                    if exclude_current and proc.info['pid'] == current_pid:
                        continue
                    
                    # Check if it's one of our executables
                    if self._is_app_process(proc.info):
                        found_processes.append(proc)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process might have disappeared or we don't have access
                    continue
                    
        except Exception as e:
            logger.error(f"Error scanning processes: {e}")
            
        return found_processes
    
    def _is_app_process(self, proc_info: dict) -> bool:
        """
        Check if a process is related to this application.
        
        Args:
            proc_info: Process information dictionary
        
        Returns:
            True if this is an app process, False otherwise
        """
        name = proc_info.get('name', '').lower()
        exe = proc_info.get('exe', '')
        cmdline = proc_info.get('cmdline', [])
        
        # Check executable name
        if any(script_name.lower() in name for script_name in [s.lower() for s in self.script_names]):
            return True
            
        # Check executable path
        if exe and any(script_name.lower() in exe.lower() for script_name in self.script_names):
            return True
            
        # Check command line arguments
        if cmdline:
            cmdline_str = ' '.join(cmdline).lower()
            if any(script_name.lower() in cmdline_str for script_name in self.script_names):
                return True
                
            # Check for Python processes running our scripts
            if 'python' in cmdline_str:
                for script_name in self.script_names:
                    if script_name.lower() in cmdline_str:
                        return True
        
        return False
    
    def stop_all_processes(self, force: bool = False, timeout: int = 10) -> dict:
        """
        Stop all running instances of the application.
        
        Args:
            force: Whether to force kill processes that don't terminate gracefully
            timeout: Timeout in seconds for graceful termination
        
        Returns:
            Dictionary with results: {'stopped': count, 'failed': count, 'details': []}
        """
        processes = self.find_app_processes(exclude_current=True)
        
        if not processes:
            logger.info("No running application processes found")
            return {'stopped': 0, 'failed': 0, 'details': []}
        
        results = {
            'stopped': 0,
            'failed': 0,
            'details': []
        }
        
        logger.info(f"Found {len(processes)} application processes to stop")
        
        for proc in processes:
            try:
                proc_info = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'exe': proc.exe() if hasattr(proc, 'exe') else 'N/A',
                    'cmdline': ' '.join(proc.cmdline()) if hasattr(proc, 'cmdline') else 'N/A'
                }
                
                logger.info(f"Stopping process {proc.pid}: {proc_info['name']}")
                
                # Try graceful termination first
                proc.terminate()
                
                try:
                    # Wait for process to terminate gracefully
                    proc.wait(timeout=timeout)
                    results['stopped'] += 1
                    results['details'].append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'status': 'terminated_gracefully'
                    })
                    logger.info(f"Process {proc.pid} terminated gracefully")
                    
                except psutil.TimeoutExpired:
                    if force:
                        # Force kill if graceful termination failed
                        logger.warning(f"Process {proc.pid} didn't terminate gracefully, force killing")
                        proc.kill()
                        proc.wait(timeout=5)
                        results['stopped'] += 1
                        results['details'].append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'status': 'force_killed'
                        })
                        logger.info(f"Process {proc.pid} force killed")
                    else:
                        results['failed'] += 1
                        results['details'].append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'status': 'failed_to_terminate'
                        })
                        logger.error(f"Process {proc.pid} failed to terminate gracefully")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                results['failed'] += 1
                results['details'].append({
                    'pid': proc.pid,
                    'name': getattr(proc, 'name', lambda: 'Unknown')(),
                    'status': f'error: {str(e)}'
                })
                logger.error(f"Error stopping process {proc.pid}: {e}")
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'pid': proc.pid,
                    'name': getattr(proc, 'name', lambda: 'Unknown')(),
                    'status': f'unexpected_error: {str(e)}'
                })
                logger.error(f"Unexpected error stopping process {proc.pid}: {e}")
        
        return results
    
    def list_app_processes(self) -> List[dict]:
        """
        List all running application processes with details.
        
        Returns:
            List of dictionaries with process information
        """
        processes = self.find_app_processes(exclude_current=False)
        current_pid = os.getpid()
        
        process_list = []
        for proc in processes:
            try:
                proc_info = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'exe': proc.exe() if hasattr(proc, 'exe') else 'N/A',
                    'cmdline': ' '.join(proc.cmdline()) if hasattr(proc, 'cmdline') else 'N/A',
                    'is_current': proc.pid == current_pid
                }
                process_list.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return process_list


def stop_all_app_processes(force: bool = False, timeout: int = 10) -> dict:
    """
    Stop all running instances of the application.
    
    Args:
        force: Whether to force kill processes that don't terminate gracefully
        timeout: Timeout in seconds for graceful termination
    
    Returns:
        Dictionary with results
    """
    manager = ProcessManager()
    return manager.stop_all_processes(force=force, timeout=timeout)


def list_app_processes() -> List[dict]:
    """
    List all running application processes.
    
    Returns:
        List of process information dictionaries
    """
    manager = ProcessManager()
    return manager.list_app_processes()


def get_process_count(exclude_current: bool = True) -> int:
    """
    Get the count of running application processes.
    
    Args:
        exclude_current: Whether to exclude the current process
    
    Returns:
        Number of running processes
    """
    manager = ProcessManager()
    processes = manager.find_app_processes(exclude_current=exclude_current)
    return len(processes) 