"""
dates_to_spanish.translator
===========================

Minimal, dependency-free utilities to obtain **Spanish month** and **Spanish weekday**
names from a given date. Input can be a `date`, `datetime`, or a `str` in one of these
orders (separators `/`, `-`, `.` are accepted — internally normalized to `/`):

- `YMD` → `YYYY/MM/DD`
- `MDY` → `MM/DD/YYYY`
- `DMY` → `DD/MM/YYYY`

Public API
----------
- `month_es(...)`         → full Spanish month name (e.g., "Enero").
- `day_es(...)`           → full Spanish weekday name (e.g., "Lunes").
- `month_abbr_es(...)`    → standard 3-letter month abbreviation (e.g., "Ene").
- `day_abbr_es(...)`      → standard 3-letter weekday abbreviation (e.g., "Lun").
- `month_prefix_es(...)`  → prefix of length `n` from the month full name.
- `day_prefix_es(...)`    → prefix of length `n` from the weekday full name.

Typing follows Python’s `typing` module conventions (see FastAPI’s motivation page).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Union

# ---------------------------------------------------------------------------
# Type aliases (for clear intent in editors/linters/IDEs)
# ---------------------------------------------------------------------------

DateLike = Union[date, datetime, str]
"""Accepted input types for public functions:
- `date`
- `datetime`
- `str` in a format controlled via `order` (`YMD`, `MDY`, `DMY`)."""

Case = Literal["title", "lower"]
"""Output capitalization:
- `"title"` → Title Case (e.g., `Enero`, `Lunes`)
- `"lower"` → lowercase (e.g., `enero`, `lunes`)"""

Order = Literal["YMD", "MDY", "DMY"]
"""Expected order when `value` is `str`:
- `"YMD"` → `YYYY/MM/DD`
- `"MDY"` → `MM/DD/YYYY`
- `"DMY"` → `DD/MM/YYYY`"""

__all__ = [
    "month_es",
    "day_es",
    "month_abbr_es",
    "day_abbr_es",
    "month_prefix_es",
    "day_prefix_es",
    "DateLike",
    "Case",
    "Order",
]  # Public API

# =========================
# Data (name tables)
# =========================

# Index 1..12 (position 0 unused so that month index maps directly)
_MONTHS_ES_TITLE: list[str | None] = [
    None,
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]
"""Full Spanish month names (1-based index; index 0 unused)."""

# Standard Spanish month abbreviations (3 chars, with accents where applicable)
# Commonly used in Spanish: Ene, Feb, Mar, Abr, May, Jun, Jul, Ago, Sep, Oct, Nov, Dic
_MONTHS_ES_ABBR: list[str | None] = [
    None,
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]
"""Standard 3-letter Spanish month abbreviations (1-based index; index 0 unused)."""

# `date.weekday()`: Monday=0 .. Sunday=6
_DAYS_ES_TITLE: list[str] = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]
"""Full Spanish weekday names aligned with `date.weekday()` (0=Monday..6=Sunday)."""

# Standard Spanish weekday abbreviations (3 chars): Lun, Mar, Mié, Jue, Vie, Sáb, Dom
_DAYS_ES_ABBR: list[str] = [
    "Lun",
    "Mar",
    "Mié",
    "Jue",
    "Vie",
    "Sáb",
    "Dom",
]
"""Standard 3-letter Spanish weekday abbreviations aligned with `date.weekday()`."""


# =========================
# Internal helpers (private)
# =========================


def _apply_case(s: str, case: Case) -> str:
    """Apply the requested capitalization style.

    Args:
        s: Base string (e.g., "Enero").
        case: `"title"` to keep Title Case, `"lower"` to lowercase.

    Returns:
        The transformed string, e.g., `"Enero"` or `"enero"`.
    """
    return s if case == "title" else s.lower()


def _normalize_separators(s: str) -> str:
    """Normalize `-` and `.` separators to `/` for consistent parsing.

    Args:
        s: Date as a string.

    Returns:
        The string with separators normalized to `/`.
    """
    return s.replace("-", "/").replace(".", "/")


def _fmt(order: Order) -> str:
    """Return the `strptime` pattern for the requested order.

    Args:
        order: One of `"YMD"`, `"MDY"`, or `"DMY"`.

    Returns:
        A `strptime` format string, for example: `"%Y/%m/%d"`.

    Raises:
        ValueError: If an unsupported literal is provided.
    """
    if order == "YMD":
        return "%Y/%m/%d"
    if order == "MDY":
        return "%m/%d/%Y"
    if order == "DMY":
        return "%d/%m/%Y"
    raise ValueError(f"Unsupported order: {order}")


def _to_date(value: DateLike, order: Order) -> date:
    """Convert the input to a `date`.

    - If `value` is `datetime`, calls `.date()`.
    - If `value` is `date`, returns it as-is.
    - If `value` is `str`, parses it according to `order` (`YMD`/`MDY`/`DMY`), accepting
      `-`, `.`, `/` separators (normalized internally to `/`).

    Args:
        value: Date as `date`, `datetime`, or `str`.
        order: Expected order when `value` is `str`.

    Returns:
        A `date` object resulting from parsing/conversion.

    Raises:
        TypeError: If `value`'s type is unsupported.
        ValueError: If the `str` does not match the expected format for `order`.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        norm = _normalize_separators(value.strip())
        fmt = _fmt(order)
        return datetime.strptime(norm, fmt).date()
    raise TypeError(
        "Provide a date/datetime or a str in YYYY/MM/DD, MM/DD/YYYY, or DD/MM/YYYY."
    )


