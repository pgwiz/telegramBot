"""Generic HTTP fetch + simple HTML extraction.

Lets users wire the bot to *any* public REST API or web page right from chat.
"""
from __future__ import annotations

import json
import re

import httpx

from settings import get_settings

from . import Integration, IntegrationResult, register

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    return _WS_RE.sub(" ", text).strip()


def _truncate(text: str, limit: int = 3500) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…(truncated)"


class FetchIntegration(Integration):
    name = "fetch"
    description = "GET any URL (returns JSON pretty-printed or text)"
    usage = "/fetch <url>"

    async def run(self, *args: str) -> IntegrationResult:
        if not args:
            return IntegrationResult(False, "Usage: /fetch <url>")
        url = args[0]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        settings = get_settings()
        async with httpx.AsyncClient(timeout=settings.http_timeout, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "telegramBot/1.0"})
        ctype = r.headers.get("content-type", "")
        body: str
        if "json" in ctype:
            try:
                body = json.dumps(r.json(), indent=2, ensure_ascii=False)
            except ValueError:
                body = r.text
        elif "html" in ctype:
            body = _strip_html(r.text)
        else:
            body = r.text
        return IntegrationResult(
            True,
            f"`{r.status_code}` {url}\n```\n{_truncate(body)}\n```",
            {"status": r.status_code, "url": url},
        )


class ScrapeIntegration(Integration):
    name = "scrape"
    description = "Fetch a page and extract text (optionally via regex)"
    usage = "/scrape <url> [regex]"

    async def run(self, *args: str) -> IntegrationResult:
        if not args:
            return IntegrationResult(False, "Usage: /scrape <url> [regex]")
        url = args[0]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        pattern = " ".join(args[1:]).strip()

        settings = get_settings()
        async with httpx.AsyncClient(timeout=settings.http_timeout, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "telegramBot/1.0"})
        text = _strip_html(r.text)
        if pattern:
            try:
                matches = re.findall(pattern, text, flags=re.IGNORECASE)[:25]
            except re.error as exc:
                return IntegrationResult(False, f"Bad regex: {exc}")
            body = "\n".join(map(str, matches)) if matches else "(no matches)"
        else:
            body = text
        return IntegrationResult(True, f"`{url}`\n```\n{_truncate(body, 3000)}\n```")


register(FetchIntegration())
register(ScrapeIntegration())
