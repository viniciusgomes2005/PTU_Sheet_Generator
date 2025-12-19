from typing import Any, Dict


DEFAULT_SKILLS = {
    "acrobatics": 0,
    "athletics": 0,
    "combat": 0,
    "intimidate": 0,
    "stealth": 0,
    "survival": 0,
    "general_education": 0,
    "medicine_education": 0,
    "occult_education": 0,
    "pokemon_education": 0,
    "technology_education": 0,
    "guile": 0,
    "perception": 0,
    "charm": 0,
    "command": 0,
    "focus": 0,
    "intuition": 0,
}

DEFAULT_COMBAT_STATS = {
    "hp": {"base": 10, "allocated": 0, "bonus": 0, "stage": 0},
    "attack": {"base": 5, "allocated": 0, "bonus": 0, "stage": 0},
    "defense": {"base": 5, "allocated": 0, "bonus": 0, "stage": 0},
    "special_attack": {"base": 5, "allocated": 0, "bonus": 0, "stage": 0},
    "special_defense": {"base": 5, "allocated": 0, "bonus": 0, "stage": 0},
    "speed": {"base": 5, "allocated": 0, "bonus": 0, "stage": 0},
}

def _stat_current(stat: Dict[str, int]) -> int:
    return int(stat.get("base", 0) + stat.get("allocated", 0) + stat.get("bonus", 0))

def _calc_ap_max(level: int) -> int:
    return 5 + (level // 5)

def _calc_trainer_hp_max(level: int, hp_stat: int) -> int:
    return (level * 2) + (hp_stat * 3) + 10

def _calc_evasion_from_stat(stat_value: int) -> int:
    return min(6, stat_value // 5)

def compute_derived(trainer: Dict[str, Any]) -> Dict[str, Any]:
    level = int(trainer["progression"]["level"])
    cs = trainer["combat_stats"]

    hp = _stat_current(cs["hp"])
    defense = _stat_current(cs["defense"])
    spdef = _stat_current(cs["special_defense"])
    speed = _stat_current(cs["speed"])

    derived = {
        "ap_max": _calc_ap_max(level),
        "hp_max": _calc_trainer_hp_max(level, hp),
        "evasion": {
            "physical": _calc_evasion_from_stat(defense),
            "special": _calc_evasion_from_stat(spdef),
            "speed": _calc_evasion_from_stat(speed),
        },
    }
    return derived
