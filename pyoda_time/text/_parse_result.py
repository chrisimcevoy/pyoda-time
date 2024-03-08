# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, final, overload

from .._calendar_system import CalendarSystem
from ..calendars._era import Era
from ..utility import _Preconditions, _private, _sealed
from ._text_error_messages import TextErrorMessages
from ._unparsable_value_error import UnparsableValueError

if TYPE_CHECKING:
    from . import _ValueCursor


T = TypeVar("T")
TTarget = TypeVar("TTarget")


class _ParseResultMeta(type):
    @property
    @functools.cache
    def _format_only_pattern(cls) -> ParseResult:
        """This isn't really an issue with the value so much as the pattern...

        but the result is the same.
        """
        # Pyoda Time implementation note:
        # This is a field on ParseResult in Noda Time.
        # To make this property possible without a complete hack,
        # I've made ported the private constructor as an internal one.
        # So `_ctor` rather than `__ctor`.
        # This is also cached so that the same instance is returned
        # eache time the getter is accessed.
        # We need that for `assert ==` in tests, because the equality
        # operator is not implemented for ParseResult, and equality
        # checks fall back to default object.__eq__() behaviour.
        return ParseResult._ctor(
            exception_provider=functools.partial(UnparsableValueError, TextErrorMessages.FORMAT_ONLY_PATTERN),
            continue_with_multiple=True,
        )


