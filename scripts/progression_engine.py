#!/usr/bin/env python3
"""
PT Gary — Progression Engine (Amy — Conditioning-First)

Reads completed session logs (JSON), calibrates weights, flags progression
opportunities, and updates the program MD.

Conditioning-first progression (Amy):
  - Primary: week-based rest reduction and rep/round addition (in program MD)
  - Weight calibration: update estimated/'TBD' weights with actuals
  - Weight only climbs when conditioning improves (easily hitting all targets)
  - Flag when reps crushed → suggest rep bump for next cycle

Usage:
  python3 progression_engine.py [path/to/session.json]
  (called automatically after each session completes)
"""

import re
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

ADL = timezone(timedelta(hours=9, minutes=30))
REPO = Path("/Users/gary/Projects/amy-pt")
PROGRAM_FILE = REPO / "programs" / "cycle-1-week-1.md"
CONFIG_FILE = REPO / "config" / "amy-hancock.md"
STALL_FILE = REPO / "programs" / ".stall_tracker.json"


# ── Parse Helpers ────────────────────────────────────────────────────────────

def parse_log_file(filepath: Path) -> dict:
    return json.loads(filepath.read_text())


def parse_target_from_exercise(exercise: dict) -> dict:
    """Parse exercise JSON into target dict: {weight, rep_low, rep_high}."""
    t = {
        "weight": exercise.get("target_weight_kg"),
        "rep_low": 8,
        "rep_high": 12,
    }

    reps_str = str(exercise.get("target_reps", ""))
    if reps_str and '-' in reps_str:
        parts = reps_str.split('-')
        try:
            t["rep_low"] = int(parts[0].strip())
            t["rep_high"] = int(parts[1].strip())
        except ValueError:
            pass
    elif reps_str and reps_str.isdigit():
        v = int(reps_str.strip())
        t["rep_low"] = v
        t["rep_high"] = v

    return t


def actual_reps_from_exercise(exercise: dict) -> list[int]:
    if exercise.get("skipped"):
        return []
    sets = exercise.get("sets") or []
    return [s["reps"] for s in sets if "reps" in s]


def actual_weights_from_exercise(exercise: dict) -> list[float]:
    if exercise.get("skipped"):
        return []
    sets = exercise.get("sets") or []
    return [s["weight_kg"] for s in sets if "weight_kg" in s]


# ── Conditioning-First Progression ───────────────────────────────────────────

def calculate_conditioning_progression(target: dict, actual_reps: list[int],
                                        actual_weights: list[float],
                                        exercise_name: str) -> dict:
    """Conditioning-first progression logic.

    Amy's progression is density-based (rest reduction, rep/round addition),
    not weight-on-bar. This engine:
      - Calibrates TBD or underestimated weights
      - Flags when targets are crushed (for manual or cycle-based rep bumps)
      - Drops weight if performance degraded significantly
    """
    if not actual_reps or all(r == 0 for r in actual_reps):
        return {"action": "skip", "new_weight": target["weight"], "reason": "Exercise skipped"}

    rep_high = target["rep_high"]
    rep_low = target["rep_low"]
    target_weight = target["weight"]
    avg_actual_weight = sum(actual_weights) / len(actual_weights) if actual_weights else 0

    total_sets = len(actual_reps)

    # Check if actual weight significantly exceeds target → calibrate
    if target_weight and avg_actual_weight > target_weight * 1.1:
        return {
            "action": "calibrate",
            "new_weight": round(avg_actual_weight, 1),
            "reason": f"Weight calibrated up: {target_weight}kg → {avg_actual_weight:.1f}kg"
        }

    # Check if target was TBD/None → calibrate from actuals
    if target_weight is None and avg_actual_weight > 0:
        return {
            "action": "calibrate",
            "new_weight": round(avg_actual_weight, 1),
            "reason": f"Weight calibrated from TBD: → {avg_actual_weight:.1f}kg"
        }

    # All sets crushed the rep target → flag (conditioning improving)
    sets_crushed = sum(1 for r in actual_reps if r > rep_high)
    if sets_crushed == total_sets and total_sets >= 2:
        return {
            "action": "flag_crush",
            "new_weight": target_weight,
            "reason": f"All {total_sets} sets exceeded {rep_high} reps — ready for rep bump or rest reduction"
        }

    # Two or more sets below bottom of range → performance degraded
    sets_below = sum(1 for r in actual_reps if r < rep_low)
    if sets_below >= 2:
        new_weight = round((target_weight or 0) * 0.95, 1) if target_weight else None
        return {
            "action": "drop",
            "new_weight": new_weight,
            "reason": f"{sets_below} sets below {rep_low} reps — consider deload or form focus"
        }

    # Partial crush → within range, hold
    sets_hit_top = sum(1 for r in actual_reps if r >= rep_high)
    if sets_hit_top > 0:
        return {
            "action": "repeat",
            "new_weight": target_weight,
            "reason": f"{sets_hit_top}/{total_sets} sets at top of range: hold"
        }

    return {
        "action": "repeat",
        "new_weight": target_weight,
        "reason": f"All sets within {rep_low}–{rep_high} range: hold"
    }


