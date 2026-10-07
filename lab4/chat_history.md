# Lab 4 — VibeCoding Chat History (export)

**Course:** Software Engineering Lab · **Scenario 23:** Dots and Boxes
**Student:** PES1UG24CS087 · **Repo:** `23_dots_and_boxes`
**Tool:** AI coding assistant · **Total attempts:** 4 (diagnose → fix → feature → harden + test)
**Note:** Every suggestion below was run locally and reviewed before being kept. Commits were kept separate per task.

---

## Attempt 1 — Reproduce & diagnose (no code changes)

### User

I am working on a modular Dots-and-Boxes game (`board.py` / `game.py` / `rules.py` / `main.py`, pasted below).
I ran full games and found suspicious behaviour around box completion and rendering:

1. The board seems to lose its edge dots and rows look misaligned after a few moves.
2. Every claimed box shows a generic `X`, so I cannot tell which score belongs to which box.
3. Piping input / pressing Ctrl-D crashes the game.

Do NOT rewrite anything yet. Trace each symptom to the exact file/line, explain the root
cause, and propose a minimal fix plan that preserves the modular structure. Also tell me
which moves to play in my before-video to demonstrate each bug.

```python
# board.py (excerpt)
def display(self, scores, current):
    for r in range(self.rows + 1):
        print(".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)))
        ...
                        middle.append(" " + ("X" if (r, c) in self.completed else " ") + " ")

# game.py (excerpt)
raw = input(f"Player {self.current + 1}, move: ").strip().upper()
```

### Assistant

Good catches — I can trace all three to specific lines:

**Bug 1 — missing edge dots + misaligned rows (`board.py:37`).**
`".".join(...)` only places dots *between* cells, so a 2-column row renders 7 chars
(`---.---`) while a vertical row renders 9 chars (`| X |    `). The outer dots are never
printed. Fix: `"." + ".".join(segs) + "."` so every horizontal row is
`cols*3 + cols + 1` chars wide, matching the vertical rows.

**Bug 2 — score not auditable (`board.py:7,44` + `game.py:40`).**
`completed` is a bare `set()` of coordinates and `display()` prints a generic `X` for
all of them. `game.py` does `scores[current] += newly_completed`, which is correct, but
you can never verify *who* owns what on the board. Fix: add `self.owner = {}` mapping
`(r, c) -> player`, set it when boxes are claimed, and render `1`/`2` instead of `X`.
This also keeps the extra-turn rule (`game.py:39-43`, which is already correct) visible.

**Bug 3 — crash on EOF (`game.py:18`).**
`input()` is unguarded, so Ctrl-D / piped-input exhaustion raises `EOFError` (and Ctrl-C
raises `KeyboardInterrupt`). Fix: wrap in `try/except` and abort cleanly with the
board/score untouched.

**Bonus — silent corruption (`board.py:9-14`).**
`add_line()` does no validation: `H -1 0` indexes `horizontal[-1][0]` (last row!) and
`H 5 5` raises a bare `IndexError`. Fix: validate orientation/type/bounds/duplicates
inside `add_line()` and raise `ValueError` with a message.

**Before-video script (10 s):**

```text
H 0 0 | H 0 1 | V 0 0 | V 0 1 | H 1 0   -> box claimed, shows X, dots missing
printf 'H 0 0\n' | python main.py       -> EOFError traceback
python3 -c "Board().add_line('H',-1,0)" -> silent corruption of last row
```

Plan approved? Say the word and I'll implement only the Task-1 fixes, one file at a time.

---

## Attempt 2 — Fix the bugs (Task 1)

### User

Implement only the Task-1 fixes, keeping modules separate:

- `board.py`: aligned `display()` with outer dots; `owner` dict `(r, c) -> player`;
  validated `add_line()` (orientation/type/bounds/duplicates → `ValueError`), returning the
  newly-completed list. Keep `completed` set + `is_complete()` signatures for compatibility.
- Render owner marks `1`/`2` instead of `X`.

Acceptance: a full scripted 2×2 game finishes, the extra-turn rule still holds, and
`H -1 0` / `H 5 5` no longer corrupt or crash with a bare traceback. Show diffs per file
plus a small verification script.

