# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest

from pyoda_time import Duration, Instant, PyodaConstants
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._instant_pattern import InstantPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.utility._csharp_compatibility import _CsharpConstants, _sealed

from ..culture_saver import CultureSaver
from .cultures import Cultures
from .pattern_test_base import PatternTestBase
from .pattern_test_data import PatternTestData


@_sealed
class Data(PatternTestData[Instant]):
    """A container for test data for formatting and parsing ``Instant`` objects."""

    @property
    def default_template(self) -> Instant:
        return PyodaConstants.UNIX_EPOCH

    def __init__(
        self,
        *,
        value: Instant = PyodaConstants.UNIX_EPOCH,
        culture: CultureInfo = CultureInfo.invariant_culture,
        standard_pattern: IPattern[Instant] | None = None,
        pattern: str | None = None,
        text: str | None = None,
        template: Instant | None = None,
        description: str | None = None,
        message: str | None = None,
        parameters: list[Any] | None = None,
    ) -> None:
        super().__init__(
            value=value,
            culture=culture,
            standard_pattern=standard_pattern,
            pattern=pattern,
            text=text,
            template=template,
            description=description,
            message=message,
            parameters=parameters,
        )

    def create_pattern(self) -> IPattern[Instant]:
        assert self.pattern is not None
        return (
            InstantPattern.create_with_invariant_culture(self.pattern)
            .with_template_value(self.template)
            .with_culture(self.culture)
        )


INVALID_PATTERN_DATA: list[Data] = [
    Data(pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(pattern="!", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["!", "Instant"]),
    Data(pattern="%", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["%", "Instant"]),
    Data(pattern="\\", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["\\", "Instant"]),
    # Just a few - these are taken from other tests
    Data(pattern="%%", message=_TextErrorMessages.PERCENT_DOUBLED),
    Data(pattern="%\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="ffffffffff", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["f", 9]),
    Data(pattern="FFFFFFFFFF", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["F", 9]),
]

PARSE_FAILURE_DATA: list[Data] = [
    Data(
        text="rubbish", pattern="uuuuMMdd'T'HH:mm:ss", message=_TextErrorMessages.MISMATCHED_NUMBER, parameters=["uuuu"]
    ),
    Data(
        text="17 6",
        pattern="HH h",
        message=_TextErrorMessages.INCONSISTENT_VALUES_2,
        parameters=["H", "h", "LocalDateTime"],
    ),
    Data(
        text="17 AM",
        pattern="HH tt",
        message=_TextErrorMessages.INCONSISTENT_VALUES_2,
        parameters=["H", "t", "LocalDateTime"],
    ),
]

# PARSE_ONLY_DATA is also empty in Noda Time...
PARSE_ONLY_DATA: list[Data] = []

FORMAT_ONLY_DATA: list[Data] = [
    # Custom template with "wrong" year; this won't roundtrip
    Data(
        value=Instant.from_utc(1970, 6, 19, 12, 0, 0),
        template=Instant.from_utc(1950, 1, 1, 0, 0),
        text="06-19 12:00",
        pattern="MM-dd HH:mm",
    )
]

# Common test data for both formatting and parsing. A test should be placed here unless is truly
# cannot be run both ways. This ensures that as many round-trip type tests are performed as possible.
FORMAT_AND_PARSE_DATA: list[Data] = [
    Data(value=Instant.from_utc(2012, 1, 31, 17, 36, 45), text="2012-01-31T17:36:45", pattern="uuuu-MM-dd'T'HH:mm:ss"),
    # Check that unquoted T still works.
    Data(value=Instant.from_utc(2012, 1, 31, 17, 36, 45), text="2012-01-31T17:36:45", pattern="uuuu-MM-ddTHH:mm:ss"),
    Data(
        value=Instant.from_utc(2012, 4, 28, 0, 0, 0), text="2012 avr. 28", pattern="uuuu MMM dd", culture=Cultures.fr_fr
    ),
    Data(text=" 1970 ", pattern=" uuuu "),
    Data(value=Instant.min_value, text="-9998-01-01T00:00:00Z", pattern="uuuu-MM-dd'T'HH:mm:ss.FFFFFFFFF'Z'"),
    Data(value=Instant.max_value, text="9999-12-31T23:59:59.999999999Z", pattern="uuuu-MM-dd'T'HH:mm:ss.FFFFFFFFF'Z'"),
    # General pattern has no standard single character.
    Data(
        value=Instant.from_utc(2012, 1, 31, 17, 36, 45),
        standard_pattern=InstantPattern.general,
        text="2012-01-31T17:36:45Z",
        pattern="uuuu-MM-ddTHH:mm:ss'Z'",
    ),
    # Custom template
    Data(
        value=Instant.from_utc(1950, 6, 19, 12, 0, 0),
        template=Instant.from_utc(1950, 1, 1, 0, 0),
        text="06-19 12:00",
        pattern="MM-dd HH:mm",
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


class TestInstantPattern(PatternTestBase[Instant]):
    def test_iso_handles_commas(self) -> None:
        expected = Instant.from_utc(2012, 1, 1, 0, 0) + Duration.epsilon
        actual = InstantPattern.extended_iso.parse("2012-01-01T00:00:00,000000001Z").value
        assert actual == expected

    def test_create_with_current_culture(self) -> None:
        with CultureSaver.set_cultures(Cultures.dot_time_separator):
            pattern = InstantPattern.create_with_current_culture("HH:mm:ss")
            text = pattern.format(Instant.from_utc(2000, 1, 1, 12, 34, 56))
            assert text == "12.34.56"

    def test_create(self) -> None:
        pattern = InstantPattern.create("HH:mm:ss", Cultures.dot_time_separator)
        text = pattern.format(Instant.from_utc(2000, 1, 1, 12, 34, 56))
        assert text == "12.34.56"

    def test_parse_null(self) -> None:
        self.assert_parse_null(InstantPattern.general)

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
        pattern = InstantPattern.create_with_invariant_culture("yy-MM-dd'T'HH:mm:ss").with_two_digit_year_max(
            two_digit_year_max
        )
        value = pattern.parse(text).value
        assert value.in_utc().year == expected_year

    @pytest.mark.parametrize(
        "two_digit_year_max",
        [
            -1,
            100,
            _CsharpConstants.INT_MIN_VALUE,
            _CsharpConstants.INT_MAX_VALUE,
        ],
    )
    def test_with_two_digit_year_max_invalid(self, two_digit_year_max: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            InstantPattern.general.with_two_digit_year_max(two_digit_year_max)
