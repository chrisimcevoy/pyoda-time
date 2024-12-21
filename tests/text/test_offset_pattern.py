# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import TYPE_CHECKING

import pytest
from _pytest.fixtures import FixtureRequest

from pyoda_time import Offset
from pyoda_time.text import OffsetPattern
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages

from ..culture_saver import CultureSaver
from ..helpers import create_negative_offset, create_positive_offset
from .cultures import Cultures
from .pattern_test_base import PatternTestBase
from .pattern_test_data import PatternTestData

if TYPE_CHECKING:
    from pyoda_time._compatibility._culture_info import CultureInfo


class Data(PatternTestData[Offset]):
    @property
    def default_template(self) -> Offset:
        return Offset.zero

    def create_pattern(self) -> IPattern[Offset]:
        assert self.pattern is not None, "Must provide `pattern` for this test"
        return OffsetPattern.create_with_invariant_culture(self.pattern).with_culture(self.culture)

    def create_partial_pattern(self) -> _IPartialPattern[Offset]:
        assert self.pattern is not None, "Must provide `pattern` for this test"
        return OffsetPattern.create_with_invariant_culture(self.pattern).with_culture(self.culture)._underlying_pattern


FORMAT_ONLY_DATA = [
    Data(create_positive_offset(3, 0, 0), culture=Cultures.en_us, text="", pattern="%-"),
    # Losing information
    Data(create_positive_offset(5, 6, 7), culture=Cultures.en_us, text="05", pattern="HH"),
    Data(create_positive_offset(5, 6, 7), culture=Cultures.en_us, text="06", pattern="mm"),
    Data(create_positive_offset(5, 6, 7), culture=Cultures.en_us, text="07", pattern="ss"),
    Data(create_positive_offset(5, 6, 7), culture=Cultures.en_us, text="5", pattern="%H"),
    Data(create_positive_offset(5, 6, 7), culture=Cultures.en_us, text="6", pattern="%m"),
    Data(create_positive_offset(5, 6, 7), culture=Cultures.en_us, text="7", pattern="%s"),
    Data(Offset.max_value, culture=Cultures.en_us, text="+18", pattern="g"),
    Data(Offset.max_value, culture=Cultures.en_us, text="18", pattern="%H"),
    Data(Offset.max_value, culture=Cultures.en_us, text="0", pattern="%m"),
    Data(Offset.max_value, culture=Cultures.en_us, text="0", pattern="%s"),
    Data(Offset.max_value, culture=Cultures.en_us, text="m", pattern="\\m"),
    Data(Offset.max_value, culture=Cultures.en_us, text="m", pattern="'m'"),
    Data(Offset.max_value, culture=Cultures.en_us, text="mmmmmmmmmm", pattern="'mmmmmmmmmm'"),
    Data(Offset.max_value, culture=Cultures.en_us, text="z", pattern="'z'"),
    Data(Offset.max_value, culture=Cultures.en_us, text="zqw", pattern="'zqw'"),
    Data(create_negative_offset(3, 0, 0), culture=Cultures.en_us, text="-", pattern="%-"),
    Data(create_positive_offset(3, 0, 0), culture=Cultures.en_us, text="+", pattern="%+"),
    Data(create_negative_offset(3, 0, 0), culture=Cultures.en_us, text="-", pattern="%+"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+05", pattern="s"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+05:12", pattern="m"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+05:12:34", pattern="l"),
]

PARSE_ONLY_DATA = [
    Data(Offset.zero, culture=Cultures.en_us, text="*", pattern="%*"),
    Data(Offset.zero, culture=Cultures.en_us, text="zqw", pattern="'zqw'"),
    Data(Offset.zero, culture=Cultures.en_us, text="-", pattern="%-"),
    Data(Offset.zero, culture=Cultures.en_us, text="+", pattern="%+"),
    Data(Offset.zero, culture=Cultures.en_us, text="-", pattern="%+"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.en_us, text="+05", pattern="s"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.en_us, text="+05:12", pattern="m"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+05:12:34", pattern="l"),
    Data(Offset.zero, pattern="Z+HH:mm", text="+00:00"),  # Lenient when parsing Z-prefixed patterns.
]


INVALID_PATTERN_DATA = [
    Data(value=Offset.zero, pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(value=Offset.zero, pattern="%Z", message=_TextErrorMessages.EMPTY_ZPREFIXED_OFFSET_PATTERN),
    Data(value=Offset.zero, pattern="HH:mmZ", message=_TextErrorMessages.ZPREFIX_NOT_AT_START_OF_PATTERN),
    Data(value=Offset.zero, pattern="%%H", message=_TextErrorMessages.PERCENT_DOUBLED),
    Data(value=Offset.zero, pattern="HH:HH", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["H"]),
    Data(value=Offset.zero, pattern="mm:mm", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["m"]),
    Data(value=Offset.zero, pattern="ss:ss", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["s"]),
    Data(value=Offset.zero, pattern="+HH:-mm", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["-"]),
    Data(value=Offset.zero, pattern="-HH:+mm", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["+"]),
    Data(
        value=Offset.zero,
        pattern="!",
        message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT,
        parameters=["!", Offset.__name__],
    ),
    Data(
        value=Offset.zero,
        pattern="%",
        message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT,
        parameters=["%", Offset.__name__],
    ),
    Data(value=Offset.zero, pattern="%%", message=_TextErrorMessages.PERCENT_DOUBLED),
    Data(value=Offset.zero, pattern="%\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(
        value=Offset.zero,
        pattern="\\",
        message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT,
        parameters=["\\", Offset.__name__],
    ),
    Data(value=Offset.zero, pattern="H%", message=_TextErrorMessages.PERCENT_AT_END_OF_STRING),
    Data(
        value=Offset.zero,
        pattern="hh",
        message=_TextErrorMessages.HOUR12_PATTERN_NOT_SUPPORTED,
        parameters=[Offset.__name__],
    ),
    Data(value=Offset.zero, pattern="HHH", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["H", 2]),
    Data(value=Offset.zero, pattern="mmm", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["m", 2]),
    Data(
        value=Offset.zero,
        pattern="mmmmmmmmmmmmmmmmmmm",
        message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED,
        parameters=["m", 2],
    ),
    Data(value=Offset.zero, pattern="'qwe", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(value=Offset.zero, pattern="'qwe\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(value=Offset.zero, pattern="'qwe\\'", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(value=Offset.zero, pattern="sss", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["s", 2]),
]

PARSE_FAILURE_DATA = [
    Data(
        value=Offset.zero, culture=Cultures.en_us, text="", pattern="g", message=_TextErrorMessages.VALUE_STRING_EMPTY
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="1",
        pattern="HH",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["HH"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="1",
        pattern="mm",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["mm"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="1",
        pattern="ss",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["ss"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="12:34 ",
        pattern="HH:mm",
        message=_TextErrorMessages.EXTRA_VALUE_CHARACTERS,
        parameters=[" "],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="1a",
        pattern="H ",
        message=_TextErrorMessages.MISMATCHED_CHARACTER,
        parameters=[" "],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="2:",
        pattern="%H",
        message=_TextErrorMessages.EXTRA_VALUE_CHARACTERS,
        parameters=[":"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern="%.",
        message=_TextErrorMessages.MISMATCHED_CHARACTER,
        parameters=["."],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern="%:",
        message=_TextErrorMessages.TIME_SEPARATOR_MISMATCH,
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern="%H",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["H"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern="%m",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["m"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern="%s",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["s"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern=".H",
        message=_TextErrorMessages.MISMATCHED_CHARACTER,
        parameters=["."],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="a",
        pattern="\\'",
        message=_TextErrorMessages.ESCAPED_CHARACTER_MISMATCH,
        parameters=["'"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="axc",
        pattern="'abc'",
        message=_TextErrorMessages.QUOTED_STRING_MISMATCH,
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="z",
        pattern="%*",
        message=_TextErrorMessages.MISMATCHED_CHARACTER,
        parameters=["*"],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="24",
        pattern="HH",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[24, "H", Offset.__name__],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="60",
        pattern="mm",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[60, "m", Offset.__name__],
    ),
    Data(
        value=Offset.zero,
        culture=Cultures.en_us,
        text="60",
        pattern="ss",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[60, "s", Offset.__name__],
    ),
    Data(value=Offset.zero, text="+12", pattern="-HH", message=_TextErrorMessages.POSITIVE_SIGN_INVALID),
]

FORMAT_AND_PARSE_DATA = [
    Data(Offset.zero, culture=Cultures.en_us, text=".", pattern="%."),  # decimal separator
    Data(Offset.zero, culture=Cultures.en_us, text=":", pattern="%:"),  # date separator
    Data(Offset.zero, culture=Cultures.dot_time_separator, text=".", pattern="%."),  # decimal separator (always period)
    Data(Offset.zero, culture=Cultures.dot_time_separator, text=".", pattern="%:"),  # date separator
    Data(Offset.zero, culture=Cultures.en_us, text="H", pattern="\\H"),
    Data(Offset.zero, culture=Cultures.en_us, text="HHss", pattern="'HHss'"),
    Data(create_positive_offset(0, 0, 12), culture=Cultures.en_us, text="12", pattern="%s"),
    Data(create_positive_offset(0, 0, 12), culture=Cultures.en_us, text="12", pattern="ss"),
    Data(create_positive_offset(0, 0, 2), culture=Cultures.en_us, text="2", pattern="%s"),
    Data(create_positive_offset(0, 12, 0), culture=Cultures.en_us, text="12", pattern="%m"),
    Data(create_positive_offset(0, 12, 0), culture=Cultures.en_us, text="12", pattern="mm"),
    Data(create_positive_offset(0, 2, 0), culture=Cultures.en_us, text="2", pattern="%m"),
    Data(create_positive_offset(12, 0, 0), culture=Cultures.en_us, text="12", pattern="%H"),
    Data(create_positive_offset(12, 0, 0), culture=Cultures.en_us, text="12", pattern="HH"),
    Data(create_positive_offset(2, 0, 0), culture=Cultures.en_us, text="2", pattern="%H"),
    # Standard patterns with punctuation...
    Data(create_positive_offset(5, 0, 0), culture=Cultures.en_us, text="+05", pattern="G"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.en_us, text="+05:12", pattern="G"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+05:12:34", pattern="G"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.en_us, text="+05", pattern="g"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.en_us, text="+05:12", pattern="g"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+05:12:34", pattern="g"),
    Data(Offset.min_value, culture=Cultures.en_us, text="-18", pattern="g"),
    Data(Offset.zero, culture=Cultures.en_us, text="Z", pattern="G"),
    Data(Offset.zero, culture=Cultures.en_us, text="+00", pattern="g"),
    Data(Offset.zero, culture=Cultures.en_us, text="+00", pattern="s"),
    Data(Offset.zero, culture=Cultures.en_us, text="+00:00", pattern="m"),
    Data(Offset.zero, culture=Cultures.en_us, text="+00:00:00", pattern="l"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.fr_fr, text="+05", pattern="g"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.fr_fr, text="+05:12", pattern="g"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.fr_fr, text="+05:12:34", pattern="g"),
    Data(Offset.max_value, culture=Cultures.fr_fr, text="+18", pattern="g"),
    Data(Offset.min_value, culture=Cultures.fr_fr, text="-18", pattern="g"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.dot_time_separator, text="+05", pattern="g"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.dot_time_separator, text="+05.12", pattern="g"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.dot_time_separator, text="+05.12.34", pattern="g"),
    Data(Offset.max_value, culture=Cultures.dot_time_separator, text="+18", pattern="g"),
    Data(Offset.min_value, culture=Cultures.dot_time_separator, text="-18", pattern="g"),
    # Standard patterns without punctuation
    Data(create_positive_offset(5, 0, 0), culture=Cultures.en_us, text="+05", pattern="I"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.en_us, text="+0512", pattern="I"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+051234", pattern="I"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.en_us, text="+05", pattern="i"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.en_us, text="+0512", pattern="i"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.en_us, text="+051234", pattern="i"),
    Data(Offset.min_value, culture=Cultures.en_us, text="-18", pattern="i"),
    Data(Offset.zero, culture=Cultures.en_us, text="Z", pattern="I"),
    Data(Offset.zero, culture=Cultures.en_us, text="+00", pattern="i"),
    Data(Offset.zero, culture=Cultures.en_us, text="+00", pattern="S"),
    Data(Offset.zero, culture=Cultures.en_us, text="+0000", pattern="M"),
    Data(Offset.zero, culture=Cultures.en_us, text="+000000", pattern="L"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.fr_fr, text="+05", pattern="i"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.fr_fr, text="+0512", pattern="i"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.fr_fr, text="+051234", pattern="i"),
    Data(Offset.max_value, culture=Cultures.fr_fr, text="+18", pattern="i"),
    Data(Offset.min_value, culture=Cultures.fr_fr, text="-18", pattern="i"),
    Data(create_positive_offset(5, 0, 0), culture=Cultures.dot_time_separator, text="+05", pattern="i"),
    Data(create_positive_offset(5, 12, 0), culture=Cultures.dot_time_separator, text="+0512", pattern="i"),
    Data(create_positive_offset(5, 12, 34), culture=Cultures.dot_time_separator, text="+051234", pattern="i"),
    Data(Offset.max_value, culture=Cultures.dot_time_separator, text="+18", pattern="i"),
    Data(Offset.min_value, culture=Cultures.dot_time_separator, text="-18", pattern="i"),
    # Explicit patterns
    Data(create_negative_offset(0, 30, 0), culture=Cultures.en_us, text="-00:30", pattern="+HH:mm"),
    Data(create_negative_offset(0, 30, 0), culture=Cultures.en_us, text="-00:30", pattern="-HH:mm"),
    Data(create_positive_offset(0, 30, 0), culture=Cultures.en_us, text="00:30", pattern="-HH:mm"),
    # Z-prefixes
    Data(Offset.zero, text="Z", pattern="Z+HH:mm:ss"),
    Data(create_positive_offset(5, 12, 34), text="+05:12:34", pattern="Z+HH:mm:ss"),
    Data(create_positive_offset(5, 12, 0), text="+05:12", pattern="Z+HH:mm"),
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


class TestOffsetPattern(PatternTestBase[Offset]):
    @pytest.mark.parametrize("data", PARSE_DATA)
    def test_parse_partial(self, data: PatternTestData[Offset]) -> None:
        data.test_parse_partial()

    def test_parse_null(self) -> None:
        self.assert_parse_null(OffsetPattern.general_invariant)

    def test_number_format_ignored(self) -> None:
        culture: CultureInfo = Cultures.en_us.clone()
        culture.number_format.positive_sign = "P"
        culture.number_format.negative_sign = "N"
        pattern = OffsetPattern.create("+HH:mm", culture)

        assert pattern.format(Offset.from_hours(5)) == "+05:00"
        assert pattern.format(Offset.from_hours(-5)) == "-05:00"

    def test_create_with_current_culture(self) -> None:
        with CultureSaver.set_cultures(Cultures.dot_time_separator):
            pattern = OffsetPattern.create_with_current_culture("H:mm")
            text = pattern.format(Offset.from_hours_and_minutes(1, 30))
            assert text == "1.30"
