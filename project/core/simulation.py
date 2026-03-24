import math
import random
from typing import List, Tuple

import numpy as np
import pygame

from config import CFG
from environment.environnement import Environnement, SOIL_EMPTY, SOIL_VIRUS
from agents.agent import Agent
from agents.virus import Virus
from agents.globule_blanc import GlobuleBlanc


class Simulation:
    """
    Orchestre la boucle principale :
      - initialisation et reset
      - spawn continu de virus
      - mise à jour des agents (decide → move → paint_soil)
      - gestion des collisions et anti-overlap
      - rendu (sol → agents → UI)
      - gestion des événements clavier
    """

    def __init__(self, cfg=CFG):
        self.cfg = cfg
        pygame.init()

        info = pygame.display.Info()
        self.cfg.SCREEN_WIDTH  = info.current_w
        self.cfg.SCREEN_HEIGHT = info.current_h

        self.screen = pygame.display.set_mode(
            (self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT),
            pygame.NOFRAME
        )
        pygame.display.set_caption("Globules Blancs vs Virus")

        self.clock    = pygame.time.Clock()
        self.font     = pygame.font.SysFont("monospace", 14)
        self.font_big = pygame.font.SysFont("monospace", 22, bold=True)
        self.ui_surf  = pygame.Surface((330, 68), pygame.SRCALPHA)

        self.env    = Environnement(self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT,
                                    self.cfg.GRID_CELL_SIZE)
        self.agents: List[Agent] = []
        self.paused       = False
        self.elapsed      = 0.0
        self._spawn_timer = 0.0

        self._spawn_initial()

    # ── Initialisation ─────────────────────────────────────────────────────

    def _edge_pos(self) -> Tuple[float, float]:
        edge = random.randint(0, 3)
        m = 5.0
        w, h = self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT
        if edge == 0:   return random.uniform(m, w - m), m
        elif edge == 1: return random.uniform(m, w - m), h - m
        elif edge == 2: return m, random.uniform(m, h - m)
        else:           return w - m, random.uniform(m, h - m)

    def _spawn_initial(self):
        self.agents.clear()
        for _ in range(20):
            x, y = self._edge_pos()
            self.agents.append(Virus(x, y))
        cx = self.cfg.SCREEN_WIDTH  / 2
        cy = self.cfg.SCREEN_HEIGHT / 2
        for _ in range(self.cfg.N_WBC):
            angle = random.uniform(0, 2 * math.pi)
            r     = random.uniform(0, 100)
            self.agents.append(GlobuleBlanc(
                cx + r * math.cos(angle),
                cy + r * math.sin(angle)
            ))

    def _reset(self):
        self.env.reset()
        self.elapsed      = 0.0
        self._spawn_timer = 0.0
        self._spawn_initial()

    # ── Spawn continu ──────────────────────────────────────────────────────

    def _spawn_virus_wave(self):
        current = sum(1 for a in self.agents if isinstance(a, Virus) and a.alive)
        if current >= self.cfg.VIRUS_MAX:
            return
        count = min(self.cfg.VIRUS_SPAWN_BATCH, self.cfg.VIRUS_MAX - current)
        for _ in range(count):
            x, y = self._edge_pos()
            self.agents.append(Virus(x, y))

    # ── Collisions ─────────────────────────────────────────────────────────

    def _handle_collisions(self):
        wbcs    = [a for a in self.agents if isinstance(a, GlobuleBlanc) and a.alive]
        viruses = [a for a in self.agents if isinstance(a, Virus) and a.alive]

        for wbc in wbcs:
            for virus in viruses:
                if not virus.alive:
                    continue
                if np.linalg.norm(wbc.pos - virus.pos) < self.cfg.COLLISION_KILL_DIST:
                    virus.alive = False
                    self.env.paint_radius(virus.pos[0], virus.pos[1],
                                          SOIL_EMPTY, r_cells=3)

        # Anti-overlap physique
        alive = [a for a in self.agents if a.alive]
        for i, a in enumerate(alive):
            for b in alive[i + 1:]:
                diff = a.pos - b.pos
                dist = np.linalg.norm(diff)
                min_dist = a.radius + b.radius
                if 0 < dist < min_dist:
                    push   = diff / dist * (min_dist - dist) * 0.5
                    a.pos += push
                    b.pos -= push

    # ── Mise à jour ────────────────────────────────────────────────────────

    def update(self, dt: float):
        alive = [a for a in self.agents if a.alive]
        for agent in alive:
            agent.decide(self.env, self.agents, dt)
            agent.move(dt, self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT)
            agent.paint_soil(self.env)

        self._handle_collisions()
        self.env.update(dt)
        self.elapsed += dt

        self._spawn_timer += dt
        if self._spawn_timer >= self.cfg.VIRUS_SPAWN_INTERVAL:
            self._spawn_timer = 0.0
            self._spawn_virus_wave()

        self.agents = [a for a in self.agents if a.alive]

    # ── Rendu ──────────────────────────────────────────────────────────────

    def render(self):
        self.env.render(self.screen)
        for agent in self.agents:
            agent.render(self.screen)
        self._render_ui()
        pygame.display.flip()

    def _render_ui(self):
        n_virus = sum(1 for a in self.agents if isinstance(a, Virus))
        n_wbc   = sum(1 for a in self.agents if isinstance(a, GlobuleBlanc))
        mins    = int(self.elapsed // 60)
        secs    = int(self.elapsed % 60)
        W, H    = self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT

        self.ui_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(self.ui_surf, (0, 0, 0, 150), (0, 0, 330, 68), border_radius=8)
        self.screen.blit(self.ui_surf, (W - 340, 8))

        for i, line in enumerate([
            f"Temps : {mins:02d}:{secs:02d}",
            f"Virus : {n_virus}   |   Globules : {n_wbc}",
            "[ESPACE] Pause   [R] Reset   [ESC] Quitter",
        ]):
            self.screen.blit(self.font.render(line, True, self.cfg.COLOR_UI_TEXT),
                             (W - 334, 14 + i * 18))

        lx, ly = 14, H - 52
        pygame.draw.circle(self.screen, self.cfg.COLOR_VIRUS, (lx + 8, ly + 8), 7)
        self.screen.blit(self.font.render("Virus", True, (30, 10, 10)), (lx + 20, ly + 1))
        pygame.draw.circle(self.screen, self.cfg.COLOR_WBC, (lx + 8, ly + 30), 7)
        self.screen.blit(self.font.render("Globule blanc", True, (240, 240, 240)), (lx + 20, ly + 23))

        if self.paused:
            s = self.font_big.render("  PAUSE  ", True, (255, 230, 60))
            self.screen.blit(s, (W // 2 - s.get_width() // 2, H // 2 - 15))

    # ── Boucle principale ──────────────────────────────────────────────────

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(self.cfg.FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self._reset()

            if not self.paused:
                self.update(dt)

            self.render()

        pygame.quit()