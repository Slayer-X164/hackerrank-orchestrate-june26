"""Entry point and runtime helpers for the claim verification workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from claim_workflow import (
    ClaimWorkflowState,
    build_claim_verification_graph,
    create_initial_state,
)


def detect_project_python(repo_root: Path) -> Path:
    """Return the preferred Python executable for this repository.

    The project keeps dependencies in a local `.venv`, so we prefer that
    interpreter when it exists. If no project virtualenv is present, we fall
    back to the current interpreter.
    """

    candidates = [
        repo_root / ".venv" / "bin" / "python",
        repo_root / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


def run_smoke_test(repo_root: Path) -> subprocess.CompletedProcess[str]:
    """Execute the smoke test using the detected project interpreter."""

    python_executable = detect_project_python(repo_root)
    smoke_test = repo_root / "code" / "smoke_test.py"
    return subprocess.run(
        [str(python_executable), str(smoke_test)],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )


__all__ = [
    "ClaimWorkflowState",
    "build_claim_verification_graph",
    "create_initial_state",
    "detect_project_python",
    "run_smoke_test",
]


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    result = run_smoke_test(repo_root)
    print(f"Using interpreter: {detect_project_python(repo_root)}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
