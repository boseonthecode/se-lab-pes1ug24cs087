"""Rule validation for Dots and Boxes.

All input parsing and move legality checks live here so game.py
never touches raw strings and board.py never sees bad coordinates.
"""


def valid_move(board, orientation, row, col):
    """True if (orientation, row, col) is a legal, unused line."""
    if orientation not in {"H", "V"}:
        return False
    if isinstance(row, bool) or isinstance(col, bool):
        return False
    if not isinstance(row, int) or not isinstance(col, int):
        return False

    if orientation == "H":
        return (
            0 <= row <= board.rows
            and 0 <= col < board.cols
            and not board.horizontal[row][col]
        )

    return (
        0 <= row < board.rows
        and 0 <= col <= board.cols
        and not board.vertical[row][col]
    )


def parse_move(raw, board=None):
    """Parse a raw input line into (orientation, row, col, error).

    Returns error=None on success. Never raises on bad input, so
    callers can reject malformed commands without touching the
    board or the score. `board` is optional; when given, bounds
    and duplicate-line checks produce specific messages.
    """
    if raw is None or not isinstance(raw, str):
        return None, None, None, "Invalid format. Use: H row col or V row col."
    text = raw.strip().upper()
    if not text:
        return None, None, None, "Empty input. Use: H row col or V row col."
    parts = text.split()
    if len(parts) != 3:
        return None, None, None, "Invalid format. Use: H row col or V row col."
    orientation, row_s, col_s = parts
    if orientation not in ("H", "V"):
        return None, None, None, "Orientation must be H or V."
    try:
        row = int(row_s)
        col = int(col_s)
    except ValueError:
        return None, None, None, "Row and column must be integers."
    if board is not None and not valid_move(board, orientation, row, col):
        # Distinguish "already drawn" from "out of range" for UX.
        in_range = (
            (0 <= row <= board.rows and 0 <= col < board.cols)
            if orientation == "H"
            else (0 <= row < board.rows and 0 <= col <= board.cols)
        )
        if in_range:
            return None, None, None, "Line already drawn. Pick another."
        if orientation == "H":
            return (
                None,
                None,
                None,
                f"Coordinates out of range. H needs row 0..{board.rows}, "
                f"col 0..{board.cols - 1}.",
            )
        return (
            None,
            None,
            None,
            f"Coordinates out of range. V needs row 0..{board.rows - 1}, "
            f"col 0..{board.cols}.",
        )
    return orientation, row, col, None


def completed_boxes(board, before):
    """Number of boxes completed since the `before` snapshot."""
    return len(board.completed - before)


def is_game_over(board):
    """True when every line has been drawn."""
    return board.is_complete()