# =========================
# Public API (full names)
# =========================


def month_es(value: DateLike, *, order: Order = "MDY", case: Case = "title") -> str:
    """Get the **full Spanish month name**.

    Supports `date`, `datetime`, or `str`. When the input is `str`, you must
    specify the expected format via `order`:
    - `"YMD"`: `YYYY/MM/DD`
    - `"MDY"`: `MM/DD/YYYY`
    - `"DMY"`: `DD/MM/YYYY`

    Separators `-` and `.` are valid; they are normalized to `/`.

    Args:
        value: Date as `date`, `datetime`, or `str`.
        order: Expected order if `value` is `str`. Defaults to `"MDY"`.
        case: Output capitalization: `"title"` (`Enero`) or `"lower"` (`enero`).

    Returns:
        Spanish month name, e.g., `"Enero"` or `"enero"`.

    Examples:
        >>> month_es("2025/01/06", order="YMD")
        'Enero'
        >>> month_es("01/06/2025", order="MDY", case="lower")
        'enero'
        >>> from datetime import date
        >>> month_es(date(2025, 7, 20))
        'Julio'
    """
    d = _to_date(value, order)
    name = _MONTHS_ES_TITLE[d.month]
    # `name` cannot be None for indices 1..12; index 0 placeholder is never used.
    return _apply_case(name or "", case)


def day_es(value: DateLike, *, order: Order = "MDY", case: Case = "title") -> str:
    """Get the **full Spanish weekday name**.

    Uses `date.weekday()` (Monday=0 .. Sunday=6). Supports `date`, `datetime`, or `str`.
    For `str`, `order` defines the expected format (see `month_es`).

    Args:
        value: Date as `date`, `datetime`, or `str`.
        order: Expected order if `value` is `str`. Defaults to `"MDY"`.
        case: Output capitalization: `"title"` (`Lunes`) or `"lower"` (`lunes`).

    Returns:
        Spanish weekday name, e.g., `"Lunes"` or `"lunes"`.

    Examples:
        >>> day_es("2025/01/06", order="YMD")
        'Lunes'
        >>> day_es("06/01/2025", order="DMY", case="lower")
        'lunes'
        >>> from datetime import datetime
        >>> day_es(datetime(2025, 1, 7, 12, 0))
        'Martes'
    """
    d = _to_date(value, order)
    name = _DAYS_ES_TITLE[d.weekday()]
    return _apply_case(name, case)


# =========================
# Public API (standard abbreviations)
# =========================


