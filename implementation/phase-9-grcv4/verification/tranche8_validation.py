"""Operation-local reuse of frozen, read-only Tranche 8 prerequisites.

No persistent cache, numerical-result cache, changed historical source or new
authority. Only named zero-argument metadata builders are memoized. Returned
objects are detached copies; every observed file is content-checked on exit.
"""

from contextlib import ExitStack, contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
import hashlib
import importlib
import inspect
import json
from pathlib import Path
from threading import RLock
from types import ModuleType
from unittest.mock import patch

ACTIVE = ContextVar("tranche8_validation_snapshot", default=None)
LOCK = RLock()
ROOT = Path(__file__).resolve().parents[3]
PREFIXES = ("p984", "prepare_p984", "verify_p983")
HELPERS = ("predecessor", "accepted_oracle", "make_manifest")
DIRECT_FILES = ("SELF", "TEST", "INPUTS", "RESULTS", "REVIEW", "PREDECESSOR", "RECORD")
BOUNDARY_MODULES = ("p984c_cos", "p984c_aos_oracle", "p984c_aos_runtime",
    "p984c_cci_preparation", "p984c_cci_runtime", "p984c_aci_oracle", "p984c_aci_runtime", "p984c_cpc_runtime", "p984c_apc_runtime", "p984c_ccipc_runtime")


class Snapshot:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self._bytes, self._json, self._hashes, self._memo = {}, {}, {}, {}
        self.hits = 0
        self.modules = ()

    def config_key(self):
        # In-process pressure may replace an acceptance constant or helper.
        # Such changes must not reuse a verdict computed under the old value.
        return tuple((m.__name__, tuple((k, repr(v)) for k, v in sorted(vars(m).items())
            if k.isupper() or k in HELPERS)) for m in self.modules)

    def path(self, name):
        name = str(name)
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("nonportable snapshot path")
        path = self.root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(self.root):
            raise ValueError("unsafe snapshot path")
        return path

    def raw(self, name):
        name = str(name)
        if name not in self._bytes:
            self._bytes[name] = self.path(name).read_bytes()
            self._hashes[name] = hashlib.sha256(self._bytes[name]).hexdigest()
        return self._bytes[name]

    def read(self, name):
        name = str(name)
        if name not in self._json:
            self._json[name] = json.loads(self.raw(name))
        return deepcopy(self._json[name])

    def bind(self, paths):
        rows = []
        for name in sorted(set(paths)):
            self.raw(name)
            rows.append(dict(path=name, sha256=self._hashes[str(name)]))
        return rows

    def check_bindings(self, rows):
        if len(rows) != len({r["path"] for r in rows}):
            raise ValueError("duplicate bindings")
        for row in rows:
            self.raw(row["path"])
            if self._hashes[str(row["path"])] != row["sha256"]:
                raise ValueError("source drift: " + row["path"])

    def unchanged(self):
        for name, sha in self._hashes.items():
            if hashlib.sha256(self.path(name).read_bytes()).hexdigest() != sha:
                raise ValueError("source changed during validation: " + name)


def modules(names):
    pending = [importlib.import_module(n) for n in names]
    found = {}
    while pending:
        module = pending.pop()
        if module.__name__ in found or not module.__name__.startswith(PREFIXES):
            continue
        found[module.__name__] = module
        pending.extend(v for v in vars(module).values() if isinstance(v, ModuleType)
            and v.__name__.startswith(PREFIXES))
    return list(found.values())


def memoized(function):
    @wraps(function)
    def call(*args, **kwargs):
        snapshot = ACTIVE.get()
        if snapshot is None or args or kwargs:
            return function(*args, **kwargs)
        key = (function, snapshot.config_key())
        if key not in snapshot._memo:
            snapshot._memo[key] = deepcopy(function())
        else:
            snapshot.hits += 1
        return deepcopy(snapshot._memo[key])
    return call


def reader(function, method):
    @wraps(function)
    def call(*args, **kwargs):
        snapshot = ACTIVE.get()
        if snapshot is None:
            return function(*args, **kwargs)
        if Path(function.__globals__["ROOT"]).resolve() != snapshot.root:
            raise ValueError("snapshot root mismatch")
        return getattr(snapshot, method)(*args, **kwargs)
    return call


@contextmanager
def validation_session(names=BOUNDARY_MODULES, root=ROOT):
    """One immutable-byte snapshot; ordinary callers outside it remain uncached.

    Serializes adapter installation, with context-local state so other threads
    still call original functions. Source drift fails before a result escapes.
    Frozen numerical checkers and validators are never memoized or replaced.
    """
    if ACTIVE.get() is not None:
        raise ValueError("nested validation sessions are not supported")
    with LOCK, ExitStack() as stack:
        snapshot = Snapshot(root)
        snapshot.raw(str(Path(__file__).resolve().relative_to(snapshot.root)))
        selected = modules(names)
        snapshot.modules = selected
        for module in selected:
            for key in DIRECT_FILES:
                name = getattr(module, key, None)
                if isinstance(name, str) and snapshot.path(name).is_file():
                    snapshot.raw(name)
            if getattr(module, "__file__", None):
                snapshot.raw(str(Path(module.__file__).resolve().relative_to(snapshot.root)))
            for name in HELPERS:
                function = getattr(module, name, None)
                if inspect.isfunction(function) and function.__module__ == module.__name__:
                    stack.enter_context(patch.object(module, name, memoized(function)))
            # The accepted boundary helpers share this IO layer. Never patch
            # Path, native producers, numerical equations or validation results.
            if module.__name__ == "p984b_runtime":
                for name in ("read", "bind", "check_bindings"):
                    stack.enter_context(patch.object(module, name, reader(getattr(module, name), name)))
        token = ACTIVE.set(snapshot)
        try:
            yield snapshot
            snapshot.unchanged()
        finally:
            ACTIVE.reset(token)
