"""Exercise release setup's real source guard without network or publication."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize("damage", ["clean", "tracked", "untracked"])
def test_prepare_dependency_setup_reports_and_refuses_source_changes(tmp_path, damage):
    workflow = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / ".github/workflows/qa-release.yml").read_text()
    )
    steps = workflow["jobs"]["prepare"]["steps"]
    diagnostic = next(
        (s for s in steps if s.get("name") == "Verify release source hygiene without credentials"),
        None,
    )
    assert diagnostic is not None, "PREPARE must reproduce source hygiene before human review"
    source = tmp_path / "source"
    (source / "clients/mobile").mkdir(parents=True)
    (source / "requirements-lock.txt").write_text("synthetic dependencies\n")
    for args in [
        ["init", "-q"],
        ["add", "."],
        ["-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "source"],
    ]:
        subprocess.run(["git", "-C", str(source), *args], check=True)
    # Package installers are the slow external boundary. Git and the workflow
    # shell remain real; a simulated installer changes source just as a faulty
    # setup might. The guard must catch the resulting observable repository state.
    binaries = tmp_path / "bin"
    binaries.mkdir()
    for name in ["pip", "npm"]:
        script = binaries / name
        script.write_text(
            "#!/bin/sh\n"
            + (
                "if [ \"$1\" = ci ]; then\n"
                " case \"$DAMAGE\" in\n"
                " tracked) printf changed > ../../requirements-lock.txt ;;\n"
                " untracked) printf private-content > unexpected-generated.txt ;;\n"
                " esac\nfi\n"
                if name == "npm"
                else ""
            )
        )
        script.chmod(0o700)
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", diagnostic["run"]],
        cwd=source,
        env={**os.environ, "PATH": str(binaries) + os.pathsep + os.environ["PATH"], "DAMAGE": damage},
        capture_output=True,
        text=True,
        check=False,
    )
    if damage == "clean":
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0
        expected = "requirements-lock.txt" if damage == "tracked" else "unexpected-generated.txt"
        assert expected in result.stdout
        assert "private-content" not in result.stdout + result.stderr
        # It reports and stops; it never cleans or hides the evidence.
        changed = subprocess.check_output(
            ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"], text=True
        )
        assert expected in changed
