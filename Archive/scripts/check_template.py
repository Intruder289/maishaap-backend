#!/usr/bin/env python3
"""
Simple template syntax checker for Django templates
"""
import re
import sys
import os

def check_template_syntax(file_path):
    """Check basic Django template syntax"""
    errors = []
    warnings = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Track template tags
    tag_stack = []
    
    for line_num, line in enumerate(lines, 1):
        # Find all Django template tags
        template_tags = re.findall(r'{% *(\w+).*?%}', line)
        
        for tag in template_tags:
            if tag in ['if', 'for', 'with', 'block', 'comment']:
                tag_stack.append((tag, line_num))
            elif tag in ['endif', 'endfor', 'endwith', 'endblock', 'endcomment']:
                expected_start = tag.replace('end', '')
                if tag_stack:
                    start_tag, start_line = tag_stack.pop()
                    if start_tag != expected_start:
                        errors.append(f"Line {line_num}: Mismatched tags - expected 'end{start_tag}' but found '{tag}'")
                else:
                    errors.append(f"Line {line_num}: Unexpected closing tag '{tag}' with no matching opening tag")
        
        # Check for potential filter issues
        if '|sub:' in line:
            warnings.append(f"Line {line_num}: 'sub' filter doesn't exist, use 'add' with negative values")
        
        if '|add_days:' in line:
            warnings.append(f"Line {line_num}: 'add_days' filter doesn't exist, consider using timedelta in view")
    
    # Check for unclosed tags
    if tag_stack:
        for tag, line_num in tag_stack:
            errors.append(f"Line {line_num}: Unclosed '{tag}' tag")
    
    return errors, warnings

def main():
    template_path = sys.argv[1] if len(sys.argv) > 1 else 'rent/templates/rent/dashboard.html'
    
    if not os.path.exists(template_path):
        print(f"Template file not found: {template_path}")
        return 1
    
    errors, warnings = check_template_syntax(template_path)
    
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("Template syntax looks good!")
    
    return len(errors)

if __name__ == '__main__':
    sys.exit(main())