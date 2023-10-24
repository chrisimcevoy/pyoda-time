# pyoda-time

An alternative datetime library for Python.

Based on [Noda Time](https://github.com/nodatime/nodatime), an alternative DateTime library for .NET. (Which itself draws inspiration from [Joda Time](https://github.com/JodaOrg/joda-time).)

# Guiding Principles

> Some developers assume that a pattern which works in Java will work in Python, or the equivalent for any other pair of platforms. Don’t make this assumption. Always read the documentation – and if you’re porting code from one platform to another, you’ll need to “decode” the pattern with one set of documentation, then “encode” it with the other.
>
> -- <cite>[Jon Skeet's coding blog](https://codeblog.jonskeet.uk/2015/05/05/common-mistakes-in-datetime-formatting-and-parsing/)</cite>

- In Noda Time there is an `Instant.Max()` static method for comparing two instances. In Python, we use the `max()` builtin to compare instances.
