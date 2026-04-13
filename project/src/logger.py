import csv
import os
from datetime import datetime


HEADER = [
    "date",
    "heure_debut",
    "heure_fin",
    "gagnant",
    "duree_sec",
    "pct_virus_final",
    "virus_elimines",
    "virus_spawnes_total",
    "cases_nettoyees_wbc",
    "n_wbc",
    "virus_speed",
    "wbc_speed",
    "virus_spawn_interval",
    "virus_spawn_batch",
    "virus_max",
    "boid_separation_radius",
    "boid_w_separation",
    "boid_w_alignment",
    "boid_w_cohesion",
    "boid_w_hunt",
    "boid_w_avoid_wall",
    "virus_win_coverage_pct",
    "wbc_win_time",
]

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGS_DIR = os.path.join(_BASE_DIR, "..", "logs")
_LOG_PATH = os.path.join(_LOGS_DIR, "runs.csv")


class SimLogger:

    def __init__(self, cfg, verbose: bool = True):
        self._cfg         = cfg
        self._verbose     = verbose
        self._heure_debut = datetime.now()
        self._closed      = False

        os.makedirs(_LOGS_DIR, exist_ok=True)
        write_header = not os.path.exists(_LOG_PATH)
        self._file   = open(_LOG_PATH, "a", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        if write_header:
            self._writer.writerow(HEADER)
            self._file.flush()
            if self._verbose:
                print(f"[logger] Nouveau fichier de log créé : {_LOG_PATH}")
        else:
            if self._verbose:
                print(f"[logger] Log → {_LOG_PATH}")

    def close(self, gagnant: str, duree_sec: float, pct_virus_final: float,
              virus_elimines: int, virus_spawnes_total: int,
              cases_nettoyees_wbc: int):
        """Écrit la ligne de résultats. Sans effet si déjà appelé."""
        if self._closed:
            return
        self._closed = True

        cfg = self._cfg
        now = datetime.now()

        self._writer.writerow([
            self._heure_debut.strftime("%Y-%m-%d"),
            self._heure_debut.strftime("%H:%M:%S"),
            now.strftime("%H:%M:%S"),
            gagnant,
            f"{duree_sec:.1f}",
            f"{pct_virus_final:.2f}",
            virus_elimines,
            virus_spawnes_total,
            cases_nettoyees_wbc,
            cfg.N_WBC,
            cfg.VIRUS_SPEED,
            cfg.WBC_SPEED,
            cfg.VIRUS_SPAWN_INTERVAL,
            cfg.VIRUS_SPAWN_BATCH,
            cfg.VIRUS_MAX,
            cfg.BOID_SEPARATION_RADIUS,
            cfg.BOID_W_SEPARATION,
            cfg.BOID_W_ALIGNMENT,
            cfg.BOID_W_COHESION,
            cfg.BOID_W_HUNT,
            cfg.BOID_W_AVOID_WALL,
            cfg.VIRUS_WIN_COVERAGE_PCT,
            cfg.WBC_WIN_TIME,
        ])
        self._file.flush()
        self._file.close()
        if self._verbose:
            print(f"[logger] Partie enregistrée ({gagnant}, {duree_sec:.0f}s)")