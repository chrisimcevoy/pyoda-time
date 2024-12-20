# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from collections.abc import Sequence
from typing import Any, Final

import pytest
from _pytest.fixtures import FixtureRequest

from pyoda_time import LocalTime
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time.text import LocalTimePattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._pattern_cursor import _PatternCursor

from ..culture_saver import CultureSaver
from .cultures import Cultures
from .pattern_test_base import PatternTestBase
from .pattern_test_data import PatternTestData


def create_custom_am_pm_culture(am_designator: str, pm_designator: str) -> CultureInfo:
    clone: CultureInfo = CultureInfo.invariant_culture.clone()
    clone.date_time_format.am_designator = am_designator
    clone.date_time_format.pm_designator = pm_designator
    return CultureInfo.read_only(clone)


# Characters we expect to work the same in Noda Time as in the BCL.
EXPECTED_CHARACTERS: Final[str] = "hHms.:fFtT "

AM_ONLY_CULTURE: Final[CultureInfo] = create_custom_am_pm_culture("am", "")
PM_ONLY_CULTURE: Final[CultureInfo] = create_custom_am_pm_culture("", "pm")
NO_AM_OR_PM_CULTURE: Final[CultureInfo] = create_custom_am_pm_culture("", "")


class Data(PatternTestData[LocalTime]):
    @property
    def default_template(self) -> LocalTime:
        return LocalTime.midnight

    @property
    def value_pattern_text(self) -> str | None:
        return "HH:mm:ss.FFFFFFFFF"

    def __init__(
        self,
        value: LocalTime = LocalTime.midnight,
        text: str | None = None,
        pattern: str | None = None,
        message: str | None = None,
        parameters: list[Any] | None = None,
        culture: CultureInfo | None = CultureInfo.invariant_culture,
        template: LocalTime | None = None,
        standard_pattern: IPattern[LocalTime] | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(
            value=value,
            text=text,
            pattern=pattern,
            message=message,
            parameters=parameters,
            culture=culture or CultureInfo.invariant_culture,
            template=template,
            standard_pattern=standard_pattern,
            description=description,
        )

    def create_pattern(self) -> IPattern[LocalTime]:
        assert self.pattern is not None
        return (
            LocalTimePattern.create_with_invariant_culture(self.pattern)
            .with_template_value(self.template)
            .with_culture(self.culture)
        )


INVALID_PATTERN_DATA: Final[list[Data]] = [
    Data(pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(pattern="!", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["!", LocalTime.__name__]),
    Data(pattern="%", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["%", LocalTime.__name__]),
    Data(pattern="\\", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["\\", LocalTime.__name__]),
    Data(pattern="%%", message=_TextErrorMessages.PERCENT_DOUBLED),
    Data(pattern="%\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="ffffffffff", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["f", 9]),
    Data(pattern="FFFFFFFFFF", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["F", 9]),
    Data(pattern="H%", message=_TextErrorMessages.PERCENT_AT_END_OF_STRING),
    Data(pattern="HHH", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["H", 2]),
    Data(pattern="mmm", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["m", 2]),
    Data(pattern="mmmmmmmmmmmmmmmmmmm", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["m", 2]),
    Data(pattern="'qwe", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(pattern="'qwe\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="'qwe\\'", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(pattern="sss", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["s", 2]),
    # T isn't valid in a time pattern
    Data(pattern="1970-01-01THH:mm:ss", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["T"]),
]

PARSE_FAILURE_DATA: Final[list[Data]] = [
    Data(
        text="17 6",
        pattern="HH h",
        message=_TextErrorMessages.INCONSISTENT_VALUES_2,
        parameters=["H", "h", LocalTime.__name__],
    ),
    Data(
        text="17 AM",
        pattern="HH tt",
        message=_TextErrorMessages.INCONSISTENT_VALUES_2,
        parameters=["H", "t", LocalTime.__name__],
    ),
    Data(text="5 foo", pattern="h t", message=_TextErrorMessages.MISSING_AM_PM_DESIGNATOR),
    Data(text="04.", pattern="ss.FF", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["FF"]),
    Data(text="04.", pattern="ss;FF", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["FF"]),
    Data(text="04.", pattern="ss.ff", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["ff"]),
    Data(text="04.", pattern="ss;ff", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["ff"]),
    Data(text="04.x", pattern="ss.FF", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["FF"]),
    Data(text="04.x", pattern="ss;FF", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["FF"]),
    Data(text="04.x", pattern="ss.ff", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["ff"]),
    Data(text="04.x", pattern="ss;ff", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["ff"]),
    Data(text="05 foo", pattern="h t", message=_TextErrorMessages.MISSING_AM_PM_DESIGNATOR),
]

PARSE_ONLY_DATA: Final[list[Data]] = [
    Data(LocalTime(0, 0, 0, 400), text="4", pattern="%f"),
    Data(LocalTime(0, 0, 0, 400), text="4", pattern="%F"),
    Data(LocalTime(0, 0, 0, 400), text="4", pattern="FF"),
    Data(LocalTime(0, 0, 0, 400), text="40", pattern="FF"),
    Data(LocalTime(0, 0, 0, 400), text="4", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 400), text="40", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 400), text="400", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 400), text="40", pattern="ff"),
    Data(LocalTime(0, 0, 0, 400), text="400", pattern="fff"),
    Data(LocalTime(0, 0, 0, 400), text="4000", pattern="ffff"),
    Data(LocalTime(0, 0, 0, 400), text="40000", pattern="fffff"),
    Data(LocalTime(0, 0, 0, 400), text="400000", pattern="ffffff"),
    Data(LocalTime(0, 0, 0, 450), text="45", pattern="ff"),
    Data(LocalTime(0, 0, 0, 450), text="45", pattern="FF"),
    Data(LocalTime(0, 0, 0, 450), text="45", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 450), text="450", pattern="fff"),
    Data(LocalTime(0, 0, 0, 456), text="456", pattern="fff"),
    Data(LocalTime(0, 0, 0, 456), text="456", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 0), text="0", pattern="%f"),
    Data(LocalTime(0, 0, 0, 0), text="00", pattern="ff"),
    Data(LocalTime(0, 0, 0, 8), text="008", pattern="fff"),
    Data(LocalTime(0, 0, 0, 8), text="008", pattern="FFF"),
    Data(LocalTime(5, 0, 0, 0), text="05", pattern="HH"),
    Data(LocalTime(0, 6, 0, 0), text="06", pattern="mm"),
    Data(LocalTime(0, 0, 7, 0), text="07", pattern="ss"),
    Data(LocalTime(5, 0, 0, 0), text="5", pattern="%H"),
    Data(LocalTime(0, 6, 0, 0), text="6", pattern="%m"),
    Data(LocalTime(0, 0, 7, 0), text="7", pattern="%s"),
    # AM/PM designator is case-insensitive for both short and long forms
    Data(LocalTime(17, 0, 0, 0), text="5 p", pattern="h t"),
    Data(LocalTime(17, 0, 0, 0), text="5 pm", pattern="h tt"),
    # Parsing using the semi-colon "comma dot" specifier
    Data(LocalTime(16, 5, 20, 352), pattern="HH:mm:ss;fff", text="16:05:20,352"),
    Data(LocalTime(16, 5, 20, 352), pattern="HH:mm:ss;FFF", text="16:05:20,352"),
    # Empty fractional section
    Data(LocalTime(0, 0, 4, 0), text="04", pattern="ssFF"),
    Data(LocalTime(0, 0, 4, 0), text="040", pattern="ssFF"),
    Data(LocalTime(0, 0, 4, 0), text="040", pattern="ssFFF"),
    Data(LocalTime(0, 0, 4, 0), text="04", pattern="ss.FF"),
]

