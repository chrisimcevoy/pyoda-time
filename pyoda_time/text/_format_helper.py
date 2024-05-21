# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.utility._csharp_compatibility import _csharp_modulo, _CsharpConstants, _towards_zero_division


class _FormatHelper:
    """Provides helper methods for formatting values using pattern strings."""

    @staticmethod
    def _format_2_digits_non_negative(value: int, output_buffer: StringBuilder) -> None:
        """Formats the given value to two digits, left-padding with '0' if necessary.

        It is assumed that the value is in the range [0, 100). This is usually used for month, day-of-month, hour,
        minute, second and year-of-century values.
        """
        # TODO: Preconditions.DebugCheckArgumentRange
        # TODO: unchecked
        # TODO: This is pretty different (but more idiomatic Python) compared to Noda Time.
        output_buffer.append(f"{value:02}")

    @staticmethod
    def _format_4_digits_value_fits(value: int, output_buffer: StringBuilder) -> None:
        """Formats the given value to two digits, left-padding with '0' if necessary.

        It is assumed that the value is in the range [-9999, 10000). This is usually used for year values. If the value
        is negative, a '-' character is prepended.
        """
        # TODO: Preconditions.DebugCheckArgumentRange
        # TODO: unchecked
        # TODO: This is pretty different (but more idiomatic Python) compared to Noda Time.
        if value < 0:
            value = -value
            output_buffer.append("-")
        output_buffer.append(f"{value:04}")

    @classmethod
    def _left_pad(cls, value: int, length: int, output_buffer: StringBuilder) -> None:
        """Formats the given value left padded with zeros.

        Left pads with zeros the value into a field of ``length`` characters. If the value
        is longer than ``length``, the entire value is formatted. If the value is negative,
        it is preceded by "-" but this does not count against the length.

        :param value: The value to format.
        :param length: The length to fill.
        :param output_buffer: The output buffer to add the digits to.
        :return:
        """
        # TODO: Preconditions.DebugCheckArgumentRange(nameof(length), length, 1, MaximumPaddingLength);
        # TODO: unchecked
        if value >= 0:
            cls._left_pad_non_negative(value, length, output_buffer)
            return
        output_buffer.append("-")
        # Special case, as we can't use Math.Abs.
        if value == _CsharpConstants.INT_MIN_VALUE:
            if length > 10:
                output_buffer.append("000000"[16 - length :])
            output_buffer.append("2147483648")
            return
        cls._left_pad_non_negative(-value, length, output_buffer)

    @staticmethod
    def _left_pad_non_negative(value: int, length: int, output_buffer: StringBuilder) -> None:
        """Formats the given value left padded with zeros. The value is assumed to be non-negative.

        Left pads with zeros the value into a field of ``length`` characters. If the value
        is longer than ``length``, the entire value is formatted. If the value is negative,
        it is preceded by "-" but this does not count against the length.

        :param value: The value to format.
        :param length: The length to fill.
        :param output_buffer: The output buffer to add the digits to.
        :return:
        """
        # TODO: Preconditions.DebugCheckArgumentRange, something like:
        #  assert if value > 0 and length > 1, "Value must be non-negative and length must be at least 1")

        # TODO: unchecked

        # TODO: This is dramatically more simple than the Noda Time implementation,
        #  which optimizes common cases to prevent heap allocations.

        # Using an f-string for formatting
        formatted_value = f"{value:0>{length}}"

        output_buffer.append(formatted_value)

    @classmethod
    def _append_fraction(cls, value: int, length: int, scale: int, output_buffer: StringBuilder) -> None:
        """Formats the given value, which is an integer representation of a fraction.

        Note: current usage means this never has to cope with negative numbers.

        ``AppendFraction(1200, 4, 5, builder`` will result in "0120" being
        appended to the builder. The value is treated as effectively 0.01200 because
        the scale is 5, but only 4 digits are formatted.

        :param value: The value to format.
        :param length: The length to fill. Must be at most ``scale``.
        :param scale: The scale of the value i.e. the number of significant digits is the range of the value. Must be
            in the range [1, 7].
        :param output_buffer: The output buffer to add the digits to.
        """
        relevant_digits = value

        while scale > length:
            relevant_digits = _towards_zero_division(relevant_digits, 10)
            scale -= 1

        # Create the formatted string with leading zeros.
        # This is very different to the Noda Time implementation.
        formatted_string = f"{relevant_digits:0{length}d}"

        output_buffer.append(formatted_string)

    @classmethod
    def _append_fraction_truncate(cls, value: int, length: int, scale: int, output_buffer: StringBuilder) -> None:
        """Formats the given value, which is an integer representation of a fraction, truncating any right-most zero
        digits.

        If the entire value is truncated then the preceding decimal separator is also removed.

        Note: current usage means this never has to cope with negative numbers.

        ``_append_fraction_truncate(1200, 4, 5, builder)`` will result in "001" being
        appended to the builder. The value is treated as effectively 0.01200 because
        the scale is 5; only 4 digits are formatted (leaving "0120") and then the rightmost
        0 digit is truncated.

        :param value: The value to format.
        :param length: The length to fill. Must be at most ``scale``.
        :param scale: The scale of the value i.e. the number of significant digits is the range of the value. Must be
            in the range [1, 7].
        :param output_buffer: The output buffer to add the digits to.
        """
        relevant_digits = value

        while scale > length:
            relevant_digits = _towards_zero_division(relevant_digits, 10)
            scale -= 1

        relevant_length = length
        while relevant_length > 0:
            if _csharp_modulo(relevant_digits, 10) != 0:
                break
            relevant_digits = _towards_zero_division(relevant_digits, 10)
            relevant_length -= 1

        if relevant_length > 0:
            formatted_string = f"{relevant_digits:0{relevant_length}d}"
            output_buffer.append(formatted_string)
        # Check and remove a preceding decimal point if necessary
        elif output_buffer.length > 0 and output_buffer[output_buffer.length - 1] == ".":
            output_buffer.length -= 1

    @classmethod
    def _format_invariant(cls, value: int, output_buffer: StringBuilder) -> None:
        """Formats the given value using the invariant culture, with no truncation or padding.

        :param value: The value to format.
        :param output_buffer: The output buffer to add the digits to.
        """
        # TODO: This is very, very different from the Noda Time implementation
        output_buffer.append(str(value))
