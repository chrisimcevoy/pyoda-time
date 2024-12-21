# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO

if TYPE_CHECKING:
    from collections.abc import Buffer


class _IoStream:
    """Provides a simple, fixed-size, pipe-like stream that has a writer and a reader.

    When the buffer fills up an exception is thrown and currently the buffer is fixed at 4096. The write pointer does
    not wrap so only a total of 4096 bytes can ever be written to the stream. This is designed for testing purposes and
    not real-world uses.
    """

    def __init__(self) -> None:
        self._buffer: bytearray = bytearray(4096)
        self._read_index = 0
        self.__read_stream: BinaryIO | None = None
        self._write_index = 0
        self.__write_stream: BinaryIO | None = None

    def __get_byte(self) -> int:
        """Returns the next byte from the stream if there is one.

        :return: The next byte.
        """
        if self._read_index >= self._write_index:
            raise OSError("IoStream buffer empty in GetByte()")
        self._read_index += 1
        return self._buffer[self._read_index]

    def assert_end_of_stream(self) -> None:
        assert self._read_index == self._write_index

    def assert_unread_contents(self, expected: bytes) -> None:
        assert self._write_index - self._read_index == len(expected)
        actual = self._buffer[self._read_index : self._write_index]
        assert actual == expected
        self._read_index = self._write_index

    def get_read_stream(self) -> BinaryIO:
        """Returns a ``BinaryIO`` that can be used to read from the buffer.

        This can only be called once for each instance i.e. only one reader is permitted per buffer.

        :return: The read-only ``BinaryIO``.
        :raises RuntimeError: A reader was already requested.
        """
        if self.__read_stream is not None:
            raise RuntimeError("Cannot call GetReadStream() twice on the same object.")
        self.__read_stream = self._ReadStreamImpl(self)
        return self.__read_stream

    def get_write_stream(self) -> BinaryIO:
        """Returns a ``BinaryIO`` that can be used to write to the buffer.

        This can only be called once for each instance i.e. only one writer is permitted per buffer.

        :return: The write-only ``BinaryIO``.
        :raises RuntimeError: A writer was already requested.
        """
        if self.__write_stream is not None:
            raise RuntimeError("Cannot call GetWriteStream() twice on the same object.")
        self.__write_stream = self._WriteStreamImpl(self)
        return self.__write_stream

    def put_byte(self, value: int) -> None:
        """Adds a byte to the buffer.

        :param value: The byte to add.
        """
        if self._write_index >= len(self._buffer):
            raise OSError(f"Exceeded the IoStream buffer size of {len(self._buffer)}")
        self._write_index += 1
        self._buffer[self._write_index] = value

    def reset(self) -> None:
        """Resets the stream to be empty."""
        self._write_index = self._read_index = 0

    class _ReadStreamImpl(BytesIO):
        """Provides a read-only ``BinaryIO`` implementation for reading from the buffer."""

        def __init__(self, stream: _IoStream) -> None:
            super().__init__()
            self.__io_stream = stream
            self.__closed = False

        def readable(self) -> bool:
            return True

        def read(self, size: int | None = -1) -> bytes:
            """Read up to 'size' bytes from the stream.

            Returns the data read as bytes. If size is negative or None, read until the end of the stream.
            """
            if size is None:
                size = -1
            if self.__closed:
                raise ValueError("read from closed file")
            if size < 0:
                size = self.__io_stream._write_index - self.__io_stream._read_index
            else:
                size = min(size, self.__io_stream._write_index - self.__io_stream._read_index)

            start_index = self.__io_stream._read_index
            self.__io_stream._read_index += size
            return bytes(self.__io_stream._buffer[start_index : self.__io_stream._read_index])

        def close(self) -> None:
            """Flush and close the IO object."""
            self.__closed = True
            super().close()

    class _WriteStreamImpl(BytesIO):
        """Provides a write-only stream implementation for writing to the buffer."""

        def __init__(self, io_stream: _IoStream) -> None:
            super().__init__()
            self._io_stream = io_stream
            self._closed = False

        def writable(self) -> bool:
            """Return True if the stream supports writing."""
            return True

        def write(self, __buffer: Buffer, /) -> int:
            """Write the bytes-like object, b, to the underlying buffer.

            Returns the number of bytes written, which may be less than the length of b.
            """
            if self._closed:
                raise ValueError("write to closed file")
            if not isinstance(__buffer, bytes):
                raise TypeError("a bytes-like object is required, not " + type(__buffer).__name__)
            available_space = len(self._io_stream._buffer) - self._io_stream._write_index

            if available_space <= 0:
                raise OSError("Buffer is full")

            num_bytes_to_write = min(len(__buffer), available_space)

            self._io_stream._buffer[
                self._io_stream._write_index : self._io_stream._write_index + num_bytes_to_write
            ] = __buffer[:num_bytes_to_write]
            self._io_stream._write_index += num_bytes_to_write
            return num_bytes_to_write

        def close(self) -> None:
            """Flush and close the IO object."""
            self._closed = True
            super().close()

        def flush(self) -> None:
            """Flush the stream buffer."""
            # In this case, flush doesn't need to do anything because
            # we are directly writing to the buffer and not holding anything in a temporary storage.
            pass
