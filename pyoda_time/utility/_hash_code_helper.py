# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable

__all__: list[str] = []


def _hash_code_helper(*values: Hashable) -> int:
    """Provides help with generating hash codes."""
    # In Noda Time, this is a builder pattern struct.
    multiplier = 37
    ret = 17
    for v in values:
        ret += ret * multiplier + hash(v)
    return ret
