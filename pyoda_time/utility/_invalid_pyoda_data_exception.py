# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.


from typing import final

from ._csharp_compatibility import _sealed


@final
@_sealed
class InvalidPyodaDataError(Exception):
    """Exception thrown when data read by Pyoda Time (such as serialized time zone data) is invalid.

    This includes data which is truncated, i.e. we expect more data than we can read.
    """
