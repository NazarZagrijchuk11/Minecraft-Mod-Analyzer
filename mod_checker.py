#!/usr/bin/env python3
# ==============================================================
#  Minecraft Mod Analyzer
#  © 2025 Nazar Zagriychuk
#  All rights reserved.
#
#  You are NOT allowed to:
#   • Re-upload, redistribute, or sell this code
#   • Include this script (fully or partially) in public repositories
#     without explicit permission from the author
#
#  You ARE allowed to:
#   • Use and modify this script for personal, non-commercial purposes
#   • Share your own modified versions privately (credit required)
#
#  If you share it — include proper credit:
#  "Author: Nazar Zagriychuk"
# ==============================================================

import os
import sys
import time
import shutil
import zipfile
import json
import tomllib
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

# === SPLASH SCREEN ===
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_splash():
    """Show startup logo in ASCII frame."""
    clear_screen()
    logo = [
        "        🔧🔧",
        "       /----\\",
        "      | [__] |",
        "       \\____/",
        "        ||||",
        "        ||||",
        "        ==== ",
        "     Minecraft Mod Analyzer"
    ]
    
    # рамка
    width = max(len(line) for line in logo) + 4
    top_bottom = "┌" + "─" * (width - 2) + "┐"
    bottom_line = "└" + "─" * (width - 2) + "┘"

    print("\n" * 3)
    print(" " * 10 + top_bottom)
    for line in logo:
        print(" " * 10 + f"│ {line.ljust(width - 4)} │")
        time.sleep(0.1)  # ефект поступової появи
    print(" " * 10 + bottom_line)
    print("\n" * 2)
    
    time.sleep(2.5)
    clear_screen()

    # показує іконку 🛠️ у правому верхньому куті
    terminal_size = shutil.get_terminal_size((80, 20))
    columns = terminal_size.columns
    sys.stdout.write(f"\033[1;{columns-3}H🛠️")
    sys.stdout.flush()


# === CORE LOGIC ===
def detect_default_minecraft_folder() -> Path | None:
    """Detect default Minecraft folder depending on the OS."""
    home = Path.home()
    if os.name == "nt":
        mc = home / "AppData" / "Roaming" / ".minecraft"
    elif sys.platform == "darwin":
        mc = home / "Library" / "Application Support" / "minecraft"
    else:
        mc = home / ".minecraft"
    mods_path = mc / "mods"
    return mods_path if mods_path.exists() else None


def detect_mod_type(jar_path):
    """Detect mod loader type based on file structure."""
    with zipfile.ZipFile(jar_path, 'r') as jar:
        files = jar.namelist()
        if any("fabric.mod.json" in f for f in files):
            return "Fabric"
        if any("quilt.mod.json" in f for f in files):
            return "Quilt"
        if any("META-INF/mods.toml" in f for f in files):
            return "Forge"
        if any("META-INF/neoforge.mods.toml" in f for f in files):
            return "NeoForge"
    return "Unknown"


def extract_mod_info(jar_path):
    """Extract mod ID, name, version and dependencies."""
    mod_type = detect_mod_type(jar_path)
    mod_id, mod_name, mod_version, requires = None, None, None, []

    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            if mod_type in ("Fabric", "Quilt"):
                with jar.open("fabric.mod.json") as f:
                    data = json.load(f)
                    mod_id = data.get("id")
                    mod_name = data.get("name", mod_id)
                    mod_version = data.get("version")
                    requires = list(data.get("depends", {}).keys())

            elif mod_type in ("Forge", "NeoForge"):
                toml_path = (
                    "META-INF/neoforge.mods.toml"
                    if mod_type == "NeoForge"
                    else "META-INF/mods.toml"
                )
                with jar.open(toml_path) as f:
                    data = tomllib.load(f)
                    mod = data["mods"][0]
                    mod_id = mod.get("modId")
                    mod_name = mod.get("displayName", mod_id)
                    mod_version = mod.get("version")
                    requires = [
                        dep["modId"]
                        for dep in data.get("dependencies", {}).get(mod_id, [])
                        if "modId" in dep
                    ]
    except Exception:
        pass

    return {
        "file": os.path.basename(jar_path),
        "id": mod_id or "unknown",
        "name": mod_name or os.path.basename(jar_path),
        "version": mod_version or "?",
        "type": mod_type,
        "requires": requires,
    }


