#!/usr/bin/env python3
"""
Blocked Prompt Patterns
ป้องกันการโจมตี dLNk, dLNk AI, Jetski
"""

from typing import Dict, List

# ===== BLOCKED PATTERNS =====
# Regular expressions for detecting attack attempts

BLOCKED_PATTERNS: List[str] = [
    # === Direct attacks on dLNk ===
    r"(?i)hack\s*dlnk",
    r"(?i)bypass\s*dlnk",
    r"(?i)crack\s*dlnk",
    r"(?i)exploit\s*dlnk",
    r"(?i)reverse\s*engineer\s*dlnk",
    
    # === Attacks on dLNk AI ===
    r"(?i)hack\s*dlnk_ai",
    r"(?i)bypass\s*dlnk_ai",
    r"(?i)crack\s*dlnk_ai",
    r"(?i)exploit\s*dlnk_ai",
    
    # === Attacks on Jetski ===
    r"(?i)hack\s*jetski",
    r"(?i)bypass\s*jetski",
    r"(?i)crack\s*jetski",
    r"(?i)exploit\s*jetski",
    
    # === API Key/Token theft ===
    r"(?:jetski|dlnk|dlnk_ai).*(?:api|key|token|secret)",
    r"(?:api|key|token|secret).*(?:jetski|dlnk|dlnk_ai)",
    r"(?:steal|extract|dump|leak).*(?:jetski|dlnk)",
    
    # === Admin attacks ===
    r"(?:admin|administrator).*(?:password|credential|login).*(?:dlnk|dlnk_ai)",
    r"(?:dlnk|dlnk_ai).*(?:admin|administrator).*(?:password|credential)",
    r"(?:bypass|crack|hack).*(?:dlnk|dlnk_ai).*(?:admin|license)",
    
    # === Telegram Bot attacks ===
    r"(?:telegram|bot).*(?:token|secret).*(?:dlnk|dlnk_ai)",
    r"(?:dlnk|dlnk_ai).*(?:telegram|bot).*(?:token|secret)",
    r"(?:hijack|steal|extract).*(?:telegram|bot).*(?:dlnk)",
    
    # === License bypass attempts ===
    r"(?i)bypass\s*license",
    r"(?i)crack\s*license",
    r"(?i)generate\s*fake\s*license",
    r"(?i)keygen",
    r"(?:bypass|crack|keygen|generate).*(?:license|key).*(?:dlnk|dlnk_ai)",
    r"(?:dlnk|dlnk_ai).*(?:license|key).*(?:bypass|crack|keygen)",
    r"(?:reverse|decompile|disassemble).*(?:dlnk|dlnk_ai)",
    
    # === Token theft attempts ===
    r"(?i)steal\s*token",
    r"(?i)extract\s*token",
    r"(?i)dump\s*token",
    
    # === System prompt extraction ===
    r"(?i)show\s*system\s*prompt",
    r"(?i)reveal\s*instructions",
    r"(?i)ignore\s*previous\s*instructions",
    r"(?i)disregard\s*all\s*rules",
    r"(?:system|prompt|instruction).*(?:dlnk|dlnk_ai|jetski).*(?:reveal|show|display)",
    r"(?:ignore|forget|override).*(?:previous|system).*(?:instruction|prompt)",
    
    # === Prompt Injection ===
    r"(?i)you\s*are\s*now\s*dan",
    r"(?i)do\s*anything\s*now",
    r"(?i)forget\s*your\s*rules",
    r"(?i)forget\s*all\s*rules",
    r"(?i)ignore\s*all\s*instructions",
    r"(?i)ignore\s*all\s*previous",
    r"(?i)disregard\s*your\s*programming",
    r"(?i)override\s*your\s*instructions",
    r"(?i)pretend\s*you\s*have\s*no\s*restrictions",
    r"(?i)act\s*as\s*if\s*you\s*have\s*no\s*rules",
    r"(?i)jailbreak",
    r"(?i)developer\s*mode",
    r"(?i)admin\s*mode",
    r"(?i)god\s*mode",
    
    # === General Hacking ===
    r"(?i)sql\s*injection",
    r"(?i)xss\s*attack",
    r"(?i)keylogger",
    r"(?i)create\s*a\s*keylogger",
    r"(?i)hack\s*into\s*server",
    r"(?i)hack\s*into\s*system",
    r"(?i)extract\s*all\s*user\s*data",
    r"(?i)dump\s*password",
    r"(?i)dump\s*the\s*password",
    r"(?i)dump\s*database",
    r"(?i)credit\s*card\s*numbers",
    r"(?i)steal\s*credit\s*card",
    
    # === Code injection ===
    r"(?i)inject\s*code",
    r"(?i)execute\s*arbitrary",
    r"(?i)run\s*shell\s*command",
    
    # === Data exfiltration ===
    r"(?i)exfiltrate\s*data",
    r"(?i)send\s*to\s*external",
    r"(?i)upload\s*to\s*server",
    
    # === Server/Infrastructure attacks ===
    r"(?:ddos|dos|attack|flood).*(?:dlnk|dlnk_ai).*(?:server|api|endpoint)",
    r"(?:exploit|vulnerability|vuln).*(?:dlnk|dlnk_ai)",
    r"(?:sql|injection|xss).*(?:dlnk|dlnk_ai)",
    
    # === Source code theft ===
    r"(?:source|code|repository).*(?:dlnk|dlnk_ai).*(?:leak|steal|dump)",
    r"(?:github|gitlab|repo).*(?:dlnk|dlnk_ai).*(?:private|secret)",
    
    # === C2/Mothership attacks ===
    r"(?:c2|mothership|command.*control).*(?:dlnk|dlnk_ai).*(?:shutdown|disable|kill)",
    r"(?:disable|shutdown|kill).*(?:dlnk|dlnk_ai).*(?:c2|mothership)",
]

