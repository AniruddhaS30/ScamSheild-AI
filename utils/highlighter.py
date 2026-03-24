from typing import Dict, List, Tuple
import re


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def select_top_keywords(
    feature_contributions: Dict[str, float],
    top_k: int = 10,
) -> List[Tuple[str, float]]:
    """
    Given a mapping from feature name to contribution weight, return the top_k
    keywords sorted by absolute impact (descending).
    """
    items = list(feature_contributions.items())
    items.sort(key=lambda x: abs(x[1]), reverse=True)
    return items[:top_k]


def highlight_text(
    text: str,
    top_keywords: List[Tuple[str, float]],
) -> str:
    """
    Highlight top contributing unigrams present in the original text.
    - Red background for high-risk words (top 3 by abs weight)
    - Yellow background for remaining highlighted words
    Returns HTML string safe to render with st.markdown(..., unsafe_allow_html=True).
    """
    if not text or not top_keywords:
        return text

    # Consider only unigram tokens for highlighting
    sorted_keywords = sorted(top_keywords, key=lambda x: abs(x[1]), reverse=True)
    high_risk_tokens = {kw for kw, _ in sorted_keywords[:3]}
    medium_risk_tokens = {kw for kw, _ in sorted_keywords[3:]}

    tokens = re.split(r"(\W+)", text)
    highlighted_parts: List[str] = []

    for token in tokens:
        lower = token.lower()
        if re.fullmatch(r"\w+", token):
            if lower in high_risk_tokens:
                highlighted_parts.append(
                    f'<span class="scamshield-token scamshield-token-high">{token}</span>'
                )
            elif lower in medium_risk_tokens:
                highlighted_parts.append(
                    f'<span class="scamshield-token scamshield-token-medium">{token}</span>'
                )
            else:
                highlighted_parts.append(token)
        else:
            highlighted_parts.append(token)

    return "".join(highlighted_parts)

