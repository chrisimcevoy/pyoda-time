# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.


from pyoda_time.text.patterns._pattern_fields import _PatternFields


class TestPatternFieldExtensions:
    def test_is_used_no_match(self) -> None:
        assert not (_PatternFields.HOURS_12 | _PatternFields.MINUTES).has_any(_PatternFields.HOURS_24)

    def test_is_used_single_value_match(self) -> None:
        assert _PatternFields.HOURS_24.has_any(_PatternFields.HOURS_24)

    def test_is_field_used_multi_value_match(self) -> None:
        assert (_PatternFields.HOURS_24 | _PatternFields.MINUTES).has_any(_PatternFields.HOURS_24)

    def test_is_field_used_no_match(self) -> None:
        assert not (_PatternFields.HOURS_12 | _PatternFields.MINUTES).has_any(
            _PatternFields.HOURS_24 | _PatternFields.SECONDS
        )

    def test_all_are_used_partial_match(self) -> None:
        assert not (_PatternFields.HOURS_12 | _PatternFields.MINUTES).has_all(
            _PatternFields.HOURS_12 | _PatternFields.SECONDS
        )

    def test_all_are_used_complete_match(self) -> None:
        assert (_PatternFields.HOURS_12 | _PatternFields.MINUTES).has_all(
            _PatternFields.HOURS_12 | _PatternFields.MINUTES
        )

    def test_all_are_used_complete_match_with_more(self) -> None:
        assert (_PatternFields.HOURS_24 | _PatternFields.MINUTES | _PatternFields.HOURS_12).has_all(
            _PatternFields.HOURS_24 | _PatternFields.MINUTES | _PatternFields.HOURS_12
        )
