import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pygame

from src.entities.difficulty_indicator import DifficultyIndicator
from src.entities.pipe import Pipes
from src.entities.score import Score
from src.utils.high_scores import load_high_scores, save_high_scores


class GameFeatureTests(unittest.TestCase):
    """Unit tests for leaderboard persistence and progressive difficulty."""

    def setUp(self):
        pygame.init()
        pygame.font.init()
        self.temp_directory = tempfile.TemporaryDirectory()
        self.score_file = Path(self.temp_directory.name) / "highscore.json"
        pipe_image = pygame.Surface((52, 320), pygame.SRCALPHA)
        self.config = SimpleNamespace(
            window=SimpleNamespace(width=288, viewport_height=404),
            images=SimpleNamespace(pipe=[pipe_image, pipe_image]),
            screen=pygame.Surface((288, 512)),
        )

    def tearDown(self):
        self.temp_directory.cleanup()
        pygame.quit()

    def test_load_returns_empty_list_when_file_is_missing(self):
        self.assertEqual(load_high_scores(self.score_file), [])

    def test_load_returns_empty_list_for_corrupt_json(self):
        self.score_file.write_text("{not valid json", encoding="utf-8")

        self.assertEqual(load_high_scores(self.score_file), [])

    def test_load_filters_invalid_values_and_keeps_top_five(self):
        self.score_file.write_text(
            json.dumps({"scores": [3, -1, "9", 12, 7, 4, 11, 8]}),
            encoding="utf-8",
        )

        self.assertEqual(load_high_scores(self.score_file), [12, 11, 8, 7, 4])

    def test_save_writes_sorted_top_five_json(self):
        self.assertTrue(save_high_scores([2, 11, 5, 9, 1, 7], self.score_file))

        self.assertEqual(
            json.loads(self.score_file.read_text(encoding="utf-8")),
            {"scores": [11, 9, 7, 5, 2]},
        )

    @patch(
        "src.utils.high_scores.NamedTemporaryFile", side_effect=PermissionError
    )
    def test_save_returns_false_when_storage_cannot_be_written(
        self, _temporary_file
    ):
        self.assertFalse(save_high_scores([10], self.score_file))

    @patch("src.entities.score.save_high_scores", return_value=True)
    def test_record_result_updates_and_persists_top_five(self, save_scores):
        score = Score.__new__(Score)
        score.score = 18
        score.high_scores = [30, 20, 15, 10, 5]

        self.assertTrue(score.record_result())
        self.assertEqual(score.high_scores, [30, 20, 18, 15, 10])
        save_scores.assert_called_once_with([30, 20, 18, 15, 10])

    def test_difficulty_increases_pipe_speed_after_five_passes(self):
        pipes = Pipes(self.config)

        for _ in range(5):
            advanced = pipes.register_passed_pipe()

        self.assertTrue(advanced)
        self.assertEqual(pipes.difficulty_level, 1)
        self.assertEqual(pipes.speed, 5.5)
        self.assertTrue(
            all(pipe.vel_x == -5.5 for pipe in pipes.upper + pipes.lower)
        )

    def test_new_pipes_use_the_current_difficulty_speed(self):
        pipes = Pipes(self.config)
        for _ in range(10):
            pipes.register_passed_pipe()

        upper, lower = pipes.make_random_pipes()

        self.assertEqual(pipes.speed, 6.0)
        self.assertEqual((upper.vel_x, lower.vel_x), (-6.0, -6.0))

    @patch("src.entities.difficulty_indicator.pygame.draw.rect")
    def test_difficulty_indicator_uses_level_colour_and_progress(
        self, draw_rect
    ):
        pipes = SimpleNamespace(
            difficulty_level=3,
            passed_pipes=17,
            PIPES_PER_LEVEL=5,
            speed=6.5,
        )
        indicator = DifficultyIndicator(self.config, pipes)

        indicator.draw()

        self.assertEqual(draw_rect.call_args_list[1].args[1], (255, 135, 55))
        self.assertEqual(draw_rect.call_args_list[1].args[2][2], 35)


if __name__ == "__main__":
    unittest.main()
