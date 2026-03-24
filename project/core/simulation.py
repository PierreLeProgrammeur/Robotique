import math
import random
from typing import List, Tuple

import numpy as np
import pygame

from config import CFG
from environment.environnement import Environnement, SOIL_EMPTY, SOIL_WBC, SOIL_VIRUS
from agents.agent import Agent
from agents.virus import Virus
from agents.globule_blanc import GlobuleBlanc


class Simulation:
    """
    Orchestre la boucle principale.

    Règles de fin :
      - Les VIRUS gagnent s'ils peignent >= VIRUS_WIN_COVERAGE_PCT % du sol.
      - Les GLOBULES BLANCS gagnent si les virus n'ont pas gagné
        au bout de WBC_WIN_TIME secondes.

    Touches :
      ESPACE      Pause / Reprendre
      R           Reset
      + / =       Palier de vitesse suivant (1x → 1.5x → 2x)
      -           Palier de vitesse précédent
      ESC         Quitter
    """

    def __init__(self, cfg=CFG):
        self.cfg = cfg
        pygame.init()

        info = pygame.display.Info()
        self.cfg.SCREEN_WIDTH  = info.current_w
        self.cfg.SCREEN_HEIGHT = info.current_h

        self.screen = pygame.display.set_mode(
            (self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.display.set_caption("Globules Blancs vs Virus")

        self.clock    = pygame.time.Clock()
        self.font     = pygame.font.SysFont("monospace", 14)
        self.font_big = pygame.font.SysFont("monospace", 22, bold=True)

        self.env    = Environnement(self.cfg.SCREEN_WIDTH, self.cfg.SCREEN_HEIGHT,
                                    self.cfg.GRID_CELL_SIZE)
        self.agents: List[Agent] = []
        self.paused       = False
        self.elapsed      = 0.0
        self._spawn_timer = 0.0
        self._step_accum  = 0.0

        self._game_over        = False
        self._game_over_reason = ""
        self._winner           = ""   # "virus" | "wbc"

        self._spawn_initial()

    # ── Initialisation ────────────────────────────────────────────────────

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
        self.elapsed            = 0.0
        self._spawn_timer       = 0.0
        self._step_accum        = 0.0
        self._game_over         = False
        self._game_over_reason  = ""
        self._winner            = ""
        self.cfg.SPEED_STEP_IDX = 0
        self._spawn_initial()

    # ── Couverture du sol ─────────────────────────────────────────────────

    def _coverage(self) -> Tuple[float, float]:
        """Retourne (pct_wbc, pct_virus) en % du total des cases."""
        total = self.env.grid.size
        if total == 0:
            return 0.0, 0.0
        n_wbc   = int(np.sum(self.env.grid == SOIL_WBC))
        n_virus = int(np.sum(self.env.grid == SOIL_VIRUS))
        return n_wbc / total * 100.0, n_virus / total * 100.0

    # ── Spawn continu ─────────────────────────────────────────────────────

    def _spawn_virus_wave(self):
        current = sum(1 for a in self.agents if isinstance(a, Virus) and a.alive)
        if current >= self.cfg.VIRUS_MAX:
            return
        count = min(self.cfg.VIRUS_SPAWN_BATCH, self.cfg.VIRUS_MAX - current)
        for _ in range(count):
            x, y = self._edge_pos()
            self.agents.append(Virus(x, y))

    # ── Collisions ────────────────────────────────────────────────────────

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
                                          SOIL_WBC, r_cells=3)

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

    # ── Condition de fin ──────────────────────────────────────────────────

    def _check_end_conditions(self, pct_virus: float):
        if self._game_over:
            return

        # Les virus gagnent s'ils couvrent assez de surface
        if self.cfg.VIRUS_WIN_COVERAGE_PCT > 0:
            if pct_virus >= self.cfg.VIRUS_WIN_COVERAGE_PCT:
                self._game_over        = True
                self._winner           = "virus"
                self._game_over_reason = (
                    f"Les virus ont envahi {pct_virus:.1f}% du sol !"
                )
                return

        # Les globules blancs gagnent si le temps est écoulé sans invasion
        if self.cfg.WBC_WIN_TIME > 0:
            if self.elapsed >= self.cfg.WBC_WIN_TIME:
                self._game_over        = True
                self._winner           = "wbc"
                mins = int(self.elapsed // 60)
                secs = int(self.elapsed % 60)
                self._game_over_reason = (
                    f"Les globules ont tenu {mins:02d}:{secs:02d} !"
                )

    # ── Un pas de simulation ──────────────────────────────────────────────

    def _step(self, dt: float):
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

    # ── Mise à jour ───────────────────────────────────────────────────────

    def update(self, dt: float):
        speed = self.cfg.SPEED_STEPS[self.cfg.SPEED_STEP_IDX]
        self._step_accum += speed
        steps = int(self._step_accum)
        self._step_accum -= steps

        for _ in range(steps):
            self._step(dt)

        _, pct_virus = self._coverage()
        self._check_end_conditions(pct_virus)

    # ── Rendu ─────────────────────────────────────────────────────────────

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

        pct_wbc, pct_virus = self._coverage()
        speed     = self.cfg.SPEED_STEPS[self.cfg.SPEED_STEP_IDX]
        speed_str = f"{speed:.1f}".rstrip('0').rstrip('.')

        # Temps restant avant victoire des globules blancs
        time_left_str = ""
        if self.cfg.WBC_WIN_TIME > 0 and not self._game_over:
            remaining = max(0.0, self.cfg.WBC_WIN_TIME - self.elapsed)
            rm = int(remaining // 60)
            rs = int(remaining % 60)
            time_left_str = f"  (J-{rm:02d}:{rs:02d})"

        # ── Panneau infos ─────────────────────────────────────────────────
        panel_h = 104
        ui_surf = pygame.Surface((360, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(ui_surf, (0, 0, 0, 150), (0, 0, 360, panel_h), border_radius=8)
        self.screen.blit(ui_surf, (W - 370, 8))

        # Barre de progression virus (rouge) sous les textes
        bar_x = W - 364
        bar_y = 14 + 4 * 17 - 2
        bar_w = 348
        bar_h = 8
        pygame.draw.rect(self.screen, (60, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * min(pct_virus / max(self.cfg.VIRUS_WIN_COVERAGE_PCT, 1), 1.0))
        if fill_w > 0:
            pygame.draw.rect(self.screen, (180, 40, 40),
                             (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        lines = [
            f"Temps : {mins:02d}:{secs:02d}{time_left_str}   Vitesse : x{speed_str}",
            f"Virus : {n_virus}   |   Globules : {n_wbc}",
            f"Sol blanc  : {pct_wbc:5.1f}%",
            f"Sol virus  : {pct_virus:5.1f}%  (objectif {self.cfg.VIRUS_WIN_COVERAGE_PCT:.0f}%)",
            "",  # ligne réservée à la barre
        ]
        for i, line in enumerate(lines):
            if line:
                self.screen.blit(
                    self.font.render(line, True, self.cfg.COLOR_UI_TEXT),
                    (W - 364, 14 + i * 17)
                )

        # ── Légende agents ────────────────────────────────────────────────
        lx, ly = 14, H - 52
        pygame.draw.circle(self.screen, self.cfg.COLOR_VIRUS, (lx + 8, ly + 8), 7)
        self.screen.blit(self.font.render("Virus", True, (220, 200, 200)), (lx + 20, ly + 1))
        pygame.draw.circle(self.screen, self.cfg.COLOR_WBC, (lx + 8, ly + 30), 7)
        self.screen.blit(self.font.render("Globule blanc", True, (240, 240, 240)), (lx + 20, ly + 23))

        # ── Pause ─────────────────────────────────────────────────────────
        if self.paused:
            s = self.font_big.render("  PAUSE  ", True, (255, 230, 60))
            self.screen.blit(s, (W // 2 - s.get_width() // 2, H // 2 - 15))

        # ── Game over ─────────────────────────────────────────────────────
        if self._game_over:
            pct_wbc_f, pct_virus_f = self._coverage()

            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            if self._winner == "virus":
                title_text  = "— INFECTION TOTALE —"
                title_color = (220, 60, 60)
            else:
                title_text  = "— IMMUNITÉ ACQUISE —"
                title_color = (100, 200, 255)

            title   = self.font_big.render(title_text, True, title_color)
            reason  = self.font.render(self._game_over_reason, True, (255, 255, 255))
            score_w = self.font.render(f"Globules blancs : {pct_wbc_f:.1f}%", True, (180, 220, 255))
            score_v = self.font.render(f"Virus           : {pct_virus_f:.1f}%", True, (255, 160, 160))
            hint    = self.font.render("[R] Recommencer   [ESC] Quitter", True, (200, 200, 200))

            cx, cy = W // 2, H // 2
            self.screen.blit(title,   (cx - title.get_width()   // 2, cy - 70))
            self.screen.blit(reason,  (cx - reason.get_width()  // 2, cy - 25))
            self.screen.blit(score_w, (cx - score_w.get_width() // 2, cy + 12))
            self.screen.blit(score_v, (cx - score_v.get_width() // 2, cy + 34))
            self.screen.blit(hint,    (cx - hint.get_width()    // 2, cy + 68))

    # ── Boucle principale ─────────────────────────────────────────────────

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
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                        self.cfg.SPEED_STEP_IDX = min(
                            self.cfg.SPEED_STEP_IDX + 1,
                            len(self.cfg.SPEED_STEPS) - 1
                        )
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.cfg.SPEED_STEP_IDX = max(
                            self.cfg.SPEED_STEP_IDX - 1, 0
                        )

            if not self.paused and not self._game_over:
                self.update(dt)

            self.render()

        pygame.quit()