#!/usr/bin/env python3
"""
Bump version script — single source of truth for version.
Updates VERSION and pyproject.toml from a single argument.
"""
import sys
import re
import os

def bump(new_version):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    version_file = os.path.join(root, "VERSION")
    with open(version_file, "w") as f:
        f.write(new_version + "\n")
    print(f"Updated {version_file} -> {new_version}")

    pyproject = os.path.join(root, "pyproject.toml")
    with open(pyproject) as f:
        content = f.read()
    content = re.sub(r'^version = ".*"$', f'version = "{new_version}"', content, flags=re.MULTILINE)
    with open(pyproject, "w") as f:
        f.write(content)
    print(f"Updated {pyproject} -> {new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>")
        sys.exit(1)
    bump(sys.argv[1])