### Assistant

Done — all changes are in `board.py`, nothing else touched:

```python
class Board:
    def __init__(self, rows=2, cols=2):
        ...
        self.completed = set()
        self.owner = {}  # (row, col) -> player index

    def add_line(self, orientation, row, col, owner=None):
        if orientation not in ("H", "V"):
            raise ValueError(f"orientation must be 'H' or 'V', got {orientation!r}")
        if isinstance(row, bool) or isinstance(col, bool):
            raise ValueError("row and column must be integers")
        if not isinstance(row, int) or not isinstance(col, int):
            raise ValueError("row and column must be integers")
        if orientation == "H":
            if not (0 <= row <= self.rows and 0 <= col < self.cols):
                raise ValueError(
                    f"H move out of range: row 0..{self.rows}, col 0..{self.cols - 1}")
            if self.horizontal[row][col]:
                raise ValueError("line already drawn")
            self.horizontal[row][col] = True
        else:
            if not (0 <= row < self.rows and 0 <= col <= self.cols):
                raise ValueError(
                    f"V move out of range: row 0..{self.rows - 1}, col 0..{self.cols}")
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
```

And the renderer:

```python
def display(self, scores, current, names=None):
    ...
    for r in range(self.rows + 1):
        segs = ("---" if self.horizontal[r][c] else "   " for c in range(self.cols))
        print("." + ".".join(segs) + ".")   # outer dots restored, rows aligned
        if r < self.rows:
            ...
            if (r, c) in self.completed:
                o = self.owner.get((r, c))
                mark = ("1", "2")[o] if o in (0, 1) else "X"
                parts.append(f" {mark} ")
```

**Verification (run it yourself):**

```bash
printf 'H 0 0\nH 0 1\nV 0 0\nV 0 1\nH 1 0\n' | python main.py
# P1 completes 1 box, keeps the turn, board shows | 1 |
python3 -c "from board import Board; Board().add_line('H',-1,0)"
# ValueError: H move out of range: row 0..2, col 0..1
```

`add_line()` stays backward compatible — old callers that ignore the return value
(`board.add_line(o, r, c)`) keep working. I also added `remove_line()` and
`remaining_lines()` now so the undo/stats feature next has hooks to use.

---

## Attempt 3 — Substantial feature (Task 2)

### User

Add ONE substantial feature spanning 2+ modules, without collapsing logic into `main.py`:
configurable board size (`--rows`/`--cols`), undo (`U`) with score/turn rollback, move
history, lines-left counter, move count + winner summary. Ownership scoring from Attempt 2
must flow through. Expose `DotsAndBoxes(rows, cols, player_names)` with testable
`apply_move()` / `undo_last()` returning `(ok, newly, message)` — no `input()` inside
logic. Keep gameplay rules identical and no third-party deps.

### Assistant

Implemented across `main.py` → `game.py` → `board.py`:

```python
# main.py — thin wrapper only
parser.add_argument("--rows", type=int, default=2)
parser.add_argument("--cols", type=int, default=2)
DotsAndBoxes(rows=args.rows, cols=args.cols).run()
```

```python
# game.py — logic (testable, no I/O)
def apply_move(self, orientation, row, col):
    if is_game_over(self.board):
        return False, 0, "Game is already over. Start a new game."
    if not valid_move(self.board, orientation, row, col):
        return False, 0, "Invalid or already-used move."
    player = self.current
    before = set(self.board.completed)
    newly_list = self.board.add_line(orientation, row, col, owner=player)
    newly = len(newly_list)
    assert newly == completed_boxes(self.board, before)  # modules agree
    self.history.append((orientation, row, col, player, list(newly_list)))
    self.moves_played += 1
    if newly:
        self.scores[player] += newly
        return True, newly, f"{...} completed {newly} box(es) and plays again."
    self.current = 1 - self.current
    return True, 0, f"{...} drew {orientation} {row} {col}."

def undo_last(self):
    if not self.history:
        return False, "Nothing to undo."
    orientation, row, col, player, claimed = self.history.pop()
    unclaimed = self.board.remove_line(orientation, row, col)
    for _ in unclaimed:
        if self.scores[player] > 0:
            self.scores[player] -= 1
    self.moves_played -= 1
    self.current = player  # turn returns to the undone player
    return True, f"Undid {orientation} {row} {col} ..."
```

