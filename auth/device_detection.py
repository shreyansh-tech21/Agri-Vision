from __future__ import annotations

import re
from typing import Optional, Tuple


def detect_browser(user_agent: str) -> Optional[str]:
    ua = (user_agent or "").lower()

    # Order matters: Brave has Chrome-like tokens.
    if "brave" in ua:
        return "Brave"
    if "edg/" in ua or "edge" in ua:
        return "Edge"
    if "opr/" in ua or "opera" in ua:
        return "Opera"
    if "chrome" in ua and "chromium" not in ua and "edge" not in ua and "opr" not in ua:
        return "Chrome"
    if "firefox" in ua:
        return "Firefox"
    if "safari" in ua and "chrome" not in ua and "chromium" not in ua:
        return "Safari"

    return None


def detect_os(user_agent: str) -> Optional[str]:
    ua = (user_agent or "").lower()

    if "android" in ua:
        return "Android"
    if "iphone" in ua or "ipad" in ua or "ios" in ua:
        return "iOS"
    if "windows" in ua:
        return "Windows"
    if "mac os" in ua or re.search(r"macintosh|mac os x", ua):
        return "macOS"
    if "linux" in ua and "android" not in ua:
        return "Linux"

    return None


def detect_device_type(user_agent: str) -> Optional[str]:
    ua = (user_agent or "").lower()

    if "android" in ua or "iphone" in ua or "ipad" in ua:
        # iPads are often tablets; we don't have reliable sizes here.
        if "ipad" in ua:
            return "Tablet"
        return "Mobile"

    # Desktop heuristics
    if "windows" in ua or "mac os" in ua or "linux" in ua:
        return "Desktop"

    return None


def detect_device_name(browser_name: Optional[str], operating_system: Optional[str]) -> Optional[str]:
    if not browser_name and not operating_system:
        return None
    if browser_name and operating_system:
        return f"{operating_system} {browser_name}"
    return browser_name or operating_system


def parse_device_metadata(user_agent: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    browser = detect_browser(user_agent)
    operating_system = detect_os(user_agent)
    device_type = detect_device_type(user_agent)
    device_name = detect_device_name(browser, operating_system)
    return device_name, browser, operating_system, device_type

