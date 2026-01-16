"""
Script to identify all endpoints missing @extend_schema decorators
"""
import re

# Read the file
with open('properties/api_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all @api_view decorators
api_view_pattern = r'@api_view\(\[.*?\]\)'
api_views = list(re.finditer(api_view_pattern, content))

# Find all class definitions with APIView
class_pattern = r'class (\w+APIView)\(APIView\):'
classes = list(re.finditer(class_pattern, content))

print("Function-based views (@api_view):")
for match in api_views:
    start = match.start()
    # Find the function definition after this decorator
    func_match = re.search(r'def (\w+)\(', content[start:start+200])
    if func_match:
        func_name = func_match.group(1)
        # Check if @extend_schema exists before this
        before = content[max(0, start-500):start]
        has_extend = '@extend_schema' in before
        status = "✓" if has_extend else "✗ MISSING"
        print(f"  {status} {func_name}")

print("\nClass-based views (APIView):")
for match in classes:
    class_name = match.group(1)
    start = match.start()
    # Find methods in this class
    class_end = content.find('\nclass ', start + 1)
    if class_end == -1:
        class_end = len(content)
    class_content = content[start:class_end]
    
    # Check for @extend_schema in methods
    methods = re.findall(r'def (get|post|put|patch|delete)\(', class_content)
    for method in methods:
        method_start = class_content.find(f'def {method}(')
        before_method = class_content[max(0, method_start-300):method_start]
        has_extend = '@extend_schema' in before_method
        status = "✓" if has_extend else "✗ MISSING"
        print(f"  {status} {class_name}.{method}()")
