#!/usr/bin/env python3

import argparse
import json
from collections import deque

import jsonschema
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('schema', help='Path to the YAML schema file')
parser.add_argument('file', help='Path to the YAML file to validate')

args = parser.parse_args()
schema_file = args.schema
yaml_file = args.file

# Load the YAML file to validate
with open(yaml_file, 'r') as file:
    data = yaml.safe_load(file)

# Load the schema
with open(schema_file, 'r') as file:
    schema = json.load(file)


def make_properties_required(partial_schema: dict):
    if 'properties' not in partial_schema.keys():
        return partial_schema

    properties = {}
    required = []

    for prop, details in partial_schema['properties'].items():
        details = make_properties_required(partial_schema=details)
        properties[prop] = details

        required.append(prop)

    partial_schema['properties'] = properties
    partial_schema['required'] = required

    return partial_schema


# Make every property in the schema required
schema = make_properties_required(partial_schema=schema)

known_paths_with_validation_issues_to_ignore = [
    ["Discord", "BotToken"],
    ["Tautulli", "APIKey"],
]

validator = jsonschema.Draft7Validator(schema)
errors_occurred = False

for error in validator.iter_errors(data):
    path = deque(error.absolute_path)

    if list(path) in known_paths_with_validation_issues_to_ignore:
        print(f"Ignoring error in {path}: {error.message}")
        continue

    errors_occurred = True
    print(f"Error in {path}: {error.message}")

if errors_occurred:
    exit(1)
else:
    print("No errors found")
    exit(0)
