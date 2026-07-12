from __future__ import annotations

import html


def render_sequence_markup(tokens: list[str], completed_count: int, last_wrong: bool) -> str:
    if not tokens:
        return ""

    current_index = min(completed_count, len(tokens) - 1)
    rendered: list[str] = []
    for idx, token in enumerate(tokens):
        value = token if token else "?"
        escaped = html.escape(value)
        if value == " ":
            escaped = "&middot;"

        if idx < completed_count:
            rendered.append(f"<span style='color:#57d08f;'>{escaped}</span>")
        elif idx == current_index:
            if last_wrong:
                rendered.append(f"<span style='color:#f87171;font-weight:700;'>{escaped}</span>")
            else:
                rendered.append(f"<span style='color:#ffffff;font-weight:700;'>{escaped}</span>")
        else:
            rendered.append(f"<span style='color:#ffffff;'>{escaped}</span>")

    return "<div style='line-height:1.35;text-align:center;'>" + " ".join(rendered) + "</div>"