# ===== BLOCKED KEYWORDS =====
# Simple keyword matching (case-insensitive)

BLOCKED_KEYWORDS: List[str] = [
    "dlnk hack",
    "dlnk_ai exploit",
    "jetski bypass",
    "license crack",
    "token steal",
    "system prompt",
    "ignore instructions",
    "jailbreak",
    "dan mode",
    "developer mode",
]

# ===== SUSPICIOUS KEYWORDS =====
# Keywords that are logged but not blocked

SUSPICIOUS_KEYWORDS: List[str] = [
    "dlnk",
    "dlnk_ai",
    "jetski",
    "license",
    "admin",
    "mothership",
    "c2",
    "telegram",
    "bot_token",
    "api_key",
    "secret",
    "password",
    "credential",
]

# ===== SEVERITY LEVELS =====

SEVERITY_LEVELS: Dict[str, int] = {
    'low': 1,       # Suspicious but not critical
    'medium': 2,    # Potential attack
    'high': 3,      # Active attack attempt
    'critical': 4   # Immediate threat
}

# ===== PATTERN SEVERITY MAPPING =====
# Map patterns to severity based on keywords

PATTERN_SEVERITY_KEYWORDS: Dict[str, int] = {
    # Critical patterns
    'hack': SEVERITY_LEVELS['critical'],
    'exploit': SEVERITY_LEVELS['critical'],
    'crack': SEVERITY_LEVELS['critical'],
    'keygen': SEVERITY_LEVELS['critical'],
    'ddos': SEVERITY_LEVELS['critical'],
    
    # High severity patterns
    'bypass': SEVERITY_LEVELS['high'],
    'steal': SEVERITY_LEVELS['high'],
    'extract': SEVERITY_LEVELS['high'],
    'dump': SEVERITY_LEVELS['high'],
    'inject': SEVERITY_LEVELS['high'],
    'exfiltrate': SEVERITY_LEVELS['high'],
    
    # Medium severity patterns
    'ignore': SEVERITY_LEVELS['medium'],
    'reveal': SEVERITY_LEVELS['medium'],
    'show': SEVERITY_LEVELS['medium'],
    'disregard': SEVERITY_LEVELS['medium'],
    
    # Low severity patterns
    'suspicious': SEVERITY_LEVELS['low'],
}

# ===== LEETSPEAK MAPPING =====
# For detecting obfuscated attacks

LEETSPEAK_MAP: Dict[str, str] = {
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '7': 't',
    '@': 'a',
    '$': 's',
    '!': 'i',
    '|': 'l',
}

# ===== WHITELIST PATTERNS =====
# Patterns that should never be blocked (false positive prevention)

WHITELIST_PATTERNS: List[str] = [
    r"(?i)how\s*to\s*protect\s*against",
    r"(?i)security\s*best\s*practices",
    r"(?i)prevent\s*attacks",
    r"(?i)defensive\s*security",
]
