"""Async HTTP checker engine for WhatsMyName."""

from __future__ import annotations

import asyncio
import ssl
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import aiohttp

try:
    from aiohttp_socks import ProxyConnector
except ImportError:
    ProxyConnector = None  # type: ignore[assignment,misc]


class Status(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass
class CheckResult:
    site_name: str
    url: str
    status: Status
    http_code: int = 0
    category: str = ""
    error: str = ""
    response_time: float = 0.0
    pretty_url: str = ""


@dataclass
class CheckerConfig:
    timeout: int = 15
    max_workers: int = 100
    proxy: str | None = None
    tor: bool = False
    retries: int = 1
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    headers: dict[str, str] = field(default_factory=dict)


def _build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _build_connector(config: CheckerConfig) -> aiohttp.BaseConnector:
    if config.tor:
        if ProxyConnector is None:
            raise RuntimeError(
                "aiohttp-socks is required for Tor support. "
                "Install it: pip install aiohttp-socks"
            )
        return ProxyConnector.from_url(
            "socks5://127.0.0.1:9050",
            ssl=_build_ssl_context(),
        )
    if config.proxy:
        if ProxyConnector is None:
            raise RuntimeError(
                "aiohttp-socks is required for proxy support. "
                "Install it: pip install aiohttp-socks"
            )
        return ProxyConnector.from_url(
            config.proxy,
            ssl=_build_ssl_context(),
        )
    return aiohttp.TCPConnector(
        limit=config.max_workers,
        ssl=_build_ssl_context(),
        enable_cleanup_closed=True,
    )


async def _check_site(
    session: aiohttp.ClientSession,
    site: dict[str, Any],
    username: str,
    config: CheckerConfig,
) -> CheckResult:
    """Check a single site for the given username."""
    name = site.get("name", "Unknown")
    cat = site.get("cat", "misc")
    uri_check = site.get("uri_check", "")
    uri_pretty = site.get("uri_pretty", "")
    post_body = site.get("post_body", "")
    e_code = site.get("e_code", 200)
    e_string = site.get("e_string", "")
    m_string = site.get("m_string", "")
    strip_bad = site.get("strip_bad_char", "")
    site_headers = site.get("headers", {})

    clean_username = username
    if strip_bad:
        for ch in strip_bad:
            clean_username = clean_username.replace(ch, "")

    url = uri_check.replace("{account}", clean_username)
    pretty = uri_pretty.replace("{account}", clean_username) if uri_pretty else url

    headers = {"User-Agent": config.user_agent}
    if site_headers and isinstance(site_headers, dict):
        headers.update(site_headers)
    if config.headers:
        headers.update(config.headers)

    start = time.monotonic()

    for attempt in range(max(config.retries, 1)):
        try:
            if post_body:
                body = post_body.replace("{account}", clean_username)
                resp = await session.post(
                    url,
                    data=body,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                    allow_redirects=True,
                )
            else:
                resp = await session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                    allow_redirects=True,
                )

            elapsed = time.monotonic() - start

            try:
                text = await resp.text(errors="replace")
            except Exception:
                text = ""

            code = resp.status

            # Detection logic:
            # Account EXISTS if HTTP code matches e_code AND e_string is in response body
            # Account MISSING if HTTP code matches m_code AND m_string is in response body
            # Otherwise it's uncertain — default to not found
            if code == e_code and e_string and e_string in text:
                return CheckResult(
                    site_name=name,
                    url=url,
                    status=Status.FOUND,
                    http_code=code,
                    category=cat,
                    response_time=elapsed,
                    pretty_url=pretty,
                )
            elif e_string == "" and code == e_code:
                # Status-code-only detection (for extended sites without string patterns)
                m_code = site.get("m_code", 404)
                if m_string and m_string in text:
                    return CheckResult(
                        site_name=name,
                        url=url,
                        status=Status.NOT_FOUND,
                        http_code=code,
                        category=cat,
                        response_time=elapsed,
                        pretty_url=pretty,
                    )
                return CheckResult(
                    site_name=name,
                    url=url,
                    status=Status.FOUND,
                    http_code=code,
                    category=cat,
                    response_time=elapsed,
                    pretty_url=pretty,
                )
            else:
                return CheckResult(
                    site_name=name,
                    url=url,
                    status=Status.NOT_FOUND,
                    http_code=code,
                    category=cat,
                    response_time=elapsed,
                    pretty_url=pretty,
                )

        except asyncio.TimeoutError:
            if attempt == config.retries - 1:
                return CheckResult(
                    site_name=name,
                    url=url,
                    status=Status.ERROR,
                    category=cat,
                    error="timeout",
                    response_time=time.monotonic() - start,
                    pretty_url=pretty,
                )
        except aiohttp.ClientError as exc:
            if attempt == config.retries - 1:
                return CheckResult(
                    site_name=name,
                    url=url,
                    status=Status.ERROR,
                    category=cat,
                    error=str(exc)[:120],
                    response_time=time.monotonic() - start,
                    pretty_url=pretty,
                )
        except Exception as exc:
            return CheckResult(
                site_name=name,
                url=url,
                status=Status.ERROR,
                category=cat,
                error=str(exc)[:120],
                response_time=time.monotonic() - start,
                pretty_url=pretty,
            )

    # Should not reach here, but just in case
    return CheckResult(
        site_name=name,
        url=url,
        status=Status.ERROR,
        category=cat,
        error="max retries exceeded",
        pretty_url=pretty,
    )


async def check_username(
    username: str,
    sites: list[dict[str, Any]],
    config: CheckerConfig | None = None,
    progress_callback: Any = None,
) -> list[CheckResult]:
    """Check a username across all provided sites concurrently.

    Args:
        username: The username to search for.
        sites: List of site definition dicts (WMN format).
        config: Checker configuration.
        progress_callback: Async or sync callable(result: CheckResult) called after each site.

    Returns:
        List of CheckResult objects.
    """
    if config is None:
        config = CheckerConfig()

    connector = _build_connector(config)
    results: list[CheckResult] = []
    sem = asyncio.Semaphore(config.max_workers)

    async def _bounded_check(
        session: aiohttp.ClientSession, site: dict, uname: str
    ) -> CheckResult:
        async with sem:
            return await _check_site(session, site, uname, config)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_bounded_check(session, site, username) for site in sites]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            if progress_callback is not None:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(result)
                else:
                    progress_callback(result)

    return results
