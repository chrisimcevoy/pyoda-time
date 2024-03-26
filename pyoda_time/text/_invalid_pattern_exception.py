# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import Any, final

from ..utility._csharp_compatibility import _sealed


@final
@_sealed
class InvalidPatternError(ValueError):
    """Exception thrown to indicate that the format pattern provided for either formatting or parsing is invalid."""

    def __init__(self, message: str, *args: Any) -> None:
        """Creates a new InvalidPatternException by formatting the given format string with the specified parameters.

        :param message: Format string to use in order to create the final message
        :param args: Format string parameters
        """
        if args:
            message = message.format(*args)
        super().__init__(message)
