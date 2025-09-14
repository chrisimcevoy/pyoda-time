# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING, Final, _ProtocolMeta, final

from pyoda_time._i_clock import IClock
from pyoda_time.utility._csharp_compatibility import _private, _sealed

if TYPE_CHECKING:
    from pyoda_time._instant import Instant


class __SystemClockMeta(_ProtocolMeta):
    __lock: Final[threading.Lock] = threading.Lock()
    __instance: SystemClock | None = None

    @property
    def instance(self) -> SystemClock:
        """The singleton instance of ``SystemClock``.

        :return: The singleton instance of ``SystemClock``.
        """
        if not self.__instance:
            with self.__lock:
                if not self.__instance:
                    self.__instance = object.__new__(SystemClock)
        return self.__instance


@final
@_sealed
@_private
class SystemClock(IClock, metaclass=__SystemClockMeta):
    """Singleton implementation of ``IClock`` which reads the current system time.

    It is recommended that for anything other than throwaway code, this is only referenced
    in a single place in your code: where you provide a value to inject into the rest of
    your application, which should only depend on the interface.
    """

    def get_current_instant(self) -> Instant:
        """Gets the current time as an ``Instant``.

        :return: The current time in nanoseconds as an ``Instant``.
        """
        from pyoda_time._pyoda_constants import PyodaConstants

        return PyodaConstants.UNIX_EPOCH.plus_nanoseconds(time.time_ns())
