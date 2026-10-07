"""Game flow for Dots and Boxes: turns, scoring, history."""

from board import Board
from rules import valid_move, parse_move, completed_boxes, is_game_over


class DotsAndBoxes:
    def __init__(self, rows=2, cols=2, player_names=None):
        self.board = Board(rows=rows, cols=cols)
        self.current = 0
        self.scores = [0, 0]
        self.player_names = list(player_names) if player_names else ["Player 1", "Player 2"]
        # History entries: (orientation, row, col, player, newly_completed_boxes)
        self.history = []
        self.moves_played = 0

    # -- core logic (testable, no I/O) ---------------------------------
    def apply_move(self, orientation, row, col):
        """Apply one move. Returns (ok, newly_completed, message).

        Never corrupts board/score on invalid input: validation
        happens before any mutation, and moves after game-over
        are rejected.
        """
        if is_game_over(self.board):
            return False, 0, "Game is already over. Start a new game."
        if not valid_move(self.board, orientation, row, col):
            return False, 0, "Invalid or already-used move."
        player = self.current
        before = set(self.board.completed)
        try:
            newly_list = self.board.add_line(orientation, row, col, owner=player)
        except ValueError as exc:
            return False, 0, str(exc)
        newly = len(newly_list)
        # Cross-check with the rules helper (keeps modules consistent).
        assert newly == completed_boxes(self.board, before), "box-count mismatch"
        self.history.append((orientation, row, col, player, list(newly_list)))
        self.moves_played += 1
        if newly:
            self.scores[player] += newly
            # Extra turn: current player keeps the move.
            return True, newly, (
                f"{self.player_names[player]} completed {newly} box(es) and plays again."
            )
        self.current = 1 - self.current
        return True, 0, f"{self.player_names[player]} drew {orientation} {row} {col}."

    def undo_last(self):
        """Undo the most recent move. Returns (ok, message)."""
        if not self.history:
            return False, "Nothing to undo."
        orientation, row, col, player, claimed = self.history.pop()
        unclaimed = self.board.remove_line(orientation, row, col)
        # Revert score for boxes that were claimed by that move.
        for _ in unclaimed:
            if self.scores[player] > 0:
                self.scores[player] -= 1
        self.moves_played -= 1
        # Turn goes back to the player who made the undone move.
        self.current = player
        return True, (
            f"Undid {orientation} {row} {col} by {self.player_names[player]}."
        )

    def winner_text(self):
        if self.scores[0] == self.scores[1]:
            return "The game is a draw."
        winner = 0 if self.scores[0] > self.scores[1] else 1
        return f"{self.player_names[winner]} wins!"

    # -- interactive loop ----------------------------------------------
    def run(self):
        print("Dots and Boxes")
        print("Enter moves as H row col or V row col. Commands: U=undo, Q=quit.")
        print("Rows and columns start at 0.")
        print("Example: H 0 1")

        while not self.board.is_complete():
            self.board.display(self.scores, self.current, self.player_names)
            try:
                raw = input(f"{self.player_names[self.current]}, move: ")
            except EOFError:
                print("\nInput closed. Game aborted — board and score unchanged.")
                return
            except KeyboardInterrupt:
                print("\nInterrupted. Game aborted — board and score unchanged.")
                return
            if raw is None:
                print("Invalid format. Use: H row col or V row col.")
                continue
            cmd = raw.strip().upper()
            if cmd in ("Q", "QUIT", "EXIT"):
                print("Quit. Final state:")
                self.board.display(self.scores, self.current, self.player_names)
                return
            if cmd in ("U", "UNDO"):
                ok, msg = self.undo_last()
                print(msg)
                continue

            orientation, row, col, error = parse_move(raw, self.board)
            if error:
                print(error)
                continue
            ok, newly, msg = self.apply_move(orientation, row, col)
            print(msg)

        self.board.display(self.scores, self.current, self.player_names)
        print(f"Game over after {self.moves_played} moves!")
        print(self.winner_text())