@_private
@final
@_sealed
class ParseResult(Generic[T], metaclass=_ParseResultMeta):
    """The result of a parse operation."""

    # Invariant: exactly one of value or exceptionProvider is null.
    __value: T | None = None
    __exception_provider: Callable[[], Exception] | None = None

    __continue_after_error_with_multiple_formats: bool = False

    @property
    def _continue_after_error_with_multiple_formats(self) -> bool:
        return self.__continue_after_error_with_multiple_formats

    @classmethod
    def _ctor(
        cls,
        value: T | None = None,
        exception_provider: Callable[[], Exception] | None = None,
        continue_with_multiple: bool = False,
    ) -> ParseResult[T]:
        # Implementation Note:
        # In Noda Time this is a private constructor.
        # Normally we'd port those to a `__ctor` classmethod,
        # but we need this one to be accessible to the metaclass
        # for @property usage.

        if (value and exception_provider) or (value is None and exception_provider is None):
            raise RuntimeError("Exactly one of value and exception_provider can be specified")

        self = super().__new__(cls)

        if value:
            self.__value = value
        elif exception_provider:
            self.__exception_provider = exception_provider
            self.__continue_after_error_with_multiple_formats = continue_with_multiple

        return self

    @property
    def value(self) -> T:
        """Gets the value from the parse operation if it was successful, or throws an exception indicating the parse
        failure otherwise.

        This method is exactly equivalent to calling the ``get_value_or_throw()`` method, but is terser if the code is
        already clear that it will throw if the parse failed.

        :return: The result of the parsing operation if it was successful.
        """
        return self.get_value_or_throw()

    @property
    def exception(self) -> Exception:
        """Gets an exception indicating the cause of the parse failure.

        This property is typically used to wrap parse failures in higher level exceptions.

        :return: The exception indicating the cause of the parse failure.
        :raises RuntimeError: The parse operation succeeded.
        """
        if self.__exception_provider:
            return self.__exception_provider()
        raise RuntimeError("Parse operation succeeded, so no exception is available")

    def get_value_or_throw(self) -> T:
        """Gets the value from the parse operation if it was successful, or throws an exception indicating the parse
        failure otherwise.

        This method is exactly equivalent to fetching the ``value`` property, but more explicit in terms of throwing
        an exception on failure.

        :return: The result of the parsing operation if it was successful.
        """
        if self.__value is not None:
            return self.__value
        raise self.exception

    def try_get_value(self, failure_value: T) -> tuple[bool, T]:
        """Returns a two-tuple of the success value, and either the default ``failure_value`` of T or the successful
        parse result value.

        :param failure_value: The "default" value to set in ``result`` if parsing failed.
        :return: A two-tuple of a boolean representing success, and either the parsed value or the default value.
        """
        return (self.success, self.value) if self.success else (self.success, failure_value)

    @property
    def success(self) -> bool:
        """Indicates whether the parse operation was successful.

        :return: ``True`` if the parse operation was successful; otherwise ``False``.
        """
        return self.__exception_provider is None

    def convert(self, projection: Callable[[T], TTarget]) -> ParseResult[TTarget]:
        """Converts this result to a new target type, either by executing the given projection for a success result, or
        propagating the exception provider for failure.

        :param projection: The projection to apply for the value of this result, if it's a success result.
        :return: A ParseResult for the target type, either with a value obtained by applying the specified projection to
            the value in this result, or with the same error as this result.
        """
        _Preconditions._check_not_null(projection, "projection")
        return (
            ParseResult[TTarget].for_value(projection(self.value))
            if self.success
            else ParseResult[TTarget]._ctor(
                exception_provider=self.__exception_provider,
                continue_with_multiple=self._continue_after_error_with_multiple_formats,
            )
        )

    def convert_error(self: ParseResult[T], target_type: type[TTarget]) -> ParseResult[TTarget]:
        # TODO: docstring
        if self.success:
            raise RuntimeError("convert_error should not be called on a successful parse result")
        return ParseResult[TTarget]._ctor(
            exception_provider=self.__exception_provider,
            continue_with_multiple=self.__continue_after_error_with_multiple_formats,
        )

    # region Factory methods and readonly static fields

    @classmethod
    def for_value(cls: type[ParseResult[T]], value: T) -> ParseResult[T]:
        """Produces a ParseResult which represents a successful parse operation.

        :param value: The successfully parsed value.
        :return: A ParseResult representing a successful parsing operation.
        """
        return cls._ctor(value)

    @classmethod
    def for_exception(cls: type[ParseResult[T]], exception_provider: Callable[[], Exception]) -> ParseResult[T]:
        """Produces a ``ParseResult`` which represents a failed parsing operation.

        This method accepts a ``Callable`` rather than the exception itself because
        if the client doesn't need the actual exception - just the information
        that the parse failed - there's no point in creating the exception.

        :param exception_provider: A ``Callable`` which produces the exception
            representing the error that caused the parse to fail.
        :return: A ``ParseResult`` representing a failed parsing operation.
        """
        return cls._ctor(
            exception_provider=_Preconditions._check_not_null(exception_provider, "exception_provider"),
            continue_with_multiple=False,
        )

    @classmethod
    def _for_invalid_value_post_parse(cls, text: str, format_string: str, *args: Any) -> ParseResult[T]:
        def expection_provider() -> Exception:
            detail_message = format_string.format(*args)
            overall_message = TextErrorMessages.UNPARSABLE_VALUE_POST_PARSE.format(detail_message, text)
            return UnparsableValueError(overall_message)

        return cls._for_invalid_value(expection_provider)

    @classmethod
    @overload
    def _for_invalid_value(cls, exception_provider: Callable[[], Exception], /) -> ParseResult[T]: ...

    @classmethod
    @overload
    def _for_invalid_value(cls, cursor: _ValueCursor, format_string: str, /, *parameters: Any) -> ParseResult[T]: ...

    @classmethod
    def _for_invalid_value(
        cls, cursor_or_exception_provider: _ValueCursor | Callable[[], Exception], *args: Any
    ) -> ParseResult[T]:
        from . import _ValueCursor

        exception_provider: Callable[[], Exception]

        if isinstance(cursor_or_exception_provider, _ValueCursor):
            cursor: _ValueCursor = cursor_or_exception_provider
            format_string: str = args[0]
            parameters = args[1:]
            detail_message = format_string.format(*parameters)
            overall_message = TextErrorMessages.UNPARSABLE_VALUE.format(detail_message, cursor)

            def exception_provider() -> Exception:
                return UnparsableValueError(overall_message)

        elif callable(cursor_or_exception_provider):
            exception_provider = cursor_or_exception_provider
        else:
            raise TypeError(f"Expected cursor or exception_provider, got {type(cursor_or_exception_provider)}")

        return cls._ctor(exception_provider=exception_provider, continue_with_multiple=True)

    @classmethod
    def _argument_null(cls, parameter: str) -> ParseResult[T]:
        def exception_provider() -> Exception:
            # TODO: ArgumentNullException
            return ValueError(parameter)

        return cls._ctor(exception_provider=exception_provider, continue_with_multiple=False)

    @classmethod
    def _positive_sign_invalid(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.POSITIVE_SIGN_INVALID)

    @classmethod
    def _value_string_empty(cls) -> ParseResult[T]:
        """Special case: it's a fault with the value, but we still don't want to continue with multiple patterns.
        Also, there's no point in including the text.
        """

        def exception_provider() -> Exception:
            return UnparsableValueError(TextErrorMessages.VALUE_STRING_EMPTY)

        return cls._ctor(exception_provider=exception_provider, continue_with_multiple=False)

    @classmethod
    def _extra_value_characters(cls, cursor: _ValueCursor, remainder: str) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.EXTRA_VALUE_CHARACTERS, remainder)

    @classmethod
    def _quoted_string_mismatch(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.QUOTED_STRING_MISMATCH)

    @classmethod
    def _escaped_character_missmatch(cls, cursor: _ValueCursor, pattern_character: str) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.ESCAPED_CHARACTER_MISMATCH, pattern_character)

    @classmethod
    def _end_of_string(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.END_OF_STRING)

    @classmethod
    def _time_separator_mismatch(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.TIME_SEPARATOR_MISMATCH)

    @classmethod
    def _date_separator_mismatch(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.DATE_SEPARATOR_MISMATCH)

    @classmethod
    def _missing_number(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.MISSING_NUMBER)

    @classmethod
    def _unexpected_negative(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.UNEXPECTED_NEGATIVE)

    @classmethod
    def _mismatched_number(cls, cursor: _ValueCursor, pattern: str) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.MISMATCHED_NUMBER, pattern)

    @classmethod
    def _mismatched_character(cls, cursor: _ValueCursor, pattern_character: str) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.MISMATCHED_CHARACTER, pattern_character)

    @classmethod
    def _mismatched_text(cls, cursor: _ValueCursor, field: str) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.MISMATCHED_TEXT, field)

    @classmethod
    def _no_matching_format(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.NO_MATCHING_FORMAT)

    @classmethod
    def _value_out_of_range(cls, value_cursor: _ValueCursor, value: T) -> ParseResult[T]:
        return cls._for_invalid_value(value_cursor, TextErrorMessages.VALUE_OUT_OF_RANGE, value, type(value))

    @classmethod
    def _missing_sign(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.MISSING_SIGN)

    @classmethod
    def _missing_am_pm_designator(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.MISSING_AM_PM_DESIGNATOR)

    @classmethod
    def _no_matching_calendar_system(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.NO_MATCHING_CALENDAR_SYSTEM)

    @classmethod
    def _no_matching_zone_id(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.NO_MATCHING_ZONE_ID)

    @classmethod
    def _invalid_hour_24(cls, cursor: _ValueCursor) -> ParseResult[T]:
        return cls._for_invalid_value(cursor, TextErrorMessages.INVALID_HOUR_24)

    @classmethod
    def _field_value_out_of_range(cls, cursor: _ValueCursor, value: int, field: str, type_: type[T]) -> ParseResult[T]:
        # TODO: This differs from Noda Time insofar as we can't do `typeof(T)` for the
        #  final argument. This means that we've had to pass the actual type at runtime
        #  which required several method signature changes. (Wherever this method is used.)
        return cls._for_invalid_value(cursor, TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE, value, field, type_.__name__)

    @classmethod
    def _field_value_out_of_range_post_parse(
        cls, text: str, value: int, field: str, eventual_result_type: type
    ) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(
            text, TextErrorMessages.FIELD_VALUE_OUT_OF_RANGE, value, field, eventual_result_type
        )

    @classmethod
    def _inconsistent_values(cls, text: str, field_1: str, field_2: str, eventual_result_type: type) -> ParseResult[T]:
        """Two fields (e.g. "hour of day" and "hour of half day") were mutually inconsistent."""
        return cls._for_invalid_value_post_parse(
            text, TextErrorMessages.INCONSISTENT_VALUES_2, field_1, field_2, eventual_result_type
        )

    @classmethod
    def _inconsistent_month_values(cls, text: str) -> ParseResult[T]:
        """The month of year is inconsistent between the text and numeric specifications.

        We can't use InconsistentValues for this as the pattern character is the same in both cases.
        """
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.INCONSISTENT_MONTH_TEXT_VALUE)

    @classmethod
    def _inconsistent_day_of_week_text_value(cls, text: str) -> ParseResult[T]:
        """The day of month is inconsistent with the day of week value.

        We can't use InconsistentValues for this as the pattern character is the same in both cases.
        """
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.INCONSISTENT_DAY_OF_WEEK_TEXT_VALUE)

    @classmethod
    def _expected_end_of_string(cls, cursor: _ValueCursor) -> ParseResult[T]:
        """We'd expected to get to the end of the string now, but we haven't."""
        return cls._for_invalid_value(cursor, TextErrorMessages.EXPECTED_END_OF_STRING)

    @classmethod
    def _year_era_out_of_range(cls, text: str, value: int, era: Era, calendar: CalendarSystem) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(
            text, TextErrorMessages.YEAR_OF_ERA_OUT_OF_RANGE, value, era.name, calendar.name
        )

    @classmethod
    def _month_out_of_range(cls, text: str, month: int, year: int) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.MONTH_OUT_OF_RANGE, month, year)

    @classmethod
    def _iso_month_out_of_range(cls, text: str, month: int) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.ISO_MONTH_OUT_OF_RANGE, month)

    @classmethod
    def _day_of_month_out_of_range(cls, text: str, day: int, month: int, year: int) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE, day, month, year)

    @classmethod
    def _day_of_month_out_of_range_no_year(cls, text: str, day: int, month: int) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.DAY_OF_MONTH_OUT_OF_RANGE_NO_YEAR, day, month)

    @classmethod
    def _invalid_offset(cls, text: str) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.INVALID_OFFSET)

    @classmethod
    def _skipped_local_time(cls, text: str) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.SKIPPED_LOCAL_TIME)

    @classmethod
    def _ambiguous_local_time(cls, text: str) -> ParseResult[T]:
        return cls._for_invalid_value_post_parse(text, TextErrorMessages.AMBIGUOUS_LOCAL_TIME)

    # endregion
