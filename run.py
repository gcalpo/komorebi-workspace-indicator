#!/usr/bin/env python3
"""
Launcher script for Komorebi Floating Workspace Indicator

Run this script to start the floating workspace indicator application.
"""

import sys
import os
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import main only when needed to avoid initializing GUI components for command-line operations
# Other imports are lightweight and can be imported immediately

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Komorebi Floating Workspace Indicator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Template Examples:
  --template "{workspace}"                    # Just workspace number
  --template "M{monitor} W{workspace}"        # Monitor and workspace
  --template "M{monitor}:W{workspace} {name}" # All info with separator
  --template "Monitor {monitor}\\nW{workspace}\\n{name}" # Multi-line

Available placeholders:
  {monitor}   - Monitor index (1-based)
  {workspace} - Workspace number (1-based)
  {name}      - Workspace name (if available)

Logging Examples:
  --log-level info                           # Enable info level logging
  --log-level debug                          # Enable debug level logging
  --verbose                                  # Shortcut for info level
  --debug                                    # Shortcut for debug level

Autostart Examples:
  --enable-autostart                         # Enable application autostart
  --disable-autostart                        # Disable application autostart

Process Management Examples:
  --stop                                     # Stop all running instances
  --stop --force                             # Force stop all running instances
  --list-processes                           # List all running instances
        """
    )
    
    parser.add_argument(
        '--template', '-t',
        type=str,
        default="{workspace}",
        help="Template string for workspace indicator display. "
             "Use {monitor}, {workspace}, and {name} as placeholders."
    )
    
    parser.add_argument(
        '--show-monitor',
        action='store_true',
        help="Show monitor index (overrides template if not specified)"
    )
    
    parser.add_argument(
        '--show-name',
        action='store_true',
        help="Show workspace name (overrides template if not specified)"
    )
    
    # Logging level arguments
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        '--log-level',
        type=str,
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help="Set logging level (default: no logging)"
    )
    log_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose (info level) logging"
    )
    log_group.add_argument(
        '--debug',
        action='store_true', 
        help="Enable debug level logging"
    )
    
    # Autostart arguments
    autostart_group = parser.add_mutually_exclusive_group()
    autostart_group.add_argument(
        '--enable-autostart',
        action='store_true',
        help="Generate the komorebi-workspace-indicator.lnk shortcut in shell:startup to autostart the application"
    )
    autostart_group.add_argument(
        '--disable-autostart',
        action='store_true',
        help="Delete the komorebi-workspace-indicator.lnk shortcut in shell:startup to disable autostart"
    )
    
    # Process management arguments
    parser.add_argument(
        '--stop',
        action='store_true',
        help="Stop all running instances of the application"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Force kill processes if they don't terminate gracefully (use with --stop)"
    )
    parser.add_argument(
        '--list-processes',
        action='store_true',
        help="List all running instances of the application"
    )
    
    # Internal argument for detached mode (hidden from help)
    parser.add_argument(
        '--detached',
        action='store_true',
        help=argparse.SUPPRESS  # Hide from help output
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Set detached flag if running in detached mode
    if args.detached:
        sys._komorebi_detached = True
    
    # Handle process management commands
    if args.list_processes:
        from src.process_manager import list_app_processes
        print("Listing running application processes...")
        try:
            processes = list_app_processes()
            if not processes:
                print("No running application processes found.")
            else:
                print(f"Found {len(processes)} running process(es):")
                for proc in processes:
                    current_marker = " (current)" if proc['is_current'] else ""
                    print(f"  PID {proc['pid']}: {proc['name']}{current_marker}")
                    print(f"    Command: {proc['cmdline']}")
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)  # Force immediate exit without cleanup
    
    if args.stop:
        from src.process_manager import stop_all_app_processes, get_process_count
        print("Stopping all running application instances...")
        try:
            process_count = get_process_count(exclude_current=True)
            
            if process_count == 0:
                print("No running application processes found to stop.")
                sys.stdout.flush()
                sys.stderr.flush()
                os._exit(0)
                
            print(f"Found {process_count} running process(es) to stop...")
            results = stop_all_app_processes(force=args.force, timeout=10)
            
            if results['stopped'] > 0:
                print(f"[SUCCESS] Stopped {results['stopped']} process(es)")
                for detail in results['details']:
                    if detail['status'] in ['terminated_gracefully', 'force_killed']:
                        print(f"  PID {detail['pid']}: {detail['name']} - {detail['status']}")
            
            if results['failed'] > 0:
                print(f"[WARNING] Failed to stop {results['failed']} process(es)")
                for detail in results['details']:
                    if detail['status'] not in ['terminated_gracefully', 'force_killed']:
                        print(f"  PID {detail['pid']}: {detail['name']} - {detail['status']}")
            
            exit_code = 0 if (results['stopped'] > 0 and results['failed'] == 0) else 1
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(exit_code if 'exit_code' in locals() else 1)
    
    # Handle autostart commands
    if args.enable_autostart:
        from src.autostart import enable_autostart, get_autostart_status
        print("Enabling autostart...")
        try:
            success = enable_autostart()
            if success:
                print("[SUCCESS] Autostart enabled successfully")
                print(f"Status: {get_autostart_status()}")
                exit_code = 0
            else:
                print("[ERROR] Failed to enable autostart")
                exit_code = 1
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(exit_code if 'exit_code' in locals() else 1)
    
    if args.disable_autostart:
        from src.autostart import disable_autostart, get_autostart_status
        print("Disabling autostart...")
        try:
            success = disable_autostart()
            if success:
                print("[SUCCESS] Autostart disabled successfully")
                print(f"Status: {get_autostart_status()}")
                exit_code = 0
            else:
                print("[ERROR] Failed to disable autostart")
                exit_code = 1
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(exit_code if 'exit_code' in locals() else 1)
    
    # Default behavior: start as background service and return to command prompt
    import subprocess
    import time
    
    # Determine logging level
    log_level = None  # Default to no logging
    if args.debug:
        log_level = 'debug'
    elif args.verbose:
        log_level = 'info'
    elif args.log_level:
        log_level = args.log_level
    
    # Check if we're already running as a detached process
    is_detached = getattr(sys, '_komorebi_detached', False)
    
    if not is_detached and getattr(sys, 'frozen', False):
        # Running as executable - start detached background process
        try:
            # Build command line arguments for the detached process
            cmd_args = [sys.executable, '--detached']
            
            # Add original arguments
            if args.template != "{workspace}":
                cmd_args.extend(['--template', args.template])
            if args.show_monitor:
                cmd_args.append('--show-monitor')
            if args.show_name:
                cmd_args.append('--show-name')
            if log_level:
                if args.debug:
                    cmd_args.append('--debug')
                elif args.verbose:
                    cmd_args.append('--verbose')
                else:
                    cmd_args.extend(['--log-level', log_level])
            
            # Start detached process using Windows CreateProcess
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Use CREATE_NEW_PROCESS_GROUP to detach from current console
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            process = subprocess.Popen(
                cmd_args,
                creationflags=creation_flags,
                startupinfo=startupinfo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            
            # Give the process a moment to start
            time.sleep(0.5)
            
            print(f"Komorebi Workspace Indicator started as background service (PID: {process.pid})")
            print("Use 'komorebi-indicator.exe --stop' to stop all running instances")
            
        except Exception as e:
            print(f"[ERROR] Failed to start background service: {e}")
            sys.exit(1)
        
        # Exit immediately to return user to command prompt
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
        
    elif not is_detached:
        # Running as Python script - use subprocess to detach
        try:
            import platform
            if platform.system() == "Windows":
                # Use PowerShell Start-Process for detachment
                script_path = os.path.abspath(__file__)
                ps_cmd = f'Start-Process -FilePath "python" -ArgumentList \'"{script_path}", "--detached"\' -WindowStyle Hidden'
                subprocess.run(['powershell', '-Command', ps_cmd], check=True)
                print("Komorebi Workspace Indicator started as background service")
                print("Use 'python run.py --stop' to stop all running instances")
            else:
                # Unix-like systems
                subprocess.Popen([sys.executable, __file__, '--detached'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL,
                               stdin=subprocess.DEVNULL,
                               start_new_session=True)
                print("Komorebi Workspace Indicator started as background service")
                print("Use 'python run.py --stop' to stop all running instances")
                
        except Exception as e:
            print(f"[ERROR] Failed to start background service: {e}")
            # Fallback to direct execution
            from src.main import main
            sys.exit(main(
                template=args.template, 
                show_monitor=args.show_monitor, 
                show_name=args.show_name,
                log_level=log_level
            ))
        
        # Exit immediately to return user to command prompt
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
    
    else:
        # We are the detached process - run the actual GUI application
        from src.main import main
        sys.exit(main(
            template=args.template, 
            show_monitor=args.show_monitor, 
            show_name=args.show_name,
            log_level=log_level
        )) 