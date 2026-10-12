"""Run a case's check in an isolated copy and enforce the patch-scope rule.

Reruns happen locally (or on any box you like); every model call goes to Token Factory.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import venv
from dataclasses import dataclass
from pathlib import Path

from medic import config
from medic.case import PROTECTED, Case

WORK = Path(__file__).resolve().parent.parent / ".medic_work"


@dataclass
class CheckResult:
    passed: bool
    exit_code: int
    output: str
    seconds: float


def _digest(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in PROTECTED if (root / name).exists()}


def python_for(case: Case) -> str:
    if not case.has_lock:
        return sys.executable
    env_dir = WORK / "venvs" / case.id
    py = env_dir / "bin" / "python"
    if not py.exists():
        venv.create(env_dir, with_pip=True)
        subprocess.run([str(py), "-m", "pip", "install", "-q", "-r", str(case.path / "requirements.lock")],
                       check=True)
    return str(py)


def workspace(case: Case) -> Path:
    WORK.mkdir(exist_ok=True)
    dst = Path(tempfile.mkdtemp(prefix=f"{case.id}-", dir=WORK))
    shutil.copytree(case.path, dst, dirs_exist_ok=True)
    return dst


def run_check(case: Case, root: Path) -> CheckResult:
    import time
    t0 = time.time()
    try:
        p = subprocess.run([python_for(case), "check.py"], cwd=root, capture_output=True, text=True,
                           timeout=config.CHECK_TIMEOUT_S)
        out = (p.stdout + "\n" + p.stderr).strip()
        code = p.returncode
    except subprocess.TimeoutExpired as e:
        out = f"TIMEOUT after {config.CHECK_TIMEOUT_S}s\n{(e.stdout or '')}{(e.stderr or '')}"
        code = 124
    return CheckResult(code == 0, code, out[-6000:], round(time.time() - t0, 2))


def protected_intact(case: Case, root: Path) -> bool:
    return _digest(case.path) == _digest(root)
