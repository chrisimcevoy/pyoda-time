# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from pathlib import Path

import pytest

APACHE_LICENSE_HEADER = """
# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
"""

PROJECT_ROOT = Path(__file__).parent.parent


def get_python_files_under_directory(directory: str) -> list[Path]:
    directory_path = PROJECT_ROOT / directory
    if not directory_path.exists():
        raise Exception(f"Directory {directory_path} does not exist")
    python_file_paths = list(directory_path.glob("**/*.py"))
    if not python_file_paths:
        raise Exception(f"No python files found under {directory_path}")
    return python_file_paths


@pytest.mark.parametrize(
    "file_path",
    sorted(
        [
            *get_python_files_under_directory("pyoda_time"),
            *get_python_files_under_directory("tests"),
        ]
    ),
    ids=lambda p: str(p.relative_to(PROJECT_ROOT)),
)
def test_license_headers(file_path: Path) -> None:
    text = file_path.read_text()
    assert text.startswith(APACHE_LICENSE_HEADER.strip())
