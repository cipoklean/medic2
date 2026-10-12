"""A benchmark case: one broken agent plus the check that decides if it works.

cases/<id>/
  case.yaml          id, type (general|docs), title, held_out, editable globs, released (docs cases)
  agent/             the broken agent's code (the only place Medic may edit)
  check.py           exits 0 when the agent works. Medic may never edit it.
  requirements.lock  optional pinned deps; installed into a per-case venv
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CASES_DIR = Path(__file__).resolve().parent.parent / "cases"
PROTECTED = ("check.py", "requirements.lock", "case.yaml")


@dataclass
class Case:
    id: str
    path: Path
    type: str
    title: str
    held_out: bool
    editable: list = field(default_factory=lambda: ["agent/**/*.py"])
    released: str | None = None

    @property
    def has_lock(self) -> bool:
        return (self.path / "requirements.lock").exists()

    def editable_files(self, root: Path | None = None) -> list[Path]:
        root = root or self.path
        out: list[Path] = []
        for pattern in self.editable:
            out.extend(p for p in root.glob(pattern) if p.is_file())
        return sorted(set(out))


def load(case_id: str) -> Case:
    path = CASES_DIR / case_id
    meta = yaml.safe_load((path / "case.yaml").read_text())
    return Case(id=meta.get("id", case_id), path=path, type=meta.get("type", "general"),
                title=meta.get("title", case_id), held_out=bool(meta.get("held_out", False)),
                editable=meta.get("editable", ["agent/**/*.py"]), released=meta.get("released"))


def all_cases() -> list[Case]:
    return [load(p.name) for p in sorted(CASES_DIR.iterdir())
            if (p / "case.yaml").exists() and not p.name.startswith("_")]
