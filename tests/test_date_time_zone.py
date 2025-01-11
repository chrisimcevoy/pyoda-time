# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

import pytest

from pyoda_time import (
    AmbiguousTimeError,
    DateTimeZone,
    DateTimeZoneProviders,
    Duration,
    Instant,
    Interval,
    IsoDayOfWeek,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Offset,
    PyodaConstants,
    SkippedTimeError,
    ZonedDateTime,
)
from pyoda_time.testing.time_zones import SingleTransitionDateTimeZone
from pyoda_time.text import LocalDatePattern
from pyoda_time.time_zones import Resolvers, ZoneInterval, ZoneLocalMapping


class TestDateTimeZone:
    def test_for_offset_uncached_example_not_on_half_hour(self) -> None:
        """The current implementation caches every half hour, -12 to +15."""
        offset = Offset.from_seconds(123)
        zone1 = DateTimeZone.for_offset(offset)
        zone2 = DateTimeZone.for_offset(offset)

        assert zone1 is not zone2
        assert zone1._is_fixed
        assert zone1.max_offset == offset
        assert zone1.min_offset == offset

    def for_offset_uncached_example_outside_cache_range(self) -> None:
        offset = Offset.from_hours(-14)
        zone1 = DateTimeZone.for_offset(offset)
        zone2 = DateTimeZone.for_offset(offset)

        assert zone1 is not zone2
        assert zone1._is_fixed
        assert zone1.max_offset == offset
        assert zone1.min_offset == offset

    def test_for_offset_cached_example(self) -> None:
        offset = Offset.from_hours(2)
        zone1 = DateTimeZone.for_offset(offset)
        zone2 = DateTimeZone.for_offset(offset)
        # Caching check...
        assert zone1 is zone2

        assert zone1._is_fixed
        assert zone1.max_offset == offset
        assert zone1.min_offset == offset

    def test_for_offset_zero_same_as_utc(self) -> None:
        assert DateTimeZone.for_offset(Offset.zero) is DateTimeZone.utc


