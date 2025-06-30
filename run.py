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

from src.main import main

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
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Determine logging level
    log_level = None  # Default to no logging
    if args.debug:
        log_level = 'debug'
    elif args.verbose:
        log_level = 'info'
    elif args.log_level:
        log_level = args.log_level
    
    sys.exit(main(
        template=args.template, 
        show_monitor=args.show_monitor, 
        show_name=args.show_name,
        log_level=log_level
    )) 