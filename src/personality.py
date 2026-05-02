"""Personality engine: vibes (``funny`` / ``pro`` / ``chill``) and a banter pool.

If an LLM is configured (``LLM_PROVIDER`` + ``LLM_API_KEY``) the engine will
delegate ``ask`` calls to it. Otherwise it falls back to curated responses so
the bot stays fun even fully offline.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass

import httpx

from settings import get_settings

logger = logging.getLogger(__name__)

VALID_VIBES = ("funny", "pro", "chill")

JOKES = [
    "Why don't programmers like nature? It has too many bugs.",
    "I told my computer I needed a break, and it said: 'no problem — I'll go to sleep.'",
    "There are 10 kinds of people: those who get binary, and those who don't.",
    "Debugging: being the detective in a crime movie where you are also the murderer.",
    "I'd tell you a UDP joke, but you might not get it.",
    "Why did the developer go broke? Because he used up all his cache.",
    "My code doesn't have bugs. It just develops random features.",
    "Real programmers count from 0.",
    "I would tell you a joke about an empty array, but it would have nothing in it.",
    "Algorithm: word used by programmers when they don't want to explain what they did.",
]

ROASTS = [
    "If laziness was a sport, you'd come in fourth — too lazy to make the podium.",
    "You bring everyone so much joy… when you leave the room.",
    "Your code reviews are like horoscopes — vague, dramatic, and always wrong.",
    "I'd agree with you, but then we'd both be wrong.",
    "You're proof that even autocomplete has limits.",
    "Don't worry — I think you're a great person… by your own standards.",
]

COMEBACKS = [
    "I would explain it to you, but I left my crayons at home.",
    "I'm not arguing, I'm just explaining why I'm right.",
    "If I wanted to hear from someone like you, I'd have asked.",
    "Light travels faster than sound, which is why some people seem bright until they speak.",
]

FACTS = [
    "Honey never spoils. Archaeologists have eaten 3000-year-old honey from tombs.",
    "Octopuses have three hearts and blue blood.",
    "A day on Venus is longer than its year.",
    "Bananas are berries, but strawberries aren't.",
    "There are more possible chess games than atoms in the observable universe.",
    "Wombat poop is cube-shaped.",
    "Sharks existed before trees.",
]

VIBE_INTROS = {
    "funny": ["lol ok —", "alright comedian —", "buckle up —", "hot take incoming —"],
    "pro":   ["Sure.", "Here you go:", "Got it."],
    "chill": ["yeah, no worries —", "easy —", "all good —"],
}

VIBE_OUTROS = {
    "funny": [" 😎", " 🤪", " — don't tell my therapist."],
    "pro":   [""],
    "chill": [" ✌️", ""],
}


@dataclass
class PersonalityConfig:
    vibe: str = "funny"

    def normalized(self) -> str:
        return self.vibe if self.vibe in VALID_VIBES else "funny"


def joke() -> str:
    return random.choice(JOKES)


def roast() -> str:
    return random.choice(ROASTS)


def comeback() -> str:
    return random.choice(COMEBACKS)


def fun_fact() -> str:
    return random.choice(FACTS)


def stylize(text: str, vibe: str = "funny") -> str:
    """Wrap a plain message with the given vibe's intro/outro."""
    vibe = vibe if vibe in VALID_VIBES else "funny"
    intro = random.choice(VIBE_INTROS[vibe])
    outro = random.choice(VIBE_OUTROS[vibe])
    return f"{intro} {text}{outro}".strip()


_SYSTEM_PROMPTS = {
    "funny": (
        "You are a witty, irreverent Telegram bot. Keep replies short (under 80 words), "
        "punchy, and sprinkle light humor. Never be mean or unsafe."
    ),
    "pro": (
        "You are a precise, professional assistant. Answer concisely and clearly with "
        "no fluff. Bullet points when listing."
    ),
    "chill": (
        "You are a relaxed, friendly assistant. Replies are warm, casual, and concise."
    ),
}


async def ask_llm(prompt: str, vibe: str = "funny") -> str | None:
    """Best-effort LLM call. Returns ``None`` if no LLM is configured or the
    request fails — callers fall back to canned responses."""
    settings = get_settings()
    provider = settings.llm_provider
    if not provider or not settings.llm_api_key:
        return None

    base_url = settings.llm_base_url or "https://api.openai.com/v1"
    url = base_url.rstrip("/") + "/chat/completions"

    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPTS.get(vibe, _SYSTEM_PROMPTS["funny"])},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8 if vibe == "funny" else 0.4,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning("LLM call failed (%s): %s", provider, exc)
        return None


async def reply_to(prompt: str, vibe: str = "funny") -> str:
    """Public entry point used by ``/ask``: try LLM, fall back to canned banter."""
    answer = await ask_llm(prompt, vibe=vibe)
    if answer:
        return answer
    canned = (
        f"My LLM brain is offline 🧠💤 — but here's a {vibe} thought: "
        f"{joke() if vibe == 'funny' else fun_fact()}"
    )
    return stylize(canned, vibe)