# ── Stall Detection ──────────────────────────────────────────────────────────

def check_stalls(exercise_name: str, action: str) -> bool:
    stalls = {}
    if STALL_FILE.exists():
        stalls = json.loads(STALL_FILE.read_text())

    if action in ["repeat", "drop"]:
        stalls[exercise_name] = stalls.get(exercise_name, 0) + 1
    else:
        stalls[exercise_name] = 0

    STALL_FILE.write_text(json.dumps(stalls, indent=2))
    return stalls[exercise_name] >= 2


# ── Program Updater ──────────────────────────────────────────────────────────

def update_program_weights(progression_results: dict):
    """Update the program MD with calibrated weights."""
    content = PROGRAM_FILE.read_text()

    for ex_name, result in progression_results.items():
        if result["action"] in ["calibrate"] and result["new_weight"] is not None:
            new_weight_str = f"{result['new_weight']}kg"

            # Find and replace the weight for this exercise in the program
            escaped = re.escape(ex_name)
            # Pattern: exercise row with kg weight
            pattern = rf'(\|.*?{escaped}.*?\|\s*[\d.\-]+kg)'  # matches '50–55kg' etc
            match = re.search(pattern, content)
            if match:
                old_cell = match.group(0)
                # Replace the last kg value in the row
                new_cell = re.sub(r'[\d.\-]+kg', new_weight_str, old_cell, count=1)
                # Only replace if it's a single value (not a range like 50–55kg)
                if '–' not in old_cell.split('|')[-2] and '-' not in old_cell.split('|')[-2].replace('kg',''):
                    content = content.replace(old_cell, new_cell)

    PROGRAM_FILE.write_text(content)
    return content


# ── Main ─────────────────────────────────────────────────────────────────────

def run_progression(latest_log_path: Path = None):
    logs_dir = REPO / "logs"
    if latest_log_path:
        log_file = latest_log_path
    else:
        log_files = sorted(logs_dir.glob("*.json"))
        log_files = [f for f in log_files if not f.name.startswith('_') and f.name != "index.json"]
        if not log_files:
            print("No session logs found.")
            return None
        log_file = log_files[-1]

    session = parse_log_file(log_file)
    session_type = session.get("type", "")
    session_date = session.get("date", "")
    print(f"📊 Processing: {session_date} — {session_type}")

    results = {}
    for ex in session.get("exercises", []):
        ex_name = ex["name"]
        if ex.get("skipped"):
            results[ex_name] = {"action": "skip", "new_weight": None, "reason": "Skipped"}
            continue

        target = parse_target_from_exercise(ex)
        actual_reps = actual_reps_from_exercise(ex)
        actual_weights = actual_weights_from_exercise(ex)

        if not actual_reps:
            continue

        result = calculate_conditioning_progression(target, actual_reps, actual_weights, ex_name)
        results[ex_name] = result

        # Check stalls
        is_stalled = check_stalls(ex_name, result["action"])
        if is_stalled:
            result["stalled"] = True
            result["reason"] += " ⚠️ STALLED — consider exercise rotation"

        flag = {"calibrate": "📐", "flag_crush": "🚀", "drop": "⚠️", "repeat": "—", "skip": "⊘"}.get(result["action"], "?")
        weight_str = f"→ {result['new_weight']}kg" if result["new_weight"] else ""
        print(f"  {flag} {ex_name}: {result['reason']} {weight_str}")

    # Update program
    update_program_weights(results)

    # Commit
    import os
    os.chdir(REPO)
    os.system("git add programs/cycle-1-week-1.md programs/.stall_tracker.json 2>/dev/null")
    os.system(f"git commit -m 'progression: {session_date} {session_type}' 2>&1")
    os.system("git push origin main 2>&1")

    # Rebuild logs/index.json for dashboard
    rebuild_log_index()
    os.system("git add logs/index.json && git commit -m 'chore: rebuild logs index' && git push origin main 2>&1")

    return results


def rebuild_log_index():
    """Rebuild logs/index.json with metadata for all session logs."""
    logs_dir = REPO / "logs"
    index = []
    for f in sorted(logs_dir.glob("*.json"), reverse=True):
        if f.name.startswith("_") or f.name == "index.json":
            continue
        try:
            data = json.loads(f.read_text())
            index.append({
                "name": f.name,
                "date": data.get("date", ""),
                "type": data.get("type", ""),
                "status": data.get("status", "complete"),
                "duration_min": data.get("duration_min", 0),
                "ad_hoc": data.get("ad_hoc", False),
                "resumed_from": data.get("resumed_from", None),
                "exercise_count": len(data.get("exercises", [])),
                "skipped_count": sum(1 for e in data.get("exercises", []) if e.get("skipped"))
            })
        except Exception:
            pass
    (logs_dir / "index.json").write_text(json.dumps(index, indent=2))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_progression(Path(sys.argv[1]))
    else:
        run_progression()
