import ast

def extract_routes_from_code(file_path):
    print(f"Extracting routes from {file_path}")
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    routes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                # Check if the decorator has an attribute named "func"
                if hasattr(decorator, "func") and isinstance(decorator.func, ast.Attribute):
                    # Extract route details
                    if decorator.func.attr in ['route']:
                        route_path = decorator.args[0].value if len(decorator.args) > 0 else None
                        routes.append({
                            "function": node.name,
                            "route": route_path,
                            "docstring": ast.get_docstring(node)
                        })
    return routes

# Example Usage
from glob import glob
api_files = glob('src/zinny_api/v1/api/v1/*.py')
print(api_files)

for api_file in api_files:
    routes = extract_routes_from_code(api_file)
    for route in routes:
        print(f"Function: {route['function']}")
        print(f"Route: {route['route']}")
        print(f"Docstring: {route['docstring']}")
        print("=" * 40)
