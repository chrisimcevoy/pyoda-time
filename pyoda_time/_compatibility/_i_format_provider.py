# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import abstractmethod
from typing import Any, Protocol


class IFormatProvider(Protocol):
    """Provides a mechanism for retrieving an object to control formatting.

    https://learn.microsoft.com/en-us/dotnet/api/system.iformatprovider
    """

    @abstractmethod
    def get_format(self, format_type: type) -> Any | None:
        """Returns an object that provides formatting services for the specified type.

        https://learn.microsoft.com/en-us/dotnet/api/system.iformatprovider.getformat

        :param format_type: An object that specifies the type of format object to return.
        :return: An instance of the object specified by ``format_type``, if the
            ``IFormatProvider`` implementation can supply that type of object; otherwise,
            ``None``.
        """
        ...
