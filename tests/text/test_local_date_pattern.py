# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Any, Final

import pytest
from _pytest.fixtures import FixtureRequest

from pyoda_time import CalendarSystem, LocalDate
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time.text import LocalDatePattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.utility._csharp_compatibility import _CsharpConstants

from ..culture_saver import CultureSaver
from .cultures import Cultures
from .pattern_test_base import PatternTestBase
from .pattern_test_data import PatternTestData


class Data(PatternTestData[LocalDate]):
    @property
    def default_template(self) -> LocalDate:
        # Default to the start of the year 2000.
        return LocalDatePattern._DEFAULT_TEMPLATE_VALUE

    def __init__(
        self,
        *,
        value: LocalDate = LocalDatePattern._DEFAULT_TEMPLATE_VALUE,
        text: str | None = None,
        pattern: str | None = None,
        message: str | None = None,
        parameters: list[Any] | None = None,
        culture: CultureInfo | None = CultureInfo.invariant_culture,
        template: LocalDate | None = None,
        standard_pattern: IPattern[LocalDate] | None = None,
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

    def create_pattern(self) -> IPattern[LocalDate]:
        assert self.pattern is not None
        return (
            LocalDatePattern.create_with_invariant_culture(self.pattern)
            .with_template_value(self.template)
            .with_culture(self.culture)
        )


SAMPLE_LOCAL_DATE: Final[LocalDate] = LocalDate(year=1976, month=6, day=19)

INVALID_PATTERN_DATA: list[Data] = [
    Data(pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(pattern="!", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["!", LocalDate.__name__]),
    Data(pattern="%", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["%", LocalDate.__name__]),
    Data(pattern="\\", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["\\", LocalDate.__name__]),
    Data(pattern="%%", message=_TextErrorMessages.PERCENT_DOUBLED),
    Data(pattern="%\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="MMMMM", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["M", 4]),
    Data(pattern="ddddd", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["d", 4]),
    Data(pattern="M%", message=_TextErrorMessages.PERCENT_AT_END_OF_STRING),
    Data(pattern="yyyyy", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["y", 4]),
    Data(pattern="uuuuu", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["u", 4]),
    Data(pattern="ggg", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["g", 2]),
    Data(pattern="'qwe", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(pattern="'qwe\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="'qwe\\'", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    # Note incorrect use of "u" (year) instead of "y" (year of era)
    Data(pattern="dd MM uuuu gg", message=_TextErrorMessages.ERA_WITHOUT_YEAR_OF_ERA),
    # Era specifier and calendar specifier in the same pattern.
    Data(pattern="dd MM yyyy gg c", message=_TextErrorMessages.CALENDAR_AND_ERA),
    # Invalid patterns directly after the uuuu specifier. This will detect the issue early, but then
    # continue and reject it in the normal path.
    Data(pattern="uuuu'", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(pattern="uuuu\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    # Common typo, which is caught in 2.0...
    Data(pattern="uuuu-mm-dd", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["m"]),
    # T isn't valid in a date pattern
    Data(pattern="uuuu-MM-ddT00:00:00", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["T"]),
    # These became invalid in v2.0, when we decided that y and yyy weren't sensible.
    Data(pattern="y M d", message=_TextErrorMessages.INVALID_REPEAT_COUNT, parameters=["y", 1]),
    Data(pattern="yyy M d", message=_TextErrorMessages.INVALID_REPEAT_COUNT, parameters=["y", 3]),
]

PARSE_FAILURE_DATA: list[Data] = [
    Data(pattern="yyyy gg", text="2011 PyodaEra", message=_TextErrorMessages.MISMATCHED_TEXT, parameters=["g"]),
    Data(
        pattern="yyyy uuuu gg",
        text="0010 0009 B.C.",
        message=_TextErrorMessages.INCONSISTENT_VALUES_2,
        parameters=["g", "u", LocalDate.__name__],
    ),
    Data(
        pattern="uuuu MM dd dddd",
        text="2011 10 09 Saturday",
        message=_TextErrorMessages.INCONSISTENT_DAY_OF_WEEK_TEXT_VALUE,
    ),
    Data(
        pattern="uuuu MM dd ddd", text="2011 10 09 Sat", message=_TextErrorMessages.INCONSISTENT_DAY_OF_WEEK_TEXT_VALUE
    ),
    Data(
        pattern="uuuu MM dd MMMM", text="2011 10 09 January", message=_TextErrorMessages.INCONSISTENT_MONTH_TEXT_VALUE
    ),
    Data(
        pattern="uuuu MM dd ddd", text="2011 10 09 FooBar", message=_TextErrorMessages.MISMATCHED_TEXT, parameters=["d"]
    ),
    Data(
        pattern="uuuu MM dd dddd",
        text="2011 10 09 FooBar",
        message=_TextErrorMessages.MISMATCHED_TEXT,
        parameters=["d"],
    ),
    Data(pattern="uuuu/MM/dd", text="2011/02-29", message=_TextErrorMessages.DATE_SEPARATOR_MISMATCH),
    # Don't match a short name against a long pattern
    Data(pattern="uuuu MMMM dd", text="2011 Oct 09", message=_TextErrorMessages.MISMATCHED_TEXT, parameters=["M"]),
    # Or vice versa... although this time we match the "Oct" and then fail as we're expecting a space
    Data(
        pattern="uuuu MMM dd", text="2011 October 09", message=_TextErrorMessages.MISMATCHED_CHARACTER, parameters=[" "]
    ),
    # Invalid month even when we've got genitive and non-genitive names to pick from
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMMM",
        text="BogusName",
        culture=Cultures._genitive_name_test_culture,
        message=_TextErrorMessages.MISMATCHED_TEXT,
        parameters=["M"],
    ),
    # Invalid year-of-era, month, day
    Data(
        pattern="yyyy MM dd",
        text="0000 01 01",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[0, "y", LocalDate.__name__],
    ),
    Data(
        pattern="yyyy MM dd",
        text="2011 15 29",
        message=_TextErrorMessages.MONTH_OUT_OF_RANGE,
        parameters=[15, 2011],
    ),
    Data(
        pattern="yyyy MM dd",
        text="2011 02 35",
        message=_TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE,
        parameters=[35, 2, 2011],
    ),
    # Year of era can't be negative...
    Data(
        pattern="yyyy MM dd",
        text="-15 01 01",
        message=_TextErrorMessages.UNEXPECTED_NEGATIVE,
    ),
    # Invalid leap years
    Data(
        pattern="uuuu MM dd",
        text="2011 02 29",
        message=_TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE,
        parameters=[29, 2, 2011],
    ),
    Data(
        pattern="uuuu MM dd",
        text="1900 02 29",
        message=_TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE,
        parameters=[29, 2, 1900],
    ),
    # Year of era and two-digit year, but they don't match
    Data(
        pattern="yyyy uu",
        text="2011 10",
        message=_TextErrorMessages.INCONSISTENT_VALUES_2,
        parameters=["y", "u", LocalDate.__name__],
    ),
    # Invalid calendar name
    Data(
        pattern="c uuuu MM dd",
        text="2015 01 01",
        message=_TextErrorMessages.NO_MATCHING_CALENDAR_SYSTEM,
    ),
    # Invalid year
    Data(
        template=LocalDate(year=1, month=1, day=1, calendar=CalendarSystem.islamic_bcl),
        pattern="uuuu",
        text="9999",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[9999, "u", LocalDate.__name__],
    ),
    Data(
        template=LocalDate(year=1, month=1, day=1, calendar=CalendarSystem.islamic_bcl),
        pattern="yyyy",
        text="9999",
        message=_TextErrorMessages.YEAR_OF_ERA_OUT_OF_RANGE,
        parameters=[9999, "EH", "Hijri"],
    ),
    # https://github.com/nodatime/nodatime/issues/414
    Data(
        pattern="yyyy-MM-dd",
        text="1984-00-15",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[0, "M", LocalDate.__name__],
    ),
    Data(
        pattern="M/d/yyyy",
        text="00/15/1984",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[0, "M", LocalDate.__name__],
    ),
    # Calendar ID parsing is now ordinal, case-sensitive
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MM dd c",
        text="2011 10 19 iso",
        message=_TextErrorMessages.NO_MATCHING_CALENDAR_SYSTEM,
    ),
]

PARSE_ONLY_DATA: list[Data] = [
    # Alternative era names
    Data(
        value=LocalDate(year=0, month=10, day=3),
        pattern="yyyy MM dd gg",
        text="0001 10 03 BCE",
    ),
    # Valid leap years
    Data(
        value=LocalDate(year=2000, month=2, day=29),
        pattern="uuuu MM dd",
        text="2000 02 29",
    ),
    Data(
        value=LocalDate(year=2004, month=2, day=29),
        pattern="uuuu MM dd",
        text="2004 02 29",
    ),
    # Month parsing should be case-insensitive
    Data(
        value=LocalDate(year=2011, month=10, day=3),
        pattern="uuuu MMM dd",
        text="2011 OcT 03",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=3),
        pattern="uuuu MMMM dd",
        text="2011 OcToBeR 03",
    ),
    # Day-of-week parsing should be case-insensitive
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MM dd ddd",
        text="2011 10 09 sUN",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MM dd dddd",
        text="2011 10 09 SuNDaY",
    ),
    # Genitive name is an extension of the non-genitive name; parse longer first.
    Data(
        value=LocalDate(year=2011, month=1, day=10),
        pattern="uuuu MMMM dd",
        text="2011 MonthName-Genitive 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=10),
        pattern="uuuu MMMM dd",
        text="2011 MonthName 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=10),
        pattern="uuuu MMM dd",
        text="2011 MN-Gen 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=10),
        pattern="uuuu MMM dd",
        text="2011 MN 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
]

FORMAT_ONLY_DATA: list[Data] = [
    # Would parse back to 2011
    Data(
        value=LocalDate(year=1811, month=7, day=3),
        pattern="yy M d",
        text="11 7 3",
    ),
    # Tests for the documented 2-digit formatting of BC years
    # (Less of an issue since yy became "year of era")
    Data(
        value=LocalDate(year=-94, month=7, day=3),
        pattern="yy M d",
        text="95 7 3",
    ),
    Data(
        value=LocalDate(year=-93, month=7, day=3),
        pattern="yy M d",
        text="94 7 3",
    ),
]

FORMAT_AND_PARSE_DATA: list[Data] = [
    # Standard patterns
    # Invariant culture uses the crazy MM/dd/yyyy format. Blech.
    Data(
        value=LocalDate(year=2011, month=10, day=20),
        pattern="d",
        text="10/20/2011",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=20),
        pattern="D",
        text="Thursday, 20 October 2011",
    ),
    # Year comes from the template
    Data(
        value=LocalDate(year=2000, month=10, day=20),
        pattern="M",
        text="October 20",
    ),
    # ISO pattern uses a sensible format
    Data(
        value=LocalDate(year=2011, month=10, day=20),
        standard_pattern=LocalDatePattern.iso,
        pattern="R",
        text="2011-10-20",
    ),
    # Round trip with calendar system
    Data(
        value=LocalDate(year=2011, month=10, day=20, calendar=CalendarSystem.coptic),
        standard_pattern=LocalDatePattern.full_roundtrip,
        pattern="r",
        text="2011-10-20 (Coptic)",
    ),
    # Custom patterns
    Data(
        value=LocalDate(year=2011, month=10, day=3),
        pattern="uuuu/MM/dd",
        text="2011/10/03",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=3),
        pattern="uuuu/MM/dd",
        text="2011-10-03",
        culture=Cultures.fr_ca,
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=3),
        pattern="uuuuMMdd",
        text="20111003",
    ),
    # 2-digit year-of-era patterns
    Data(
        value=LocalDate(year=2001, month=7, day=3),
        pattern="yy M d",
        text="01 7 3",
    ),
    Data(
        value=LocalDate(year=2011, month=7, day=3),
        pattern="yy M d",
        text="11 7 3",
    ),
    Data(
        value=LocalDate(year=2030, month=7, day=3),
        pattern="yy M d",
        text="30 7 3",
    ),
    # Cutoff defaults to 30 (at the moment...)
    Data(
        value=LocalDate(year=1931, month=7, day=3),
        pattern="yy M d",
        text="31 7 3",
    ),
    Data(
        value=LocalDate(year=1976, month=7, day=3),
        pattern="yy M d",
        text="76 7 3",
    ),
    # In the first century, we don't skip back a century for "high" two-digit year numbers.
    Data(
        value=LocalDate(year=25, month=7, day=3),
        pattern="uu M d",
        text="25 7 3",
        template=LocalDate(year=50, month=1, day=1),
    ),
    Data(
        value=LocalDate(year=35, month=7, day=3),
        pattern="uu M d",
        text="35 7 3",
        template=LocalDate(year=50, month=1, day=1),
    ),
    Data(
        value=LocalDate(year=2000, month=10, day=3),
        pattern="MM/dd",
        text="10/03",
    ),
    Data(
        value=LocalDate(year=1885, month=10, day=3),
        pattern="MM/dd",
        text="10/03",
        template=LocalDate(year=1885, month=10, day=1),
    ),
    # When we parse in all of the below tests, we'll use the month and day-of-month if it's provided;
    # the template value is specified to allow simple roundtripping.
    # (Day of week doesn't affect what value is parsed; it just validates.)
    # Non-genitive month name when there's no "day of month", even if there's a "day of week"
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMMM",
        text="FullNonGenName",
        culture=Cultures._genitive_name_test_culture,
        template=LocalDate(year=2011, month=5, day=3),
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMMM dddd",
        text="FullNonGenName Monday",
        culture=Cultures._genitive_name_test_culture,
        template=LocalDate(year=2011, month=5, day=3),
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMM",
        text="AbbrNonGenName",
        culture=Cultures._genitive_name_test_culture,
        template=LocalDate(year=2011, month=5, day=3),
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMM ddd",
        text="AbbrNonGenName Mon",
        culture=Cultures._genitive_name_test_culture,
        template=LocalDate(year=2011, month=5, day=3),
    ),
    # Genitive month name when the pattern includes "day of month"
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMMM dd",
        text="FullGenName 03",
        culture=Cultures._genitive_name_test_culture,
        template=LocalDate(year=2011, month=5, day=3),
    ),
    # TODO: Check whether or not this is actually appropriate
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="MMM dd",
        text="AbbrGenName 03",
        culture=Cultures._genitive_name_test_culture,
        template=LocalDate(year=2011, month=5, day=3),
    ),
    # Era handling
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="yyyy MM dd gg",
        text="2011 01 03 A.D.",
    ),
    Data(
        value=LocalDate(year=2011, month=1, day=3),
        pattern="uuuu yyyy MM dd gg",
        text="2011 2011 01 03 A.D.",
    ),
    Data(
        value=LocalDate(year=-1, month=1, day=3),
        pattern="yyyy MM dd gg",
        text="0002 01 03 B.C.",
    ),
    # Day of week handling
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MM dd dddd",
        text="2011 10 09 Sunday",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MM dd ddd",
        text="2011 10 09 Sun",
    ),
    # Month handling
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MMMM dd",
        text="2011 October 09",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MMM dd",
        text="2011 Oct 09",
    ),
    # Year and two-digit year-of-era in the same format. Note that the year
    # gives the full year information, so we're not stuck in the 20th/21st century
    Data(
        value=LocalDate(year=1825, month=10, day=9),
        pattern="uuuu yy MM/dd",
        text="1825 25 10/09",
    ),
    # Negative years
    Data(
        value=LocalDate(year=-43, month=3, day=15),
        pattern="uuuu MM dd",
        text="-0043 03 15",
    ),
    # Calendar handling
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="c uuuu MM dd",
        text="ISO 2011 10 09",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=9),
        pattern="uuuu MM dd c",
        text="2011 10 09 ISO",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=9, calendar=CalendarSystem.coptic),
        pattern="c uuuu MM dd",
        text="Coptic 2011 10 09",
    ),
    Data(
        value=LocalDate(year=2011, month=10, day=9, calendar=CalendarSystem.coptic),
        pattern="uuuu MM dd c",
        text="2011 10 09 Coptic",
    ),
    Data(
        value=LocalDate(year=180, month=15, day=19, calendar=CalendarSystem.badi),
        pattern="uuuu MM dd c",
        text="0180 15 19 Badi",
    ),
    # Awkward day-of-week handling
    # December 14th 2012 was a Friday. Friday is "Foo" or "FooBar" in AwkwardDayOfWeekCulture.
    Data(
        value=LocalDate(year=2012, month=12, day=14),
        pattern="ddd uuuu MM dd",
        text="Foo 2012 12 14",
        culture=Cultures._awkward_day_of_week_culture,
    ),
    Data(
        value=LocalDate(year=2012, month=12, day=14),
        pattern="dddd uuuu MM dd",
        text="FooBar 2012 12 14",
        culture=Cultures._awkward_day_of_week_culture,
    ),
    # December 13th 2012 was a Thursday. Friday is "FooBaz" or "FooBa" in AwkwardDayOfWeekCulture.
    Data(
        value=LocalDate(year=2012, month=12, day=13),
        pattern="ddd uuuu MM dd",
        text="FooBaz 2012 12 13",
        culture=Cultures._awkward_day_of_week_culture,
    ),
    Data(
        value=LocalDate(year=2012, month=12, day=13),
        pattern="dddd uuuu MM dd",
        text="FooBa 2012 12 13",
        culture=Cultures._awkward_day_of_week_culture,
    ),
    # 3 digit year patterns (odd, but valid)
    Data(
        value=LocalDate(year=12, month=1, day=2),
        pattern="uuu MM dd",
        text="012 01 02",
    ),
    Data(
        value=LocalDate(year=-12, month=1, day=2),
        pattern="uuu MM dd",
        text="-012 01 02",
    ),
    Data(
        value=LocalDate(year=123, month=1, day=2),
        pattern="uuu MM dd",
        text="123 01 02",
    ),
    Data(
        value=LocalDate(year=-123, month=1, day=2),
        pattern="uuu MM dd",
        text="-123 01 02",
    ),
    Data(
        value=LocalDate(year=1234, month=1, day=2),
        pattern="uuu MM dd",
        text="1234 01 02",
    ),
    Data(
        value=LocalDate(year=-1234, month=1, day=2),
        pattern="uuu MM dd",
        text="-1234 01 02",
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


class TestLocalDatePattern(PatternTestBase[LocalDate]):
    # TODO:
    #  public void BclLongDatePatternGivesSameResultsInNoda(CultureInfo culture)
    #  public void BclShortDatePatternGivesSameResultsInNoda(CultureInfo culture)

    def test_create_with_current_culture(self) -> None:
        date = LocalDate(year=2017, month=8, day=23)
        with CultureSaver.set_cultures(Cultures.fr_fr):
            pattern = LocalDatePattern.create_with_current_culture("d")
            assert pattern.format(date) == "23/08/2017"
        with CultureSaver.set_cultures(Cultures.fr_ca):
            pattern = LocalDatePattern.create_with_current_culture("d")
            assert pattern.format(date) == "2017-08-23"

    def test_parse_null(self) -> None:
        self.assert_parse_null(LocalDatePattern.iso)

    @pytest.mark.parametrize(
        "two_digit_year_max,text,expected_year",
        [
            (0, "00-01-01", 2000),
            (0, "01-01-01", 1901),
            (50, "49-01-01", 2049),
            (50, "50-01-01", 2050),
            (50, "51-01-01", 1951),
            (99, "00-01-01", 2000),
            (99, "99-01-01", 2099),
        ],
    )
    def test_with_two_digit_year_max(self, two_digit_year_max: int, text: str, expected_year: int) -> None:
        pattern = LocalDatePattern.create_with_invariant_culture("yy-MM-dd").with_two_digit_year_max(two_digit_year_max)
        value = pattern.parse(text).value
        assert value.year == expected_year

    @pytest.mark.parametrize(
        "two_digit_year_max", [-1, 100, _CsharpConstants.INT_MIN_VALUE, _CsharpConstants.INT_MAX_VALUE]
    )
    def test_with_two_digit_year_max_invalid(self, two_digit_year_max: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDatePattern.iso.with_two_digit_year_max(two_digit_year_max)
