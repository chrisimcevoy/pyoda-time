"""https://github.com/nodatime/nodatime/blob/main/src/NodaTime.Test/DurationTest.cs"""

from pyoda_time.duration import Duration


class TestDuration:

    def test_default_initialiser(self):
        """Using the default constructor is equivalent to Duration.Zero."""
        actual = Duration()
        assert Duration.zero == actual
