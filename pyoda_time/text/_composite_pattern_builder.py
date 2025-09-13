# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from collections.abc import Callable, Sequence
from typing import Final, Generic, TypeVar, cast, final

from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text._value_cursor import _ValueCursor
from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._preconditions import _Preconditions

T = TypeVar("T")


@final
@_sealed
class CompositePatternBuilder(Generic[T]):  # TODO: IEnumerable<Pattern<T>>
    """A builder for composite patterns.

    A composite pattern is a combination of multiple patterns. When parsing, these are checked
    in the order in which they are added to the builder with the ``add(IPattern[T], Callable[[T], bool])``
    method, by trying to parse and seeing if the result is a successful one. When formatting,
    the patterns are checked in the reverse order, using the predicate provided along with the pattern
    when calling ``add``. The intention is that patterns are added in "most precise first" order,
    and the predicate should indicate whether it can fully represent the given value - so the "less precise"
    (and therefore usually shorter) pattern can be used first.
    """

    def __init__(
        self,
        patterns: Sequence[IPattern[T]] | None = None,
        format_predicates: Sequence[Callable[[T], bool]] | None = None,
    ) -> None:
        self.__patterns: Final[list[IPattern[T]]] = list(patterns) if patterns else []
        self.__format_predicates: Final[list[Callable[[T], bool]]] = (
            list(format_predicates) if format_predicates else []
        )

    def add(self, pattern: IPattern[T], format_predicates: Callable[[T], bool]) -> None:
        """Adds a component pattern to this builder.

        :param pattern: The component pattern to use as part of the eventual composite pattern.
        :param format_predicates: A predicate to determine whether this pattern is suitable for formatting the given
            value
        :return:
        """
        self.__patterns.append(_Preconditions._check_not_null(pattern, "pattern"))
        self.__format_predicates.append(_Preconditions._check_not_null(format_predicates, "format_predicates"))

    def build(self) -> IPattern[T]:
        _Preconditions._check_state(
            len(self.__patterns) != 0, "A composite pattern must have at least one component pattern."
        )
        return self._build_as_partial()

    def _build_as_partial(self) -> _IPartialPattern[T]:
        # TODO: Preconditions.DebugCheckState
        return _CompositePattern(self.__patterns, self.__format_predicates)


class _CompositePattern(_IPartialPattern[T]):
    def __init__(self, patterns: list[IPattern[T]], format_predicates: list[Callable[[T], bool]]) -> None:
        self.__patterns: Final[list[IPattern[T]]] = patterns
        self.__format_predicates: Final[list[Callable[[T], bool]]] = format_predicates

    def parse(self, text: str) -> ParseResult[T]:
        for pattern in self.__patterns:
            result: ParseResult[T] = pattern.parse(text)
            if result.success or not result._continue_after_error_with_multiple_formats:
                return result
        return ParseResult[T]._no_matching_format(_ValueCursor(text))

    def parse_partial(self, cursor: _ValueCursor) -> ParseResult[T]:
        index = cursor.index
        for pattern in self.__patterns:
            cursor.move(index)
            result: ParseResult[T] = cast(_IPartialPattern[T], pattern).parse_partial(cursor)
            if result.success or not result._continue_after_error_with_multiple_formats:
                return result
        cursor.move(index)
        return ParseResult[T]._no_matching_format(cursor)

    def format(self, value: T) -> str:
        return self.__find_format_pattern(value).format(value)

    def append_format(self, value: T, builder: StringBuilder) -> StringBuilder:
        return self.__find_format_pattern(value).append_format(value, builder)

    def __find_format_pattern(self, value: T) -> IPattern[T]:
        for format_predicate in reversed(self.__format_predicates):
            if format_predicate(value):
                return self.__patterns[self.__format_predicates.index(format_predicate)]
        # TODO: FormatException equivalent?
        raise RuntimeError("Composite pattern was unable to format value using any of the provided patterns.")
