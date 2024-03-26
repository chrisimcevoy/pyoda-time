# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import functools
import typing

from ..utility._csharp_compatibility import _private, _sealed


class _EraMeta(type):
    """Class properties for ``Era``.

    This implementation mimics the API of Noda Time by providing attribute-like
    access against the ``Era`` class.

    An important implementation detail is that equality checks in the codebase
    depend on these properties returning the same instance, because __eq__ is not
    implemented (so we rely on reference equality). Era._ctor() is called from
    each of these properties, and is decorated with `@functools.cache` to provide
    just that behaviour.

    Why not use functools.cached_property?
    https://discuss.python.org/t/finding-a-path-forward-for-functools-cached-property/23757
    """

    @property
    def common(cls) -> Era:
        """The "Common" era (CE), also known as Anno Domini (AD).

        This is used in the ISO, Gregorian and Julian calendars.
        """
        return Era._ctor("CE", "Eras_Common")

    @property
    def before_common(cls) -> Era:
        """The "before common" era (BCE), also known as Before Christ (BC).

        This is used in the ISO, Gregorian and Julian calendars.
        """
        return Era._ctor("BCE", "Eras_BeforeCommon")

    @property
    def anno_martyrum(self) -> Era:
        """The "Anno Martyrum" or "Era of the Martyrs".

        This is the sole era used in the Coptic calendar.
        """
        return Era._ctor("AM", "Eras_AnnoMartyrum")

    @property
    def anno_hegirae(self) -> Era:
        """The "Anno Hegira" era.

        This is the sole era used in the Hijri (Islamic) calendar.
        """
        return Era._ctor("EH", "Eras_AnnoHegirae")

    @property
    def anno_mundi(self) -> Era:
        """The "Anno Mundi" era.

        This is the sole era used in the Hebrew calendar.
        """
        return Era._ctor("AM", "Eras_AnnoMundi")

    @property
    def anno_persico(self) -> Era:
        """The "Anno Persico" era.

        This is the sole era used in the Persian calendar.
        """
        return Era._ctor("AP", "Eras_AnnoPersico")

    @property
    def bahai(cls) -> Era:
        """The "Bahá'í" era.

        This is the sole era used in the Badi calendar.
        """
        return Era._ctor("BE", "Eras_Bahai")


@typing.final
@_private
@_sealed
class Era(metaclass=_EraMeta):
    """Represents an era used in a calendar.

    All the built-in calendars in Pyoda Time use the values specified by the classmethods in this class. These may be
    compared for reference equality to check for specific eras.
    """

    @property
    def _resource_identifier(self) -> str:
        return self.__resource_identifier

    @property
    def name(self) -> str:
        """Return the name of this era, e.g. "CE" or "BCE"."""
        return self.__name

    __name: str
    __resource_identifier: str

    @classmethod
    @functools.cache
    def _ctor(cls, name: str, resource_identifier: str) -> Era:
        """Internal constructor implementation.

        Note: This constructor is cached and will return the same instance each
        time it is called with the same arguments.

        This is an implementation detail which is particular to pyoda-time and is
        not present in the mother project. (Although it is intended to mimic the
        characteristics of the static read-only properties in that world).

        The reason is that the class-level properties of _EraMeta all call this constructor.
        There are several places in the codebase where Eras are evaluated for equality,
        but as Era does not implement __eq__(), referential equality is relied upon
        hence the need to return the same instance each time this is called.

        Why not use functools.cached_property? Well, maybe in future:
        https://discuss.python.org/t/finding-a-path-forward-for-functools-cached-property/23757
        """
        self = super().__new__(cls)
        self.__name = name
        self.__resource_identifier = resource_identifier
        return self

    def __str__(self) -> str:
        """Return the name of this era."""
        return self.name
