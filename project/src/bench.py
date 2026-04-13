#!/usr/bin/env python3
"""
bench.py ─ Sweep paramétrique automatisé.

Lance REPEATS parties en mode headless (sans affichage, sans limite FPS)
pour chaque valeur de chaque paramètre défini dans SWEEP.
Les résultats sont ajoutés dans logs/runs.csv via le SimLogger existant.

Usage :
    python project/src/bench.py
"""

import os
import sys
import time

# ── Mode headless SDL : DOIT être défini avant tout import pygame ─────────────
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from configuration.cfg import Config
from core.simulation import Simulation

# =============================================================================
# Paramètres du sweep
# =============================================================================

# Nombre de répétitions par valeur testée
REPEATS = 3

# Pour chaque paramètre : liste des valeurs à tester.
# La valeur par défaut de cfg.py est incluse dans la liste (marquée ← défaut).
# Toutes les valeurs sont testées REPEATS fois.
SWEEP = {

    # ── Règles de fin ──────────────────────────────────────────────────────
    "VIRUS_WIN_COVERAGE_PCT": [40.0, 50.0, 60.0, 70.0, 80.0],    # ← 50.0
    "WBC_WIN_TIME":           [60.0, 90.0, 120.0, 150.0, 180.0],  # ← 120.0

    # ── Virus ──────────────────────────────────────────────────────────────
    "VIRUS_SPEED":          [35.0, 45.0, 55.0, 65.0, 75.0],  # ← 55.0
    "VIRUS_TURN_SPEED":     [1.5,  2.0,  2.5,  3.0,  3.5],   # ← 2.5
    "VIRUS_RANDOM_BIAS":    [0.2,  0.4,  0.6,  0.8,  1.0],   # ← 0.6
    "VIRUS_SPAWN_INTERVAL": [1.0,  1.4,  1.8,  2.2,  2.8],   # ← 1.8
    "VIRUS_SPAWN_BATCH":    [1,    2,    3,    4,    5],       # ← 2
    "VIRUS_MAX":            [80,   100,  120,  140,  160],     # ← 120

    # ── Globules blancs ────────────────────────────────────────────────────
    "N_WBC":          [8,    10,   14,   18,   22],    # ← 14
    "WBC_SPEED":      [55.0, 65.0, 75.0, 85.0, 95.0], # ← 75.0
    "WBC_TURN_SPEED": [2.0,  2.5,  3.5,  4.5,  5.5],  # ← 3.5

    # ── Boids ──────────────────────────────────────────────────────────────
    "BOID_SEPARATION_RADIUS": [15.0, 22.0, 30.0, 40.0, 50.0],  # ← 30.0
    "BOID_W_SEPARATION":      [0.8,  1.2,  1.8,  2.4,  3.0],   # ← 1.8
    "BOID_W_ALIGNMENT":       [0.3,  0.6,  0.9,  1.2,  1.8],   # ← 0.9
    "BOID_W_COHESION":        [0.2,  0.4,  0.7,  1.0,  1.5],   # ← 0.7
    "BOID_W_HUNT":            [0.5,  1.0,  1.4,  1.8,  2.5],   # ← 1.4
    "BOID_W_AVOID_WALL":      [0.8,  1.4,  2.0,  2.8,  3.5],   # ← 2.0
    "WALL_REPULSION_DIST":    [20.0, 30.0, 40.0, 55.0, 70.0],  # ← 40.0

    # ── Vision / Collision ─────────────────────────────────────────────────
    "VISION_RADIUS":       [50.0, 70.0,  90.0, 110.0, 130.0],  # ← 90.0
    "COLLISION_KILL_DIST": [8.0,  11.0,  14.0,  17.0,  20.0],  # ← 14.0
}

# =============================================================================
# Runner
# =============================================================================

def _fmt_eta(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}m{s:02d}s"


def main():
    total_runs = sum(len(vals) * REPEATS for vals in SWEEP.values())
    run_num    = 0
    t_bench    = time.time()
    durations  = []  # pour estimer l'ETA

    print(f"\n{'='*60}")
    print(f"  Sweep paramétrique : {len(SWEEP)} paramètres")
    print(f"  {total_runs} runs  ({len(SWEEP)} params × ~5 valeurs × {REPEATS} rép.)")
    print(f"{'='*60}\n")

    for param, values in SWEEP.items():
        print(f"┌─ {param}  ({len(values)} valeurs × {REPEATS} runs)")

        for val in values:
            for rep in range(1, REPEATS + 1):
                run_num += 1

                # Estimation ETA
                if durations:
                    avg    = sum(durations) / len(durations)
                    remaining = avg * (total_runs - run_num + 1)
                    eta_str = f"  ETA ~{_fmt_eta(remaining)}"
                else:
                    eta_str = ""

                label = f"│  [{run_num:3d}/{total_runs}] {param}={val!r}  run {rep}/{REPEATS}{eta_str}"
                print(label, end="", flush=True)

                t0  = time.time()
                cfg = Config()
                setattr(cfg, param, val)
                sim = Simulation(cfg, headless=True)
                sim.run_headless()
                dt  = time.time() - t0

                durations.append(dt)
                print(f"  → {dt:.1f}s")

        print(f"└{'─'*55}\n")

    total_elapsed = time.time() - t_bench
    print(f"{'='*60}")
    print(f"  Terminé : {total_runs} runs en {_fmt_eta(total_elapsed)}")
    print(f"  Résultats → logs/runs.csv")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