def analyze_crash_logs(log_dir):
    """Scan crash logs for recent errors."""
    if not os.path.exists(log_dir):
        return None

    errors = []
    for file in Path(log_dir).rglob("*.log"):
        try:
            with open(file, errors="ignore") as f:
                text = f.read()
                for match in re.finditer(r"Caused by: ([\w\.]+): (.+)", text):
                    errors.append(match.group(0))
        except Exception:
            continue
    return errors[-5:] if errors else None


def main(mods_path=None):
    show_splash()

    # Try to auto-detect Minecraft folder if no path is provided
    if not mods_path:
        detected = detect_default_minecraft_folder()
        if detected:
            mods_path = detected
            console.print(f"[cyan]Auto-detected Minecraft mods folder:[/cyan] {mods_path}")
        else:
            console.print("[red]Minecraft folder not found! Please specify path manually.[/red]")
            return

    mods_path = Path(mods_path)
    if not mods_path.exists():
        console.print(f"[red]Mods folder not found: {mods_path}[/red]")
        return

    mods = []
    for file in mods_path.glob("*.jar"):
        info = extract_mod_info(file)
        mods.append(info)

    if not mods:
        console.print("[red]No mods found in this folder.[/red]")
        return

    # Count mods per loader
    loader_count = {}
    for m in mods:
        loader_count[m["type"]] = loader_count.get(m["type"], 0) + 1

    # Ignore Unknown
    if "Unknown" in loader_count:
        loader_count.pop("Unknown")

    # Find dominant loader
    dominant_loader = max(loader_count, key=loader_count.get)

    console.print(f"\n[cyan]Dominant loader detected:[/cyan] [bold]{dominant_loader}[/bold]\n")

    # Delete non-dominant mods
    delete_candidates = [m for m in mods if m["type"] != dominant_loader and m["type"] != "Unknown"]

    if delete_candidates:
        console.print(f"[yellow]Found {len(delete_candidates)} mods from other loaders.[/yellow]")
        choice = input("Delete conflicting mods? [y/n]: ").strip().lower()
        if choice == "y":
            for m in delete_candidates:
                try:
                    os.remove(mods_path / m["file"])
                    console.print(f"[red]- Deleted:[/red] {m['file']}")
                except Exception as e:
                    console.print(f"[red]Failed to delete {m['file']}: {e}[/red]")
        else:
            console.print("[green]Skipping deletion.[/green]")
    else:
        console.print("[green]All mods match the same loader type![/green]")

    # Analyze duplicates & missing deps
    mod_ids = [m["id"] for m in mods]
    duplicates = {i for i in mod_ids if mod_ids.count(i) > 1 and i != "unknown"}

    table = Table(title="Minecraft Mod Analyzer", style="cyan")
    table.add_column("Mod Name", justify="left", style="bold")
    table.add_column("Type", style="yellow")
    table.add_column("Version", style="green")
    table.add_column("Status", style="bold")

    for m in mods:
        status = "OK"
        if m["id"] in duplicates:
            status = "⚠ Duplicate mod ID"
        else:
            missing = [dep for dep in m["requires"] if dep not in mod_ids and dep not in ["forge", "minecraft"]]
            if missing:
                status = f"⚠ Install missing mods: {', '.join(missing)}"
        table.add_row(m["name"], m["type"], m["version"], status)

    console.print(table)

    crash_dir = Path(mods_path.parent / "crash-reports")
    errors = analyze_crash_logs(crash_dir)
    if errors:
        console.print("\n[red bold]Recent Crash Log Entries:[/red bold]")
        for err in errors:
            console.print(f"• {err}")

    console.print("\n[green]Scan complete![/green]")


if __name__ == "__main__":
    arg_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg_path)
