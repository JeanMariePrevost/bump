# queries/__init__.py

import pkgutil
import importlib

__all__ = []  # Public API

# Discover and dynamically import all submodules and their public classes
# This is needed so we can import all queries in the queries module DYNAMICALLY and reference them by importing the queries package only
# It is needed to resolve Query types dynamically in the Monitor class
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    if not is_pkg:  # Ignore subpackages
        module = importlib.import_module(module_name)
        for attr_name in dir(module):
            if not attr_name.startswith("_"):  # Ignore private attributes
                attr = getattr(module, attr_name)
                if isinstance(attr, type):  # Only add classes
                    globals()[attr_name] = attr  # Add to package namespace
                    __all__.append(attr_name)  # Add to public API
