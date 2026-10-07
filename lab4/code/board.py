"""Board state for Dots and Boxes.

Owns the grid lines, completed boxes and per-box ownership.
Rendering and mutation live here so game flow (game.py) and
validation (rules.py) stay thin.
"""


class Board:
    def __init__(self, rows=2, cols=2):
        if not isinstance(rows, int) or not isinstance(cols, int):
            raise ValueError("rows and cols must be integers")
        if rows < 1 or cols < 1 or rows > 9 or cols > 9:
            raise ValueError("rows and cols must be between 1 and 9")
        self.rows = rows
        self.cols = cols
        self.horizontal = [[False] * cols for _ in range(rows + 1)]
        self.vertical = [[False] * (cols + 1) for _ in range(rows)]
        self.completed = set()
        # (row, col) -> player index (0 or 1) that claimed the box.
        self.owner = {}

    # -- mutation ------------------------------------------------------
    def add_line(self, orientation, row, col, owner=None):
        """Draw a line, claim any newly completed boxes.

        Validates bounds/types and rejects duplicates instead of
        silently corrupting state (old code indexed with negative
        numbers or raised a bare IndexError).

        Returns the list of newly completed (r, c) boxes.
        Raises ValueError on any invalid move.
        """
        if orientation not in ("H", "V"):
            raise ValueError(f"orientation must be 'H' or 'V', got {orientation!r}")
        if isinstance(row, bool) or isinstance(col, bool):
            raise ValueError("row and column must be integers")
        if not isinstance(row, int) or not isinstance(col, int):
            raise ValueError("row and column must be integers")

        if orientation == "H":
            if not (0 <= row <= self.rows and 0 <= col < self.cols):
                raise ValueError(
                    f"H move out of range: row 0..{self.rows}, col 0..{self.cols - 1}"
                )
            if self.horizontal[row][col]:
                raise ValueError("line already drawn")
            self.horizontal[row][col] = True
        else:
            if not (0 <= row < self.rows and 0 <= col <= self.cols):
                raise ValueError(
                    f"V move out of range: row 0..{self.rows - 1}, col 0..{self.cols}"
                )
            if self.vertical[row][col]:
                raise ValueError("line already drawn")
            self.vertical[row][col] = True

        before = set(self.completed)
        self._update_completed()
        newly = sorted(self.completed - before)
        if owner is not None:
            for box in newly:
                self.owner[box] = owner
        return newly

    def remove_line(self, orientation, row, col):
        """Remove a line (used by undo). Returns unclaimed boxes."""
        if orientation == "H":
            self.horizontal[row][col] = False
        else:
            self.vertical[row][col] = False
        still = self._scan_completed()
        unclaimed = sorted(self.completed - still)
        self.completed = still
        for box in unclaimed:
            self.owner.pop(box, None)
        return unclaimed

    def _scan_completed(self):
        found = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if (
                    self.horizontal[r][c]
                    and self.horizontal[r + 1][c]
                    and self.vertical[r][c]
                    and self.vertical[r][c + 1]
                ):
                    found.add((r, c))
        return found

    def _update_completed(self):
        self.completed = self._scan_completed()

    # -- queries -------------------------------------------------------
    def total_lines(self):
        return self.rows * (self.cols + 1) + self.cols * (self.rows + 1)

    def used_lines(self):
        return sum(map(sum, self.horizontal)) + sum(map(sum, self.vertical))

    def remaining_lines(self):
        return self.total_lines() - self.used_lines()

    def is_complete(self):
        return self.used_lines() == self.total_lines()

    def box_owner(self, row, col):
        return self.owner.get((row, col))

    # -- rendering -----------------------------------------------------
    def display(self, scores, current, names=None):
        """Render an aligned grid with edge dots and owners.

        Old code used ".".join(...) which dropped the outer dots and
        produced 7-char horizontal rows against 9-char vertical rows.
        Every row here is (cols * 3 + cols + 1) chars wide and each
        claimed box shows its owner's mark (1/2) instead of a
        generic X so the score can be audited against the board.
        """
        if names is None:
            names = ("Player 1", "Player 2")
        marks = ("1", "2")
        print()
        print(
            f"Scores: {names[0]}={scores[0]}  {names[1]}={scores[1]} "
            f"| Turn: {names[current]} | Lines left: {self.remaining_lines()}"
        )

        for r in range(self.rows + 1):
            # Horizontal dot row: .---.---.  (outer dots included)
            segs = ("---" if self.horizontal[r][c] else "   " for c in range(self.cols))
            print("." + ".".join(segs) + ".")
            if r < self.rows:
                parts = []
                for c in range(self.cols + 1):
                    wall = "|" if self.vertical[r][c] else " "
                    parts.append(wall)
                    if c < self.cols:
                        if (r, c) in self.completed:
                            o = self.owner.get((r, c))
                            mark = marks[o] if o in (0, 1) else "X"
                            parts.append(f" {mark} ")
                        else:
                            parts.append("   ")
                print("".join(parts))
        print()
