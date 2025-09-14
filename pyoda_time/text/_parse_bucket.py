# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import ABC, abstractmethod

from ._parse_result import ParseResult
from .patterns._pattern_fields import _PatternFields


class _ParseBucket[T](ABC):
    """Base class for "buckets" of parse data - as field values are parsed, they are stored in a bucket,
    then the final value is calculated at the end.
    """

    @abstractmethod
    def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[T]:
        """Performs the final conversion from fields to a value. The parse can still fail here, if there are
        incompatible field values.

        :param used_fields: Indicates which fields were part of the original text pattern.
        :param value: Complete value being parsed
        :return: The result of the parse operation.
        """
        raise NotImplementedError
