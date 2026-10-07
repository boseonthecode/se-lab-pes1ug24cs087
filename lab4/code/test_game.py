"""Automated tests for Dots and Boxes game rules.

Covers the required cases:
- valid horizontal move
- valid vertical move
- invalid / repeated move
- completion of a box (incl. extra turn + ownership)
- end-of-game condition
plus validation, undo, double-box and game-over guards.
"""

import unittest

from board import Board
from game import DotsAndBoxes
from rules import valid_move, parse_move, completed_boxes, is_game_over


class TestMoves(unittest.TestCase):
    def test_valid_horizontal_move(self):
        game = DotsAndBoxes()
        ok, newly, _ = game.apply_move("H", 0, 0)
        self.assertTrue(ok)
        self.assertEqual(newly, 0)
        self.assertTrue(game.board.horizontal[0][0])

    def test_valid_vertical_move(self):
        game = DotsAndBoxes()
        ok, newly, _ = game.apply_move("V", 0, 0)
        self.assertTrue(ok)
        self.assertEqual(newly, 0)
        self.assertTrue(game.board.vertical[0][0])

    def test_invalid_repeated_move(self):
        game = DotsAndBoxes()
        ok, _, _ = game.apply_move("H", 0, 0)
        self.assertTrue(ok)
        before_scores = list(game.scores)
        before_lines = game.board.used_lines()
        ok, newly, _ = game.apply_move("H", 0, 0)  # repeat
        self.assertFalse(ok)
        self.assertEqual(newly, 0)
        # Board and score must be unchanged.
        self.assertEqual(game.scores, before_scores)
        self.assertEqual(game.board.used_lines(), before_lines)

    def test_out_of_range_rejected(self):
        game = DotsAndBoxes()
        for move in [("H", 9, 0), ("V", 0, 9), ("H", -1, 0), ("X", 0, 0)]:
            ok, _, _ = game.apply_move(*move)
            self.assertFalse(ok, f"{move} should be rejected")

    def test_completion_of_box_scores_and_keeps_turn(self):
        game = DotsAndBoxes()
        # Box (0,0) needs H0,0 H1,0 V0,0 V0,1. Interleave so P1 closes it.
        game.apply_move("H", 0, 0)  # P1 -> P2
        self.assertEqual(game.current, 1)
        game.apply_move("H", 0, 1)  # P2 -> P1
        game.apply_move("V", 0, 0)  # P1 -> P2
        game.apply_move("V", 0, 1)  # P2 -> P1, box still open
        self.assertEqual(game.scores, [0, 0])
        ok, newly, _ = game.apply_move("H", 1, 0)  # P1 closes box
        self.assertTrue(ok)
        self.assertEqual(newly, 1)
        self.assertEqual(game.scores[0], 1)
        self.assertEqual(game.current, 0)  # extra turn: P1 plays again
        self.assertIn((0, 0), game.board.completed)
        self.assertEqual(game.board.box_owner(0, 0), 0)

    def test_double_box_completion(self):
        game = DotsAndBoxes()
        # Leave only the shared edge H1,0; boxes (0,0)+(1,0) close together.
        for move in [("H", 0, 0), ("V", 0, 0), ("V", 0, 1),
                     ("H", 2, 0), ("V", 1, 0), ("V", 1, 1)]:
            game.board.add_line(*move)
        before = set(game.board.completed)
        newly = game.board.add_line("H", 1, 0, owner=1)
        self.assertEqual(len(newly), 2)
        self.assertEqual(completed_boxes(game.board, before), 2)

    def test_end_of_game_condition(self):
        game = DotsAndBoxes(rows=1, cols=1)  # smallest board: 4 lines, 1 box
        self.assertFalse(is_game_over(game.board))
        game.apply_move("H", 0, 0)
        game.apply_move("H", 1, 0)
        game.apply_move("V", 0, 0)
        self.assertFalse(is_game_over(game.board))
        ok, newly, _ = game.apply_move("V", 0, 1)
        self.assertTrue(ok)
        self.assertEqual(newly, 1)
        self.assertTrue(is_game_over(game.board))
        self.assertTrue(game.board.is_complete())
        # Moves after game-over must be rejected without mutation.
        scores = list(game.scores)
        ok, _, _ = game.apply_move("H", 0, 0)
        self.assertFalse(ok)
        self.assertEqual(game.scores, scores)

    def test_parse_move_malformed(self):
        board = Board()
        for raw in ["", "   ", "H", "H 0", "H 0 0 0", "X 0 0", "H a b", None, 123]:
            _, _, _, err = parse_move(raw, board)
            self.assertIsNotNone(err, f"{raw!r} should fail")
        o, r, c, err = parse_move("h 0 1", board)
        self.assertIsNone(err)
        self.assertEqual((o, r, c), ("H", 0, 1))

    def test_undo_restores_state(self):
        game = DotsAndBoxes()
        game.apply_move("H", 0, 0)
        self.assertTrue(game.board.horizontal[0][0])
        ok, _ = game.undo_last()
        self.assertTrue(ok)
        self.assertFalse(game.board.horizontal[0][0])
        self.assertEqual(game.moves_played, 0)

    def test_undo_after_box_reverts_score(self):
        game = DotsAndBoxes()
        game.apply_move("H", 0, 0)
        game.apply_move("H", 0, 1)
        game.apply_move("V", 0, 0)
        game.apply_move("V", 0, 1)
        game.apply_move("H", 1, 0)  # P1 claims box
        self.assertEqual(game.scores[0], 1)
        ok, _ = game.undo_last()
        self.assertTrue(ok)
        self.assertEqual(game.scores[0], 0)
        self.assertNotIn((0, 0), game.board.completed)

    def test_board_add_line_validates(self):
        board = Board()
        with self.assertRaises(ValueError):
            board.add_line("H", -1, 0)
        with self.assertRaises(ValueError):
            board.add_line("H", 5, 5)
        with self.assertRaises(ValueError):
            board.add_line("Z", 0, 0)
        board.add_line("H", 0, 0)
        with self.assertRaises(ValueError):
            board.add_line("H", 0, 0)  # duplicate

    def test_display_runs_without_error(self):
        game = DotsAndBoxes()
        game.apply_move("H", 0, 0)
        game.apply_move("V", 0, 0)
        # Should not raise; visual check is manual.
        game.board.display(game.scores, game.current, game.player_names)


if __name__ == "__main__":
    unittest.main()
