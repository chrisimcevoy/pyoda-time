![PyPI - Status](https://img.shields.io/pypi/status/pyoda-time)
![PyPI - Version](https://img.shields.io/pypi/v/pyoda-time)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyoda-time)

# pyoda-time

An alternative datetime library for Python.

Based on [Noda Time](https://github.com/nodatime/nodatime), an alternative DateTime library for .NET. (Which itself draws inspiration from [Joda Time](https://github.com/JodaOrg/joda-time).)

# Guiding Principles

> Some developers assume that a pattern which works in Java will work in Python, or the equivalent for any other pair of platforms. Don’t make this assumption. Always read the documentation – and if you’re porting code from one platform to another, you’ll need to “decode” the pattern with one set of documentation, then “encode” it with the other.
>
> -- <cite>[Jon Skeet's coding blog](https://codeblog.jonskeet.uk/2015/05/05/common-mistakes-in-datetime-formatting-and-parsing/)</cite>

# Tests

By convention:

- Tests which are not nested inside a test class are unique to Pyoda Time.
- Tests which are nested within a test class (along with the class itself) are derived from the Noda Time equivalent.

This way, it is easy to keep track of which tests are based on Noda Time tests and which aren't.

