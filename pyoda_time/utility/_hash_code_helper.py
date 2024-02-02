# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations as _annotations

__all__: list[str] = []

import typing as _typing


def _hash_code_helper(*values: _typing.Hashable) -> int:
    """Provides help with generating hash codes."""
    # In Noda Time, this is a builder pattern struct.
    multiplier = 37
    ret = 17
    for v in values:
        ret += ret * multiplier + hash(v)
    return ret
