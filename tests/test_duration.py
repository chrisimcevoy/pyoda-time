"""https://github.com/nodatime/nodatime/blob/main/src/NodaTime.Test/DurationTest.cs"""

from pyoda_time import Duration


class TestDuration:
    def test_default_initialiser(self) -> None:
        """Using the default constructor is equivalent to Duration.Zero."""
        actual = Duration()
        assert Duration.zero == actual
