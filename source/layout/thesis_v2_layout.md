# Thesis V2 Layout

`scripts/thesis_render_v2.py` reads one-line Markdown directives from this file.

Supported directives:

- `:::page-break-before match="REGEX"`
- `:::style match="REGEX" style="STYLE_NAME"`
- `:::build-image match="REGEX" script="relative/script.py" path="relative/output.png"`
- `:::image match="REGEX" path="relative/path.png" width_in="6.8"`

Starter rules:

:::page-break-before match="^(Chapter [1-5]:|第\s*[1-5一二三四五]\s*章)"
:::page-break-before match="^(Appendices|附錄)$"

Add project-specific figure and style rules after your chapter structure is stable.
