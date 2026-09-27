"""Smart model router for Student Ops Desk.

Determines request complexity locally without calling any LLM.
Routes simple requests to Flash-Lite, complex to full Flash.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.config import get_simple_model_name, get_complex_model_name

logger = logging.getLogger(__name__)


class Complexity(Enum):
    """Request complexity classification."""
    SIMPLE = "simple"
    COMPLEX = "complex"


@dataclass(frozen=True)
class RoutingDecision:
    """Result of model routing decision."""
    complexity: Complexity
    model_name: str
    reason: str


# Patterns that indicate complex requests
COMPLEX_PATTERNS = [
    # Coding/debugging
    r"\b(debug|fix|error|exception|traceback|stack\s*trace)\b",
    r"\b(code|script|function|class|method|async|await|promise)\b",
    r"\b(refactor|optimize|performance|memory|leak)\b",
    # Multi-step reasoning
    r"\b(analyze|evaluate|compare|contrast|synthesize)\b",
    r"\b(step.by.step|break.down|reason.through)\b",
    # Multiple operations
    r"\b(and\s+then|then\s+also|also\s+do|plus\s+)\b",
    r"\b(multiple|several|various)\b",
    # Explicit specialist/tool requirements
    r"\b(handoff|transfer|specialist|escalate)\b",
    r"\b(debug|fix|implement|create|generate|build)\b",
    # Complex assignment/career requests
    r"\b(plan|roadmap|strategy|comprehensive|detailed)\b",
    r"\b(interview|portfolio|resume|career\s+path)\b",
    # Long technical analysis
    r"\b(architecture|design|system|infrastructure)\b",
]

# Patterns that indicate simple requests
SIMPLE_PATTERNS = [
    # Simple lookups
    r"^(what|which|when|where|who)\s+(is|are|was|were)\b",
    r"^(what|which)\s+(course|assignment|schedule|policy)\b",
    r"^(list|show|show\s+me)\b",
    r"^tell\s+me\s+about\b",
    r"^explain\s+(this|that|it)\b",
    r"^what\s+(does|is)\s+\w+\s+mean\b",
    r"^(when|what\s+time)\s+(is|does)\b",
    r"^deadline\b",
    r"^summarize\s+(this|that|it)\b",
    r"^define\s+\w+\b",
]

# Compile patterns
COMPILED_COMPLEX = [re.compile(p, re.IGNORECASE) for p in COMPLEX_PATTERNS]
COMPILED_SIMPLE = [re.compile(p, re.IGNORECASE) for p in SIMPLE_PATTERNS]


def _count_sentences(text: str) -> int:
    """Rough sentence count."""
    return len(re.split(r"[.!?]+", text.strip())) if text.strip() else 0


def _count_words(text: str) -> int:
    """Word count."""
    return len(text.split())


def _has_code_indicators(text: str) -> bool:
    """Check for code-like patterns."""
    code_indicators = [
        r"\b(def|class|import|from|async|await|return|yield)\b",
        r"[{};]",
        r"`{3}",
        r"```",
        r"\b(python|javascript|typescript|sql|json)\b",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in code_indicators)


def _has_multiple_questions(text: str) -> bool:
    """Check if message contains multiple questions."""
    return text.count("?") > 1


def _has_explicit_handoff_request(text: str) -> bool:
    """Check for explicit specialist/handoff requests."""
    handoff_keywords = [
        "transfer", "handoff", "specialist", "escalate",
        "assignments specialist", "careers specialist"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in handoff_keywords)


def classify_complexity(message: str, context: Optional[dict] = None) -> RoutingDecision:
    """Classify request complexity and select appropriate model.
    
    Args:
        message: User's message text
        context: Optional context dict with keys like:
            - conversation_length: number of previous turns
            - previous_handoffs: count of previous handoffs
            - tools_used: list of tools used in conversation
    
    Returns:
        RoutingDecision with complexity, model_name, and reason
    """
    if not message or not message.strip():
        return RoutingDecision(
            complexity=Complexity.SIMPLE,
            model_name=get_simple_model_name(),
            reason="empty_message"
        )
    
    text = message.strip()
    text_lower = text.lower()
    word_count = _count_words(text)
    sentence_count = _count_sentences(text)
    
    # Context factors
    conversation_length = context.get("conversation_length", 0) if context else 0
    previous_handoffs = context.get("previous_handoffs", 0) if context else 0
    tools_used = context.get("tools_used", []) if context else []
    
    # Start with SIMPLE, check for COMPLEX indicators
    is_complex = False
    reasons = []
    
    # 1. Explicit complex patterns
    for pattern in COMPILED_COMPLEX:
        if pattern.search(text):
            is_complex = True
            reasons.append(f"complex_pattern:{pattern.pattern[:30]}")
            break
    
    # 2. Explicit handoff/specialist request
    if _has_explicit_handoff_request(text):
        is_complex = True
        reasons.append("explicit_handoff_request")
    
    # 3. Code indicators
    if _has_code_indicators(text):
        is_complex = True
        reasons.append("code_indicators")
    
    # 4. Multiple questions
    if _has_multiple_questions(text):
        is_complex = True
        reasons.append("multiple_questions")
    
    # 5. Long message (many words/sentences)
    if word_count > 100 or sentence_count > 5:
        is_complex = True
        reasons.append(f"length:words={word_count},sentences={sentence_count}")
    
    # 6. Code indicators in text
    if _has_code_indicators(text):
        is_complex = True
        reasons.append("code_indicators")
    
    # 7. Conversation context - if already deep in conversation or had handoffs
    if conversation_length > 3:
        is_complex = True
        reasons.append(f"conversation_length={conversation_length}")
    
    if previous_handoffs > 0:
        is_complex = True
        reasons.append(f"previous_handoffs={previous_handoffs}")
    
    # 8. Tools already used in conversation
    if len(tools_used) > 2:
        is_complex = True
        reasons.append(f"tools_used={len(tools_used)}")
    
    # Check simple patterns (can override if ONLY simple patterns match)
    if not is_complex:
        for pattern in COMPILED_SIMPLE:
            if pattern.search(text):
                # Only simple if no complex indicators found
                reasons.append(f"simple_pattern:{pattern.pattern[:30]}")
                break
    
    # Decision
    if is_complex:
        model = get_complex_model_name()
        complexity = Complexity.COMPLEX
        reason = ";".join(reasons) if reasons else "default_complex"
    else:
        model = get_simple_model_name()
        complexity = Complexity.SIMPLE
        reason = ";".join(reasons) if reasons else "default_simple"
    
    logger.info("[MODEL_ROUTER] complexity=%s model=%s reason=%s words=%d",
                complexity.value, model, reason, word_count)
    
    return RoutingDecision(
        complexity=complexity,
        model_name=model,
        reason=reason
    )


def get_model_for_request(message: str, context: Optional[dict] = None) -> str:
    """Convenience function to get model name for a request."""
    return classify_complexity(message, context).model_name