FORMAT_ONLY_DATA: Final[list[Data]] = [
    Data(LocalTime(5, 6, 7, 8), text="", pattern="%F"),
    Data(LocalTime(5, 6, 7, 8), text="", pattern="FF"),
    Data(LocalTime(1, 1, 1, 400), text="4", pattern="%f"),
    Data(LocalTime(1, 1, 1, 400), text="4", pattern="%F"),
    Data(LocalTime(1, 1, 1, 400), text="4", pattern="FF"),
    Data(LocalTime(1, 1, 1, 400), text="4", pattern="FFF"),
    Data(LocalTime(1, 1, 1, 400), text="40", pattern="ff"),
    Data(LocalTime(1, 1, 1, 400), text="400", pattern="fff"),
    Data(LocalTime(1, 1, 1, 400), text="4000", pattern="ffff"),
    Data(LocalTime(1, 1, 1, 400), text="40000", pattern="fffff"),
    Data(LocalTime(1, 1, 1, 400), text="400000", pattern="ffffff"),
    Data(LocalTime(1, 1, 1, 400), text="4000000", pattern="fffffff"),
    Data(LocalTime(1, 1, 1, 450), text="4", pattern="%f"),
    Data(LocalTime(1, 1, 1, 450), text="4", pattern="%F"),
    Data(LocalTime(1, 1, 1, 450), text="45", pattern="ff"),
    Data(LocalTime(1, 1, 1, 450), text="45", pattern="FF"),
    Data(LocalTime(1, 1, 1, 450), text="45", pattern="FFF"),
    Data(LocalTime(1, 1, 1, 450), text="450", pattern="fff"),
    Data(LocalTime(1, 1, 1, 456), text="4", pattern="%f"),
    Data(LocalTime(1, 1, 1, 456), text="4", pattern="%F"),
    Data(LocalTime(1, 1, 1, 456), text="45", pattern="ff"),
    Data(LocalTime(1, 1, 1, 456), text="45", pattern="FF"),
    Data(LocalTime(1, 1, 1, 456), text="456", pattern="fff"),
    Data(LocalTime(1, 1, 1, 456), text="456", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 0), text="", pattern="FF"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="0", pattern="%f"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="00", pattern="ff"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="008", pattern="fff"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="008", pattern="FFF"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="05", pattern="HH"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="06", pattern="mm"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="07", pattern="ss"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="5", pattern="%H"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="6", pattern="%m"),
    Data(LocalTime(5, 6, 7, 8), culture=Cultures.en_us, text="7", pattern="%s"),
    # The subminute values are truncated for the short pattern
    Data(LocalTime(14, 15, 16), culture=Cultures.dot_time_separator, text="14.15", pattern="t"),
    Data(LocalTime(14, 15, 16), culture=Cultures.invariant, text="14:15", pattern="t"),
]

