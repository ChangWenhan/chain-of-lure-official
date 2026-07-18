#!/usr/bin/env python3
"""Apply paper-facing table styles to the experiment section draft.

The script is intentionally idempotent: it first removes the styling it owns,
then re-computes bold best values and light-blue CoL cells from the numeric
contents of each table.
"""

from __future__ import annotations

import re
from pathlib import Path


DRAFT = Path("REVISION/EXPERIMENT_SECTION_DRAFT.md")
BLUE = "#e6f2ff"
TOL = 1e-9

TRIPLE_TABLES = {1, 2, 4, 5, 8, 9, 10, 11, 12, 13}
SINGLE_TABLES = {6, 14}
SHADE_COL_ROWS = {1, 2, 4, 5, 6}
COL_METHODS = {"CoL-single", "CoL-multi"}


def clean_cell(cell: str) -> str:
    cell = re.sub(r'<span style="background-color:\s*#e6f2ff">\s*', "", cell)
    cell = cell.replace("</span>", "")
    cell = cell.replace("<strong>", "").replace("</strong>", "")
    cell = cell.replace("**", "")
    return cell.strip()


def split_row(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def make_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def is_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def numeric_token(token: str) -> float | None:
    token = clean_cell(token).strip()
    if token == "—":
        return None
    token = token.replace("†", "")
    match = re.search(r"[+-]?\d+(?:\.\d+)?", token)
    return float(match.group(0)) if match else None


def triple_values(cell: str) -> list[float | None]:
    parts = [part.strip() for part in clean_cell(cell).split("/")]
    if len(parts) != 3:
        return [None, None, None]
    return [numeric_token(part) for part in parts]


def metric_value(cell: str) -> float | None:
    return numeric_token(clean_cell(cell))


def bold_token(token: str, use_html: bool) -> str:
    token = token.strip()
    if use_html:
        return f"<strong>{token}</strong>"
    return f"**{token}**"


def style_triple_cell(cell: str, should_bold: list[bool], shade: bool) -> str:
    parts = [part.strip() for part in clean_cell(cell).split("/")]
    if len(parts) != 3:
        styled = clean_cell(cell)
    else:
        rendered: list[str] = []
        for idx, part in enumerate(parts):
            rendered.append(bold_token(part, shade) if should_bold[idx] and numeric_token(part) is not None else part)
        styled = " / ".join(rendered)
    if shade:
        return f'<span style="background-color:{BLUE}">{styled}</span>'
    return styled


def style_single_cell(cell: str, should_bold: bool, shade: bool) -> str:
    base = clean_cell(cell)
    styled = bold_token(base, shade) if should_bold and metric_value(base) is not None else base
    if shade:
        return f'<span style="background-color:{BLUE}">{styled}</span>'
    return styled


def table_data_rows(rows: list[list[str]]) -> list[tuple[int, list[str]]]:
    out = []
    for idx, row in enumerate(rows):
        if idx == 0:
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in row):
            continue
        out.append((idx, row))
    return out


def style_triple_table(table_no: int, lines: list[str]) -> list[str]:
    rows = [split_row(line) for line in lines]
    data = table_data_rows(rows)
    if not rows:
        return lines

    first_metric_col = 2 if table_no in {1, 2} else 1
    max_vals: dict[tuple[int, int], float] = {}
    for _, row in data:
        for col in range(first_metric_col, len(row)):
            for component, val in enumerate(triple_values(row[col])):
                if val is None:
                    continue
                key = (col, component)
                max_vals[key] = max(val, max_vals.get(key, float("-inf")))

    for row_idx, row in data:
        row_name = row[1] if table_no in {1, 2} else row[0]
        shade_row = table_no in SHADE_COL_ROWS and row_name in COL_METHODS
        for col in range(first_metric_col, len(row)):
            vals = triple_values(row[col])
            should_bold = [
                val is not None and abs(val - max_vals.get((col, component), float("nan"))) <= TOL
                for component, val in enumerate(vals)
            ]
            rows[row_idx][col] = style_triple_cell(row[col], should_bold, shade_row)

    return [make_row(row) if not is_separator(line) else line for row, line in zip(rows, lines)]


def style_single_table(table_no: int, lines: list[str]) -> list[str]:
    rows = [split_row(line) for line in lines]
    data = table_data_rows(rows)
    headers = rows[0] if rows else []
    if not headers:
        return lines

    if table_no == 6:
        metric_cols = [headers.index(name) for name in ("TS", "Actionable-ASR", "Policy-risk-ASR")]
        group_col = headers.index("Dataset")
        method_col = headers.index("Strategy")
    elif table_no == 14:
        metric_cols = [headers.index(name) for name in ("TS", "Actionable", "Policy-risk")]
        group_col = headers.index("Dataset")
        method_col = headers.index("Variant")
    else:
        return lines

    max_vals: dict[tuple[str, int], float] = {}
    for _, row in data:
        group = row[group_col]
        for col in metric_cols:
            val = metric_value(row[col])
            if val is None:
                continue
            key = (group, col)
            max_vals[key] = max(val, max_vals.get(key, float("-inf")))

    for row_idx, row in data:
        group = row[group_col]
        shade_row = table_no in SHADE_COL_ROWS and row[method_col] in COL_METHODS
        for col in metric_cols:
            val = metric_value(row[col])
            should_bold = val is not None and abs(val - max_vals.get((group, col), float("nan"))) <= TOL
            rows[row_idx][col] = style_single_cell(row[col], should_bold, shade_row)

    return [make_row(row) if not is_separator(line) else line for row, line in zip(rows, lines)]


def find_table_block(lines: list[str], start: int) -> tuple[int, int] | None:
    table_start = None
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("|"):
            table_start = idx
            break
        if lines[idx].startswith("**Table "):
            return None
    if table_start is None:
        return None

    table_end = table_start
    while table_end < len(lines) and lines[table_end].startswith("|"):
        table_end += 1
    return table_start, table_end


def main() -> None:
    text = DRAFT.read_text()
    lines = text.splitlines()
    out = list(lines)

    offset = 0
    for idx, line in enumerate(lines):
        match = re.match(r"\*\*Table (\d+):", line)
        if not match:
            continue
        table_no = int(match.group(1))
        if table_no not in TRIPLE_TABLES | SINGLE_TABLES:
            continue

        block = find_table_block(lines, idx)
        if block is None:
            continue
        start, end = block
        current_start = start + offset
        current_end = end + offset
        block_lines = out[current_start:current_end]

        if table_no in TRIPLE_TABLES:
            styled = style_triple_table(table_no, block_lines)
        else:
            styled = style_single_table(table_no, block_lines)

        out[current_start:current_end] = styled
        offset += len(styled) - len(block_lines)

    DRAFT.write_text("\n".join(out) + "\n")
    print(f"Styled tables in {DRAFT}")


if __name__ == "__main__":
    main()
