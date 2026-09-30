from __future__ import annotations

import json
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs" / "model_registry.json"
DESTINATIONS = {
    "ttm_r2_1_daily": ROOT / "models" / "ttm-r2.1-512-48",
    "chronos_2": ROOT / "models" / "chronos-2",
    "timesfm_2_5": ROOT / "models" / "timesfm-2.5",
}
ALLOWED_LICENSES = {"apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause"}


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["models"]
    for key, destination in DESTINATIONS.items():
        spec = registry[key]
        license_id = spec["license"].lower()
        if not spec["commercial_allowed"] or license_id not in ALLOWED_LICENSES:
            raise RuntimeError(f"Commercial license gate blocked {key}: {license_id}")
        revision = spec["revision"]
        if len(revision) < 12:
            raise RuntimeError(f"Model {key} is not pinned to an immutable revision")
        destination.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {spec['model_id']}@{revision} -> {destination}")
        snapshot_download(
            repo_id=spec["model_id"],
            revision=revision,
            local_dir=destination,
        )
    print("All commercially approved, revision-pinned model snapshots are available.")


if __name__ == "__main__":
    main()
