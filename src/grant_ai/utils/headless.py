"""Headless browser fetcher (stub).

Provides a single function `fetch_rendered_html(url)` that attempts to use a
headless browser (Playwright or Selenium) if installed; otherwise falls back to
simple requests. Safe to import in minimal environments.
"""
from __future__ import annotations

from typing import Optional


def _try_playwright():
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        return sync_playwright
    except Exception:
        return None


def _try_selenium():
    try:
        from selenium import webdriver  # type: ignore
        from selenium.webdriver.firefox.options import (
            Options as FFOptions,  # type: ignore
        )
        return webdriver, FFOptions
    except Exception:
        return None, None


def fetch_rendered_html(url: str, *, timeout: int = 20) -> Optional[str]:
    """Fetch rendered HTML for a JS-heavy page.

    Tries Playwright (preferred), then Selenium (Firefox), and finally falls
    back to a simple HTTP GET using stdlib.
    Returns HTML string on success, else None. All errors are swallowed.
    """
    # Playwright path
    sp = _try_playwright()
    if sp is not None:
        try:
            with sp() as p:
                browser = p.firefox.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(timeout * 1000)
                page.goto(url)
                page.wait_for_load_state("networkidle")
                html = page.content()
                browser.close()
                return html
        except Exception:
            pass

    # Selenium path
    webdriver, FFOptions = _try_selenium()
    if webdriver is not None and FFOptions is not None:
        try:
            opts = FFOptions()
            opts.add_argument("-headless")
            driver = webdriver.Firefox(options=opts)
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            html = driver.page_source
            driver.quit()
            return html
        except Exception:
            try:
                driver.quit()  # type: ignore[name-defined]
            except Exception:
                pass

    # Stdlib fallback
    try:
        import urllib.request

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        # nosec B310: URL comes from trusted configuration/use
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None
