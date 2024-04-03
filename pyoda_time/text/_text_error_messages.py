# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import Final, final

from ..utility._csharp_compatibility import _private, _sealed


@final
@_sealed
@_private
class _TextErrorMessages:
    """Centralized location for error messages around text handling."""

    AMBIGUOUS_LOCAL_TIME: Final[str] = "The local date/time is ambiguous in the target time zone."
    CALENDAR_AND_ERA: Final[str] = (
        "The era specifier cannot be specified in the same pattern as the calendar specifier."
    )
    DATE_FIELD_AND_EMBEDDED_DATE: Final[str] = (
        "Custom date specifiers cannot be specified in the same pattern as an embedded date specifier"
    )
    DATE_SEPARATOR_MISMATCH: Final[str] = "The value string does not match a date separator in the format string."
    DAY_OF_MONTH_OUT_OF_RANGE: Final[str] = "The day {0} is out of range in month {1} of year {2}."
    DAY_OF_MONTH_OUT_OF_RANGE_NO_YEAR: Final[str] = "The day {0} is out of range in month {1}."
    EMPTY_PERIOD: Final[str] = "The specified period was empty."
    EMPTY_ZPREFIXED_OFFSET_PATTERN: Final[str] = (
        "The Z prefix for an Offset pattern must be followed by a custom pattern."
    )
    END_OF_STRING: Final[str] = "Input string ended unexpectedly early."
    ERA_WITHOUT_YEAR_OF_ERA: Final[str] = 'The era specifier cannot be used without the "year of era" specifier.'
    ESCAPE_AT_END_OF_STRING: Final[str] = (
        "The format string has an escape character (backslash '\\') at the end of the string."
    )
    ESCAPED_CHARACTER_MISMATCH: Final[str] = (
        'The value string does not match an escaped character in the format string: "{0}"'
    )
    EXPECTED_END_OF_STRING: Final[str] = "Expected end of input, but more data remains."
    EXTRA_VALUE_CHARACTERS: Final[str] = (
        'The format matches a prefix of the value string but not the entire string. Part not matching: "{0}".'
    )
    FIELD_VALUE_OUT_OF_RANGE: Final[str] = "The value {0} is out of range for the field '{1}' in the {2} type."
    FORMAT_ONLY_PATTERN: Final[str] = "This pattern is only capable of formatting, not parsing."
    FORMAT_STRING_EMPTY: Final[str] = "The format string is empty."
    HOUR12_PATTERN_NOT_SUPPORTED: Final[str] = "The 'h' pattern flag (12 hour format) is not supported by the {0} type."
    INCONSISTENT_DAY_OF_WEEK_TEXT_VALUE: Final[str] = (
        "The specified day of the week does not matched the computed value."
    )
    INCONSISTENT_MONTH_TEXT_VALUE: Final[str] = "The month values specified as text and numbers are inconsistent."
    INCONSISTENT_VALUES_2: Final[str] = (
        "The individual values for the fields '{0}' and '{1}' created an inconsistency in the {2} type."
    )
    INVALID_EMBEDDED_PATTERN_TYPE: Final[str] = "The type of embedded pattern is not supported for this type."
    INVALID_HOUR_24: Final[str] = "24 is only valid as an hour number when the units smaller than hours are all 0."
    INVALID_OFFSET: Final[str] = "The specified offset is invalid for the given date/time."
    INVALID_REPEAT_COUNT: Final[str] = (
        'The number of consecutive copies of the pattern character "{0}" in the format string ({1}) is invalid.'
    )
    INVALID_UNIT_SPECIFIER: Final[str] = "The period unit specifier '{0}' is invalid."
    ISO_MONTH_OUT_OF_RANGE: Final[str] = "The month {0} is out of range in the ISO calendar."
    MISMATCHED_CHARACTER: Final[str] = 'The value string does not match a simple character in the format string "{0}".'
    MISMATCHED_NUMBER: Final[str] = 'The value string does not match the required number from the format string "{0}".'
    MISMATCHED_TEXT: Final[str] = "The value string does not match the text-based field '{0}'."
    MISPLACED_UNIT_SPECIFIER: Final[str] = (
        "The period unit specifier '{0}' appears at the wrong place in the input string."
    )
    MISSING_AM_PM_DESIGNATOR: Final[str] = (
        "The value string does not match the AM or PM designator for the culture at the required place."
    )
    MISSING_EMBEDDED_PATTERN_END: Final[str] = (
        "The pattern has an embedded pattern which is missing its closing character ('{0}')."
    )
    MISSING_EMBEDDED_PATTERN_START: Final[str] = (
        "The pattern has an embedded pattern which is missing its opening character ('{0}')."
    )
    MISSING_END_QUOTE: Final[str] = 'The format string is missing the end quote character "{0}".'
    MISSING_NUMBER: Final[str] = "The value string does not include a number in the expected position."
    MISSING_SIGN: Final[str] = "The required value sign is missing."
    MONTH_OUT_OF_RANGE: Final[str] = "The month {0} is out of range in year {1}."
    MULTIPLE_CAPITAL_DURATION_FIELDS: Final[str] = (
        'Only one of "D", "H", "M" or "S" can occur in a duration format string.'
    )
    NO_MATCHING_CALENDAR_SYSTEM: Final[str] = "The specified calendar id is not recognized."
    NO_MATCHING_FORMAT: Final[str] = "None of the specified formats matches the given value string."
    NO_MATCHING_ZONE_ID: Final[str] = "The specified time zone identifier is not recognized."
    OVERALL_VALUE_OUT_OF_RANGE: Final[str] = "Value is out of the legal range for the {0} type."
    PERCENT_AT_END_OF_STRING: Final[str] = "A percent sign (%) appears at the end of the format string."
    PERCENT_DOUBLED: Final[str] = "A percent sign (%) is followed by another percent sign in the format string."
    POSITIVE_SIGN_INVALID: Final[str] = "A positive value sign is not valid at this point."
    QUOTED_STRING_MISMATCH: Final[str] = "The value string does not match a quoted string in the pattern."
    REPEAT_COUNT_EXCEEDED: Final[str] = (
        'There were more consecutive copies of the pattern character "{0}" than the maximum allowed ({1}) '
        "in the format string."
    )
    REPEATED_FIELD_IN_PATTERN: Final[str] = 'The field "{0}" is specified multiple times in the pattern.'
    REPEATED_UNIT_SPECIFIER: Final[str] = "The period unit specifier '{0}' appears multiple times in the input string."
    SKIPPED_LOCAL_TIME: Final[str] = "The local date/time is skipped in the target time zone."
    TIME_FIELD_AND_EMBEDDED_TIME: Final[str] = (
        "Custom time specifiers cannot be specified in the same pattern as an embedded time specifier"
    )
    TIME_SEPARATOR_MISMATCH: Final[str] = "The value string does not match a time separator in the format string."
    UNEXPECTED_NEGATIVE: Final[str] = (
        "The value string includes a negative value where only a non-negative one is allowed."
    )
    UNKNOWN_STANDARD_FORMAT: Final[str] = (
        'The standard format "{0}" is not valid for the {1} type. '
        'If the pattern was intended to be a custom format, escape it with a percent sign: "%{0}".'
    )
    UNPARSABLE_VALUE: Final[str] = "{0} Value being parsed: '{1}'. (^ indicates error position.)"
    UNPARSABLE_VALUE_POST_PARSE: Final[str] = "{0} Value being parsed: '{1}'."
    UNQUOTED_LITERAL: Final[str] = (
        "The character {0} is not a format specifier for this pattern type, and should be quoted to "
        "act as a literal. Note that each type of pattern has its own set of valid format specifiers."
    )
    VALUE_OUT_OF_RANGE: Final[str] = "The value {0} is out of the legal range for the {1} type."
    VALUE_STRING_EMPTY: Final[str] = "The value string is empty."
    YEAR_OF_ERA_OUT_OF_RANGE: Final[str] = "The year {0} is out of range for the {1} era in the {2} calendar."
    ZPREFIX_NOT_AT_START_OF_PATTERN: Final[str] = (
        "The Z prefix for an Offset pattern must occur at the beginning of the pattern."
    )
