# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._globalization_mode import _GlobalizationMode
from pyoda_time._compatibility._gregorian_calendar import GregorianCalendar
from pyoda_time._compatibility._gregorian_calendar_helper import _EraInfo


class JapaneseCalendar(Calendar):
    """JapaneseCalendar is based on Gregorian calendar.  The month and day values are the same as Gregorian calendar.
    However, the year value is an offset to the Gregorian year based on the era.

    This system is adopted by Emperor Meiji in 1868. The year value is counted based on the reign of an emperor,
    and the era begins on the day an emperor ascends the throne and continues until his death.
    The era changes at 12:00AM.

    For example, the current era is Reiwa. It started on 2019/5/1 A.D.  Therefore, Gregorian year 2019 is also Reiwa
    1st. 2019/5/1 A.D. is also Reiwa 1st 5/1.

    Any date in the year during which era is changed can be reckoned in either era. For example,
    2019/1/1 can be 1/1 Reiwa 1st year or 1/1 Heisei 31st year.

    Note: The DateTime can be represented by the JapaneseCalendar are limited to two factors:
        1. The min value and max value of DateTime class.
        2. The available era information.

    Calendar support range:
        ==========  ===========  =================
        Calendar    Minimum      Maximum
        ==========  ===========  =================
        Gregorian   1868/09/08   9999/12/31
        Japanese    Meiji 01/01  Reiwa 7981/12/31
        ==========  ===========  =================
    """

    __s_japanese_era_info: list[_EraInfo] | None = None

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.JAPAN

    def __init__(self) -> None:
        super().__init__()
        from ._culture_info import CultureInfo

        try:
            CultureInfo("ja-JP")
        except Exception as e:
            raise TypeError(self.__class__.__name__) from e

    @classmethod
    def _era_names(cls) -> list[str]:
        eras: list[_EraInfo] = cls._get_era_info()  # noqa
        # TODO: JapaneseCalendar.EraNames()
        raise NotImplementedError("unfinished implementation")

    @classmethod
    def _get_era_info(cls) -> list[_EraInfo]:
        r"""m_EraInfo must be listed in reverse chronological order. The most recent era should be the first element.
        That is, m_EraInfo[0] contains the most recent era.

        We know about 4 built-in eras, however users may add additional era(s) from the
        registry, by adding values to HKLM\SYSTEM\CurrentControlSet\Control\Nls\Calendars\Japanese\Eras
        we don't read the registry and instead we call WinRT to get the needed information

        Registry values look like:
             yyyy.mm.dd=era_abbrev_english_englishabbrev

        Where yyyy.mm.dd is the registry value name, and also the date of the era start.
        yyyy, mm, and dd are the year, month & day the era begins (4, 2 & 2 digits long)
        era is the Japanese Era name
        abbrev is the Abbreviated Japanese Era Name
        english is the English name for the Era (unused)
        englishabbrev is the Abbreviated English name for the era.
        . is a delimiter, but the value of . doesn't matter.
        '_' marks the space between the japanese era name, japanese abbreviated era name
            english name, and abbreviated english names.
        """

        # See if we need to build it
        if cls.__s_japanese_era_info is None:
            if _GlobalizationMode._use_nls:
                raise NotImplementedError("NlsGetJapaneseEras()")
            cls.__s_japanese_era_info = cls.__icu_get_japanese_eras() or [
                _EraInfo(5, 2019, 5, 1, 2018, 1, GregorianCalendar._MAX_YEAR - 2018, "\u4ee4\u548c", "\u4ee4", "R"),
                _EraInfo(4, 1989, 1, 8, 1988, 1, 2019 - 1988, "\u5e73\u6210", "\u5e73", "H"),
                _EraInfo(3, 1926, 12, 25, 1925, 1, 1989 - 1925, "\u662d\u548c", "\u662d", "S"),
                _EraInfo(2, 1912, 7, 30, 1911, 1, 1926 - 1911, "\u5927\u6b63", "\u5927", "T"),
                _EraInfo(1, 1868, 1, 1, 1867, 1, 1912 - 1867, "\u660e\u6cbb", "\u660e", "M"),
            ]

        return cls.__s_japanese_era_info

    @classmethod
    def __icu_get_japanese_eras(cls) -> list[_EraInfo] | None:
        if _GlobalizationMode._invariant:
            return None

        assert not _GlobalizationMode._use_nls

        # TODO: Noped out of this for now... implement later

        return None
