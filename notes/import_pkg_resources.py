import pkg_resources
import json

from  importlib import resources, metadata

list(metadata.metadata('zinny_surveys'))
['Metadata-Version', 'Name', 'Version', 'Summary', 'Author-email', 'License', 'Project-URL', 'Project-URL', 'Keywords', 'Requires-Python', 'Description-Content-Type', 'License-File', 'Provides-Extra', 'Requires-Dist', 'Requires-Dist', 'Description']

resources.files('zinny_surveys')
# MultiplexedPath(
#     '/opt/conda/miniconda3/envs/zinny-dev/lib/python3.11/site-packages/zinny_surveys',
#     '/Volumes/Stor21/Projects/2022/Zinni/repos/zinny-surveys/src/zinny_surveys')


def load_json_file(package, resource_path):
    resource = pkg_resources.resource_string(package, resource_path)
    return json.loads(resource)

# Example usage
data = load_json_file('zinny_surveys', 'surveys/shared/example.json')
print(data)