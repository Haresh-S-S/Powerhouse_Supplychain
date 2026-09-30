from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


class CommercialLicenseError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ModelSpec:
    key: str
    model_id: str
    revision: str
    license: str
    commercial_allowed: bool
    role: str


class ModelRegistry:
    ALLOWED_LICENSES: ClassVar[frozenset[str]] = frozenset(
        {"apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause"}
    )

    def __init__(self, specs: dict[str, ModelSpec]) -> None:
        self.specs = specs

    @classmethod
    def load(cls, path: str | Path | None = None) -> ModelRegistry:
        if path is None:
            source_tree_registry = (
                Path(__file__).resolve().parents[2] / "configs" / "model_registry.json"
            )
            packaged_registry = Path(__file__).with_name("model_registry.json")
            path = (
                source_tree_registry if source_tree_registry.exists() else packaged_registry
            )
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        specs = {
            key: ModelSpec(key=key, **value) for key, value in payload["models"].items()
        }
        return cls(specs)

    def require_commercial(self, keys: list[str] | tuple[str, ...]) -> list[ModelSpec]:
        approved = []
        for key in keys:
            if key not in self.specs:
                raise CommercialLicenseError(f"model {key!r} is not registered")
            spec = self.specs[key]
            if not spec.commercial_allowed or spec.license.lower() not in self.ALLOWED_LICENSES:
                raise CommercialLicenseError(
                    f"model {key!r} is blocked: license={spec.license}, "
                    f"commercial_allowed={spec.commercial_allowed}"
                )
            if len(spec.revision) < 12:
                raise CommercialLicenseError(f"model {key!r} does not pin an immutable revision")
            approved.append(spec)
        return approved
