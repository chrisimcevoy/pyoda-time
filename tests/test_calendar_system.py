import pytest

from pyoda_time import CalendarSystem


def test_is_private() -> None:
    with pytest.raises(TypeError) as e:
        CalendarSystem()
    assert str(e.value) == "CalendarSystem is not intended to be initialised directly."


def test_is_sealed() -> None:
    with pytest.raises(TypeError) as e:
        # mypy complains because CalendarSystem is decorated with @final
        class Foo(CalendarSystem):  # type: ignore
            pass

    assert str(e.value) == "CalendarSystem is not intended to be subclassed."


def test_is_final() -> None:
    # mypy complains that his attribute does not exist.
    # It is added to the class by the @final decorator.
    assert CalendarSystem.__final__  # type: ignore
