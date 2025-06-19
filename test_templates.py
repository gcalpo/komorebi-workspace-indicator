#!/usr/bin/env python3
"""
Test script for template functionality

This script demonstrates how the template system works without requiring
Komorebi to be running.
"""

def format_display_text(template: str, monitor_index: int, workspace_index: int, workspace_name: str = None) -> str:
    """
    Format display text according to template.
    
    Args:
        template: Template string with placeholders
        monitor_index: Monitor index (1-based)
        workspace_index: Workspace index (1-based for display)
        workspace_name: Workspace name (optional)
    
    Returns:
        Formatted display text
    """
    return template.format(
        monitor=monitor_index,
        workspace=workspace_index,
        name=workspace_name if workspace_name else ""
    ).strip().rstrip(':')  # Remove trailing colon if no name

def test_templates():
    """Test various template formats."""
    
    # Test data
    test_cases = [
        (1, 2, "Work"),
        (2, 1, "Personal"),
        (1, 3, None),
        (2, 4, "Gaming")
    ]
    
    templates = [
        "{workspace}",
        "M{monitor} W{workspace}",
        "M{monitor}:W{workspace} {name}",
        "Monitor {monitor}\\nW{workspace}\\n{name}",
        "[{monitor}] {workspace} {name}",
        "M{monitor} | W{workspace} | {name}"
    ]
    
    print("Template Testing Results:")
    print("=" * 50)
    
    for template in templates:
        print(f"\nTemplate: '{template}'")
        print("-" * 30)
        
        for monitor, workspace, name in test_cases:
            result = format_display_text(template, monitor, workspace, name)
            print(f"  Monitor {monitor}, Workspace {workspace}, Name '{name}' -> '{result}'")

if __name__ == "__main__":
    test_templates() 