"""Alias `src.grant_ai` to `grant_ai` using a meta path hook.

Minimal and robust; avoids duplicate module objects (e.g., SQLAlchemy tables).
"""

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys

PREFIX = "src.grant_ai"


class GrantAIShim(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == PREFIX or fullname.startswith(PREFIX + "."):
            real_name = "grant_ai" + fullname[len(PREFIX) :]
            real_spec = importlib.util.find_spec(real_name)
            if real_spec is None:
                return None
            is_pkg = real_spec.submodule_search_locations is not None
            spec = importlib.machinery.ModuleSpec(fullname, self, is_package=is_pkg)
            spec.origin = getattr(real_spec, "origin", "shim")
            if is_pkg:
                spec.submodule_search_locations = real_spec.submodule_search_locations
            return spec
        return None

    def create_module(self, spec):
        fullname = spec.name
        real_name = "grant_ai" + fullname[len(PREFIX) :]
        mod = importlib.import_module(real_name)
        sys.modules[fullname] = mod
        return mod

    def exec_module(self, module):
        return None


_shim = GrantAIShim()
if not any(isinstance(f, GrantAIShim) for f in sys.meta_path):
    sys.meta_path.insert(0, _shim)
