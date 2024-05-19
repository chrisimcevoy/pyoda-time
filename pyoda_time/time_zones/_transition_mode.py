# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from enum import IntEnum


class _TransitionMode(IntEnum):
    """Specifies how transitions are calculated.

    Whether relative to UTC, the time zones standard offset, or the wall (or daylight savings) offset.
    """

    UTC = 0
    """Calculate transitions against UTC."""
    WALL = 1
    """Calculate transitions against wall offset."""
    STANDARD = 2
    """Calculate transitions against standard offset."""
