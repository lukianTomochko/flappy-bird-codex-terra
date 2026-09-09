"""Headless frame-time benchmark for the pipe and HUD rendering paths."""

import gc
import os
import statistics
import sys
import time
from pathlib import Path
from types import MethodType, SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from src.entities.difficulty_indicator import DifficultyIndicator
from src.entities.pipe import Pipes
from src.entities.score import Score

FRAMES = 6000
SAMPLES = 1000


def make_config():
    pipe = pygame.Surface((52, 320), pygame.SRCALPHA)
    digit = pygame.Surface((12, 18), pygame.SRCALPHA)
    return SimpleNamespace(
        window=SimpleNamespace(width=288, height=512, viewport_height=404),
        images=SimpleNamespace(pipe=[pipe, pipe], numbers=[digit] * 10),
        screen=pygame.Surface((288, 512)),
        sounds=SimpleNamespace(point=SimpleNamespace(play=lambda: None)),
        debug=False,
    )


def baseline_remove_old_pipes(self):
    for pipe in self.upper:
        if pipe.x < -pipe.w:
            self.upper.remove(pipe)
    for pipe in self.lower:
        if pipe.x < -pipe.w:
            self.lower.remove(pipe)


def summary(samples):
    samples.sort()
    return {
        "median_ms": statistics.median(samples) / 1_000_000,
        "p95_ms": samples[int(len(samples) * 0.95)] / 1_000_000,
        "max_ms": max(samples) / 1_000_000,
    }


def time_action(action, repetitions):
    samples = []
    gc.disable()
    try:
        for _ in range(repetitions):
            started = time.perf_counter_ns()
            action()
            samples.append(time.perf_counter_ns() - started)
    finally:
        gc.enable()
    return summary(samples)


def run_loop(use_baseline_cleanup):
    config = make_config()
    pipes = Pipes(config)
    if use_baseline_cleanup:
        pipes.remove_old_pipes = MethodType(baseline_remove_old_pipes, pipes)
    score = Score(config)
    indicator = DifficultyIndicator(config, pipes)

    def frame():
        config.screen.fill((0, 0, 0))
        pipes.tick()
        score.tick()
        indicator.tick()

    return time_action(frame, FRAMES)


def level_up_spawn_frame():
    config = make_config()
    pipes = Pipes(config)

    def frame():
        pipes.passed_pipes = 4
        pipes.register_passed_pipe()
        pipes.spawn_new_pipes()

    return time_action(frame, SAMPLES)


def game_over_board_frame():
    config = make_config()
    score = Score(config)
    score.high_scores = [55, 45, 33, 9, 5]
    return time_action(score.draw_high_scores, SAMPLES)


def hud_flash_frame():
    config = make_config()
    pipes = Pipes(config)
    pipes.difficulty_level = 4
    pipes.passed_pipes = 4
    indicator = DifficultyIndicator(config, pipes)
    return time_action(indicator.draw, SAMPLES)


def print_result(name, result):
    print(
        f"{name}: median={result['median_ms']:.4f} ms, "
        f"p95={result['p95_ms']:.4f} ms, max={result['max_ms']:.4f} ms"
    )


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    print_result(
        "Game loop (before cleanup refactor, 6000 frames)", run_loop(True)
    )
    print_result(
        "Game loop (after cleanup refactor, 6000 frames)", run_loop(False)
    )
    print_result(
        "Level-up + spawn frame (1000 samples)", level_up_spawn_frame()
    )
    print_result(
        "Game-over board frame (1000 samples)", game_over_board_frame()
    )
    print_result("HUD flash frame (1000 samples)", hud_flash_frame())
    pygame.quit()
