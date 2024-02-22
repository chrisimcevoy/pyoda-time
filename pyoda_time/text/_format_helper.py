# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._string_builder import StringBuilder


class FormatHelper:
    """Provides helper methods for formatting values using pattern strings."""

    @staticmethod
    def format_2_digits_non_negative(value: int, output_buffer: StringBuilder) -> None:
        """Formats the given value to two digits, left-padding with '0' if necessary.

        It is assumed that the value is in the range [0, 100). This is usually used for month, day-of-month, hour,
        minute, second and year-of-century values.
        """
        # TODO: Preconditions.DebugCheckArgumentRange
        # TODO: unchecked
        # TODO: This is pretty different (but more idiomatic Python) compared to Noda Time.
        output_buffer.append(f"{value:02}")

    @staticmethod
    def format_4_digits_value_fits(value: int, output_buffer: StringBuilder) -> None:
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

    @staticmethod
    def left_pad(value: int, length: int, output_buffer: StringBuilder) -> None:
        """Formats the given value left padded with zeros.

        Left pads with zeros the value into a field of ``length`` characters. If the value
        is longer than ``length``, the entire value is formatted. If the value is negative,
        it is preceded by "-" but this does not count against the length.

        :param value: The value to format.
        :param length: The length to fill.
        :param output_buffer: The output buffer to add the digits to.
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def left_pad_non_negative(value: int, length: int, output_buffer: StringBuilder) -> None:
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
