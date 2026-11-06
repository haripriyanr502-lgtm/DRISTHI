# -*- coding: utf-8 -*-
"""Configure test import path for project packages.
Adds the backend/app directory to sys.path so that `import app` works in tests.
"""
import os, sys
# Resolve the project root (repository root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
