![PyPI - Status](https://img.shields.io/pypi/status/pyoda-time)
![PyPI - Version](https://img.shields.io/pypi/v/pyoda-time)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyoda-time)
![GitHub License](https://img.shields.io/github/license/chrisimcevoy/pyoda-time)
[![Documentation Status](https://readthedocs.org/projects/pyoda-time/badge/?version=latest)](https://pyoda-time.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/github/chrisimcevoy/pyoda-time/graph/badge.svg?token=I1QQES7AVT)](https://codecov.io/github/chrisimcevoy/pyoda-time)

# Pyoda Time

Pyoda Time is an alternative date and time API for Python. 

It helps you to think about your data more clearly, and express operations on that data more precisely.

This project is a Python port of [Noda Time](https://github.com/nodatime/nodatime), an alternative DateTime library for .NET (which in turn was inspired by [Joda Time](https://github.com/JodaOrg/joda-time)).

The project goal is to provide a powerful alternative for time management in Python, drawing inspiration from the strengths of Noda Time and adapting them to a Pythonic API.

## Quick Start

### Installation:

```commandline
pip install pyoda-time
```

### Examples:

```python
from pyoda_time import *

# Instant represents time from epoch
now: Instant = SystemClock.instance.get_current_instant()

# Convert an instant to a ZonedDateTime
now_in_iso_utc: ZonedDateTime = now.in_utc()

# Create a duration
duration: Duration = Duration.from_minutes(3)

# Add it to our ZonedDateTime
then_in_iso_utc: ZonedDateTime = now_in_iso_utc + duration

# Time zone support
london = DateTimeZoneProviders.tzdb["Europe/London"]

# Time zone conversions
local_date = LocalDateTime(2012, 3, 27, 0, 45, 0)
before = london.at_strictly(local_date)
```

For more information, see [the docs](https://pyodatime.org/).

## Contributions

Contributions of all kinds are welcome.

If you are interested in contributing to this project, please refer to the [guidelines](CONTRIBUTING.md).

## Acknowledgements

We express our gratitude to the authors and contributors of Noda Time and Joda Time for their pioneering work in the field of date and time management. Pyoda Time aspires to continue this tradition within the Python ecosystem.
