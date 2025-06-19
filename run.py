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
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(template=args.template, show_monitor=args.show_monitor, show_name=args.show_name)) 