class TestDateTimeZoneGetZoneIntervals:
    TEST_ZONE = SingleTransitionDateTimeZone(
        transition_point=Instant.from_utc(2000, 1, 1, 0, 0),
        offset_before=-3,
        offset_after=4,
    )

    def test_get_zone_intervals_end_before_start(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            DateTimeZone.utc.get_zone_intervals(
                start=Instant.from_unix_time_ticks(100),
                end=Instant.from_unix_time_ticks(99),
            )

    def test_get_zone_intervals_end_equal_to_start(self) -> None:
        zone_intervals = DateTimeZone.utc.get_zone_intervals(
            start=Instant.from_unix_time_ticks(100),
            end=Instant.from_unix_time_ticks(100),
        )
        assert list(zone_intervals) == []

    # TODO: def test_get_zone_intervals_invalid_options(self) -> None:

    def test_get_zone_intervals_fixed_zone(self) -> None:
        zone = DateTimeZone.for_offset(Offset.from_hours(3))
        expected = {zone.get_zone_interval(Instant.min_value)}
        # Give a reasonably wide interval...
        actual = zone.get_zone_intervals(
            start=Instant.from_utc(1900, 1, 1, 0, 0),
            end=Instant.from_utc(2100, 1, 1, 0, 0),
        )
        assert set(actual) == expected

    def test_get_zone_intervals_single_transition_zone_interval_covers_transition(self) -> None:
        start: Instant = self.TEST_ZONE.transition - Duration.from_days(5)
        end: Instant = self.TEST_ZONE.transition + Duration.from_days(5)
        expected = {self.TEST_ZONE.early_interval, self.TEST_ZONE.late_interval}
        actual = set(self.TEST_ZONE.get_zone_intervals(start=start, end=end))
        assert actual == expected

    def test_get_zone_intervals_single_transition_zone_interval_does_not_cover_transition(self) -> None:
        start: Instant = self.TEST_ZONE.transition - Duration.from_days(10)
        end: Instant = self.TEST_ZONE.transition - Duration.from_days(5)
        expected = {self.TEST_ZONE.early_interval}
        actual = set(self.TEST_ZONE.get_zone_intervals(start=start, end=end))
        assert actual == expected

    def test_get_zone_intervals_includes_start(self) -> None:
        start: Instant = self.TEST_ZONE.transition - Duration.epsilon
        end: Instant = self.TEST_ZONE.transition + Duration.from_days(5)
        expected = {self.TEST_ZONE.early_interval, self.TEST_ZONE.late_interval}
        actual = set(self.TEST_ZONE.get_zone_intervals(start=start, end=end))
        assert actual == expected

    def test_get_zone_intervals_excludes_end(self) -> None:
        start: Instant = self.TEST_ZONE.transition - Duration.from_days(10)
        end: Instant = self.TEST_ZONE.transition
        expected = {self.TEST_ZONE.early_interval}
        actual = set(self.TEST_ZONE.get_zone_intervals(start=start, end=end))
        assert actual == expected

    def test_get_zone_intervals_complex(self) -> None:
        london = DateTimeZoneProviders.tzdb["Europe/London"]
        # Transitions are always Spring/Autumn, so June and January should be clear.
        expected = {
            london.get_zone_interval(Instant.from_utc(1999, 6, 1, 0, 0)),
            london.get_zone_interval(Instant.from_utc(2000, 1, 1, 0, 0)),
            london.get_zone_interval(Instant.from_utc(2000, 6, 1, 0, 0)),
            london.get_zone_interval(Instant.from_utc(2001, 1, 1, 0, 0)),
            london.get_zone_interval(Instant.from_utc(2001, 6, 1, 0, 0)),
            london.get_zone_interval(Instant.from_utc(2002, 1, 1, 0, 0)),
        }
        # After the instant we used to fetch the expected zone interval, but that's fine:
        # it'll be the same one, as there's no transition within June.
        start = Instant.from_utc(1999, 6, 19, 0, 0)
        end = Instant.from_utc(2002, 2, 4, 0, 0)
        actual = set(london.get_zone_intervals(start=start, end=end))
        assert actual == expected
        # Just to exercise the other overload
        actual = set(london.get_zone_intervals(interval=Interval(start=start, end=end)))
        assert actual == expected

    # TODO: def test_get_zone_intervals_with_options_no_coalescing(self) -> None:
    # TODO: def test_get_zone_intervals_with_options_coalescing(self) -> None:


class TestDateTimeZoneIds:
    def test_utc_is_not_null(self) -> None:
        assert DateTimeZone.utc is not None


class TestDateTimeZoneLocalConversion:
    """Tests for aspects of DateTimeZone to do with converting from LocalDateTime and LocalDate to ZonedDateTime."""

    # Sample time zones for DateTimeZone.AtStartOfDay etc. I didn't want to only test midnight transitions.
    LOS_ANGELES: Final[DateTimeZone] = DateTimeZoneProviders.tzdb["America/Los_Angeles"]
    NEW_ZEALAND: Final[DateTimeZone] = DateTimeZoneProviders.tzdb["Pacific/Auckland"]
    PARIS: Final[DateTimeZone] = DateTimeZoneProviders.tzdb["Europe/Paris"]
    NEW_YORK: Final[DateTimeZone] = DateTimeZoneProviders.tzdb["America/New_York"]
    PACIFIC: Final[DateTimeZone] = DateTimeZoneProviders.tzdb["America/Los_Angeles"]

    TRANSITION_FORWARD_AT_MIDNIGHT_ZONE: Final[DateTimeZone] = SingleTransitionDateTimeZone(
        transition_point=Instant.from_utc(2000, 6, 1, 2, 0),
        offset_before=Offset.from_hours(-2),
        offset_after=Offset.from_hours(-1),
    )
    """Local midnight at the start of the transition (June 1st) becomes 1am."""

    TRANSITION_BACKWARD_TO_MIDNIGHT_ZONE: Final[DateTimeZone] = SingleTransitionDateTimeZone(
        transition_point=Instant.from_utc(2000, 6, 1, 3, 0),
        offset_before=Offset.from_hours(-2),
        offset_after=Offset.from_hours(-3),
    )
    """Local 1am at the start of the transition (June 1st) becomes midnight."""

    TRANSITION_FORWARD_BEFORE_MIDNIGHT_ZONE: Final[DateTimeZone] = SingleTransitionDateTimeZone(
        transition_point=Instant.from_utc(2000, 6, 1, 1, 20),
        offset_before=Offset.from_hours(-2),
        offset_after=Offset.from_hours(-1),
    )
    """Local 11.20pm at the start of the transition (May 30th) becomes 12.20am of June 1st."""

    TRANSITION_BACKWARD_AFTER_MIDNIGHT_ZONE: Final[DateTimeZone] = SingleTransitionDateTimeZone(
        transition_point=Instant.from_utc(2000, 6, 1, 2, 20),
        offset_before=Offset.from_hours(-2),
        offset_after=Offset.from_hours(-3),
    )
    """Local 12.20am at the start of the transition (June 1st) becomes 11.20pm of the previous day."""

    TRANSITION_DATE: Final[LocalDate] = LocalDate(2000, 6, 1)

    def test_ambiguous_start_of_day_transition_at_midnight(self) -> None:
        # Occurrence before transition
        expected = ZonedDateTime._ctor(
            offset_date_time=LocalDateTime(2000, 6, 1, 0, 0).with_offset(Offset.from_hours(-2)),
            zone=self.TRANSITION_BACKWARD_TO_MIDNIGHT_ZONE,
        )
        actual = self.TRANSITION_BACKWARD_TO_MIDNIGHT_ZONE.at_start_of_day(self.TRANSITION_DATE)
        assert actual == expected
        assert self.TRANSITION_DATE.at_start_of_day_in_zone(self.TRANSITION_BACKWARD_TO_MIDNIGHT_ZONE) == expected

    def test_ambiguous_start_of_day_transition_after_midnight(self) -> None:
        # Occurrence before transition
        expected = ZonedDateTime._ctor(
            offset_date_time=LocalDateTime(2000, 6, 1, 0, 0).with_offset(Offset.from_hours(-2)),
            zone=self.TRANSITION_BACKWARD_AFTER_MIDNIGHT_ZONE,
        )
        actual = self.TRANSITION_BACKWARD_AFTER_MIDNIGHT_ZONE.at_start_of_day(self.TRANSITION_DATE)
        assert actual == expected
        assert self.TRANSITION_DATE.at_start_of_day_in_zone(self.TRANSITION_BACKWARD_AFTER_MIDNIGHT_ZONE) == expected

    def test_skipped_start_of_day_transition_at_midnight(self) -> None:
        # 1am because of the skip
        expected = ZonedDateTime._ctor(
            offset_date_time=LocalDateTime(2000, 6, 1, 1, 0).with_offset(Offset.from_hours(-1)),
            zone=self.TRANSITION_FORWARD_AT_MIDNIGHT_ZONE,
        )
        actual = self.TRANSITION_FORWARD_AT_MIDNIGHT_ZONE.at_start_of_day(self.TRANSITION_DATE)
        assert actual == expected
        assert self.TRANSITION_DATE.at_start_of_day_in_zone(self.TRANSITION_FORWARD_AT_MIDNIGHT_ZONE) == expected

    def test_skipped_start_of_day_transition_before_midnight(self) -> None:
        # 12.20am because of the skip
        expected = ZonedDateTime._ctor(
            offset_date_time=LocalDateTime(2000, 6, 1, 0, 20).with_offset(Offset.from_hours(-1)),
            zone=self.TRANSITION_FORWARD_BEFORE_MIDNIGHT_ZONE,
        )
        actual = self.TRANSITION_FORWARD_BEFORE_MIDNIGHT_ZONE.at_start_of_day(self.TRANSITION_DATE)
        assert actual == expected
        assert self.TRANSITION_DATE.at_start_of_day_in_zone(self.TRANSITION_FORWARD_BEFORE_MIDNIGHT_ZONE) == expected

    def test_unambiguous_start_of_day(self) -> None:
        # Just a simple midnight in March.
        expected = ZonedDateTime._ctor(
            offset_date_time=LocalDateTime(2000, 3, 1, 0, 0).with_offset(Offset.from_hours(-2)),
            zone=self.TRANSITION_FORWARD_AT_MIDNIGHT_ZONE,
        )
        actual = self.TRANSITION_FORWARD_AT_MIDNIGHT_ZONE.at_start_of_day(LocalDate(2000, 3, 1))
        assert actual == expected
        assert LocalDate(2000, 3, 1).at_start_of_day_in_zone(self.TRANSITION_FORWARD_AT_MIDNIGHT_ZONE) == expected

    @staticmethod
    def assert_impossible(local_time: LocalDateTime, zone: DateTimeZone) -> None:
        mapping = zone.map_local(local_time)
        assert mapping.count == 0
        with pytest.raises(SkippedTimeError) as e:
            mapping.single()
        assert e.value.local_date_time == local_time
        assert e.value.zone == zone
        # TODO: Assert.Null(e.ParamName);
        assert zone.id in str(e.value)

        with pytest.raises(SkippedTimeError) as e:
            mapping.first()
        assert e.value.local_date_time == local_time
        assert e.value.zone == zone

        with pytest.raises(SkippedTimeError) as e:
            mapping.last()
        assert e.value.local_date_time == local_time
        assert e.value.zone == zone

    @staticmethod
    def assert_ambiguous(local_time: LocalDateTime, zone: DateTimeZone) -> None:
        earlier: ZonedDateTime = zone.map_local(local_time).first()
        later: ZonedDateTime = zone.map_local(local_time).last()
        assert earlier.local_date_time == local_time
        assert later.local_date_time == local_time
        assert earlier.to_instant() < later.to_instant()

        mapping = zone.map_local(local_time)
        assert mapping.count == 2
        with pytest.raises(AmbiguousTimeError) as e:
            mapping.single()
        assert e.value.local_date_time == local_time
        assert e.value.zone == zone
        assert e.value.earlier_mapping == earlier
        assert e.value.later_mapping == later
        assert zone.id in str(e.value)

        assert mapping.first() == earlier
        assert mapping.last() == later

    @staticmethod
    def assert_offset(expected_hours: int, local_time: LocalDateTime, zone: DateTimeZone) -> None:
        mapping = zone.map_local(local_time)
        assert mapping.count == 1
        zoned = mapping.single()
        assert mapping.first() == zoned
        assert mapping.last() == zoned
        actual_hours = zoned.offset.milliseconds / PyodaConstants.MILLISECONDS_PER_HOUR
        assert actual_hours == expected_hours

    def test_get_offset_from_local_los_angeles_fall_transition(self) -> None:
        """Los Angeles goes from -7 to -8 on November 7th 2010 at 2am wall time."""
        before = LocalDateTime(2010, 11, 7, 0, 30)
        at_transition = LocalDateTime(2010, 11, 7, 1, 0)
        ambiguous = LocalDateTime(2010, 11, 7, 1, 30)
        after = LocalDateTime(2010, 11, 7, 2, 30)
        self.assert_offset(-7, before, self.LOS_ANGELES)
        self.assert_ambiguous(at_transition, self.LOS_ANGELES)
        self.assert_ambiguous(ambiguous, self.LOS_ANGELES)
        self.assert_offset(-8, after, self.LOS_ANGELES)

    def test_get_offset_from_local_los_angeles_spring_transition(self) -> None:
        before = LocalDateTime(2010, 3, 14, 1, 30)
        impossible = LocalDateTime(2010, 3, 14, 2, 30)
        at_transition = LocalDateTime(2010, 3, 14, 3, 0)
        after = LocalDateTime(2010, 3, 14, 3, 30)
        self.assert_offset(-8, before, self.LOS_ANGELES)
        self.assert_impossible(impossible, self.LOS_ANGELES)
        self.assert_offset(-7, at_transition, self.LOS_ANGELES)
        self.assert_offset(-7, after, self.LOS_ANGELES)

    def test_get_offset_from_local_new_zealand_fall_transition(self) -> None:
        """New Zealand goes from +13 to +12 on April 4th 2010 at 3am wall time."""
        before = LocalDateTime(2010, 4, 4, 1, 30)
        at_transition = LocalDateTime(2010, 4, 4, 2, 0)
        ambiguous = LocalDateTime(2010, 4, 4, 2, 30)
        after = LocalDateTime(2010, 4, 4, 3, 30)
        self.assert_offset(13, before, self.NEW_ZEALAND)
        self.assert_ambiguous(at_transition, self.NEW_ZEALAND)
        self.assert_ambiguous(ambiguous, self.NEW_ZEALAND)
        self.assert_offset(12, after, self.NEW_ZEALAND)

    def test_get_offset_from_local_new_zealand_spring_transition(self) -> None:
        """New Zealand goes from +12 to +13 on September 26th 2010 at 2am wall time."""
        before = LocalDateTime(2010, 9, 26, 1, 30)
        impossible = LocalDateTime(2010, 9, 26, 2, 30)
        at_transition = LocalDateTime(2010, 9, 26, 3, 0)
        after = LocalDateTime(2010, 9, 26, 3, 30)
        self.assert_offset(12, before, self.NEW_ZEALAND)
        self.assert_impossible(impossible, self.NEW_ZEALAND)
        self.assert_offset(13, at_transition, self.NEW_ZEALAND)
        self.assert_offset(13, after, self.NEW_ZEALAND)

    def test_get_offset_from_local_paris_fall_transition(self) -> None:
        """Paris goes from +1 to +2 on March 28th 2010 at 2am wall time."""
        before = LocalDateTime(2010, 10, 31, 1, 30)
        at_transition = LocalDateTime(2010, 10, 31, 2, 0)
        ambiguous = LocalDateTime(2010, 10, 31, 2, 30)
        after = LocalDateTime(2010, 10, 31, 3, 30)
        self.assert_offset(2, before, self.PARIS)
        self.assert_ambiguous(ambiguous, self.PARIS)
        self.assert_ambiguous(at_transition, self.PARIS)
        self.assert_offset(1, after, self.PARIS)

    def test_get_offset_from_local_paris_spring_transition(self) -> None:
        before = LocalDateTime(2010, 3, 28, 1, 30)
        impossible = LocalDateTime(2010, 3, 28, 2, 30)
        at_transition = LocalDateTime(2010, 3, 28, 3, 0)
        after = LocalDateTime(2010, 3, 28, 3, 30)
        self.assert_offset(1, before, self.PARIS)
        self.assert_impossible(impossible, self.PARIS)
        self.assert_offset(2, at_transition, self.PARIS)
        self.assert_offset(2, after, self.PARIS)

    def test_map_local_date_time_unambiguous_date_returns_unambiguous_mapping(self) -> None:
        # 2011-11-09 01:30:00 - not ambiguous in America/New York timezone
        unambiguous_time = LocalDateTime(2011, 11, 9, 1, 30)
        mapping = self.NEW_YORK.map_local(unambiguous_time)
        assert mapping.count == 1

    def test_map_local_date_time_ambiguous_date_returns_ambiguous_mapping(self) -> None:
        # 2011-11-06 01:30:00 - falls during DST - EST conversion in America/New York timezone
        ambiguous_time = LocalDateTime(2011, 11, 6, 1, 30)
        mapping = self.NEW_YORK.map_local(ambiguous_time)
        assert mapping.count == 2

    def test_map_local_date_time_skipped_date_returns_skipped_mapping(self) -> None:
        # 2011-03-13 02:30:00 - falls during EST - DST conversion in America/New York timezone
        skipped_time = LocalDateTime(2011, 3, 13, 2, 30)
        mapping = self.NEW_YORK.map_local(skipped_time)
        assert mapping.count == 0

    @pytest.mark.parametrize(
        ("zone_id", "local_date"),
        [
            ("Pacific/Apia", "2011-12-30"),
            ("Pacific/Enderbury", "1994-12-31"),
            ("Pacific/Kiritimati", "1994-12-31"),
            ("Pacific/Kwajalein", "1993-08-21"),
        ],
    )
    def test_at_start_of_day_day_doesnt_exist(self, zone_id: str, local_date: str) -> None:
        """Some zones skipped dates by changing from UTC-lots to UTC+lots.

        For example, Samoa (Pacific/Apia) skipped December 30th 2011, going from  23:59:59 December 29th local time
        UTC-10 to 00:00:00 December 31st local time UTC+14
        """
        bad_date: LocalDate = LocalDatePattern.iso.parse(local_date).value
        zone: DateTimeZone = DateTimeZoneProviders.tzdb[zone_id]
        with pytest.raises(SkippedTimeError) as e:
            zone.at_start_of_day(bad_date)
        assert e.value.local_date_time == bad_date + LocalTime.midnight

    def test_at_strictly_in_winter(self) -> None:
        when = self.PACIFIC.at_strictly(LocalDateTime(2009, 12, 22, 21, 39, 30))

        assert when.year == 2009
        assert when.month == 12
        assert when.day == 22
        assert when.day_of_week == IsoDayOfWeek.TUESDAY
        assert when.hour == 21
        assert when.minute == 39
        assert when.second == 30
        assert when.offset == Offset.from_hours(-8)

    def test_at_strictly_in_summer(self) -> None:
        when = self.PACIFIC.at_strictly(LocalDateTime(2009, 6, 22, 21, 39, 30))

        assert when.year == 2009
        assert when.month == 6
        assert when.day == 22
        assert when.day_of_week == IsoDayOfWeek.MONDAY
        assert when.hour == 21
        assert when.minute == 39
        assert when.second == 30
        assert when.offset == Offset.from_hours(-7)

    def test_at_strictly_throws_when_ambiguous(self) -> None:
        """Pacific time changed from -7 to -8 at 2am wall time on November 2nd 2009, so 2am became 1am."""
        with pytest.raises(AmbiguousTimeError):
            self.PACIFIC.at_strictly(LocalDateTime(2009, 11, 1, 1, 30, 0))

    def test_at_strictly_throws_when_skipped(self) -> None:
        """Pacific time changed from -8 to -7 at 2am wall time on March 8th 2009, so 2am became 3am.

        This means that 2.30am doesn't exist on that day.
        """
        with pytest.raises(SkippedTimeError):
            self.PACIFIC.at_strictly(LocalDateTime(2009, 3, 8, 2, 30, 0))

    def test_at_leniently_ambiguous_time_returns_earlier_mapping(self) -> None:
        """Pacific time changed from -7 to -8 at 2am wall time on November 2nd 2009, so 2am became 1am.

        We'll return the earlier result, i.e. with the offset of -7
        """
        local = LocalDateTime(2009, 11, 1, 1, 30, 0)
        zoned = self.PACIFIC.at_leniently(local)
        assert zoned.local_date_time == local
        assert zoned.offset == Offset.from_hours(-7)

    def test_at_leniently_returns_forward_shifted_value(self) -> None:
        """Pacific time changed from -8 to -7 at 2am wall time on March 8th 2009, so 2am became 3am.

        This means that 2:30am doesn't exist on that day. We'll return 3:30am, the forward-shifted value.
        """
        local = LocalDateTime(2009, 3, 8, 2, 30, 0)
        zoned = self.PACIFIC.at_leniently(local)
        assert zoned.local_date_time == LocalDateTime(2009, 3, 8, 3, 30, 0)
        assert zoned.offset == Offset.from_hours(-7)

    def test_resolve_local(self) -> None:
        # Don't need much for this - it only delegates.
        ambiguous = LocalDateTime(2009, 11, 1, 1, 30, 0)
        skipped = LocalDateTime(2009, 3, 8, 2, 30, 0)
        assert self.PACIFIC.resolve_local(ambiguous, Resolvers.lenient_resolver) == self.PACIFIC.at_leniently(ambiguous)
        assert self.PACIFIC.resolve_local(skipped, Resolvers.lenient_resolver) == self.PACIFIC.at_leniently(skipped)


class TestDateTimeZoneMapLocal:
    """Tests for MapLocal within DateTimeZone. We have two zones, each with a single transition at midnight January 1st
    2000. One goes from -5 to +10, i.e. skips from 7pm Dec 31st to 10am Jan 1st The other goes from +10 to -5, i.e. goes
    from 10am Jan 1st back to 7pm Dec 31st.

    Both zones are tested for the zone interval pairs at:
    - The start of time
    - The end of time
    - A local time well before the transition
    - A local time well after the transition
    - An unambiguous local time shortly before the transition
    - An unambiguous local time shortly after the transition
    - The start of the transition
    - In the middle of the gap / ambiguity
    - The last local instant of the gap / ambiguity
    - The local instant immediately after the gap / ambiguity
    """

    TRANSITION: Final[Instant] = Instant.from_utc(2000, 1, 1, 0, 0)

    MINUS_5: Final[Offset] = Offset.from_hours(-5)
    PLUS_10: Final[Offset] = Offset.from_hours(10)

    NEAR_START_OF_TIME: Final[LocalDateTime] = LocalDateTime(-9998, 1, 5, 0, 0)
    NEAR_END_OF_TIME: Final[LocalDateTime] = LocalDateTime(9999, 12, 25, 0, 0)
    TRANSITION_MINUS_5: Final[LocalDateTime] = TRANSITION.with_offset(MINUS_5).local_date_time
    TRANSITION_PLUS_10: Final[LocalDateTime] = TRANSITION.with_offset(PLUS_10).local_date_time
    MID_TRANSITION: Final[LocalDateTime] = TRANSITION.with_offset(Offset.zero).local_date_time

    YEAR_BEFORE_TRANSITION: Final[LocalDateTime] = LocalDateTime(1999, 1, 1, 0, 0)
    YEAR_AFTER_TRANSITION: Final[LocalDateTime] = LocalDateTime(2001, 1, 1, 0, 0)

    ZONE_WITH_GAP: Final[SingleTransitionDateTimeZone] = SingleTransitionDateTimeZone(
        transition_point=TRANSITION, offset_before=MINUS_5, offset_after=PLUS_10
    )
    INTERVAL_BEFORE_GAP: Final[ZoneInterval] = ZONE_WITH_GAP.early_interval
    INTERVAL_AFTER_GAP: Final[ZoneInterval] = ZONE_WITH_GAP.late_interval

    ZONE_WITH_AMBIGUITY: Final[SingleTransitionDateTimeZone] = SingleTransitionDateTimeZone(
        transition_point=TRANSITION, offset_before=PLUS_10, offset_after=MINUS_5
    )
    INTERVAL_BEFORE_AMBIGUITY: Final[ZoneInterval] = ZONE_WITH_AMBIGUITY.early_interval
    INTERVAL_AFTER_AMBIGUITY: Final[ZoneInterval] = ZONE_WITH_AMBIGUITY.late_interval

    def test_zone_with_ambiguity_near_start_of_time(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(LocalDateTime(-9998, 1, 5, 0, 0))
        self.check_mapping(mapping, self.INTERVAL_BEFORE_AMBIGUITY, self.INTERVAL_BEFORE_AMBIGUITY, 1)

    def test_zone_with_ambiguity_near_end_of_time(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.NEAR_END_OF_TIME)
        self.check_mapping(mapping, self.INTERVAL_AFTER_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 1)

    def test_zone_with_ambiguity_well_before_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.YEAR_BEFORE_TRANSITION)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_AMBIGUITY, self.INTERVAL_BEFORE_AMBIGUITY, 1)

    def test_zone_with_ambiguity_well_after_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.YEAR_AFTER_TRANSITION)
        self.check_mapping(mapping, self.INTERVAL_AFTER_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 1)

    def test_zone_with_ambiguity_just_before_ambiguity(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.TRANSITION_MINUS_5.plus_nanoseconds(-1))
        self.check_mapping(mapping, self.INTERVAL_BEFORE_AMBIGUITY, self.INTERVAL_BEFORE_AMBIGUITY, 1)

    def test_zone_with_ambiguity_just_after_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.TRANSITION_PLUS_10.plus_nanoseconds(1))
        self.check_mapping(mapping, self.INTERVAL_AFTER_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 1)

    def test_zone_with_ambiguity_start_of_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.TRANSITION_MINUS_5)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 2)

    def test_zone_with_ambiguity_mid_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.MID_TRANSITION)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 2)

    def test_zone_with_ambiguity_last_tick_of_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.TRANSITION_PLUS_10.plus_nanoseconds(-1))
        self.check_mapping(mapping, self.INTERVAL_BEFORE_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 2)

    def test_zone_with_ambiguity_first_tick_after_transition(self) -> None:
        mapping = self.ZONE_WITH_AMBIGUITY.map_local(self.TRANSITION_PLUS_10)
        self.check_mapping(mapping, self.INTERVAL_AFTER_AMBIGUITY, self.INTERVAL_AFTER_AMBIGUITY, 1)

    def test_zone_with_gap_near_start_of_time(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.NEAR_START_OF_TIME)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_GAP, self.INTERVAL_BEFORE_GAP, 1)

    def test_zone_with_gap_near_end_of_time(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.NEAR_END_OF_TIME)
        self.check_mapping(mapping, self.INTERVAL_AFTER_GAP, self.INTERVAL_AFTER_GAP, 1)

    def test_zone_with_gap_well_before_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.YEAR_BEFORE_TRANSITION)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_GAP, self.INTERVAL_BEFORE_GAP, 1)

    def test_zone_with_gap_well_after_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.YEAR_AFTER_TRANSITION)
        self.check_mapping(mapping, self.INTERVAL_AFTER_GAP, self.INTERVAL_AFTER_GAP, 1)

    def test_zone_with_gap_just_before_gap(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.TRANSITION_MINUS_5.plus_nanoseconds(-1))
        self.check_mapping(mapping, self.INTERVAL_BEFORE_GAP, self.INTERVAL_BEFORE_GAP, 1)

    def test_zone_with_gap_just_after_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.TRANSITION_PLUS_10.plus_nanoseconds(1))
        self.check_mapping(mapping, self.INTERVAL_AFTER_GAP, self.INTERVAL_AFTER_GAP, 1)

    def test_zone_with_gap_start_of_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.TRANSITION_MINUS_5)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_GAP, self.INTERVAL_AFTER_GAP, 0)

    def test_zone_with_gap_mid_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.MID_TRANSITION)
        self.check_mapping(mapping, self.INTERVAL_BEFORE_GAP, self.INTERVAL_AFTER_GAP, 0)

    def test_zone_with_gap_last_tick_of_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.TRANSITION_PLUS_10.plus_nanoseconds(-1))
        self.check_mapping(mapping, self.INTERVAL_BEFORE_GAP, self.INTERVAL_AFTER_GAP, 0)

    def test_zone_with_gap_first_tick_after_transition(self) -> None:
        mapping = self.ZONE_WITH_GAP.map_local(self.TRANSITION_PLUS_10)
        self.check_mapping(mapping, self.INTERVAL_AFTER_GAP, self.INTERVAL_AFTER_GAP, 1)

    def test_tricky_case(self) -> None:
        """Case added to cover everything: we want our initial guess to hit the
        *later* zone, which doesn't actually include the local instant. However,
        we want the *earlier* zone to include it. So, we want a zone with two
        positive offsets.
        """
        # 1am occurs unambiguously in the early zone.
        zone = SingleTransitionDateTimeZone(self.TRANSITION, Offset.from_hours(3), Offset.from_hours(5))
        mapping = zone.map_local(LocalDateTime(2000, 1, 1, 1, 0))
        self.check_mapping(mapping, zone.early_interval, zone.early_interval, 1)

    def check_mapping(
        self, mapping: ZoneLocalMapping, early_interval: ZoneInterval, late_interval: ZoneInterval, count: int
    ) -> None:
        assert mapping.early_interval == early_interval
        assert mapping.late_interval == late_interval
        assert mapping.count == count
