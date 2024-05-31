# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._duration import Duration
from pyoda_time.text import DurationPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages

from ..text.pattern_test_base import PatternTestBase
from ..text.pattern_test_data import PatternTestData
from .cultures import Cultures


class Data(PatternTestData[Duration]):
    @property
    def default_template(self) -> Duration:
        # Ignored anyway...
        return Duration.zero

    def __init__(
        self,
        *,
        value: Duration = Duration.zero,
        culture: CultureInfo = CultureInfo.invariant_culture,
        standard_pattern: IPattern[Duration] | None = None,
        pattern: str | None = None,
        text: str | None = None,
        template: Duration | None = None,
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

    def create_pattern(self) -> IPattern[Duration]:
        assert self.pattern is not None
        return DurationPattern.create(self.pattern, self.culture)


FORMAT_ONLY_DATA: list[Data] = [
    # No sign, so we can't parse it.
    Data(value=Duration.from_hours(-1).plus(Duration.from_minutes(0)), pattern="HH:mm", text="01:00"),
    # Loss of nano precision
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        pattern="D:hh:mm:ss.ffff",
        text="1:02:03:04.1234",
    ),
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        pattern="D:hh:mm:ss.FFFF",
        text="1:02:03:04.1234",
    ),
]

PARSE_ONLY_DATA: list[Data] = []