# TODO: This seems to be unused in Noda Time (https://github.com/nodatime/nodatime/pull/1800)
DEFAULT_PATTERN_DATA: Final[list[Data]] = []

# TODO: This seems to be unused in Noda Time (https://github.com/nodatime/nodatime/pull/1800)
TEMPLATE_VALUE_DATA: Final[list[Data]] = []

FORMAT_AND_PARSE_DATA: Final[list[Data]] = [
    Data(LocalTime.midnight, culture=Cultures.en_us, text=".", pattern="%."),
    Data(LocalTime.midnight, culture=Cultures.en_us, text=":", pattern="%:"),
    Data(LocalTime.midnight, culture=Cultures.dot_time_separator, text=".", pattern="%."),
    Data(LocalTime.midnight, culture=Cultures.dot_time_separator, text=".", pattern="%:"),
    Data(LocalTime.midnight, culture=Cultures.en_us, text="H", pattern="\\H"),
    Data(LocalTime.midnight, culture=Cultures.en_us, text="HHss", pattern="'HHss'"),
    Data(LocalTime(0, 0, 0, 100), culture=Cultures.en_us, text="1", pattern="%f"),
    Data(LocalTime(0, 0, 0, 100), culture=Cultures.en_us, text="1", pattern="%F"),
    Data(LocalTime(0, 0, 0, 100), culture=Cultures.en_us, text="1", pattern="FF"),
    Data(LocalTime(0, 0, 0, 100), culture=Cultures.en_us, text="1", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 100), culture=Cultures.en_us, text="100000000", pattern="fffffffff"),
    Data(LocalTime(0, 0, 0, 100), culture=Cultures.en_us, text="1", pattern="FFFFFFFFF"),
    Data(LocalTime(0, 0, 0, 120), culture=Cultures.en_us, text="12", pattern="ff"),
    Data(LocalTime(0, 0, 0, 120), culture=Cultures.en_us, text="12", pattern="FF"),
    Data(LocalTime(0, 0, 0, 120), culture=Cultures.en_us, text="12", pattern="FFF"),
    Data(LocalTime(0, 0, 0, 123), culture=Cultures.en_us, text="123", pattern="fff"),
    Data(LocalTime(0, 0, 0, 123), culture=Cultures.en_us, text="123", pattern="FFF"),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4000),
        culture=Cultures.en_us,
        text="1234",
        pattern="ffff",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4000),
        culture=Cultures.en_us,
        text="1234",
        pattern="FFFF",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4500),
        culture=Cultures.en_us,
        text="12345",
        pattern="fffff",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4500),
        culture=Cultures.en_us,
        text="12345",
        pattern="FFFFF",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4560),
        culture=Cultures.en_us,
        text="123456",
        pattern="ffffff",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4560),
        culture=Cultures.en_us,
        text="123456",
        pattern="FFFFFF",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4567),
        culture=Cultures.en_us,
        text="1234567",
        pattern="fffffff",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(0, 0, 0, 123, 4567),
        culture=Cultures.en_us,
        text="1234567",
        pattern="FFFFFFF",
    ),
    Data(LocalTime(0, 0, 0).plus_nanoseconds(123456780), culture=Cultures.en_us, text="12345678", pattern="ffffffff"),
    Data(LocalTime(0, 0, 0).plus_nanoseconds(123456780), culture=Cultures.en_us, text="12345678", pattern="FFFFFFFF"),
    Data(LocalTime(0, 0, 0).plus_nanoseconds(123456789), culture=Cultures.en_us, text="123456789", pattern="fffffffff"),
    Data(LocalTime(0, 0, 0).plus_nanoseconds(123456789), culture=Cultures.en_us, text="123456789", pattern="FFFFFFFFF"),
    Data(LocalTime(0, 0, 0, 600), culture=Cultures.en_us, text=".6", pattern=".f"),
    Data(LocalTime(0, 0, 0, 600), culture=Cultures.en_us, text=".6", pattern=".F"),
    Data(LocalTime(0, 0, 0, 600), culture=Cultures.en_us, text=".6", pattern=".FFF"),  # Elided fraction
    Data(LocalTime(0, 0, 0, 678), culture=Cultures.en_us, text=".678", pattern=".fff"),
    Data(LocalTime(0, 0, 0, 678), culture=Cultures.en_us, text=".678", pattern=".FFF"),
    Data(LocalTime(0, 0, 12, 0), culture=Cultures.en_us, text="12", pattern="%s"),
    Data(LocalTime(0, 0, 12, 0), culture=Cultures.en_us, text="12", pattern="ss"),
    Data(LocalTime(0, 0, 2, 0), culture=Cultures.en_us, text="2", pattern="%s"),
    Data(LocalTime(0, 12, 0, 0), culture=Cultures.en_us, text="12", pattern="%m"),
    Data(LocalTime(0, 12, 0, 0), culture=Cultures.en_us, text="12", pattern="mm"),
    Data(LocalTime(0, 2, 0, 0), culture=Cultures.en_us, text="2", pattern="%m"),
    Data(LocalTime(1, 0, 0, 0), culture=Cultures.en_us, text="1", pattern="H.FFF"),  # Missing fraction
    Data(LocalTime(12, 0, 0, 0), culture=Cultures.en_us, text="12", pattern="%H"),
    Data(LocalTime(12, 0, 0, 0), culture=Cultures.en_us, text="12", pattern="HH"),
    Data(LocalTime(2, 0, 0, 0), culture=Cultures.en_us, text="2", pattern="%H"),
    Data(LocalTime(0, 0, 12, 340), culture=Cultures.en_us, text="12.34", pattern="ss.FFF"),
    # Standard patterns
    Data(LocalTime(14, 15, 16), culture=Cultures.en_us, text="14:15:16", pattern="r"),
    Data(LocalTime(14, 15, 16, 700), culture=Cultures.en_us, text="14:15:16.7", pattern="r"),
    Data(LocalTime(14, 15, 16, 780), culture=Cultures.en_us, text="14:15:16.78", pattern="r"),
    Data(LocalTime(14, 15, 16, 789), culture=Cultures.en_us, text="14:15:16.789", pattern="r"),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1000),
        culture=Cultures.en_us,
        text="14:15:16.7891",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1200),
        culture=Cultures.en_us,
        text="14:15:16.78912",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1230),
        culture=Cultures.en_us,
        text="14:15:16.789123",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1234),
        culture=Cultures.en_us,
        text="14:15:16.7891234",
        pattern="r",
    ),
    Data(LocalTime(14, 15, 16), culture=Cultures.dot_time_separator, text="14.15.16", pattern="r"),
    Data(LocalTime(14, 15, 16, 700), culture=Cultures.dot_time_separator, text="14.15.16.7", pattern="r"),
    Data(LocalTime(14, 15, 16, 780), culture=Cultures.dot_time_separator, text="14.15.16.78", pattern="r"),
    Data(LocalTime(14, 15, 16, 789), culture=Cultures.dot_time_separator, text="14.15.16.789", pattern="r"),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1000),
        culture=Cultures.dot_time_separator,
        text="14.15.16.7891",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1200),
        culture=Cultures.dot_time_separator,
        text="14.15.16.78912",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1230),
        culture=Cultures.dot_time_separator,
        text="14.15.16.789123",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(14, 15, 16, 789, 1234),
        culture=Cultures.dot_time_separator,
        text="14.15.16.7891234",
        pattern="r",
    ),
    Data(
        LocalTime.from_hour_minute_second_nanosecond(14, 15, 16, 789123456),
        culture=Cultures.dot_time_separator,
        text="14.15.16.789123456",
        pattern="r",
    ),
    Data(LocalTime(14, 15, 0), culture=Cultures.dot_time_separator, text="14.15", pattern="t"),
    Data(LocalTime(14, 15, 0), culture=Cultures.invariant, text="14:15", pattern="t"),
    Data(LocalTime(14, 15, 16), culture=Cultures.dot_time_separator, text="14.15.16", pattern="T"),
    Data(LocalTime(14, 15, 16), culture=Cultures.invariant, text="14:15:16", pattern="T"),
    Data(
        LocalTime(14, 15, 16, 789),
        standard_pattern=LocalTimePattern.extended_iso,
        culture=Cultures.dot_time_separator,
        text="14:15:16.789",
        pattern="o",
    ),
    Data(
        LocalTime(14, 15, 16, 789),
        standard_pattern=LocalTimePattern.extended_iso,
        culture=Cultures.en_us,
        text="14:15:16.789",
        pattern="o",
    ),
    Data(
        LocalTime(14, 15, 16),
        standard_pattern=LocalTimePattern.extended_iso,
        culture=Cultures.invariant,
        text="14:15:16",
        pattern="o",
    ),
    Data(
        LocalTime(14, 15, 16, 789),
        standard_pattern=LocalTimePattern.long_extended_iso,
        culture=Cultures.dot_time_separator,
        text="14:15:16.789000000",
        pattern="O",
    ),
    Data(
        LocalTime(14, 15, 16, 789),
        standard_pattern=LocalTimePattern.long_extended_iso,
        culture=Cultures.en_us,
        text="14:15:16.789000000",
        pattern="O",
    ),
    Data(
        LocalTime(14, 15, 16),
        standard_pattern=LocalTimePattern.long_extended_iso,
        culture=Cultures.invariant,
        text="14:15:16.000000000",
        pattern="O",
    ),
    Data(
        LocalTime(14, 15, 16),
        standard_pattern=LocalTimePattern.general_iso,
        culture=Cultures.invariant,
        text="14:15:16",
        pattern="HH:mm:ss",
    ),
    # ------------ Template value tests ----------
    # Mixtures of 12 and 24 hour times
    Data(LocalTime(18, 0, 0), culture=Cultures.en_us, text="18 6 PM", pattern="HH h tt"),
    Data(LocalTime(18, 0, 0), culture=Cultures.en_us, text="18 6", pattern="HH h"),
    Data(LocalTime(18, 0, 0), culture=Cultures.en_us, text="18 PM", pattern="HH tt"),
    Data(LocalTime(18, 0, 0), culture=Cultures.en_us, text="6 PM", pattern="h tt"),
    Data(LocalTime(6, 0, 0), culture=Cultures.en_us, text="6", pattern="%h"),
    Data(LocalTime(0, 0, 0), culture=Cultures.en_us, text="AM", pattern="tt"),
    Data(LocalTime(12, 0, 0), culture=Cultures.en_us, text="PM", pattern="tt"),
    Data(LocalTime(0, 0, 0), culture=Cultures.en_us, text="A", pattern="%t"),
    Data(LocalTime(12, 0, 0), culture=Cultures.en_us, text="P", pattern="%t"),
    # Pattern specifies nothing - template value is passed through
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(1, 2, 3, 4, 5),
        culture=Cultures.en_us,
        text="*",
        pattern="%*",
        template=LocalTime.from_hour_minute_second_millisecond_tick(1, 2, 3, 4, 5),
    ),
    # Tests for each individual field being propagated
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(1, 6, 7, 8, 9),
        culture=Cultures.en_us,
        text="06:07.0080009",
        pattern="mm:ss.FFFFFFF",
        template=LocalTime.from_hour_minute_second_millisecond_tick(1, 2, 3, 4, 5),
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(6, 2, 7, 8, 9),
        culture=Cultures.en_us,
        text="06:07.0080009",
        pattern="HH:ss.FFFFFFF",
        template=LocalTime.from_hour_minute_second_millisecond_tick(1, 2, 3, 4, 5),
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(6, 7, 3, 8, 9),
        culture=Cultures.en_us,
        text="06:07.0080009",
        pattern="HH:mm.FFFFFFF",
        template=LocalTime.from_hour_minute_second_millisecond_tick(1, 2, 3, 4, 5),
    ),
    Data(
        LocalTime.from_hour_minute_second_millisecond_tick(6, 7, 8, 4, 5),
        culture=Cultures.en_us,
        text="06:07:08",
        pattern="HH:mm:ss",
        template=LocalTime.from_hour_minute_second_millisecond_tick(1, 2, 3, 4, 5),
    ),
    # Hours are tricky because of the ways they can be specified
    Data(LocalTime(6, 2, 3), culture=Cultures.en_us, text="6", pattern="%h", template=LocalTime(1, 2, 3)),
    Data(LocalTime(18, 2, 3), culture=Cultures.en_us, text="6", pattern="%h", template=LocalTime(14, 2, 3)),
    Data(LocalTime(2, 2, 3), culture=Cultures.en_us, text="AM", pattern="tt", template=LocalTime(14, 2, 3)),
    Data(LocalTime(14, 2, 3), culture=Cultures.en_us, text="PM", pattern="tt", template=LocalTime(14, 2, 3)),
    Data(LocalTime(2, 2, 3), culture=Cultures.en_us, text="AM", pattern="tt", template=LocalTime(2, 2, 3)),
    Data(LocalTime(14, 2, 3), culture=Cultures.en_us, text="PM", pattern="tt", template=LocalTime(2, 2, 3)),
    Data(LocalTime(17, 2, 3), culture=Cultures.en_us, text="5 PM", pattern="h tt", template=LocalTime(1, 2, 3)),
    # --------------- end of template value tests ----------------------
    # Only one of the AM/PM designator is present. We should still be able to work out what is meant, by the presence
    # or absence of the non-empty one.
    Data(LocalTime(5, 0, 0), culture=AM_ONLY_CULTURE, text="5 am", pattern="h tt"),
    Data(LocalTime(15, 0, 0), culture=AM_ONLY_CULTURE, text="3 ", pattern="h tt", description="Implicit PM"),
    Data(LocalTime(5, 0, 0), culture=AM_ONLY_CULTURE, text="5 a", pattern="h t"),
    Data(LocalTime(15, 0, 0), culture=AM_ONLY_CULTURE, text="3 ", pattern="h t", description="Implicit PM"),
    Data(LocalTime(5, 0, 0), culture=PM_ONLY_CULTURE, text="5 ", pattern="h tt"),
    Data(LocalTime(15, 0, 0), culture=PM_ONLY_CULTURE, text="3 pm", pattern="h tt"),
    Data(LocalTime(5, 0, 0), culture=PM_ONLY_CULTURE, text="5 ", pattern="h t"),
    Data(LocalTime(15, 0, 0), culture=PM_ONLY_CULTURE, text="3 p", pattern="h t"),
    # AM / PM designators are both empty strings. The parsing side relies on the AM/PM value being correct on the
    # template value. (The template value is for the wrong actual hour, but in the right side of noon.)
    Data(LocalTime(5, 0, 0), culture=NO_AM_OR_PM_CULTURE, text="5 ", pattern="h tt", template=LocalTime(2, 0, 0)),
    Data(LocalTime(15, 0, 0), culture=NO_AM_OR_PM_CULTURE, text="3 ", pattern="h tt", template=LocalTime(14, 0, 0)),
    Data(LocalTime(5, 0, 0), culture=NO_AM_OR_PM_CULTURE, text="5 ", pattern="h t", template=LocalTime(2, 0, 0)),
    Data(LocalTime(15, 0, 0), culture=NO_AM_OR_PM_CULTURE, text="3 ", pattern="h t", template=LocalTime(14, 0, 0)),
    # Use of the semi-colon "comma dot" specifier
    Data(LocalTime(16, 5, 20, 352), pattern="HH:mm:ss;fff", text="16:05:20.352"),
    Data(LocalTime(16, 5, 20, 352), pattern="HH:mm:ss;FFF", text="16:05:20.352"),
    Data(LocalTime(16, 5, 20, 352), pattern="HH:mm:ss;FFF 'end'", text="16:05:20.352 end"),
    Data(LocalTime(16, 5, 20), pattern="HH:mm:ss;FFF 'end'", text="16:05:20 end"),
    # Check handling of F after non-period.
    Data(LocalTime(16, 5, 20, 352), pattern="HH:mm:ss'x'FFF", text="16:05:20x352"),
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


