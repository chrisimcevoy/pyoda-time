# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest

from pyoda_time import AnnualDate
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time.text import AnnualDatePattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._text_error_messages import _TextErrorMessages

from ..culture_saver import CultureSaver
from .cultures import Cultures
from .pattern_test_base import PatternTestBase
from .pattern_test_data import PatternTestData


class Data(PatternTestData[AnnualDate]):
    @property
    def default_template(self) -> AnnualDate:
        return AnnualDatePattern._DEFAULT_TEMPLATE_VALUE

    def __init__(
        self,
        *,
        value: AnnualDate = AnnualDatePattern._DEFAULT_TEMPLATE_VALUE,
        culture: CultureInfo = CultureInfo.invariant_culture,
        standard_pattern: IPattern[AnnualDate] | None = None,
        pattern: str | None = None,
        text: str | None = None,
        template: AnnualDate | None = None,
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

    def create_pattern(self) -> IPattern[AnnualDate]:
        assert self.pattern is not None
        return (
            AnnualDatePattern.create_with_invariant_culture(self.pattern)
            .with_template_value(self.template)
            .with_culture(self.culture)
        )


INVALID_PATTERN_DATA: list[Data] = [
    Data(pattern="", message=_TextErrorMessages.FORMAT_STRING_EMPTY),
    Data(pattern="!", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["!", AnnualDate.__name__]),
    Data(pattern="%", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["%", AnnualDate.__name__]),
    Data(pattern="\\", message=_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, parameters=["\\", AnnualDate.__name__]),
    Data(pattern="%%", message=_TextErrorMessages.PERCENT_DOUBLED),
    Data(pattern="%\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="MMMMM", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["M", 4]),
    Data(pattern="ddd", message=_TextErrorMessages.REPEAT_COUNT_EXCEEDED, parameters=["d", 2]),
    Data(pattern="M%", message=_TextErrorMessages.PERCENT_AT_END_OF_STRING),
    Data(pattern="'qwe", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    Data(pattern="'qwe\\", message=_TextErrorMessages.ESCAPE_AT_END_OF_STRING),
    Data(pattern="'qwe\\'", message=_TextErrorMessages.MISSING_END_QUOTE, parameters=["'"]),
    # Common typo (m doesn't mean months)
    Data(pattern="mm-dd", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["m"]),
    # T isn't valid in a date pattern
    Data(pattern="MM-ddT00:00:00", message=_TextErrorMessages.UNQUOTED_LITERAL, parameters=["T"]),
]

PARSE_FAILURE_DATA: list[Data] = [
    Data(pattern="MM dd MMMM", text="10 09 January", message=_TextErrorMessages.INCONSISTENT_MONTH_TEXT_VALUE),
    Data(pattern="MM dd MMMM", text="10 09 FooBar", message=_TextErrorMessages.MISMATCHED_TEXT, parameters=["M"]),
    Data(pattern="MM/dd", text="02-29", message=_TextErrorMessages.DATE_SEPARATOR_MISMATCH),
    # Don't match a short name against a long pattern
    Data(pattern="MMMM dd", text="Oct 09", message=_TextErrorMessages.MISMATCHED_TEXT, parameters=["M"]),
    # Or vice versa... although this time we match the "Oct" and then fail as we're expecting a space
    Data(pattern="MMM dd", text="October 09", message=_TextErrorMessages.MISMATCHED_CHARACTER, parameters=[" "]),
    # Invalid month, day
    Data(pattern="MM dd", text="15 29", message=_TextErrorMessages.ISO_MONTH_OUT_OF_RANGE, parameters=[15]),
    Data(
        pattern="MM dd", text="02 35", message=_TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE_NO_YEAR, parameters=[35, 2]
    ),
]

PARSE_ONLY_DATA: list[Data] = [
    # Month parsing should be case-insensitive
    Data(value=AnnualDate(10, 3), pattern="MMM dd", text="OcT 03"),
    Data(value=AnnualDate(10, 3), pattern="MMMM dd", text="OcToBeR 03"),
    # Genitive name is an extension of the non-genitive name; parse longer first.
    Data(
        value=AnnualDate(1, 10),
        pattern="MMMM dd",
        text="MonthName-Genitive 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
    Data(
        value=AnnualDate(1, 10),
        pattern="MMMM dd",
        text="MonthName 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
    Data(
        value=AnnualDate(1, 10),
        pattern="MMM dd",
        text="MN-Gen 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
    Data(
        value=AnnualDate(1, 10),
        pattern="MMM dd",
        text="MN 10",
        culture=Cultures._genitive_name_test_culture_with_leading_names,
    ),
]

FORMAT_ONLY_DATA: list[Data] = []

FORMAT_AND_PARSE_DATA: list[Data] = [
    # Standard patterns
    Data(value=AnnualDate(10, 20), pattern="G", text="10-20"),
    # Custom patterns
    Data(value=AnnualDate(10, 3), pattern="MM/dd", text="10/03"),
    Data(value=AnnualDate(10, 3), pattern="MM/dd", text="10-03", culture=Cultures.fr_ca),
    Data(value=AnnualDate(10, 3), pattern="MMdd", text="1003"),
    Data(value=AnnualDate(7, 3), pattern="M d", text="7 3"),
    # Template value provides the month when we only specify the day
    Data(value=AnnualDate(5, 10), pattern="dd", text="10", template=AnnualDate(5, 20)),
    # Template value provides the day when we only specify the month
    Data(value=AnnualDate(10, 20), pattern="MM", text="10", template=AnnualDate(5, 20)),
    # When we parse in all of the below tests, we'll use the month and day-of-month if it's provided;
    # the template value is specified to allow simple roundtripping.
    # Non-genitive month name when there's no "day of month"
    Data(
        value=AnnualDate(1, 3),
        pattern="MMMM",
        text="FullNonGenName",
        culture=Cultures._genitive_name_test_culture,
        template=AnnualDate(5, 3),
    ),
    Data(
        value=AnnualDate(1, 3),
        pattern="MMM",
        text="AbbrNonGenName",
        culture=Cultures._genitive_name_test_culture,
        template=AnnualDate(5, 3),
    ),
    # Genitive month name when the pattern includes "day of month"
    Data(
        value=AnnualDate(1, 3),
        pattern="MMMM dd",
        text="FullGenName 03",
        culture=Cultures._genitive_name_test_culture,
        template=AnnualDate(5, 3),
    ),
    # TODO: Check whether or not this is actually appropriate
    Data(
        value=AnnualDate(1, 3),
        pattern="MMM dd",
        text="AbbrGenName 03",
        culture=Cultures._genitive_name_test_culture,
        template=AnnualDate(5, 3),
    ),
    # Month handling with both text and numeric
    Data(value=AnnualDate(10, 9), pattern="MMMM dd MM", text="October 09 10"),
    Data(value=AnnualDate(10, 9), pattern="MMM dd MM", text="Oct 09 10"),
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


class TestAnnualDatePattern(PatternTestBase[AnnualDate]):
    def test_create_with_current_culture(self) -> None:
        date = AnnualDate(8, 23)
        with CultureSaver.set_cultures(Cultures.fr_fr):
            pattern = AnnualDatePattern.create_with_current_culture("MM/dd")
            assert pattern.format(date) == "08/23"
        with CultureSaver.set_cultures(Cultures.fr_ca):
            pattern = AnnualDatePattern.create_with_current_culture("MM/dd")
            assert pattern.format(date) == "08-23"

    @pytest.mark.parametrize(
        "culture_id,expected",
        [
            ("fr-FR", "08/23"),
            ("fr-CA", "08-23"),
        ],
    )
    def test_create_with_culture(self, culture_id: str, expected: str) -> None:
        date = AnnualDate(8, 23)
        culture = CultureInfo(culture_id)
        pattern = AnnualDatePattern.create("MM/dd", culture)
        assert pattern.format(date) == expected

    @pytest.mark.parametrize(
        "culture_id,expected",
        [
            ("fr-FR", "08/23"),
            ("fr-CA", "08-23"),
        ],
    )
    def test_create_with_culture_and_template_value(self, culture_id: str, expected: str) -> None:
        date = AnnualDate(8, 23)
        template = AnnualDate(5, 3)
        culture = CultureInfo(culture_id)
        # Check the culture is still used
        pattern1 = AnnualDatePattern.create("MM/dd", culture, template)
        assert pattern1.format(date) == expected
        # And the template value
        pattern2 = AnnualDatePattern.create("MM", culture, template)
        parsed = pattern2.parse("08").value
        assert parsed == AnnualDate(8, 3)

    def test_parse_null(self) -> None:
        self.assert_parse_null(AnnualDatePattern.iso)
