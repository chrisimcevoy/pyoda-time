# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import Final, cast

import pytest

from pyoda_time import (
    CalendarSystem,
    Duration,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Period,
    PeriodBuilder,
    PeriodUnits,
    PyodaConstants,
    YearMonth,
)
from pyoda_time.utility import _CsharpConstants

# June 19th 2010, 2:30:15am
TEST_DATE_TIME_1: Final[LocalDateTime] = LocalDateTime(2010, 6, 19, 2, 30, 15)
# June 19th 2010, 4:45:10am
TEST_DATE_TIME_2: Final[LocalDateTime] = LocalDateTime(2010, 6, 19, 4, 45, 10)
# June 19th 2010
TEST_DATE_1: Final[LocalDate] = LocalDate(year=2010, month=6, day=19)
# March 1st 2011
TEST_DATE_2: Final[LocalDate] = LocalDate(year=2011, month=3, day=1)
# March 1st 2012
TEST_DATE_3: Final[LocalDate] = LocalDate(year=2012, month=3, day=1)

HOURS_MINUTES_PERIOD_TYPE: Final[PeriodUnits] = PeriodUnits.HOURS | PeriodUnits.MINUTES

ALL_PERIOD_UNITS: Final[list[PeriodUnits]] = list(PeriodUnits)


