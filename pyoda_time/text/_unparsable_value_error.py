# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import final

from pyoda_time.utility._csharp_compatibility import _sealed


@_sealed
@final
class UnparsableValueError(Exception):
    """Exception thrown to indicate that the specified value could not be parsed."""