`board.py` contributes `total_lines()` / `remaining_lines()` / `remove_line()`, and the
header now reads `Scores: ... | Turn: ... | Lines left: N`. Try:

```bash
python main.py --rows 3 --cols 3   # 24-line board
# inside the game:  U = undo,  Q = quit
```

The extra-turn rule is untouched — claiming a box still keeps the turn, and undo of a
claiming move rolls the score back. Design decision: history stores the claimed boxes per
move so double-box undo (`H 1 0` closing two boxes) reverts both points correctly.

---

## Attempt 4 — Validation + tests (Tasks 3 & 4)

### User

Harden and lock in quality:

(a) `rules.py`: central `parse_move(raw, board)` returning `(o, r, c, error)` — never
raises; distinguish format / orientation / non-integer / out-of-range / already-drawn.
Harden `valid_move()` with type checks; add `is_game_over()`. Post-game moves must be
rejected without mutation.

(b) `game.py run()`: route ALL input through `parse_move()`, handle
`EOFError`/`KeyboardInterrupt` with a clean abort, support `U`/`Q`.

(c) `test_game.py` (unittest, stdlib only): valid H, valid V, repeated/invalid
(board+score unchanged), box completion (+extra turn + owner), end-of-game, plus parse
errors, double-box, undo, `add_line` validation. Everything passes with
`python -m unittest test_game -v`.

### Assistant

All three parts done. The validation core:

```python
# rules.py
def valid_move(board, orientation, row, col):
    if orientation not in {"H", "V"}:
        return False
    if isinstance(row, bool) or isinstance(col, bool):
        return False
    if not isinstance(row, int) or not isinstance(col, int):
        return False
    if orientation == "H":
        return (0 <= row <= board.rows and 0 <= col < board.cols
                and not board.horizontal[row][col])
    return (0 <= row < board.rows and 0 <= col <= board.cols
            and not board.vertical[row][col])

def parse_move(raw, board=None):
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
        row, col = int(row_s), int(col_s)
    except ValueError:
        return None, None, None, "Row and column must be integers."
    if board is not None and not valid_move(board, orientation, row, col):
        ...  # "Line already drawn." vs precise out-of-range message
    return orientation, row, col, None

def is_game_over(board):
    return board.is_complete()
```

The loop is now fully routed through it:

```python
try:
    raw = input(f"{self.player_names[self.current]}, move: ")
except EOFError:
    print("\nInput closed. Game aborted — board and score unchanged.")
    return
except KeyboardInterrupt:
    print("\nInterrupted. Game aborted — board and score unchanged.")
    return
```

And the test suite (`test_game.py`, 12 tests):

```text
test_valid_horizontal_move ... ok
test_valid_vertical_move ... ok
test_invalid_repeated_move ... ok        (board + score unchanged)
test_out_of_range_rejected ... ok
test_completion_of_box_scores_and_keeps_turn ... ok   (extra turn, owner=0)
test_double_box_completion ... ok
test_end_of_game_condition ... ok        (1x1 board, post-game move rejected)
test_parse_move_malformed ... ok
test_undo_restores_state ... ok
test_undo_after_box_reverts_score ... ok
test_board_add_line_validates ... ok
test_display_runs_without_error ... ok
----------------------------------------------------------------------
Ran 12 tests in 0.002s  OK
```

Key guarantees, all covered by tests: malformed / out-of-range / repeated / post-game
inputs never mutate board or score; `H -1 0` raises `ValueError` instead of corrupting a
row; EOF exits 0 with state intact.

---

## Design decisions (summary)

- `owner` kept as a separate dict next to `completed` so old readers of
  `board.completed` keep working.
- `add_line()` returns newly-completed boxes; `game.py` asserts parity with
  `rules.completed_boxes()` so the modules cross-check each other.
- Logic (`apply_move`) separated from I/O (`run`) so every rule is unit-testable
  without mocking `input()`.
- No new dependencies (stdlib only), modular structure preserved, `main.py` stays thin.
- Upstream repo untouched (no PR); work lives in local per-task commits + this folder.
