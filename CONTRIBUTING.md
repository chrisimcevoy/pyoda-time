# How to Contribute

Thank you for your interest in contributing to Pyoda Time! We welcome all forms of contributions, from submitting issues and improving documentation to writing tests and implementing new code. Every bit of help is greatly appreciated.

Pyoda Time is a Python port of the dotnet package, Noda Time; The aim of the project (in the short to medium term at least) is to achieve parity with Noda Time.

## Code Contributions

### Prerequisites for Code Contributions

- **Text Editor or IDE:** Popular options include [PyCharm Community](https://www.jetbrains.com/pycharm/) and [Visual Studio Code](https://code.visualstudio.com/).
- **CPython Interpreter:** Version 3.12 or newer. Refer to the [installation guide](https://wiki.python.org/moin/BeginnersGuide/Download) and the [official downloads page](https://www.python.org/downloads/).
- **Git Client:** Download from [https://git-scm.com/](https://git-scm.com/).
- **GitHub Account:** Sign up at [https://github.com/join](https://github.com/join).
- **Poetry:** For managing Python dependencies. Installation instructions at [https://python-poetry.org/](https://python-poetry.org/).

### Project Structure

The `pyoda_time` package in the root of the repository maintains a structure which, as much as possible, matches that of the Noda Time library file-for-file. 

If a `.cs` file exists in Noda Time, an equivalent `.py` file should exist in Pyoda Time. 

This convention helps to minimise the overhead in tracking parity with the mother project.

### Starting a Contribution

Before contributing code, please open an issue declaring the functionality you intend to implement.

After setting up, you can [fork the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and clone your fork locally. Running `poetry install` will install all project dependencies in a project-specific environment.

Upon completing your changes, [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) for review and potential inclusion in the project.

### Useful Terminal Commands

|             Command             |                    Description                     |
|:-------------------------------:|:--------------------------------------------------:|
|        `poetry install`         |           Installs project dependencies            |
|       `poetry run pytest`       |                Runs the test suite                 |
| `poetry run pre-commit install` |             Installs pre-commit hooks              |
| `poetry run pre-commit run -a`  | Runs pre-commit checks against the entire codebase |

## Conventions for Porting C# Code to Python

> Some developers assume that a pattern which works in Java will work in Python, or the equivalent for any other pair of platforms. Don’t make this assumption. Always read the documentation – and if you’re porting code from one platform to another, you’ll need to “decode” the pattern with one set of documentation, then “encode” it with the other.
>
> -- <cite>[Jon Skeet's coding blog](https://codeblog.jonskeet.uk/2015/05/05/common-mistakes-in-datetime-formatting-and-parsing/)</cite>

What follows is an attempt at codifying the set of conventions I have arrived at while porting C# code to Python.

These are not hard and fast rules, and independent thought is encouraged.

However, I hope this will:
- Help contributors find their footing with the existing code more quickly.
- Act as a frame of reference when people are unsure how to proceed with a tricky port.

### Namespaces

- C# namespaces translate to Python packages.
- Python modules (other than `__init__.py`) should be prefixed with an underscore to discourage end users from importing those modules directly.
- A class which is `public` in C# should be imported into the appropriate `__init__.py` and added to the `__all__` list.

Following these conventions allows Pyoda Time users to enjoy a similar style of import as a Noda Time user.

C# example:

```csharp
using NodaTime;
using NodaTime.Text;
using NodaTime.TimeZones;
```

And in Python:

```python
from pyoda_time import *
from pyoda_time.text import *
from pyoda_time.time_zones import *
```

### Accessibility

- Use an underscore `_` prefix in Python to denote `internal` and `protected` elements in C#.
- Use a dunder `__` prefix in Python to denote `private` elements in C#.

#### Worked Example: Classes

C#:

```csharp
public class Foo {}

internal class Bar {}

private class Baz {}
```

Python:

```python
class Foo:  # public
    ...

class _Bar:  # internal
    ...

class __Baz:  # private
    ...
```

#### Worked Example: Methods 

C#:

```csharp
public class Foo
{
    public void DoSomething() {}
    
    internal void DoSomething() {}
    
    private void DoSomething() {}
}
```

Python:

```python
class Foo:

    def do_something(self) -> None:
        """Public method"""
        pass

    def _do_something(self) -> None:
        """Internal method"""
        pass

    def __do_something(self) -> None:
        """Private method"""
        pass
```

### Constructors

C# constructors which are `public` are translated to Python's `__init__` method.

C# constructors which are `internal` are converted to a classmethod, which by convention is named `_ctor` (single underscore).

Similarly, `private` constructors in C# are ported to a classmethod which by convention is named `__ctor` (double underscore).

#### Worked Example: Constructors

C#

```csharp
namespace Example;

public class Foo
{
    private int _privateData;
    internal string InternalData = "";
    public double PublicData;

    // Public constructor
    public Foo(double publicData)
    {
        PublicData = publicData;
        Console.WriteLine("Public constructor called.");
    }

    // Internal constructor
    internal Foo(string internalData, double publicData)
    {
        InternalData = internalData;
        PublicData = publicData;
        Console.WriteLine("Internal constructor called.");
    }

    // Private constructor
    private Foo(int privateData, string internalData, double publicData)
    {
        _privateData = privateData;
        InternalData = internalData;
        PublicData = publicData;
        Console.WriteLine("Private constructor called.");
    }

    // Example method to demonstrate calling the private constructor from within the class
    public static Foo CreateInstanceWithPrivateConstructor(int privateData, string internalData, double publicData)
    {
        return new Foo(privateData, internalData, publicData);
    }
}
```

Python:

```python
from __future__ import annotations


class Foo:

    def __init__(self, public_data: float) -> None:
        """Public constructor"""
        self.public_data = public_data
        self._internal_data = ""
        self.__private_data = 0  # In C#, int defaults to zero
        print("Public constructor called.")

    @classmethod
    def _ctor(cls, internal_data: str, public_data: float) -> Foo:
        """Internal constructor"""
        self: Foo = cls.__new__(cls)
        self.public_data = public_data
        self._internal_data = internal_data
        print("Internal constructor called.")
        return self

    @classmethod
    def __ctor(cls, private_data: int, internal_data: str, public_data: float) -> Foo:
        """Private constructor"""
        self: Foo = cls.__new__(cls)
        self.public_data = public_data
        self._internal_data = internal_data
        self.__private_data = private_data
        print("Private constructor called.")
        return self

    @classmethod
    def create_instance_with_private_constructor(
        cls, 
        private_data: int, 
        internal_data: str, 
        public_data: float
    ) -> Foo:
        """Example method to demonstrate calling the private constructor from within the class"""
        return cls.__ctor(private_data, internal_data, public_data)
```

`protected` constructors are a special case, and depend on the accessibility of the class:
- If the class is `public`, the `protected` constructor should be treated in the same manner as an `internal` constructer i.e. a `def _ctor(cls) -> Foo:` classmethod.
- If the class is `internal` or `private`, these constraints can be relaxed where it makes sense to do so, because the class itself is considered "not public". For example, an `internal abstract` C# class with a `protected` constructor will make more sense in Python as an `abc.ABC` with an `__init__()` rather than a `_ctor`

### Overloads

- Translate overloaded methods and constructors from C# to Python using `typing.overload`. 
- In Python overloads, we tend to prefer using keyword-only arguments for clarity and ease of implementation. 
- However, for simplicity and to maintain Pythonic idioms, it is acceptable to translate certain overloads without using `typing.overload` if it results in simpler, more elegant code.

#### Worked Example: using `typing.overload()`

C#:
```csharp
public void ExampleMethod(int x);
public void ExampleMethod(string y);
```
  
Python:

```python
from typing import overload

class MyClass:

  @overload
  def example_method(self, *, x: int) -> None:
      ...
  
  @overload
  def example_method(self, *, y: str) -> None:
      ...

  def example_method(self, *, x: int | None = None, y: str | None = None) -> None:
      if x is not None:
          ...
      elif y is not None:
          ...
```

#### Worked Example: Without `typing.overload()`

C#:

```csharp
public class MyClass
{
    public void ExampleMethod(int x)
    {
        // TODO
    }
    
    public void ExampleMethod(int x, int y) 
    {
        // TODO
    }
}
```
  
Python:

```python
class MyClass:

  def example_method(self, x: int, y: int | None = None) -> None:
      if y is None:
          ...
      else:
          ...
```

### Custom Decorators: @_sealed and @_private

- Some C# classes have no public constructor. To emulate this in Python, we use a custom `@_private` decorator. This decorator raises an exception when the `__init__()` method is called.
- To emulate `sealed` classes, we use a custom `@_sealed` decorator which raises an exception at runtime if a derived class is detected. The `@_sealed` decorator must always be stacked with the `@typing.final` decorator. (note: this decorator does not work for `sealed` methods)

### Interfaces

- Translate C# interfaces to Python's `typing.Protocol`.
- Apply the `@typing.runtime_checkable` decorator to Protocols where runtime `isinstance()` checks are required in library code.
- Wherever a C# class implements an interface, the equivalent Python class should explicitly inherit from the corresponding `Protocol`.

### Tests

By convention:

- Tests which are not nested inside a test class are unique to Pyoda Time.
- Tests which are ported from the classes in Noda Time's NUnit test suite *must* be within a corresponding test class in Python.

By following this convention, we minimise the overhead of tracking parity with Noda Time's test suite.