class TestPeriod:
    def test_between_local_date_times_without_specifying_units_omits_weeks(self) -> None:
        actual = Period.between(LocalDateTime(2012, 2, 21, 0, 0), LocalDateTime(2012, 2, 28, 0, 0))
        expected = Period.from_days(7)
        assert actual == expected

    def test_between_local_date_times_moving_forward_with_all_fields_gives_exact_result(self) -> None:
        actual = Period.between(TEST_DATE_TIME_1, TEST_DATE_TIME_2)
        expected = Period.from_hours(2) + Period.from_minutes(14) + Period.from_seconds(55)
        assert actual == expected

    def test_between_local_date_times_moving_backward_with_all_fields_gives_exact_result(self) -> None:
        actual = Period.between(TEST_DATE_TIME_2, TEST_DATE_TIME_1)
        expected = Period.from_hours(-2) + Period.from_minutes(-14) + Period.from_seconds(-55)
        assert actual == expected

    def test_between_local_date_times_moving_forward_with_hours_and_minutes_rounds_towards_start(self) -> None:
        actual = Period.between(TEST_DATE_TIME_1, TEST_DATE_TIME_2, HOURS_MINUTES_PERIOD_TYPE)
        expected = Period.from_hours(2) + Period.from_minutes(14)
        assert actual == expected

    def test_between_local_date_times_moving_backward_with_hours_and_minutes_rounds_towards_start(self) -> None:
        actual = Period.between(TEST_DATE_TIME_2, TEST_DATE_TIME_1, HOURS_MINUTES_PERIOD_TYPE)
        expected = Period.from_hours(-2) + Period.from_minutes(-14)
        assert actual == expected

    def test_between_local_date_times_across_days(self) -> None:
        expected = Period.from_hours(23) + Period.from_minutes(59)
        actual = Period.between(TEST_DATE_TIME_1, TEST_DATE_TIME_1.plus_days(1).plus_minutes(-1))
        assert actual == expected

    def test_between_local_date_times_across_days_minutes_and_nanoseconds(self) -> None:
        expected = Period.from_minutes(24 * 60 - 1) + Period.from_seconds(59)
        actual = Period.between(
            TEST_DATE_TIME_1, TEST_DATE_TIME_1.plus_days(1).plus_seconds(-1), PeriodUnits.MINUTES | PeriodUnits.SECONDS
        )
        assert actual == expected

    # TODO: def test_between_local_date_times_not_int64_representable(self) -> None:

    def test_between_local_dates_invalid_units(self) -> None:
        # TODO: In Noda Time these are ArgumentException
        with pytest.raises(ValueError):
            Period.between(TEST_DATE_1, TEST_DATE_2, units=PeriodUnits.NONE)
        with pytest.raises(TypeError):
            Period.between(TEST_DATE_1, TEST_DATE_2, units=cast(PeriodUnits, -1))
        with pytest.raises(ValueError):
            Period.between(TEST_DATE_1, TEST_DATE_2, PeriodUnits.ALL_TIME_UNITS)
        with pytest.raises(ValueError):
            Period.between(TEST_DATE_1, TEST_DATE_2, PeriodUnits.YEARS | PeriodUnits.HOURS)

    def test_between_local_dates_different_calendar_systems_throws(self) -> None:
        start = LocalDate(year=2017, month=11, day=1, calendar=CalendarSystem.coptic)
        end = LocalDate(year=2017, month=11, day=5, calendar=CalendarSystem.gregorian)
        with pytest.raises(ValueError):  # TODO: In Noda Time this is ArgumentException
            Period.between(start, end)

    # TODO: [requires LocalDatePattern]
    #  def test_between_local_dates_single_unit(self, start_text: str, end_text: str, units: PeriodUnits) -> None:

    def test_days_between_local_dates_different_calendars_throws(self) -> None:
        start = LocalDate(year=2020, month=6, day=13, calendar=CalendarSystem.iso)
        end = LocalDate(year=2020, month=6, day=15, calendar=CalendarSystem.julian)
        with pytest.raises(ValueError):  # TODO: In Noda Time this is ArgumentException
            Period.days_between(start, end)

    def test_days_between_local_dates_same_dates_returns_zero(self) -> None:
        start = LocalDate(year=2020, month=6, day=13, calendar=CalendarSystem.iso)
        end = start
        expected = 0
        assert Period.days_between(start, end) == expected

    # TODO: [requires LocalDatePattern]
    #  def test_days_between_local_dates(self, start_text: str, e

    # TODO: [requires LocalDatePattern]
    #  def test_days_between_local_dates_start_date_greater_than_end_date(self):

    def test_between_local_dates_moving_forward_no_leap_years_with_exact_results(self) -> None:
        actual = Period.between(TEST_DATE_1, TEST_DATE_2)
        expected = Period.from_months(8) + Period.from_days(10)
        assert actual == expected

    def test_between_local_dates_moving_forward_in_leap_year_with_exact_results(self) -> None:
        actual = Period.between(TEST_DATE_1, TEST_DATE_3)
        expected = Period.from_years(1) + Period.from_months(8) + Period.from_days(11)
        assert actual == expected

    def test_between_local_dates_moving_backward_no_leap_years_with_exact_results(self) -> None:
        actual = Period.between(TEST_DATE_2, TEST_DATE_1)
        expected = Period.from_months(-8) + Period.from_days(-12)
        assert actual == expected

    def test_between_local_dates_moving_backward_in_leap_year_with_exact_results(self) -> None:
        # This is asymmetric with moving forward, because we first take off a whole year, which
        # takes us to March 1st 2011, then 8 months to take us to July 1st 2010, then 12 days
        # to take us back to June 19th. In this case, the fact that our start date is in a leap
        # year had no effect.
        actual = Period.between(TEST_DATE_3, TEST_DATE_1)
        expected = Period.from_years(-1) + Period.from_months(-8) + Period.from_days(-12)
        assert actual == expected

    def test_between_local_dates_moving_forward_with_just_months(self) -> None:
        actual = Period.between(TEST_DATE_1, TEST_DATE_3, PeriodUnits.MONTHS)
        expected = Period.from_months(20)
        assert actual == expected

    def test_between_local_dates_moving_backward_with_just_months(self) -> None:
        actual = Period.between(TEST_DATE_3, TEST_DATE_1, PeriodUnits.MONTHS)
        expected = Period.from_months(-20)
        assert actual == expected

    def test_between_local_dates_asymmetric_moving_forward_and_backward(self) -> None:
        # February 10th 2010
        d1 = LocalDate(year=2010, month=2, day=10)
        # March 30th 2010
        d2 = LocalDate(year=2010, month=3, day=30)
        # Going forward, we go to March 10th (1 month) then March 30th (20 days)
        assert Period.between(d1, d2) == Period.from_months(1) + Period.from_days(20)
        # Going backward, we go to February 28th (-1 month, day is rounded) then February 10th (-18 days)
        assert Period.between(d2, d1) == Period.from_months(-1) + Period.from_days(-18)

    def test_between_local_dates_end_of_month(self) -> None:
        d1 = LocalDate(year=2013, month=3, day=31)
        d2 = LocalDate(year=2013, month=4, day=30)
        assert Period.between(d1, d2) == Period.from_months(1)
        assert Period.between(d2, d1) == Period.from_days(-30)

    def test_between_local_dates_on_leap_year(self) -> None:
        d1 = LocalDate(year=2012, month=2, day=29)
        d2 = LocalDate(year=2013, month=2, day=28)
        assert Period.between(d1, d2) == Period.from_years(1)
        assert Period.between(d2, d1) == Period.from_months(-11) + Period.from_days(-28)

    def test_between_local_dates_after_leap_year(self) -> None:
        d1 = LocalDate(year=2012, month=3, day=5)
        d2 = LocalDate(year=2013, month=3, day=5)
        assert Period.between(d1, d2) == Period.from_years(1)
        assert Period.between(d2, d1) == Period.from_years(-1)

    # TODO: [requires PeriodPattern]
    #  def test_between_local_date_times_on_leap_year(self) -> None:

    # TODO: [requires PeriodPattern]
    #  def test_between_local_date_times_on_leap_year_islamic(self) -> None:

    def test_between_local_date_times_invalid_units(self) -> None:
        # TODO: In Noda Time, this test passes LocalDates rather than LocalDateTimes.
        #  I think it's just a copy/paste error?
        with pytest.raises(ValueError):  # TODO: ArgumentException
            Period.between(TEST_DATE_TIME_1, TEST_DATE_TIME_2, PeriodUnits.NONE)
        with pytest.raises(TypeError):  # TODO: ArgumentException
            Period.between(TEST_DATE_TIME_1, TEST_DATE_TIME_2, cast(PeriodUnits, 0))

    def test_between_local_times_invalid_units(self) -> None:
        t1 = LocalTime(hour=10, minute=0)
        t2 = LocalTime.from_hour_minute_second_millisecond_tick(15, 30, 45, 20, 5)
        with pytest.raises(ValueError):
            Period.between(t1, t2, PeriodUnits.NONE)
        with pytest.raises(TypeError):
            Period.between(t1, t2, cast(PeriodUnits, -1))
        with pytest.raises(ValueError):
            Period.between(t1, t2, PeriodUnits.YEAR_MONTH_DAY)
        with pytest.raises(ValueError):
            Period.between(t1, t2, PeriodUnits.YEARS | PeriodUnits.HOURS)

    # TODO: [requires LocalTimePattern]
    #  def test_between_local_times_single_unit(self) -> None:

    def test_between_local_times_moving_forwards(self) -> None:
        t1 = LocalTime(hour=10, minute=0)
        t2 = LocalTime.from_hour_minute_second_millisecond_tick(15, 30, 45, 20, 5)
        assert Period.between(t1, t2) == Period.from_hours(5) + Period.from_minutes(30) + Period.from_seconds(
            45
        ) + Period.from_milliseconds(20) + Period.from_ticks(5)

    def test_between_local_times_moving_backwards(self) -> None:
        t1 = LocalTime.from_hour_minute_second_millisecond_tick(15, 30, 45, 20, 5)
        t2 = LocalTime(hour=10, minute=0)
        assert Period.between(t1, t2) == Period.from_hours(-5) + Period.from_minutes(-30) + Period.from_seconds(
            -45
        ) + Period.from_milliseconds(-20) + Period.from_ticks(-5)

    def test_between_local_times_moving_forwards_with_just_hours(self) -> None:
        t1 = LocalTime(hour=11, minute=30)
        t2 = LocalTime(hour=17, minute=15)
        assert Period.between(t1, t2, PeriodUnits.HOURS) == Period.from_hours(5)

    def test_between_local_times_moving_backwards_with_just_hours(self) -> None:
        t1 = LocalTime(hour=17, minute=15)
        t2 = LocalTime(hour=11, minute=30)
        assert Period.between(t1, t2, PeriodUnits.HOURS) == Period.from_hours(-5)

    def test_addition_with_different_period_types(self) -> None:
        p1 = Period.from_hours(5)
        p2 = Period.from_minutes(20)
        sum_ = p1 + p2
        assert sum_.hours == 5
        assert Period.add(p1, p2) == sum_

    def test_addition_day_crossing_month_boundary(self) -> None:
        start = LocalDateTime(2010, 2, 20, 10, 0)
        result = start + Period.from_days(10)
        assert result == LocalDateTime(2010, 3, 2, 10, 0)

    def test_addition_one_year_on_leap_day(self) -> None:
        start = LocalDateTime(2012, 2, 29, 10, 0)
        result = start + Period.from_years(1)
        # Feb 29th becomes Feb 28th
        assert result == LocalDateTime(2013, 2, 28, 10, 0)

    def test_addition_four_years_on_leap_day(self) -> None:
        start = LocalDateTime(2012, 2, 29, 10, 0)
        result = start + Period.from_years(4)
        # Feb 29th is still valid in 2016
        assert result == LocalDateTime(2016, 2, 29, 10, 0)

    def test_addition_year_month_day(self) -> None:
        # One year, one month, two days
        period = Period.from_years(1) + Period.from_months(1) + Period.from_days(2)
        start = LocalDateTime(2007, 1, 30, 0, 0)
        # Periods are added in order, so this becomes...
        # Add one year: Jan 30th 2008
        # Add one month: Feb 29th 2008
        # Add two days: March 2nd 2008
        # If we added the days first, we'd end up with March 1st instead.
        result = start + period
        assert result == LocalDateTime(2008, 3, 2, 0, 0)

    def test_subtraction_with_different_period_types(self) -> None:
        p1 = Period.from_hours(3)
        p2 = Period.from_minutes(20)
        difference: Period = p1 - p2
        assert difference.hours == 3
        assert difference.minutes == -20
        assert Period.subtract(p1, p2) == difference

    def test_subtraction_with_identical_period_types(self) -> None:
        p1 = Period.from_hours(3)
        p2 = Period.from_hours(2)
        difference: Period = p1 - p2
        assert difference.hours == 1
        assert Period.subtract(p1, p2) == difference

    def test_equality_when_equal(self) -> None:
        assert Period.from_hours(10) == Period.from_hours(10)
        assert Period.from_minutes(15) == Period.from_minutes(15)
        assert Period.from_days(5) == Period.from_days(5)

    def test_equality_with_different_period_types_only_considers_values(self) -> None:
        all_fields = Period.from_minutes(1) + Period.from_hours(1) - Period.from_minutes(1)
        just_hours = Period.from_hours(1)
        assert just_hours == all_fields

    def test_equality_when_unequal(self) -> None:
        assert not Period.from_hours(10).equals(Period.from_hours(20))
        assert not Period.from_minutes(15).equals(Period.from_seconds(15))
        assert not Period.from_hours(1).equals(Period.from_minutes(60))
        # TODO: In Pyoda Time these return False
        assert Period.from_hours(1).equals(object()) is NotImplemented  # type: ignore
        assert Period.from_hours(1).equals(None) is NotImplemented  # type: ignore

    def test_equality_operators(self) -> None:
        val1 = Period.from_hours(1)
        val2 = Period.from_hours(1)
        val3 = Period.from_hours(2)
        val4: Period | None = None
        assert val1 == val2
        assert not val2 == val3
        assert not val1 == val4
        assert not val4 == val1
        assert val4 is None
        assert None is val4

        assert not val1 != val2
        assert val1 != val3
        assert val1 != val4
        assert val4 != val1
        assert not (val4 is not None)
        assert not (None is not val4)

    @pytest.mark.parametrize(
        "unit,has_time_component",
        [
            (PeriodUnits.YEARS, False),
            (PeriodUnits.WEEKS, False),
            (PeriodUnits.MONTHS, False),
            (PeriodUnits.DAYS, False),
            (PeriodUnits.HOURS, True),
            (PeriodUnits.MINUTES, True),
            (PeriodUnits.SECONDS, True),
            (PeriodUnits.MILLISECONDS, True),
            (PeriodUnits.TICKS, True),
            (PeriodUnits.NANOSECONDS, True),
        ],
    )
    def test_has_time_component_single_valued(self, unit: PeriodUnits, has_time_component: bool) -> None:
        builder = PeriodBuilder()
        builder[unit] = 1
        period = builder.build()
        assert period.has_time_component is has_time_component

    @pytest.mark.parametrize(
        "unit,has_date_component",
        [
            (PeriodUnits.YEARS, True),
            (PeriodUnits.WEEKS, True),
            (PeriodUnits.MONTHS, True),
            (PeriodUnits.DAYS, True),
            (PeriodUnits.HOURS, False),
            (PeriodUnits.MINUTES, False),
            (PeriodUnits.SECONDS, False),
            (PeriodUnits.MILLISECONDS, False),
            (PeriodUnits.TICKS, False),
            (PeriodUnits.NANOSECONDS, False),
        ],
    )
    def test_has_date_component_single_valued(self, unit: PeriodUnits, has_date_component: bool) -> None:
        builder = PeriodBuilder()
        builder[unit] = 1
        period = builder.build()
        assert period.has_date_component is has_date_component

    def test_has_time_component_compound(self) -> None:
        dt1 = LocalDateTime(2000, 1, 1, 10, 45, 00)
        dt2 = LocalDateTime(2000, 2, 4, 11, 50, 00)

        # Case 1: Entire period is date-based (no time units available)
        assert not Period.between(dt1.date, dt2.date).has_time_component

        # Case 2: Period contains date and time units, but time units are all zero
        assert not Period.between(dt1.date + LocalTime.midnight, dt2.date + LocalTime.midnight).has_time_component

        # Case 3: Entire period is time-based, but 0. (Same local time twice here.)
        assert not Period.between(dt1.time_of_day, dt1.time_of_day).has_time_component

        # Case 4: Period contains date and time units, and some time units are non-zero
        assert Period.between(dt1, dt2).has_time_component

        # Case 5: Entire period is time-based, and some time units are non-zero
        assert Period.between(dt1.time_of_day, dt2.time_of_day).has_time_component

    def test_has_date_component_compound(self) -> None:
        dt1 = LocalDateTime(2000, 1, 1, 10, 45, 00)
        dt2 = LocalDateTime(2000, 2, 4, 11, 50, 00)

        # Case 1: Entire period is time-based (no date units available)
        assert not Period.between(dt1.time_of_day, dt2.time_of_day).has_date_component

        # Case 2: Period contains date and time units, but date units are all zero
        assert not Period.between(dt1, dt1.date + dt2.time_of_day).has_date_component

        # Case 3: Entire period is date-based, but 0. (Same local date twice here.)
        assert not Period.between(dt1.date, dt1.date).has_date_component

        # Case 4: Period contains date and time units, and some date units are non-zero
        assert Period.between(dt1, dt2).has_date_component

        # Case 5: Entire period is date-based, and some time units are non-zero
        assert Period.between(dt1.date, dt2.date).has_date_component

    def test_to_string_positive(self) -> None:
        period = Period.from_days(1) + Period.from_hours(2)
        assert str(period) == "P1DT2H"

    def test_to_string_all_units(self) -> None:
        period = Period._ctor(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        assert str(period) == "P1Y2M3W4DT5H6M7S8s9t10n"

    def test_to_string_negative(self) -> None:
        period = Period.from_days(-1) + Period.from_hours(-2)
        assert str(period) == "P-1DT-2H"

    def test_to_string_mixed(self) -> None:
        period = Period.from_days(-1) + Period.from_hours(2)
        assert str(period) == "P-1DT2H"

    def test_to_string_zero(self) -> None:
        assert str(Period.zero) == "P0D"

    def test_to_builder_single_unit(self) -> None:
        builder = Period.from_hours(5).to_builder()
        expected = PeriodBuilder(hours=5).build()
        assert builder.build() == expected

    def test_to_builder_multiple_units(self) -> None:
        builder = (Period.from_hours(5) + Period.from_weeks(2)).to_builder()
        expected = PeriodBuilder(hours=5, weeks=2).build()
        assert builder.build() == expected

    def test_normalize_weeks(self) -> None:
        original = PeriodBuilder(weeks=2, days=5).build()
        normalized = original.normalize()
        expected = PeriodBuilder(days=19).build()
        assert normalized == expected

    def test_normalize_hours(self) -> None:
        original = PeriodBuilder(hours=25, days=1).build()
        normalized = original.normalize()
        expected = PeriodBuilder(hours=1, days=2).build()
        assert normalized == expected

    def test_normalize_minutes(self) -> None:
        original = PeriodBuilder(hours=1, minutes=150).build()
        normalized = original.normalize()
        expected = PeriodBuilder(hours=3, minutes=30).build()
        assert normalized == expected

    def test_normalize_seconds(self) -> None:
        original = PeriodBuilder(minutes=1, seconds=150).build()
        normalized = original.normalize()
        expected = PeriodBuilder(minutes=3, seconds=30).build()
        assert normalized == expected

    def test_normalize_milliseconds(self) -> None:
        original = PeriodBuilder(seconds=1, milliseconds=1500).build()
        normalized = original.normalize()
        expected = PeriodBuilder(seconds=2, milliseconds=500).build()
        assert normalized == expected

    def test_normalize_ticks(self) -> None:
        original = PeriodBuilder(milliseconds=1, ticks=15000).build()
        normalized = original.normalize()
        expected = PeriodBuilder(milliseconds=2, ticks=0, nanoseconds=500000).build()
        assert normalized == expected

    def test_normalize_nanoseconds(self) -> None:
        original = PeriodBuilder(ticks=1, nanoseconds=150).build()
        normalized = original.normalize()
        expected = PeriodBuilder(nanoseconds=250).build()
        assert normalized == expected

    def test_normalize_multiple_fields(self) -> None:
        original = PeriodBuilder(hours=1, minutes=119, seconds=150).build()
        normalized = original.normalize()
        expected = PeriodBuilder(hours=3, minutes=1, seconds=30).build()
        assert normalized == expected

    def test_normalize_all_negative(self) -> None:
        original = PeriodBuilder(hours=-1, minutes=-119, seconds=-150).build()
        normalized = original.normalize()
        expected = PeriodBuilder(hours=-3, minutes=-1, seconds=-30).build()
        assert normalized == expected

    def test_normalize_mixed_signs_positive_result(self) -> None:
        original = PeriodBuilder(hours=3, minutes=-1).build()
        normalized = original.normalize()
        expected = PeriodBuilder(hours=2, minutes=59).build()
        assert normalized == expected

    def test_normalize_mixed_signs_negative_result(self) -> None:
        original = PeriodBuilder(hours=1, minutes=-121).build()
        normalized = original.normalize()
        expected = PeriodBuilder(hours=-1, minutes=-1).build()
        assert normalized == expected

    def test_normalize_doesnt_affect_months_and_years(self) -> None:
        original = PeriodBuilder(years=2, months=1, days=400).build()
        assert original.normalize() == original

    def test_normalize_zero_result(self) -> None:
        original = PeriodBuilder(years=0).build()
        assert original.normalize() == Period.zero

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_normalize_overflow(self) -> None:
        period = Period.from_hours(_CsharpConstants.LONG_MAX_VALUE)
        with pytest.raises(OverflowError):
            period.normalize()

    def test_to_string_single_unit(self) -> None:
        period = Period.from_hours(5)
        assert str(period) == "PT5H"

    def test_to_string_multiple_units(self) -> None:
        period = PeriodBuilder(hours=5, minutes=30).build()
        assert str(period) == "PT5H30M"

    def test_to_duration_invalid_with_years(self) -> None:
        period = Period.from_years(1)
        with pytest.raises(RuntimeError):
            period.to_duration()

    def test_to_duration_invalid_with_months(self) -> None:
        period = Period.from_months(1)
        with pytest.raises(RuntimeError):
            period.to_duration()

    def test_to_duration_valid_all_acceptable_units(self) -> None:
        period = PeriodBuilder(weeks=1, days=2, hours=3, minutes=4, seconds=5, milliseconds=6, ticks=7).build()
        assert period.to_duration().bcl_compatible_ticks == (
            1 * PyodaConstants.TICKS_PER_WEEK
            + 2 * PyodaConstants.TICKS_PER_DAY
            + 3 * PyodaConstants.TICKS_PER_HOUR
            + 4 * PyodaConstants.TICKS_PER_MINUTE
            + 5 * PyodaConstants.TICKS_PER_SECOND
            + 6 * PyodaConstants.TICKS_PER_MILLISECOND
            + 7
        )

    def test_to_duration_valid_with_zero_values_in_month_year_units(self) -> None:
        period = Period.from_months(1) + Period.from_years(1)
        period = period - period + Period.from_days(1)
        assert not period.has_time_component
        assert period.to_duration() == Duration.one_day

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_to_duration_overflow(self) -> None:
        period = Period.from_seconds(_CsharpConstants.LONG_MAX_VALUE)
        with pytest.raises(OverflowError):
            period.to_duration()

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_to_duration_overflow_when_possibly_valid(self) -> None:
        period = Period.from_seconds(_CsharpConstants.LONG_MAX_VALUE) + Period.from_minutes(
            int(_CsharpConstants.LONG_MIN_VALUE / 60)
        )
        with pytest.raises(OverflowError):
            period.to_duration()

    @pytest.mark.skip(reason="Requires NormalizingEqualityComparer")
    def test_normalizing_equality_comparer_null_to_null(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires NormalizingEqualityComparer")
    def test_normalizing_equality_comparer_null_to_non_null(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires NormalizingEqualityComparer")
    def test_normalizing_equality_comparer_period_to_itself(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires NormalizingEqualityComparer")
    def test_normalizing_equality_comparer_non_equal_after_normalization(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires NormalizingEqualityComparer")
    def test_normalizing_equality_comparer_equal_after_normalization(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires NormalizingEqualityComparer")
    def test_normalizing_equality_comparer_get_hash_code_after_normalization(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires Period.CreateComparer")
    def test_comparer_null_with_null(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires Period.CreateComparer")
    def test_comparer_null_with_non_null(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires Period.CreateComparer")
    def test_comparer_non_null_with_null(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires Period.CreateComparer")
    def test_comparer_durationable_periods(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires Period.CreateComparer")
    def test_comparer_non_durationable_periods(self) -> None:
        pass

    @pytest.mark.parametrize("units", ALL_PERIOD_UNITS)
    def test_between_extreme_values(self, units: PeriodUnits) -> None:
        # TODO: In Noda Time, Nanoseconds overflows, but not in Pyoda Time
        # We can't use None, and Nanoseconds will *correctly* overflow.
        if units == PeriodUnits.NONE or units == PeriodUnits.NANOSECONDS:
            return
        min_value = LocalDate.min_iso_value.at(LocalTime.min_value)
        max_value = LocalDate.max_iso_value.at(LocalTime.max_value)
        Period.between(min_value, max_value, units)

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_between_extreme_values_overflow(self) -> None:
        min_value = LocalDate.min_iso_value.at(LocalTime.min_value)
        max_value = LocalDate.max_iso_value.at(LocalTime.max_value)
        with pytest.raises(OverflowError):
            Period.between(min_value, max_value, PeriodUnits.NANOSECONDS)

    @pytest.mark.skip(reason="Requires LocalDateTimePattern")
    def test_between_local_date_time_awkward_time_of_day_with_single_unit(
        self, start_text: str, end_text: str, units: PeriodUnits, expected_forward: int, expected_backward: int
    ) -> None:
        raise NotImplementedError

    def test_between_local_date_time_same_value(self) -> None:
        start = LocalDateTime(2014, 1, 1, 16, 0, 0)
        assert Period.between(start, start) is Period.zero

    def test_between_local_date_time_awkward_time_of_day_with_multiple_units(self) -> None:
        start = LocalDateTime(2014, 1, 1, 16, 0, 0)
        end = LocalDateTime(2015, 2, 3, 8, 0, 0)
        actual = Period.between(start, end, PeriodUnits.YEAR_MONTH_DAY | PeriodUnits.ALL_TIME_UNITS)
        expected = PeriodBuilder(years=1, months=1, days=1, hours=16).build()
        assert actual == expected

    def test_between_year_month_invalid_units(self) -> None:
        year_month_1 = YearMonth(year=2010, month=1)
        year_month_2 = YearMonth(year=2011, month=3)
        with pytest.raises(TypeError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, cast(PeriodUnits, 0))
        with pytest.raises(TypeError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, cast(PeriodUnits, -1))
        with pytest.raises(ValueError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, PeriodUnits.ALL_TIME_UNITS)
        with pytest.raises(ValueError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, PeriodUnits.DAYS)
        with pytest.raises(ValueError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, PeriodUnits.YEARS | PeriodUnits.DAYS)
        with pytest.raises(ValueError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, PeriodUnits.YEARS | PeriodUnits.WEEKS)
        with pytest.raises(ValueError):  # TODO: ArgumentException in Noda Time
            Period.between(year_month_1, year_month_2, PeriodUnits.YEARS | PeriodUnits.HOURS)

    def test_between_year_month_different_calendar_systems_throws(self) -> None:
        start = YearMonth(year=2017, month=11, calendar=CalendarSystem.coptic)
        end = YearMonth(year=2017, month=11, calendar=CalendarSystem.gregorian)
        with pytest.raises(ValueError):  # TODO: ArgumentException in Noda Time
            Period.between(start, end)

    @pytest.mark.skip(reason="Requires YearMonthPattern.ISO.Parse()")
    def test_between_year_month_single_unit(self) -> None:
        pass

    @pytest.mark.skip(reason="Requires YearMonthPattern.ISO.Parse()")
    def test_between_year_month_both_units(self) -> None:
        pass

    def test_from_nanoseconds(self) -> None:
        period = Period.from_nanoseconds(1234567890)
        assert period.nanoseconds == 1234567890

    def test_add_period_to_period_no_overflow(self) -> None:
        p1 = Period.from_hours(_CsharpConstants.LONG_MAX_VALUE)
        p2 = Period.from_minutes(60)
        assert PeriodBuilder(hours=_CsharpConstants.LONG_MAX_VALUE, minutes=60).build() == p1 + p2

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_add_period_to_period_overflow(self) -> None:
        p1 = Period.from_hours(_CsharpConstants.LONG_MAX_VALUE)
        p2 = Period.from_hours(1)
        with pytest.raises(OverflowError):
            hash(p1 + p2)
