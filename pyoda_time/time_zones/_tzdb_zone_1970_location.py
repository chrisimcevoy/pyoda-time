# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING

from pyoda_time.utility import InvalidPyodaDataError
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
    from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter


class TzdbZone1970Location:
    """A location entry generated from the "zone1970.tab" file in a TZDB release.

    This can be used to provide users with a choice of time zone, although it is not internationalized.
    This is equivalent to ``TzdbZoneLocation``, except that multiple countries may be represented.
    """

    class Country:
        """A country represented within an entry in the "zone1970.tab" file, with the English name mapped from the
        "iso3166.tab" file.

        Equality is defined component-wise: two values are considered equal if their country names are equal to
        each other, and their country codes are equal to each other.
        """

        @property
        def name(self) -> str:
            """Gets the English name of the country.

            :return: The English name of the country.
            """
            return self.__name

        @property
        def code(self) -> str:
            """Gets the ISO-3166 2-letter country code for the country.

            :return: The ISO-3166 2-letter country code for the country.
            """
            return self.__code

        def __init__(self, name: str, code: str) -> None:
            """Constructs a new country from its name and ISO-3166 2-letter code.

            :param name: Country name; must not be empty.
            :param code: 2-letter code
            """
            self.__name: str = _Preconditions._check_not_null(name, "name")
            self.__code: str = _Preconditions._check_not_null(code, "code")
            _Preconditions._check_argument(len(self.name) > 0, "name", "Country name cannot be empty")
            _Preconditions._check_argument(len(self.code) == 2, "code", "Country code must be two characters")

        def equals(self, other: TzdbZone1970Location.Country) -> bool:
            """Compares countries for equality.

            See the type documentation for a description of equality semantics.

            :param other: The country to compare with this one.
            :return: ``True`` if the given country has the same name and code as this one; ``False`` otherwise.
            """
            return self == other

        def __eq__(self, other: object) -> bool:
            """Compares countries for equality.

            See the type documentation for a description of equality semantics.

            :param other: The country to compare with this one.
            :return: ``True`` if the given country has the same name and code as this one; ``False`` otherwise.
            """
            if not isinstance(other, TzdbZone1970Location.Country):
                return NotImplemented
            return self.code == other.code and self.name == other.name

        def __hash__(self) -> int:
            """Returns a hash code for this country.

            :return: A hash code for this country.
            """
            return _hash_code_helper(self.name, self.code)

        def __repr__(self) -> str:
            """Returns a string representation of this country, including the code and name.

            :return: A string representation of this country.
            """
            return f"{self.code} ({self.name})"

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
    def countries(self) -> Sequence[Country]:
        """Gets the list of countries associated with this location.

        The list is immutable, and will always contain at least one entry. The list is in the order specified in
        "zone1970.tab", so the first entry is always the country containing the position indicated by the latitude and
        longitude, and is the most populous country in the list. No entry in this list is ever null.

        :return: The list of countries associated with this location
        """
        return self.__countries

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
        countries: Iterable[Country],
        zone_id: str,
        comment: str,
    ) -> None:
        """Creates a new location.

        This constructor is only public for the sake of testability. Non-test code should
        usually obtain locations from a ``TzdbDateTimeZoneSource``.

        :param latitude_seconds: Latitude of the location, in seconds.
        :param longitude_seconds: Longitude of the location, in seconds.
        :param countries: Countries associated with this location. Must not be null, must have at least
            one entry, and all entries must be non-null.
        :param zone_id: Time zone identifier of the location. Must not be null.
        :param comment: Optional comment. Must not be null, but may be empty.
        :raises ValueError: If ``latitude_seconds`` or ``longitude_seconds`` are invalid.
        """
        _Preconditions._check_argument_range("latitude_seconds", latitude_seconds, -90 * 3600, 90 * 3600)
        _Preconditions._check_argument_range("longitude_seconds", longitude_seconds, -180 * 3600, 180 * 3600)
        self.__latitude_seconds = latitude_seconds
        self.__longitude_seconds = longitude_seconds
        self.__countries = tuple(_Preconditions._check_not_null(countries, "country_name"))
        _Preconditions._check_argument(
            len(self.countries) > 0, "countries", "Collection must contain at least one entry."
        )
        for country in self.countries:
            _Preconditions._check_argument(country is not None, "countries", "Collection must not contain null entries")
        self.__zone_id = _Preconditions._check_not_null(zone_id, "zone_id")
        self.__comment = _Preconditions._check_not_null(comment, "comment")

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        writer.write_signed_count(self.__latitude_seconds)
        writer.write_signed_count(self.__longitude_seconds)
        writer.write_count(len(self.countries))
        # We considered writing out the ISO-3166 file as a separate field,
        # so we can reuse objects, but we don't actually waste very much space this way,
        # due to the string pool... and the increased code complexity isn't worth it.
        for country in self.countries:
            writer.write_string(country.name)
            writer.write_string(country.code)
        writer.write_string(self.zone_id)
        writer.write_string(self.comment)

    @staticmethod
    def _read(reader: _IDateTimeZoneReader) -> TzdbZone1970Location:
        latitude_seconds: int = reader.read_signed_count()
        longitude_seconds: int = reader.read_signed_count()
        country_count: int = reader.read_count()
        countries: list[TzdbZone1970Location.Country] = [
            TzdbZone1970Location.Country(reader.read_string(), code=reader.read_string()) for _ in range(country_count)
        ]
        zone_id: str = reader.read_string()
        comment: str = reader.read_string()
        # We could duplicate the validation, but there's no good reason to. It's odd
        # to catch ArgumentException, but we're in pretty tight control of what's going on here.
        try:
            return TzdbZone1970Location(latitude_seconds, longitude_seconds, countries, zone_id, comment)
        except ValueError as e:
            raise InvalidPyodaDataError("Invalid zone location data in stream") from e
