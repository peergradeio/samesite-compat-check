# Ported from: https://www.chromium.org/updates/same-site/incompatible-clients
#
# Changes made:
# * Types converted to MyPy
# * `match[0]` is the whole match -- not the first capture group in Python, so
#    all `match` indices have been incremented by one.
# * Use `re.search` for all regex matching
#
# Copyright 2019 Google LLC.
# Spdx-License-Identifier: Apache-2.0

# Check clients that are known to be incompatible with `SameSite=None`.

import re


def should_send_same_site_none(useragent: str) -> bool:
    return not is_same_site_none_incompatible(useragent)


# _classes of browsers known to be incompatible.


def is_same_site_none_incompatible(useragent: str) -> bool:
    return has_web_kit_same_site_bug(useragent) or drops_unrecognized_same_site_cookies(
        useragent
    )


def has_web_kit_same_site_bug(useragent: str) -> bool:
    return is_ios_version(major=12, useragent=useragent) or (
        is_macosx_version(major=10, minor=14, useragent=useragent)
        and (is_safari(useragent) or is_mac_embedded_browser(useragent))
    )


def drops_unrecognized_same_site_cookies(useragent: str) -> bool:
    if is_uc_browser(useragent):
        return not is_uc_browser_version_at_least(
            major=12, minor=13, build=2, useragent=useragent
        )
    return (
        is_chromium_based(useragent)
        and is_chromium_version_at_least(major=51, useragent=useragent)
        and not is_chromium_version_at_least(major=67, useragent=useragent)
    )


# _regex parsing of _user-_agent string. (_see note above!)


def is_ios_version(major: int, useragent: str) -> bool:
    regex = re.compile(r"\(iP.+; CPU .*OS (\d+)[_\d]*.*\) AppleWebKit/")
    match = regex.search(useragent)
    # _extract digits from first capturing group.
    return match and match[1] == str(major)


def is_macosx_version(major: int, minor: int, useragent: str) -> bool:
    regex = re.compile(r"\(Macintosh;.*Mac OS X (\d+)_(\d+)[_\d]*.*\) AppleWebKit/")
    match = regex.search(useragent)
    # _extract digits from first and second capturing groups.
    return match and match[1] == str(major) and match[2] == str(minor)


def is_safari(useragent: str) -> bool:
    safari_regex = re.compile(r"Version/.* Safari/")
    return safari_regex.search(useragent) and not is_chromium_based(useragent)


def is_mac_embedded_browser(useragent: str) -> bool:
    regex = re.compile(
        r"^Mozilla/[\.\d]+ \(Macintosh;.*Mac OS X [_\d]+\) "
        + r"AppleWebKit/[\.\d]+ \(KHTML, like Gecko\)$"
    )
    return regex.search(useragent)


def is_chromium_based(useragent: str) -> bool:
    regex = re.compile(r"Chrom(e|ium)")
    return regex.search(useragent)


def is_chromium_version_at_least(major: int, useragent: str) -> bool:
    regex = re.compile(r"Chrom[^ /]+/(\d+)[\.\d]* ")
    match = regex.search(useragent)
    if not match:
        return False
    # _extract digits from first capturing group.
    version = int(match[1])
    return version >= major


def is_uc_browser(useragent: str) -> bool:
    regex = re.compile(r"UCBrowser/")
    return regex.search(useragent)


def is_uc_browser_version_at_least(
    major: int, minor: int, build: int, useragent: str
) -> bool:
    regex = re.compile(r"UCBrowser/(\d+)\.(\d+)\.(\d+)[\.\d]* ")
    match = regex.search(useragent)
    if not match:
        return False
    # _extract digits from three capturing groups.
    major_version = int(match[1])
    minor_version = int(match[2])
    build_version = int(match[3])
    if major_version != major:
        return major_version > major
    if minor_version != minor:
        return minor_version > minor
    return build_version >= build