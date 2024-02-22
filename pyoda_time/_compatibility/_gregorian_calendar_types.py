# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from enum import Enum

from pyoda_time._compatibility._calendar_id import _CalendarId


class GregorianCalendarTypes(Enum):
    """Defines the different language versions of the Gregorian calendar."""

    Localized = _CalendarId.GREGORIAN
    USEnglish = _CalendarId.GREGORIAN_US
    MiddleEastFrench = _CalendarId.GREGORIAN_ME_FRENCH
    Arabic = _CalendarId.GREGORIAN_ARABIC
    TransliteratedEnglish = _CalendarId.GREGORIAN_XLIT_ENGLISH
    TransliteratedFrench = _CalendarId.GREGORIAN_XLIT_FRENCH
