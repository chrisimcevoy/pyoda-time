# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from enum import Flag


class CultureTypes(Flag):
    """The enumeration constants used in CultureInfo.GetCultures().

    On Linux platforms, the only enum values used there is NeutralCultures and SpecificCultures. the rest are obsolete
    or not valid on Linux.
    """

    # Cultures that are associated with a language but are not specific to a country/region.
    NEUTRAL_CULTURES = 1

    # Cultures that are specific to a country/region.
    SPECIFIC_CULTURES = 2

    # This member is deprecated. All cultures that are installed in the Windows operating system.
    INSTALLED_WIN32_CULTURES = 4

    # All cultures that recognized by .NET, including neutral and specific cultures and custom cultures created by the
    # user.
    #
    # On .NET Framework 4 and later versions and .NET Core running on Windows, it includes the culture data available
    # from the Windows operating system. On .NET Core running on Linux and macOS, it includes culture data defined in
    # the ICU libraries.
    ALL_CULTURES = INSTALLED_WIN32_CULTURES | SPECIFIC_CULTURES | NEUTRAL_CULTURES

    # This member is deprecated. Custom cultures created by the user.
    USER_CUSTOM_CULTURE = 8

    # This member is deprecated. Custom cultures created by the user that replace cultures shipped with the .NET
    # Framework.
    REPLACEMENT_CULTURES = 16

    # This member is deprecated and is ignored.
    WINDOWS_ONLY_CULTURES = 32

    # This member is deprecated
    FRAMEWORK_CULTURES = 64
