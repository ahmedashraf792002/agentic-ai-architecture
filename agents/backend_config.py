from pathlib import Path

from deepagents import FilesystemPermission
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend


def build_backend(evidence_root: str | Path, systems_root: str | Path):
    
    return CompositeBackend(
        default=StateBackend(),
        routes={
            "/evidence/": FilesystemBackend(root_dir=str(evidence_root), virtual_mode=True),
            "/systems/": FilesystemBackend(root_dir=str(systems_root), virtual_mode=True),
        },
    )


def build_permissions():
    return [
        FilesystemPermission(
            operations=["write"],
            paths=["/evidence/**"],
            mode="deny",
        ),
    ]
