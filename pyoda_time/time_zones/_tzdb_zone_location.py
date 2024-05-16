# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import final

from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter
from pyoda_time.utility import InvalidPyodaDataError
from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
class TzdbZoneLocation:
    """A location entry generated from the "zone.tab" file in a TZDB release.

    This can be used to provide users with a choice of time zone, although it is not internationalized.
    """

    @property
    def latitude(self) -> float:
        """Gets the latitude in degrees; positive for North, negative for South.

        The value will be in the range [-90, 90].

        :return: The latitude in degrees; positive for North, negative for South.
        """
        return self.__latitude_seconds / 3600.0

    @property
    def longitude(self) -> float:
        """Gets the longitude in degrees; positive for East, negative for West.

        The value will be in the range [-180, 180].

        :return: The longitude in degrees; positive for East, negative for West.
        """
        return self.__longitude_seconds / 3600.0

    @property
    def country_name(self) -> str:
        """Gets the English name of the country containing the location, which is never empty.

        :return: The English name of the country containing the location.
        """
        return self.__country_name

    @property
    def country_code(self) -> str:
        """Gets the ISO-3166 2-letter country code for the country containing the location.

        :return: The ISO-3166 2-letter country code for the country containing the location.
        """
        return self.__country_code

    @property
    def zone_id(self) -> str:
        """The ID of the time zone for this location.

        If this mapping was fetched from a ``TzdbDateTimeZoneSource``, it will always be a valid ID within that source.

        :return: The ID of the time zone for this location.
        """
        return self.__zone_id

    @property
    def comment(self) -> str:
        """Gets the comment (in English) for the mapping, if any.

        This is usually used to differentiate between locations in the same country. This will return an empty string if
        no comment was provided in the original data.

        :return: The comment (in English) for the mapping, if any.
        """
        return self.__comment

    def __init__(
        self,
        latitude_seconds: int,
        longitude_seconds: int,
        country_name: str,
        country_code: str,
        zone_id: str,
        comment: str,
    ) -> None:
        """Creates a new location.

        This constructor is only public for the sake of testability. Non-test code should
        usually obtain locations from a ``TzdbDateTimeZoneSource``.

        :param latitude_seconds: Latitude of the location, in seconds.
        :param longitude_seconds: Longitude of the location, in seconds.
        :param country_name: English country name of the location, in degrees. Must not be null.
        :param country_code: ISO-3166 country code of the location. Must not be null.
        :param zone_id: Time zone identifier of the location. Must not be null.
        :param comment: Optional comment. Must not be null, but may be empty.
        :raises ValueError: If ``latitude_seconds`` or ``longitude_seconds`` are invalid.
        """
        _Preconditions._check_argument_range("latitude_seconds", latitude_seconds, -90 * 3600, 90 * 3600)
        _Preconditions._check_argument_range("longitude_seconds", longitude_seconds, -180 * 3600, 180 * 3600)
        self.__latitude_seconds = latitude_seconds
        self.__longitude_seconds = longitude_seconds
        self.__country_name = _Preconditions._check_not_null(country_name, "country_name")
        self.__country_code = _Preconditions._check_not_null(country_code, "country_code")
        _Preconditions._check_argument(len(self.country_name) > 0, "country_name", "Country name cannot be empty")
        _Preconditions._check_argument(
            len(self.country_code) == 2, "country_code", "Country code must be two characters"
        )
        self.__zone_id = _Preconditions._check_not_null(zone_id, "zone_id")
        self.__comment = _Preconditions._check_not_null(comment, "comment")

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        writer.write_signed_count(self.__latitude_seconds)
        writer.write_signed_count(self.__longitude_seconds)
        writer.write_string(self.country_name)
        writer.write_string(self.country_code)
        writer.write_string(self.zone_id)
        writer.write_string(self.comment)

    @classmethod
    def _read(cls, reader: _IDateTimeZoneReader) -> TzdbZoneLocation:
        latitude_seconds: int = reader.read_signed_count()
        longitude_seconds: int = reader.read_signed_count()
        country_name: str = reader.read_string()
        country_code: str = reader.read_string()
        zone_id: str = reader.read_string()
        comment: str = reader.read_string()
        # We could duplicate the validation, but there's no good reason to. It's odd
        # to catch ArgumentException, but we're in pretty tight control of what's going on here.
        try:
            return TzdbZoneLocation(latitude_seconds, longitude_seconds, country_name, country_code, zone_id, comment)
        except ValueError as e:
            raise InvalidPyodaDataError("Invalid zone location data in stream") from e