def month_abbr_es(
    value: DateLike, *, order: Order = "MDY", case: Case = "title"
) -> str:
    """Get the **standard 3-letter Spanish month abbreviation**.

    The set is: `Ene, Feb, Mar, Abr, May, Jun, Jul, Ago, Sep, Oct, Nov, Dic`.

    Args:
        value: Date as `date`, `datetime`, or `str`.
        order: Expected order if `value` is `str`. Defaults to `"MDY"`.
        case: Output capitalization: `"title"` (e.g., `Ene`) or `"lower"` (e.g., `ene`).

    Returns:
        The 3-letter month abbreviation in Spanish.

    Examples:
        >>> month_abbr_es("2025-12-01", order="YMD")
        'Dic'
        >>> month_abbr_es("12/01/2025", order="MDY", case="lower")
        'dic'
    """
    d = _to_date(value, order)
    abbr = _MONTHS_ES_ABBR[d.month]
    return _apply_case(abbr or "", case)


def day_abbr_es(
    value: DateLike, *, order: Order = "MDY", case: Case = "title"
) -> str:
    """Get the **standard 3-letter Spanish weekday abbreviation**.

    The set is: `Lun, Mar, Mié, Jue, Vie, Sáb, Dom`.

    Args:
        value: Date as `date`, `datetime`, or `str`.
        order: Expected order if `value` is `str`. Defaults to `"MDY"`.
        case: Output capitalization: `"title"` (e.g., `Lun`) or `"lower"` (e.g., `lun`).

    Returns:
        The 3-letter weekday abbreviation in Spanish.

    Examples:
        >>> day_abbr_es("2025-01-07", order="YMD", case="lower")
        'mar'
        >>> day_abbr_es("01/07/2025", order="DMY")
        'Mar'
    """
    d = _to_date(value, order)
    abbr = _DAYS_ES_ABBR[d.weekday()]
    return _apply_case(abbr, case)


# =========================
# Public API (prefix of length n)
# =========================


def month_prefix_es(
    value: DateLike,
    *,
    n: int = 3,
    order: Order = "MDY",
    case: Case = "title",
) -> str:
    """Get the **prefix of length `n`** from the Spanish month full name.

    Notes:
        - This simply slices the full name (preserves accents).
        - If you want standard 3-letter abbreviations, use `month_abbr_es`.

    Args:
        value: Date as `date`, `datetime`, or `str`.
        n: Desired prefix length. Must be `>= 1`.
        order: Expected order if `value` is `str`. Defaults to `"MDY"`.
        case: Output capitalization: `"title"` or `"lower"`.

    Returns:
        A prefix of length `n` from the month full name in Spanish.

    Examples:
        >>> month_prefix_es("2025/09/10", order="YMD", n=4)
        'Sept'
        >>> month_prefix_es("2025/05/10", order="YMD", n=3, case="lower")
        'may'
    """
    if n < 1:
        raise ValueError("`n` must be >= 1.")
    full = month_es(value, order=order, case="title")  # canonical Title Case
    pref = full[:n]
    return _apply_case(pref, case)


def day_prefix_es(
    value: DateLike,
    *,
    n: int = 3,
    order: Order = "MDY",
    case: Case = "title",
) -> str:
    """Get the **prefix of length `n`** from the Spanish weekday full name.

    Notes:
        - This simply slices the full name (preserves accents).
        - If you want standard 3-letter abbreviations, use `day_abbr_es`.

    Args:
        value: Date as `date`, `datetime`, or `str`.
        n: Desired prefix length. Must be `>= 1`.
        order: Expected order if `value` is `str`. Defaults to `"MDY"`.
        case: Output capitalization: `"title"` or `"lower"`.

    Returns:
        A prefix of length `n` from the weekday full name in Spanish.

    Examples:
        >>> day_prefix_es("2025/01/07", order="YMD", n=2)
        'Ma'
        >>> day_prefix_es("2025/01/06", order="YMD", n=3, case="lower")
        'lun'
    """
    if n < 1:
        raise ValueError("`n` must be >= 1.")
    full = day_es(value, order=order, case="title")  # canonical Title Case
    pref = full[:n]
    return _apply_case(pref, case)
