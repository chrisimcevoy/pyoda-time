# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import itertools
from typing import Any, Final, Iterable, Sequence

import pytest
from _pytest.fixtures import FixtureRequest
from culture_saver import CultureSaver

from pyoda_time import CalendarSystem, LocalDateTime
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time.text import InvalidPatternError, LocalDateTimePattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.utility._csharp_compatibility import _CsharpConstants

from ..text.pattern_test_base import PatternTestBase
from .cultures import Cultures
from .pattern_test_data import PatternTestData


class Data(PatternTestData[LocalDateTime]):
    def __init__(
        self,
        *,
        value: LocalDateTime = LocalDateTimePattern._DEFAULT_TEMPLATE_VALUE,
        text: str | None = None,
        pattern: str | None = None,
        message: str | None = None,
        parameters: list[Any] | None = None,
        culture: CultureInfo | None = CultureInfo.invariant_culture,
        template: LocalDateTime | None = None,
        standard_pattern: IPattern[LocalDateTime] | None = None,
    ) -> None:
        super().__init__(
            value,
            text=text,
            pattern=pattern,
            message=message,
            parameters=parameters,
            culture=culture or CultureInfo.invariant_culture,
            template=template,
            standard_pattern=standard_pattern,
        )

    @property
    def default_template(self) -> LocalDateTime:
        """Default to the start of the year 2000."""
        return LocalDateTimePattern._DEFAULT_TEMPLATE_VALUE

    def create_pattern(self) -> IPattern[LocalDateTime]:
        assert self.pattern is not None
        return (
            LocalDateTimePattern.create_with_invariant_culture(self.pattern)
            .with_template_value(self.template)
            .with_culture(self.culture)
        )


SAMPLE_LOCAL_DATE_TIME: Final[LocalDateTime] = LocalDateTime(1976, 6, 19, 21, 13, 34).plus_nanoseconds(123456789)
SAMPLE_LOCAL_DATE_TIME_TO_TICKS: Final[LocalDateTime] = LocalDateTime(1976, 6, 19, 21, 13, 34).plus_nanoseconds(
    123456700
)
SAMPLE_LOCAL_DATE_TIME_TO_MILLIS: Final[LocalDateTime] = LocalDateTime(1976, 6, 19, 21, 13, 34, 123)
SAMPLE_LOCAL_DATE_TIME_TO_SECONDS: Final[LocalDateTime] = LocalDateTime(1976, 6, 19, 21, 13, 34)
SAMPLE_LOCAL_DATE_TIME_TO_MINUTES: Final[LocalDateTime] = LocalDateTime(1976, 6, 19, 21, 13)
SAMPLE_LOCAL_DATE_TIME_COPTIC: Final[LocalDateTime] = LocalDateTime(
    1976, 6, 19, 21, 13, 34, calendar=CalendarSystem.coptic
).plus_nanoseconds(123456789)

ALL_STANDARD_PATTERNS: Final[Sequence[str]] = ["f", "F", "g", "G", "o", "O", "s"]

ALL_CULTURES_STANDARD_PATTERNS: Final[list[tuple[CultureInfo, str]]] = list(
    itertools.product(Cultures.all_cultures, ALL_STANDARD_PATTERNS)
)

# The standard example date/time used in all the MSDN samples, which means we can just cut and paste
# the expected results of the standard patterns.
MSDN_STANDARD_EXAMPLE: Final[LocalDateTime] = LocalDateTime(2009, 6, 15, 13, 45, 30, 90)
MSDN_STANDARD_EXAMPLE_NO_MILLIS: Final[LocalDateTime] = LocalDateTime(2009, 6, 15, 13, 45, 30)
MSDN_STANDARD_EXAMPLE_NO_SECONDS: Final[LocalDateTime] = LocalDateTime(2009, 6, 15, 13, 45)

