# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pyoda_time
import version


def test_version() -> None:
    assert version.__version__ == pyoda_time.__version__
