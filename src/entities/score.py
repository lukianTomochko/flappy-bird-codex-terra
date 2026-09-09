from typing import List

import pygame

from ..utils import (
    GameConfig,
    load_high_scores,
    normalize_high_scores,
    save_high_scores,
)
from .entity import Entity


class Score(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        self.y = self.config.window.height * 0.1
        self.score = 0
        self.high_scores: List[int] = load_high_scores()
        self.leaderboard_font = pygame.font.SysFont("Arial", 18, bold=True)

    def reset(self) -> None:
        self.score = 0

    def add(self) -> None:
        self.score += 1
        self.config.sounds.point.play()

    def record_result(self) -> bool:
        """Add this run to the leaderboard if it belongs in the top five."""
        if self.score <= 0:
            return False

        updated_scores = normalize_high_scores(self.high_scores + [self.score])
        is_high_score = self.score in updated_scores and (
            len(self.high_scores) < 5 or self.score >= self.high_scores[-1]
        )
        self.high_scores = updated_scores
        save_high_scores(self.high_scores)
        return is_high_score

    def draw_high_scores(self) -> None:
        """Show the current top five below the game-over message."""
        title = self.leaderboard_font.render("TOP 5", True, (255, 215, 70))
        x = (self.config.window.width - title.get_width()) // 2
        self.config.screen.blit(title, (x, self.config.window.height * 0.48))

        for index, value in enumerate(self.high_scores, start=1):
            line = self.leaderboard_font.render(
                f"{index}. {value}", True, (255, 255, 255)
            )
            line_x = (self.config.window.width - line.get_width()) // 2
            self.config.screen.blit(
                line, (line_x, self.config.window.height * 0.48 + index * 22)
            )

    @property
    def rect(self) -> pygame.Rect:
        score_digits = [int(x) for x in list(str(self.score))]
        images = [self.config.images.numbers[digit] for digit in score_digits]
        w = sum(image.get_width() for image in images)
        x = (self.config.window.width - w) / 2
        h = max(image.get_height() for image in images)
        return pygame.Rect(x, self.y, w, h)

    def draw(self) -> None:
        """displays score in center of screen"""
        score_digits = [int(x) for x in list(str(self.score))]
        images = [self.config.images.numbers[digit] for digit in score_digits]
        digits_width = sum(image.get_width() for image in images)
        x_offset = (self.config.window.width - digits_width) / 2

        for image in images:
            self.config.screen.blit(image, (x_offset, self.y))
            x_offset += image.get_width()
