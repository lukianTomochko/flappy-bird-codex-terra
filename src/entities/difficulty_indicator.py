import pygame

from ..utils import GameConfig
from .entity import Entity
from .pipe import Pipes


class DifficultyIndicator(Entity):
    """A colour-coded HUD showing the current pipe-speed level."""

    COLORS = (
        (80, 190, 255),
        (115, 210, 105),
        (255, 205, 70),
        (255, 135, 55),
        (245, 75, 85),
    )

    def __init__(self, config: GameConfig, pipes: Pipes) -> None:
        super().__init__(config)
        self.pipes = pipes
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

    def draw(self) -> None:
        level = self.pipes.difficulty_level
        color = self.COLORS[min(level, len(self.COLORS) - 1)]
        x, y = 10, 10
        width, height = 88, 9
        progress = (
            self.pipes.passed_pipes % self.pipes.PIPES_PER_LEVEL
        ) / self.pipes.PIPES_PER_LEVEL

        label = self.font.render(
            f"LEVEL {level + 1}  {self.pipes.speed:.1f}x", True, color
        )
        self.config.screen.blit(label, (x, y))
        pygame.draw.rect(
            self.config.screen, (45, 55, 70), (x, y + 18, width, height)
        )
        pygame.draw.rect(
            self.config.screen,
            color,
            (x, y + 18, int(width * progress), height),
        )
