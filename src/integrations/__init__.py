"""Pluggable integration framework.

Each integration is a class that subclasses :class:`Integration` and registers
itself via :func:`register`. Adding a new integration is two steps:

1. Drop a Python file in ``src/integrations/``.
2. Subclass :class:`Integration`, implement ``run``, and call ``register(MyClass())``
   at import time.

The discovery routine in :func:`load_all` will import every module in this
package on bot startup so plugin authors never have to touch ``__init__``.
"""
from __future__ import annotations

import importlib
import logging
import pkgutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Integration] = {}


@dataclass
class IntegrationResult:
    ok: bool
    text: str
    extra: dict[str, Any] | None = None


class Integration(ABC):
    """Base class. Implementations should be small, focused and async-safe."""

    name: str = ""
    description: str = ""
    usage: str = ""

    @abstractmethod
    async def run(self, *args: str) -> IntegrationResult: ...

    async def healthcheck(self) -> bool:  # pragma: no cover - default impl
        return True


def register(integration: Integration) -> None:
    if not integration.name:
        raise ValueError("Integration.name must be set")
    _REGISTRY[integration.name] = integration
    logger.info("Registered integration: %s", integration.name)


def get(name: str) -> Integration | None:
    return _REGISTRY.get(name)


def all_integrations() -> dict[str, Integration]:
    return dict(_REGISTRY)


def load_all() -> None:
    """Import every submodule so plugins self-register."""
    package = __name__
    for _, mod_name, _ in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        if mod_name.startswith("_"):
            continue
        try:
            importlib.import_module(f"{package}.{mod_name}")
        except Exception:
            logger.exception("Failed to load integration module: %s", mod_name)