INVALID_PATTERN_DATA = [
    Data(pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(pattern="a", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["a", LocalDateTime.__name__]),
    Data(pattern="dd MM uuuu HH:MM:SS", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["M"]),
    # Note incorrect use of "u" (year) instead of "y" (year of era)
    Data(pattern="dd MM uuuu HH:mm:ss gg", message=_TextErrorMessages.ERA_WITHOUT_YEAR_OF_ERA),
    # Era specifier and calendar specifier in the same pattern.
    Data(pattern="dd MM yyyy HH:mm:ss gg c", message=_TextErrorMessages.CALENDAR_AND_ERA),
    # Embedded pattern start without ld or lt
    Data(pattern="uuu MM dd <", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["<"]),
    # Attempt to use a full embedded date/time pattern (not valid for LocalDateTime)
    Data(pattern="l<uuuu MM dd HH:mm>", message=_TextErrorMessages.INVALID_EMBEDDED_PATTERN_TYPE),
    # Invalid nested pattern (local date pattern doesn't know about embedded patterns)
    Data(pattern="ld<<D>>", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["<"]),
]

PARSE_FAILURE_DATA = [
    Data(
        pattern="dd MM uuuu HH:mm:ss",
        text="Complete mismatch",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["dd"],
    ),
    Data(pattern="(c)", text="(xxx)", message=_TextErrorMessages.NO_MATCHING_CALENDAR_SYSTEM),
    # 24 as an hour is only valid when the time is midnight
    Data(
        pattern="uuuu-MM-dd",
        text="2017-02-30",
        message=_TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE,
        parameters=[30, 2, 2017],
    ),
    Data(pattern="uuuu-MM-dd HH:mm:ss", text="2011-10-19 24:00:05", message=_TextErrorMessages.INVALID_HOUR_24),
    Data(pattern="uuuu-MM-dd HH:mm:ss", text="2011-10-19 24:01:00", message=_TextErrorMessages.INVALID_HOUR_24),
    Data(pattern="uuuu-MM-dd HH:mm", text="2011-10-19 24:01", message=_TextErrorMessages.INVALID_HOUR_24),
    Data(
        pattern="uuuu-MM-dd HH:mm",
        text="2011-10-19 24:00",
        template=LocalDateTime(1970, 1, 1, 0, 0, 5),
        message=_TextErrorMessages.INVALID_HOUR_24,
    ),
    Data(
        pattern="uuuu-MM-dd HH",
        text="2011-10-19 24",
        template=LocalDateTime(1970, 1, 1, 0, 5, 0),
        message=_TextErrorMessages.INVALID_HOUR_24,
    ),
]

PARSE_ONLY_DATA = [
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20),
        pattern="dd MM uuuu",
        text="19 10 2011",
        template=LocalDateTime(2000, 1, 1, 16, 5, 20),
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20),
        pattern="HH:mm:ss",
        text="16:05:20",
        template=LocalDateTime(2011, 10, 19, 0, 0, 0),
    ),
    # Parsing using the semi-colon "comma dot" specifier
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20, 352),
        pattern="uuuu-MM-dd HH:mm:ss;fff",
        text="2011-10-19 16:05:20,352",
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20, 352),
        pattern="uuuu-MM-dd HH:mm:ss;FFF",
        text="2011-10-19 16:05:20,352",
    ),
    # 24:00 meaning "start of next day"
    Data(
        value=LocalDateTime(2011, 10, 20),
        pattern="uuuu-MM-dd HH:mm:ss",
        text="2011-10-19 24:00:00",
    ),
    Data(
        value=LocalDateTime(2011, 10, 20),
        pattern="uuuu-MM-dd HH:mm:ss",
        text="2011-10-19 24:00:00",
        template=LocalDateTime(1970, 1, 1, 0, 5, 0),
    ),
    Data(
        value=LocalDateTime(2011, 10, 20),
        pattern="uuuu-MM-dd HH:mm",
        text="2011-10-19 24:00",
    ),
    Data(
        value=LocalDateTime(2011, 10, 20),
        pattern="uuuu-MM-dd HH",
        text="2011-10-19 24",
    ),
]

FORMAT_ONLY_DATA = [
    Data(value=LocalDateTime(2011, 10, 19, 16, 5, 20), pattern="ddd uuuu", text="Wed 2011"),
    # Note truncation of the "89" nanoseconds; o and O are BCL roundtrip patterns, with tick precision.
    Data(value=SAMPLE_LOCAL_DATE_TIME, pattern="o", text="1976-06-19T21:13:34.1234567"),
    Data(value=SAMPLE_LOCAL_DATE_TIME, pattern="O", text="1976-06-19T21:13:34.1234567"),
]