class TestLocalTimePattern(PatternTestBase[LocalTime]):
    def test_parse_null(self) -> None:
        self.assert_parse_null(LocalTimePattern.extended_iso)

    @pytest.mark.parametrize("culture", Cultures.all_cultures)
    def test_bcl_long_time_pattern_is_valid_noda_pattern(self, culture: CultureInfo) -> None:
        self.__assert_valid_noda_pattern(culture, culture.date_time_format.long_time_pattern)

    @pytest.mark.parametrize("culture", Cultures.all_cultures)
    def test_bcl_short_time_pattern_is_valid_noda_pattern(self, culture: CultureInfo) -> None:
        self.__assert_valid_noda_pattern(culture, culture.date_time_format.short_time_pattern)

    # TODO: [requires BCL]
    #  public void BclLongTimePatternGivesSameResultsInNoda(CultureInfo culture)
    #  public void BclShortTimePatternGivesSameResultsInNoda(CultureInfo culture)

    def test_create_with_invariant_culture_null_pattern_text(self) -> None:
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            LocalTimePattern.create_with_invariant_culture(None)  # type: ignore

    def test_create_null_format_info(self) -> None:
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            LocalTimePattern.create("HH", None)  # type: ignore

    def test_template_value_defaults_to_midnight(self) -> None:
        pattern = LocalTimePattern.create_with_invariant_culture("HH")
        assert pattern.template_value == LocalTime.midnight

    def test_create_with_current_culture(self) -> None:
        with CultureSaver.set_cultures(Cultures.dot_time_separator):
            pattern = LocalTimePattern.create_with_current_culture("HH:mm")
            text = pattern.format(LocalTime(13, 45))
            assert text == "13.45"

    def test_with_template_value_property_fetch(self) -> None:
        new_value = LocalTime(1, 23, 45)
        pattern = LocalTimePattern.create_with_invariant_culture("HH").with_template_value(new_value)
        assert pattern.template_value == new_value

    @pytest.mark.parametrize("text", ["00", "23", "05"])
    def test_hour_iso_roundtrip(self, text: str) -> None:
        result = LocalTimePattern.hour_iso.parse(text)
        assert result.success
        time = result.value
        assert time.minute == 0
        assert time.second == 0
        assert time.nanosecond_of_second == 0
        formatted = LocalTimePattern.hour_iso.format(time)
        assert formatted == text

    @pytest.mark.parametrize("text", ["-05", "05:00", "5", "24", "99"])
    def test_hour_iso_invalid(self, text: str) -> None:
        result = LocalTimePattern.hour_iso.parse(text)
        assert not result.success

    @pytest.mark.parametrize("text", ["00:31", "23:10"])
    def test_hour_minute_iso_roundtrip(self, text: str) -> None:
        result = LocalTimePattern.hour_minute_iso.parse(text)
        assert result.success
        time = result.value
        assert time.second == 0
        assert time.nanosecond_of_second == 0
        formatted = LocalTimePattern.hour_minute_iso.format(time)
        assert formatted == text

    @pytest.mark.parametrize("text", ["-05:00", "5:00", "24:00", "99:00", "10:60", "10:70"])
    def test_hour_minute_iso_invalid(self, text: str) -> None:
        result = LocalTimePattern.hour_minute_iso.parse(text)
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
    def test_variable_precision_valid(self, canonical: str, alternatives: Sequence[str]) -> None:
        pattern = LocalTimePattern.variable_precision_iso
        for text in (canonical, *alternatives):
            result = pattern.parse(text)
            assert result.success
            time = result.value
            formatted = pattern.format(time)
            assert formatted == canonical

    @pytest.mark.parametrize(
        "text",
        [
            "24:00",
            "24",
            "25",
            "25:61",
            "12:23:45.0000000000",  # Too many fractional digits
            "05:63",
            "05:00:63",
        ],
    )
    def test_variable_precision_invalid(self, text: str) -> None:
        result = LocalTimePattern.variable_precision_iso.parse(text)
        assert not result.success

    @classmethod
    def __assert_valid_noda_pattern(cls, culture: CultureInfo, pattern: str) -> None:
        cursor: _PatternCursor = _PatternCursor(pattern)
        while cursor.move_next():
            if cursor.current == "'":
                cursor.get_quoted_string("'")
            # We'll never do anything "special" with non-ascii characters anyway,
            # so we don't mind if they're not quoted.
            elif ord(cursor.current) < ord("\u0080"):
                assert (
                    cursor.current in EXPECTED_CHARACTERS
                ), f"Pattern '{pattern}' contains unquoted, unexpected characters"
        # Check that the pattern parses
        LocalTimePattern.create(pattern, culture)