INVALID_PATTERN_DATA: list[Data] = [
    Data(pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(pattern="HH:MM", message=_TextErrorMessages.MULTIPLE_CAPITAL_DURATION_FIELDS),
    Data(pattern="HH D", message=_TextErrorMessages.MULTIPLE_CAPITAL_DURATION_FIELDS),
    Data(pattern="MM mm", message=_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, parameters=["m"]),
    Data(pattern="G", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["G", "Duration"]),
]

PARSE_FAILURE_DATA: list[Data] = [
    Data(
        value=Duration.zero,
        pattern="H:mm",
        text="1:60",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=[60, "m", "Duration"],
    ),
    # Total field values out of range
    # The "text" contains a value which is {max for field} + 1
    Data(
        value=Duration.min_value,
        pattern="-D:hh:mm:ss.fffffffff",
        text="1073741825:00:00:00.000000000",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=["1073741825", "D", "Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-H:mm:ss.fffffffff",
        text="25769803777:00:00.000000000",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=["25769803777", "H", "Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-M:ss.fffffffff",
        text="1546188226561:00.000000000",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=["1546188226561", "M", "Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-S.fffffffff",
        text="92771293593601.000000000",
        message=_TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE,
        parameters=["92771293593601", "S", "Duration"],
    ),
    # Each field in range, but overall result out of range
    # TODO: Each of the following eight tests fails because our Duration can have larger values than Noda Time
    Data(
        value=Duration.min_value,
        pattern="-D:hh:mm:ss.fffffffff",
        text="-1073741824:00:00:00.000000001",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-D:hh:mm:ss.fffffffff",
        text="1073741824:00:00:00.000000000",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-H:mm:ss.fffffffff",
        text="-25769803776:00:00.000000001",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-H:mm:ss.fffffffff",
        text="25769803776:00:00.000000000",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-M:ss.fffffffff",
        text="-1546188226560:00.000000001",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-M:ss.fffffffff",
        text="1546188226560:00.000000000",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-S.fffffffff",
        text="-92771293593600.000000001",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="-S.fffffffff",
        text="92771293593600.000000000",
        message=_TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE,
        parameters=["Duration"],
    ),
    Data(
        value=Duration.min_value,
        pattern="'x'S",
        text="x",
        message=_TextErrorMessages.MISMATCHED_NUMBER,
        parameters=["S"],
    ),
]

FORMAT_AND_PARSE_DATA: list[Data] = [
    Data(value=Duration.from_hours(1) + Duration.from_minutes(2), pattern="+HH:mm", text="+01:02"),
    Data(value=Duration.from_hours(-1) + Duration.from_minutes(-2), pattern="+HH:mm", text="-01:02"),
    Data(value=Duration.from_hours(1) + Duration.from_minutes(2), pattern="-HH:mm", text="01:02"),
    Data(value=Duration.from_hours(-1) + Duration.from_minutes(-2), pattern="-HH:mm", text="-01:02"),
    Data(value=Duration.from_hours(26) + Duration.from_minutes(3), pattern="D:h:m", text="1:2:3"),
    Data(value=Duration.from_hours(26) + Duration.from_minutes(3), pattern="DD:hh:mm", text="01:02:03"),
    Data(value=Duration.from_hours(242) + Duration.from_minutes(3), pattern="D:hh:mm", text="10:02:03"),
    Data(value=Duration.from_hours(2) + Duration.from_minutes(3), pattern="H:mm", text="2:03"),
    Data(value=Duration.from_hours(2) + Duration.from_minutes(3), pattern="HH:mm", text="02:03"),
    Data(value=Duration.from_hours(26) + Duration.from_minutes(3), pattern="HH:mm", text="26:03"),
    Data(value=Duration.from_hours(260) + Duration.from_minutes(3), pattern="HH:mm", text="260:03"),
    Data(
        value=Duration.from_hours(2) + Duration.from_minutes(3) + Duration.from_seconds(4),
        pattern="H:mm:ss",
        text="2:03:04",
    ),
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        pattern="D:hh:mm:ss.fffffffff",
        text="1:02:03:04.123456789",
    ),
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456000),
        pattern="D:hh:mm:ss.fffffffff",
        text="1:02:03:04.123456000",
    ),
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        pattern="D:hh:mm:ss.FFFFFFFFF",
        text="1:02:03:04.123456789",
    ),
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456000),
        pattern="D:hh:mm:ss.FFFFFFFFF",
        text="1:02:03:04.123456",
    ),
    Data(
        value=Duration.from_hours(1) + Duration.from_minutes(2) + Duration.from_seconds(3), pattern="M:ss", text="62:03"
    ),
    Data(
        value=Duration.from_hours(1) + Duration.from_minutes(2) + Duration.from_seconds(3),
        pattern="MMM:ss",
        text="062:03",
    ),
    Data(
        value=Duration.from_days(0)
        + Duration.from_hours(0)
        + Duration.from_minutes(1)
        + Duration.from_seconds(2)
        + Duration.from_nanoseconds(123400000),
        pattern="SS.FFFF",
        text="62.1234",
    ),
    # Check handling of F after non-period.
    Data(
        value=Duration.from_days(0)
        + Duration.from_hours(0)
        + Duration.from_minutes(1)
        + Duration.from_seconds(2)
        + Duration.from_nanoseconds(123400000),
        pattern="SS'x'FFFF",
        text="62x1234",
    ),
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        pattern="D:hh:mm:ss.FFFFFFFFF",
        text="1.02.03.04.123456789",
        culture=Cultures.dot_time_separator,
    ),
    # Roundtrip pattern is invariant; redundantly specify the culture to validate that it doesn't make a difference.
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        standard_pattern=DurationPattern.roundtrip,
        pattern="o",
        text="1:02:03:04.123456789",
        culture=Cultures.dot_time_separator,
    ),
    Data(
        value=Duration.from_days(-1)
        + Duration.from_hours(-2)
        + Duration.from_minutes(-3)
        + Duration.from_seconds(-4)
        + Duration.from_nanoseconds(-123456789),
        standard_pattern=DurationPattern.roundtrip,
        pattern="o",
        text="-1:02:03:04.123456789",
        culture=Cultures.dot_time_separator,
    ),
    # Same tests for the "JSON roundtrip" pattern.
    Data(
        value=Duration.from_days(1)
        + Duration.from_hours(2)
        + Duration.from_minutes(3)
        + Duration.from_seconds(4)
        + Duration.from_nanoseconds(123456789),
        standard_pattern=DurationPattern.json_roundtrip,
        pattern="j",
        text="26:03:04.123456789",
        culture=Cultures.dot_time_separator,
    ),
    Data(
        value=Duration.from_days(-1)
        + Duration.from_hours(-2)
        + Duration.from_minutes(-3)
        + Duration.from_seconds(-4)
        + Duration.from_nanoseconds(-123456789),
        standard_pattern=DurationPattern.json_roundtrip,
        pattern="j",
        text="-26:03:04.123456789",
        culture=Cultures.dot_time_separator,
    ),
    # Extremes...
    Data(value=Duration.min_value, pattern="-D:hh:mm:ss.fffffffff", text="-1073741824:00:00:00.000000000"),
    Data(value=Duration.max_value, pattern="-D:hh:mm:ss.fffffffff", text="1073741823:23:59:59.999999999"),
    Data(value=Duration.min_value, pattern="-H:mm:ss.fffffffff", text="-25769803776:00:00.000000000"),
    Data(value=Duration.max_value, pattern="-H:mm:ss.fffffffff", text="25769803775:59:59.999999999"),
    Data(value=Duration.min_value, pattern="-M:ss.fffffffff", text="-1546188226560:00.000000000"),
    Data(value=Duration.max_value, pattern="-M:ss.fffffffff", text="1546188226559:59.999999999"),
    Data(value=Duration.min_value, pattern="-S.fffffffff", text="-92771293593600.000000000"),
    Data(value=Duration.max_value, pattern="-S.fffffffff", text="92771293593599.999999999"),
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


class TestDurationPattern(PatternTestBase[Duration]):
    pass
