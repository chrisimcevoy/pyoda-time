# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import Final, final

from ..._compatibility._string_builder import StringBuilder
from ...utility import _sealed
from .._invalid_pattern_exception import InvalidPatternError
from .._text_cursor import _TextCursor
from .._text_error_messages import TextErrorMessages


@final
@_sealed
class _PatternCursor(_TextCursor):
    """Extends ``_TextCursor`` to simplify parsing patterns such as "uuuu-MM-dd"."""

    # The character signifying the start of an embedded pattern.
    _EMBEDDED_PATTERN_START: Final[str] = "<"
    # The character signifying the end of an embedded pattern.
    _EMBEDDED_PATTERN_END: Final[str] = ">"

    def get_quoted_string(self, close_quote: str) -> str:
        """Return the quoted string.

        The cursor is left positioned at the end of the quoted region.

        :param close_quote: The close quote character to match for the end of the quoted string.
        :return: The quoted string sans open and close quotes. This can be an empty string.
        """
        builder = StringBuilder()
        end_quote_found = False
        while self.move_next():
            if self.current == close_quote:
                self.move_next()
                end_quote_found = True
                break
            if self.current == "\\":
                if not self.move_next():
                    raise InvalidPatternError(TextErrorMessages.ESCAPE_AT_END_OF_STRING)
            builder.append(self.current)
        if not end_quote_found:
            raise InvalidPatternError(TextErrorMessages.MISSING_END_QUOTE, close_quote)
        self.move_previous()
        return builder.to_string()

    def get_repeat_count(self, maximum_count: int) -> int:
        """Gets the pattern repeat count.

        The cursor is left on the final character of the repeated sequence.

        :param maximum_count: The maximum number of repetitions allowed.
        :return: The repetition count which is always at least ``1``.
        """
        pattern_character = self.current
        start_position = self.index
        while self.move_next() and (self.current == pattern_character):
            pass
        repeat_length = self.index - start_position
        # Move the cursor back to the last character of the repeated pattern
        self.move_previous()
        if repeat_length > maximum_count:
            raise InvalidPatternError(TextErrorMessages.REPEAT_COUNT_EXCEEDED, pattern_character, maximum_count)
        return repeat_length

    def get_embedded_pattern(self) -> str:
        """Returns a string containing the embedded pattern within this one.

        The cursor is expected to be positioned immediately before the ``_EMBEDDED_PATTERN_START`` character (``<``),
        and on success the cursor will be positioned on the ``_EMBEDDED_PATTERN_END`` character (``>``).

        Quote characters (``'`` and ``"``) and escaped characters (escaped with a backslash) are handled
        but not unescaped: the resulting pattern should be ready for parsing as normal. It is assumed that the
        embedded pattern will itself handle embedded patterns, so if the input is on the first ``<``
        of ``"before <outer1 <inner> outer2> after"``
        this method will return ``"outer1 <inner> outer2"`` and the cursor will be positioned
        on the final ``>`` afterwards.

        :return: The embedded pattern, not including the start/end pattern characters.
        """
        if (not self.move_next()) or (self.current != self._EMBEDDED_PATTERN_START):
            raise InvalidPatternError(TextErrorMessages.MISSING_EMBEDDED_PATTERN_START, self._EMBEDDED_PATTERN_START)
        start_index = self.index + 1
        depth = 1  # For nesting
        while self.move_next():
            current = self.current
            if current == self._EMBEDDED_PATTERN_END:
                depth -= 1
                if depth == 0:
                    return self.value[start_index : self.index]
            elif current == self._EMBEDDED_PATTERN_START:
                depth += 1
            elif current == "\\":
                if not self.move_next():
                    raise InvalidPatternError(TextErrorMessages.ESCAPE_AT_END_OF_STRING)
            elif current == "'" or current == '"':
                # We really don't care about the value here. It's slightly inefficient to
                # create the substring and then ignore it, but it's unlikely to be significant.
                _ = self.get_quoted_string(current)
        # We've reached the end of the enclosing pattern without reaching the end of the embedded pattern. Oops.
        raise InvalidPatternError(TextErrorMessages.MISSING_EMBEDDED_PATTERN_END, self._EMBEDDED_PATTERN_END)
