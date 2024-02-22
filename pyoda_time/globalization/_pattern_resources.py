# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final


class _PatternResources:
    """Constants for patterns.

    In Noda Time, this is a wrapper around a ResourceManager and the eponymous .resx.
    """

    ERAS_ANNO_HEGIRAE: Final[str] = "A.H.|AH"
    ERAS_ANNO_MARTYRUM: Final[str] = "A.M.|AM"
    ERAS_ANNO_MUNDI: Final[str] = "A.M.|AM"
    ERAS_ANNO_PERSICO: Final[str] = "A.P.|AP"
    ERAS_BAHAI: Final[str] = "B.E.|BE"
    ERAS_BEFORE_COMMON: Final[str] = "B.C.|B.C.E.|BC|BCE"
    ERAS_COMMON: Final[str] = "A.D.|AD|C.E.|CE"
    OFFSET_PATTERN_LONG: Final[str] = "+HH:mm:ss"
    OFFSET_PATTERN_LONG_NO_PUNCTUATION: Final[str] = "+HHmmss"
    OFFSET_PATTERN_MEDIUM: Final[str] = "+HH:mm"
    OFFSET_PATTERN_MEDIUM_NO_PUNCTUATION: Final[str] = "+HHmm"
    OFFSET_PATTERN_SHORT: Final[str] = "+HH"
    OFFSET_PATTERN_SHORT_NO_PUNCTUATION: Final[str] = "+HH"