FORMAT_AND_PARSE_DATA = [
    # Standard Patterns (US)
    # Full date/time (short time)
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_SECONDS,
        pattern="f",
        text="Monday, June 15, 2009 1:45 PM",
        culture=Cultures.en_us,
    ),
    # Full date/time (long time)
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        pattern="F",
        text="Monday, June 15, 2009 1:45:30 PM",
        culture=Cultures.en_us,
    ),
    # General date/time (short time)
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_SECONDS,
        pattern="g",
        text="6/15/2009 1:45 PM",
        culture=Cultures.en_us,
    ),
    # General date/time (longtime)
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        pattern="G",
        text="6/15/2009 1:45:30 PM",
        culture=Cultures.en_us,
    ),
    # Round-trip (o and O - same effect)
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        pattern="o",
        text="2009-06-15T13:45:30.0900000",
        culture=Cultures.en_us,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        pattern="O",
        text="2009-06-15T13:45:30.0900000",
        culture=Cultures.en_us,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        pattern="r",
        text="2009-06-15T13:45:30.090000000 (ISO)",
        culture=Cultures.en_us,
    ),
    Data(
        value=SAMPLE_LOCAL_DATE_TIME_COPTIC,
        pattern="r",
        text="1976-06-19T21:13:34.123456789 (Coptic)",
        culture=Cultures.en_us,
    ),
    # Note: No RFC1123, as that requires a time zone.
    # Short Sortable / ISO8601
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        pattern="s",
        text="2009-06-15T13:45:30",
        culture=Cultures.en_us,
    ),
    # Long Sortable / ISO8601-extended
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        pattern="S",
        text="2009-06-15T13:45:30.09",
        culture=Cultures.en_us,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        pattern="S",
        text="2009-06-15T13:45:30",
        culture=Cultures.en_us,
    ),
    # Standard Patterns (French)
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_SECONDS,
        pattern="f",
        text="lundi 15 juin 2009 13:45",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        pattern="F",
        text="lundi 15 juin 2009 13:45:30",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_SECONDS,
        pattern="g",
        text="15/06/2009 13:45",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        pattern="G",
        text="15/06/2009 13:45:30",
        culture=Cultures.fr_fr,
    ),
    # Culture has no impact on round-trip or sortable formats
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        standard_pattern=LocalDateTimePattern.bcl_round_trip,
        pattern="o",
        text="2009-06-15T13:45:30.0900000",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        standard_pattern=LocalDateTimePattern.bcl_round_trip,
        pattern="O",
        text="2009-06-15T13:45:30.0900000",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        standard_pattern=LocalDateTimePattern.full_roundtrip_without_calendar,
        pattern="R",
        text="2009-06-15T13:45:30.090000000",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        standard_pattern=LocalDateTimePattern.full_roundtrip,
        pattern="r",
        text="2009-06-15T13:45:30.090000000 (ISO)",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE_NO_MILLIS,
        standard_pattern=LocalDateTimePattern.general_iso,
        pattern="s",
        text="2009-06-15T13:45:30",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        standard_pattern=LocalDateTimePattern.extended_iso,
        pattern="S",
        text="2009-06-15T13:45:30.09",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=SAMPLE_LOCAL_DATE_TIME,
        standard_pattern=LocalDateTimePattern.full_roundtrip_without_calendar,
        pattern="R",
        text="1976-06-19T21:13:34.123456789",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=SAMPLE_LOCAL_DATE_TIME,
        standard_pattern=LocalDateTimePattern.full_roundtrip,
        pattern="r",
        text="1976-06-19T21:13:34.123456789 (ISO)",
        culture=Cultures.fr_fr,
    ),
    # Calendar patterns are invariant
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        pattern="(c) uuuu-MM-dd'T'HH:mm:ss.FFFFFFFFF",
        text="(ISO) 2009-06-15T13:45:30.09",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        pattern="uuuu-MM-dd(c)'T'HH:mm:ss.FFFFFFFFF",
        text="2009-06-15(ISO)T13:45:30.09",
        culture=Cultures.en_us,
    ),
    Data(
        value=SAMPLE_LOCAL_DATE_TIME_COPTIC,
        pattern="(c) uuuu-MM-dd'T'HH:mm:ss.FFFFFFFFF",
        text="(Coptic) 1976-06-19T21:13:34.123456789",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=SAMPLE_LOCAL_DATE_TIME_COPTIC,
        pattern="uuuu-MM-dd'C'c'T'HH:mm:ss.FFFFFFFFF",
        text="1976-06-19CCopticT21:13:34.123456789",
        culture=Cultures.en_us,
    ),
    # Standard invariant patterns with a property but no pattern character
    Data(
        value=MSDN_STANDARD_EXAMPLE,
        standard_pattern=LocalDateTimePattern.extended_iso,
        pattern="uuuu'-'MM'-'dd'T'HH':'mm':'ss;FFFFFFFFF",
        text="2009-06-15T13:45:30.09",
        culture=Cultures.fr_fr,
    ),
    # Use of the semi-colon "comma dot" specifier
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20, 352),
        pattern="uuuu-MM-dd HH:mm:ss;fff",
        text="2011-10-19 16:05:20.352",
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20, 352),
        pattern="uuuu-MM-dd HH:mm:ss;FFF",
        text="2011-10-19 16:05:20.352",
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20, 352),
        pattern="uuuu-MM-dd HH:mm:ss;FFF 'end'",
        text="2011-10-19 16:05:20.352 end",
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20),
        pattern="uuuu-MM-dd HH:mm:ss;FFF 'end'",
        text="2011-10-19 16:05:20 end",
    ),
    # When the AM designator is a leading substring of the PM designator...
    Data(
        value=LocalDateTime(2011, 10, 19, 16, 5, 20),
        pattern="uuuu-MM-dd h:mm:ss tt",
        text="2011-10-19 4:05:20 FooBar",
        culture=Cultures._awkward_am_pm_designator_culture,
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 4, 5, 20),
        pattern="uuuu-MM-dd h:mm:ss tt",
        text="2011-10-19 4:05:20 Foo",
        culture=Cultures._awkward_am_pm_designator_culture,
    ),
    # Current culture decimal separator is irrelevant when trimming the dot for truncated fractional settings
    Data(
        value=LocalDateTime(2011, 10, 19, 4, 5, 6),
        pattern="uuuu-MM-dd HH:mm:ss.FFF",
        text="2011-10-19 04:05:06",
        culture=Cultures.fr_fr,
    ),
    Data(
        value=LocalDateTime(2011, 10, 19, 4, 5, 6, 123),
        pattern="uuuu-MM-dd HH:mm:ss.FFF",
        text="2011-10-19 04:05:06.123",
        culture=Cultures.fr_fr,
    ),
    # Check handling of F after non-period.
    Data(
        value=LocalDateTime(2011, 10, 19, 4, 5, 6, 123),
        pattern="uuuu-MM-dd HH:mm:ss'x'FFF",
        text="2011-10-19 04:05:06x123",
        culture=Cultures.fr_fr,
    ),
    # Check that unquoted T still works.
    Data(
        value=LocalDateTime(2012, 1, 31, 17, 36, 45),
        pattern="uuuu-MM-ddTHH:mm:ss",
        text="2012-01-31T17:36:45",
    ),
    # Custom embedded patterns (or mixture of custom and standard)
    Data(
        value=LocalDateTime(2015, 10, 24, 11, 55, 30, 0),
        pattern="ld<uuuu*MM*dd>'X'lt<HH_mm_ss>",
        text="2015*10*24X11_55_30",
    ),
    Data(
        value=LocalDateTime(2015, 10, 24, 11, 55, 30, 0),
        pattern="lt<HH_mm_ss>'Y'ld<uuuu*MM*dd>",
        text="11_55_30Y2015*10*24",
    ),
    Data(
        value=LocalDateTime(2015, 10, 24, 11, 55, 30, 0),
        pattern="ld<d>'X'lt<HH_mm_ss>",
        text="10/24/2015X11_55_30",
    ),
    Data(
        value=LocalDateTime(2015, 10, 24, 11, 55, 30, 0),
        pattern="ld<uuuu*MM*dd>'X'lt<T>",
        text="2015*10*24X11:55:30",
    ),
    # Standard embedded patterns (main use case of embedded patterns).
    # Short time versions have a seconds value of 0 so they can round-trip.
    Data(
        value=LocalDateTime(2015, 10, 24, 11, 55, 30, 90),
        pattern="ld<D> lt<r>",
        text="Saturday, 24 October 2015 11:55:30.09",
    ),
    Data(
        value=LocalDateTime(2015, 10, 24, 11, 55, 0),
        pattern="ld<d> lt<t>",
        text="10/24/2015 11:55",
    ),
]

