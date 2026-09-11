from pathlib import Path

import pytest

from jarvis.safe_tools import CapabilityError, _safe_workspace_path, list_files, read_file


def test_workspace_path_cannot_escape_repo() -> None:
    with pytest.raises(CapabilityError):
        _safe_workspace_path("../outside")


def test_list_files_is_scoped() -> None:
    result = list_files("tests")
    assert "test_safe_tools.py" in result


def test_read_file_reads_repo_text() -> None:
    assert "J.A.R.V.I.S." in read_file("README.md")


def test_read_file_rejects_missing_file() -> None:
    with pytest.raises(CapabilityError):
        read_file("tests/does-not-exist.txt")
