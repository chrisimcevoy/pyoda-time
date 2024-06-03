# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import threading
from typing import Final, final

from pyoda_time import IDateTimeZoneProvider
from pyoda_time.time_zones._tzdb_date_time_zone_source import TzdbDateTimeZoneSource
from pyoda_time.utility._csharp_compatibility import _private, _sealed


class __DateTimeZoneProvidersMeta(type):
    __lock: Final[threading.Lock] = threading.Lock()
    __tzdb: IDateTimeZoneProvider | None = None

    @property
    def tzdb(self) -> IDateTimeZoneProvider:
        """Gets a time zone provider which uses a ``TzdbTimeZoneSource``. The underlying source is
        ``TzdbDateTimeZoneSource.default``, which is initialized from resources within the pyoda_time package.

        :return: A time zone provider using a `TzdbDateTimeZoneSource``.
        """
        if self.__tzdb is None:
            with self.__lock:
                if self.__tzdb is None:
                    from pyoda_time.time_zones import DateTimeZoneCache

                    self.__tzdb = DateTimeZoneCache(source=TzdbDateTimeZoneSource.default)
        return self.__tzdb


@final
@_sealed
@_private
class DateTimeZoneProviders(metaclass=__DateTimeZoneProvidersMeta):
    """Static access to date/time zone providers built into Pyoda Time and for global configuration where this is
    unavoidable.

    All properties are thread-safe, and the providers returned by the read-only properties cache their results.
    """