PARSE_DATA = PARSE_ONLY_DATA + FORMAT_AND_PARSE_DATA
FORMAT_DATA = FORMAT_ONLY_DATA + FORMAT_AND_PARSE_DATA


@pytest.fixture(params=[pytest.param(data, id=f"{data.pattern=}") for data in INVALID_PATTERN_DATA])
def invalid_pattern_data(request: FixtureRequest) -> Data:
    assert isinstance(request.param, Data)
    return request.param


@pytest.fixture(params=[pytest.param(data, id=f"{data.pattern=} {data.text=}") for data in PARSE_FAILURE_DATA])
def parse_failure_data(request: FixtureRequest) -> Data:
    assert isinstance(request.param, Data)
    return request.param


@pytest.fixture(params=[pytest.param(data, id=f"{data.pattern=} {data.text=}") for data in PARSE_DATA])
def parse_data(request: FixtureRequest) -> Data:
    assert isinstance(request.param, Data)
    return request.param


@pytest.fixture(params=[pytest.param(data, id=f"{data.pattern=} {data.text=} {data.culture=}") for data in FORMAT_DATA])
def format_data(request: FixtureRequest) -> Data:
    assert isinstance(request.param, Data)
    return request.param


class TestLocalDateTimePattern(PatternTestBase[LocalDateTime]):
    def test_with_calendar(self) -> None:
        pattern: LocalDateTimePattern = LocalDateTimePattern.general_iso.with_calendar(CalendarSystem.coptic)
        value = pattern.parse("0284-08-29T12:34:56").value
        assert value == LocalDateTime(284, 8, 29, 12, 34, 56, calendar=CalendarSystem.coptic)

    def test_create_with_current_culture(self) -> None:
        date_time = LocalDateTime(2017, 8, 23, 12, 34, 56)
        with CultureSaver.set_cultures(Cultures.fr_fr):
            pattern = LocalDateTimePattern.create_with_current_culture("g")
            assert pattern.format(date_time) == "23/08/2017 12:34"
        with CultureSaver.set_cultures(Cultures.fr_ca):
            pattern = LocalDateTimePattern.create_with_current_culture("g")
            assert pattern.format(date_time) == "2017-08-23 12:34"

    def test_parse_null(self) -> None:
        self.assert_parse_null(LocalDateTimePattern.extended_iso)

    @pytest.mark.parametrize(
        "two_digit_year_max,text,expected_year",
        [
            (0, "00-01-01T00:00:00", 2000),
            (0, "01-01-01T00:00:00", 1901),
            (50, "49-01-01T00:00:00", 2049),
            (50, "50-01-01T00:00:00", 2050),
            (50, "51-01-01T00:00:00", 1951),
            (99, "00-01-01T00:00:00", 2000),
            (99, "99-01-01T00:00:00", 2099),
        ],
    )
    def test_with_two_digit_year_max(self, two_digit_year_max: int, text: str, expected_year: int) -> None:
        pattern = LocalDateTimePattern.create_with_invariant_culture("yy-MM-dd'T'HH:mm:ss").with_two_digit_year_max(
            two_digit_year_max
        )
        value = pattern.parse(text).value
        assert value.year == expected_year

    @pytest.mark.parametrize(
        "two_digit_year_max", [-1, 100, _CsharpConstants.INT_MIN_VALUE, _CsharpConstants.INT_MAX_VALUE]
    )
    def test_with_two_digit_year_max_invalid(self, two_digit_year_max: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDateTimePattern.extended_iso.with_two_digit_year_max(two_digit_year_max)

    # TODO: Figure out what we want to do here...
    #  The purpose of this test in the mother project is to:
    #  - Format the Noda Time LocalDateTime instance using the LocalDateTimePattern
    #  - Format the equivalent BCL DateTime instance using `.ToString(string? format, IFormatProvider? provider)`
    #  - Assert that the output of those two operations is equal
    #  We obviously don't have the BCL in Python.
    #  We could get something similar using strftime(), but you have to `locale.setlocale(locale.LC_TIME, "...")`
    #  which sets the locale globally for the process, which seems undesirable in a test suite.
    #  Another option would be to test against something like arrow or babel, but relying on another
    #  3rd-party lib here seems potentially fraught with pain.
    #  We could test against PyICU's datetime formatting, but that isn't going to match the output of
    #  BCL DateTime formatting of Noda Time.
    #  The same applies for third-party libs which provide Python bindings for .NET.
    #  Probably the simplest way out of this would be to generate a list of formatted DateTime strings
    #  in a dotnet project, and feed those into the test as parameters...?
    #
    # @pytest.mark.parametrize("culture,pattern", ALL_CULTURES_STANDARD_PATTERNS, ids=lambda x: str(x))
    # def test_bcl_standard_pattern_comparison(self, culture: CultureInfo, pattern: str) -> None:
    #     pass

    @pytest.mark.parametrize("culture,pattern_text", ALL_CULTURES_STANDARD_PATTERNS, ids=lambda x: str(x))
    def test_parse_formatted_standard_pattern(self, culture: CultureInfo, pattern_text: str) -> None:
        pattern = self.__create_pattern_or_none(pattern_text, culture, LocalDateTime(2000, 1, 1, 0, 0))
        if pattern is None:
            return

        # If the pattern really can't distinguish between AM and PM (e.g. it's 12 hour with an
        # abbreviated AM/PM designator) then let's let it go.
        if pattern.format(SAMPLE_LOCAL_DATE_TIME) == pattern.format(SAMPLE_LOCAL_DATE_TIME.plus_hours(-12)):
            return

        # If the culture doesn't have either AM or PM designators, we'll end up using the template value
        # AM/PM, so let's make sure that's right. (This happens on Mono for a few cultures.)
        if culture.date_time_format.am_designator == culture.date_time_format.pm_designator == "":
            pattern = pattern.with_template_value(LocalDateTime(2000, 1, 1, 12, 0))

        formatted: str = pattern.format(SAMPLE_LOCAL_DATE_TIME)
        parse_result = pattern.parse(formatted)
        assert parse_result.success
        parsed = parse_result.value
        assert parsed in (
            SAMPLE_LOCAL_DATE_TIME,
            SAMPLE_LOCAL_DATE_TIME_TO_TICKS,
            SAMPLE_LOCAL_DATE_TIME_TO_MILLIS,
            SAMPLE_LOCAL_DATE_TIME_TO_SECONDS,
            SAMPLE_LOCAL_DATE_TIME_TO_MINUTES,
        )

    @pytest.mark.parametrize("text", ["1992-01-25T00", "-1000-12-31T23", "9999-12-31T05"])
    def test_date_hour_iso_roundtrip(self, text: str) -> None:
        result = LocalDateTimePattern.date_hour_iso.parse(text)
        assert result.success
        time = result.value
        assert time.minute == 0
        assert time.second == 0
        assert time.nanosecond_of_second == 0
        formatted = LocalDateTimePattern.date_hour_iso.format(time)
        assert formatted == text

    def test_date_hour_iso_2400(self) -> None:
        result = LocalDateTimePattern.date_hour_iso.parse("1992-01-25T24")
        assert result.success
        assert result.value == LocalDateTime(1992, 1, 26, 0, 0)

    @pytest.mark.parametrize(
        "text",
        [
            "10000-01-01T05",
            "1999-13-01T05",
            "1999-09-31T05",
            "1992-01-25T-05",
            "1992-01-25T05:00",
            "1992-01-25T5",
            "1992-01-25T99",
        ],
    )
    def test_date_hour_iso_invalid(self, text: str) -> None:
        result = LocalDateTimePattern.date_hour_iso.parse(text)
        assert not result.success

    @pytest.mark.parametrize(
        "text",
        [
            "1992-01-25T00:31",
            "1992-01-25T23:10",
        ],
    )
    def test_date_hour_minute_iso_roundtrip(self, text: str) -> None:
        result = LocalDateTimePattern.date_hour_minute_iso.parse(text)
        assert result.success
        time = result.value
        assert time.second == 0
        assert time.nanosecond_of_second == 0
        formatted = LocalDateTimePattern.date_hour_minute_iso.format(time)
        assert formatted == text

    def test_date_hour_minute_iso_2400(self) -> None:
        result = LocalDateTimePattern.date_hour_minute_iso.parse("1992-01-25T24:00")
        assert result.success
        assert result.value == LocalDateTime(1992, 1, 26, 0, 0)

    @pytest.mark.parametrize(
        "text",
        [
            "10000-01-01T05:00",
            "1999-13-01T05:00",
            "1999-09-31T05:00",
            "1992-01-25T-05:00",
            "1992-01-25T5:00",
            "1992-01-25T24:01",  # 24:00 is valid; covered above.
            "1992-01-25T99:00",
            "1992-01-25T10:60",
            "1992-01-25T10:70",
        ],
    )
    def test_date_hour_minute_iso_invalid(self, text: str) -> None:
        result = LocalDateTimePattern.date_hour_minute_iso.parse(text)
        assert not result.success

    @pytest.mark.parametrize(
        "canonical,alternatives",
        [
            ("03", ("03:00", "03:00:00")),
            ("12", ("12:00", "12:00:00", "12:00:00.000000", "12:00:00.000000000")),
            ("12:01", ("12:01:00", "12:01:00.000000")),
            ("12:00:01", ("12:00:01.000000",)),
            ("12:00:01.123", ("12:00:01.123000", "12:00:01.123000000")),
            ("12:00:01.123456789", tuple()),
        ],
    )
    def test_variable_precision_valid(self, canonical: str, alternatives: Iterable[str]) -> None:
        # Just use the same prefix for all values; it's only the time part that can vary in precision.
        prefix = "1992-01-25T"
        full_canonical = prefix + canonical

        pattern: IPattern[LocalDateTime] = LocalDateTimePattern.variable_precision_iso
        for text in (canonical, *alternatives):
            result = pattern.parse(prefix + text)
            assert result.success
            time = result.value
            formatted = pattern.format(time)
            assert formatted == full_canonical

    @pytest.mark.parametrize(
        "text",
        [
            "1992-01-25T24",
            "1992-01-25T24:00",
            "1992-01-25T24:00:00",
            "1992-01-25T24:00:00.000",
            "1992-01-25T24:00:00.000000000",
        ],
    )
    def test_variable_precision_2400(self, text: str) -> None:
        result = LocalDateTimePattern.variable_precision_iso.parse(text)
        assert result.success
        assert result.value == LocalDateTime(1992, 1, 26, 0, 0)

    @pytest.mark.parametrize(
        "text",
        [
            "1992-01-32",
            "10:00",
            "1992-01-32T10:00",
            "1992-13-25T10:00",
            "1992-01-25T25:61",
            "1992-01-25T12:23:45.0000000000",  # Too many fractional digits
            "1992-01-25T05:63",
            "1992-01-25T05:00:63",
        ],
    )
    def test_variable_precision_invalid(self, text: str) -> None:
        result = LocalDateTimePattern.variable_precision_iso.parse(text)
        assert not result.success

    @staticmethod
    def __create_pattern_or_none(
        pattern_text: str, culture: CultureInfo, template_value: LocalDateTime
    ) -> LocalDateTimePattern | None:
        try:
            return LocalDateTimePattern.create(pattern_text, culture)
        except InvalidPatternError:
            # The Malta long date/time pattern in Mono 3.0 is invalid
            # (not just wrong; invalid due to the wrong number of quotes).
            # Skip it :(
            # See https://bugzilla.xamarin.com/show_bug.cgi?id=11363
            return None
