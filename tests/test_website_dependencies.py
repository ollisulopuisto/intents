"""Test website dependency versions for security fixes."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = ROOT / "website" / "package-lock.json"

# compression 1.8.2 fixes: Denial of Service via memory leak on
# premature response close (fixed in 1.8.2)


def _load_lock() -> dict:
    with LOCK_FILE.open() as handle:
        return json.load(handle)


def _compression_locations(lock: dict) -> list[tuple[str, object]]:
    """All places the lock file resolves compression."""
    locations: list[tuple[str, object]] = []

    packages: dict = lock["packages"]
    if "node_modules/compression" in packages:
        locations.append(
            ("packages[node_modules/compression]", packages["node_modules/compression"])
        )

    dependencies: dict = lock.get("dependencies", {})
    if "compression" in dependencies:
        locations.append(("dependencies[compression]", dependencies["compression"]))

    serve: dict = dependencies.get("serve", {})
    if "compression" in serve.get("requires", {}):
        locations.append(
            (
                "dependencies[serve].requires[compression]",
                serve["requires"]["compression"],
            )
        )

    return locations


def test_compression_patched_to_1_8_2() -> None:
    """compression must resolve to 1.8.2 everywhere in the lock file."""
    lock = _load_lock()
    locations = _compression_locations(lock)
    assert locations, "compression must be present in the lock file"
    for name, package in locations:
        if isinstance(package, str):
            value = package
        else:
            value = package["version"]
        assert value == "1.8.2", f"{name}: {value}"
        if not isinstance(package, str):
            assert package["resolved"].endswith(
                "compression/-/compression-1.8.2.tgz"
            ), f"{name}: {package.get('resolved')}"
