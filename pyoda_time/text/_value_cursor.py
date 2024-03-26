# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import math
from typing import final

from ..utility._csharp_compatibility import _CsharpConstants, _sealed
from ._parse_result import ParseResult
from ._text_cursor import _TextCursor


@final
@_sealed
class _ValueCursor(_TextCursor):
    def _match(self, match: str) -> bool:
        """Attempts to match the specified string with the current point in the string. If the character matches then
        the index is moved past the string.

        :param match: The string to match.
        :return: ``True`` if the string matches.
        """
        target_index = self.index + len(match)
        if self.value[self.index : target_index] == match:
            self.move(target_index)
            return True
        return False

    # TODO: We don't have CompareInfo.Compare() in Python
    #  internal bool MatchCaseInsensitive(string match, CompareInfo compareInfo, bool moveOnSuccess)
    def _match_case_insensitive(self, match: str, move_on_success: bool) -> bool:
        """Attempts to match the specified string with the current point in the string in a case-insensitive manner,
        according to the given comparison info.

        The cursor is optionally updated to the end of the match.
        """

        # TODO: This is very different to the Noda Time implementation!

        if len(match) > len(self.value) - self.index:
            return False

        # Extract the substring from the current index to the length of the match string
        substring = self.value[self.index : self.index + len(match)]

        # Compare the case-insensitive substrings
        if substring.lower() == match.lower():
            if move_on_success:
                # Move the cursor to the end of the matched segment
                self.move(self.index + len(match))
            return True
        return False

    def _compare_ordinal(self, match: str) -> int:
        """Compares the value from the current cursor position with the given match. If the
        given match string is longer than the remaining length, the comparison still goes
        ahead but the result is never 0: if the result of comparing to the end of the
        value returns 0, the result is -1 to indicate that the value is earlier than the given match.
        Conversely, if the remaining value is longer than the match string, the comparison only
        goes as far as the end of the match. So "xabcd" with the cursor at "a" will return 0 when
        matched with "abc".

        :param match: The string to compare with the current cursor position.
        :return: A negative number if the value (from the current cursor position) is lexicographically
            earlier than the given match string; 0 if they are equal (as far as the end of the match) and
            a positive number if the value is lexicographically later than the given match string.
        """
        remaining = self.value[self.index :]
        if len(match) > len(remaining):
            # If match is longer than remaining, compare up to the end of remaining.
            # If they are equal, return -1 to indicate `value` is earlier than `match`.
            result = (remaining > match[: len(remaining)]) - (remaining < match[: len(remaining)])
            return -1 if result == 0 else result
        else:
            # If remaining is longer or equal, compare up to the length of match.
            result = (remaining[: len(match)] > match) - (remaining[: len(match)] < match)
            return result

    def _parse_int64(self) -> tuple[ParseResult[None] | None, int]:
        """Parses digits at the current point in the string as a signed 64-bit integer value. Currently this method only
        supports cultures whose negative sign is "-" (and using ASCII digits).

        :return: A 2-tuple of either a ``ParseResult`` or ``None`` depending on whether the parse operation succeeded,
            and the result integer value. The value of this is not guaranteed to be anything specific if the return
            value is non-null.
        """
        # TODO: unchecked
        result = 0
        start_index = self.index
        negative = self.current == "-"
        if negative:
            if not self.move_next():
                self.move(start_index)
                return ParseResult._end_of_string(self), result
        count = 0
        digit: int
        while result < 922337203685477580 and ((digit := self.__get_digit()) != -1):
            result = result * 10 + digit
            count += 1
            if not self.move_next():
                break

        if count == 0:
            self.move(start_index)
            return ParseResult._missing_number(self), result

        if result >= 922337203685477580 and (digit := self.__get_digit()) != -1:
            if result > 922337203685477580:
                return self.__build_number_out_of_range_result(start_index), result
            if negative and (digit == 8):
                self.move_next()
                result = _CsharpConstants.LONG_MIN_VALUE
                return None, result
            if digit > 7:
                return self.__build_number_out_of_range_result(start_index), result
            # We know we can cope with this digit
            result = result * 10 + digit
            self.move_next()
            if self.__get_digit() != -1:
                # Too many digits. Die.
                return self.__build_number_out_of_range_result(start_index), result

        if negative:
            result = -result
        return None, result

    def __build_number_out_of_range_result(self, start_index: int) -> ParseResult[None]:
        self.move(start_index)
        if self.current == "-":
            self.move_next()
        # End of string works like not finding a digit.
        while self.__get_digit() != -1:
            self.move_next()
        bad_value = self.value[start_index : self.index - start_index]
        self.move(start_index)
        return ParseResult._value_out_of_range(self, bad_value)

    def _parse_digits(self, minimum_digits: int, maximum_digits: int) -> tuple[bool, int]:
        """Parses digits at the current point in the string. If the minimum required digits are not present then the
        index is unchanged. If there are more digits than the maximum allowed they are ignored.

        :param minimum_digits: The minimum allowed digits.
        :param maximum_digits: The maximum allowed digits.
        :return: A 2-tuple of a bool indicating success/failure, and the result integer value. The value of this is not
            guaranteed to be anything specific if the return value is false.
        """
        # TODO: unchecked
        result = 0
        local_index = self.index
        max_index = local_index + maximum_digits
        if max_index >= self.length:
            max_index = self.length
        while local_index < max_index:
            digit = self.value[local_index]
            if not digit.isdigit():
                break
            result = result * 10 + int(digit)
            local_index += 1
        count: int = local_index - self.index
        if count < minimum_digits:
            return False, result
        self.move(local_index)
        return True, result

    def _parse_fraction(self, maximum_digits: int, scale: int, minimum_digits: int) -> tuple[bool, int]:
        """Parses digits at the current point in the string as a fractional value.

        :param maximum_digits: The maximum allowed digits. Trusted to be less than or equal to scale.
        :param scale: The scale of the fractional value.
        :param minimum_digits: The minimum number of digits that must be specified in the value.
        :return: A 2-tuple of a bool indicating success/failure, and the result integer scaled by scale. The value of
            this integer is not guaranteed to be anything specific if the return value is false.
        """
        # TODO: unchecked

        # TODO: Preconditions.DebugCheckArgument

        result = 0
        local_index = self.index
        min_index = local_index + minimum_digits
        if min_index >= self.length:
            # If we don't have all the digits we're meant to have, we can't possibly succeed.
            return False, result
        max_index = min(local_index + maximum_digits, self.length)
        while local_index < max_index:
            digit = self.value[local_index]
            if not digit.isdigit():
                break
            result = result * 10 + int(digit)
            local_index += 1
        count: int = local_index - self.index
        # Couldn't parse the minimum number of digits required?
        if count < minimum_digits:
            return False, result
        result = int(result * math.pow(10.0, scale - count))
        self.move(local_index)
        return True, result

    def __get_digit(self) -> int:
        """Gets the integer value of the current digit character, or -1 for "not a digit".

        This currently only handles ASCII digits, which is all we have to parse to stay in line with the BCL.
        """
        # TODO unchecked
        if self.current.isdigit():
            return int(self.current)
        return -1
