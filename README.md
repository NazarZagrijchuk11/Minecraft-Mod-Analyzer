---
### 🔍 Keywords
minecraft mod analyzer, forge fabric neoforge tool, mod cleaner, modpack checker, python utility for mods

If you want to support my project you can donate on my buy me a coffee: buymeacoffee.com/general__mayones (you can receive updates earlier than others)

🧩 Minecraft Mod Analyzer & Cleaner

Minecraft Mod Analyzer is a Python-based diagnostic tool that scans your Minecraft modpack, detects conflicts between loaders (Forge, NeoForge, Fabric, Quilt), finds missing dependencies, and can automatically clean up broken or incompatible mods.

This utility is designed for players, modpack creators, and testers who want to identify issues before launching Minecraft — no guesswork, no crashes.

🚀 Key Features

✅ Scans .minecraft/mods automatically or via custom path
✅ Detects loader types (Forge, NeoForge, Fabric, Quilt)
✅ Shows results in a readable, colorized table
✅ Finds missing or duplicate mods
✅ Detects which loader dominates (the one with most mods)
✅ Offers to delete:

Mods from minority loaders

Duplicate or broken mods
✅ Creates a backup before deleting anything

🧠 Why Use It?

Prevent crashes caused by mixed loaders

Quickly find missing dependencies

Clean up duplicate or leftover mods from old modpacks

Get a full overview of your mods setup in seconds

📸 Example Output
Scanning mods folder: C:\Users\User\AppData\Roaming\.minecraft\mods

╭────────────────────── Minecraft Mod Analyzer ───────────────────────╮
│ Mod Name             │ Type       │ Version │ Status                │
│───────────────────────┼────────────┼──────────┼──────────────────────│
│ Create               │ Forge      │ 0.5.1    │ ✅ OK                 │
│ Fabric API           │ Fabric     │ 0.92.0   │ ⚠ Mixed loaders       │
│ JEI                  │ Forge      │ 15.3.1   │ ✅ OK                 │
╰─────────────────────────────────────────────────────────────────────╯

Mixed loaders detected: Forge (2), Fabric (1)
Dominant loader: Forge
Delete conflicting mods? [y/n]:

⚙️ Installation

Make sure you have Python 3.11+ installed

Install the required package:

pip install rich


Download the mod_checker.py script

Run it via:

python mod_checker.py


(You can also pass a custom mods folder as argument)

python mod_checker.py "D:\Modpacks\SkyFactory4\mods"

🧰 Safe Behavior

Automatically creates a backup folder before deleting anything

Never removes core libraries like fabric-api, architectury, kotlinforforge, etc.

You can always restore mods from the generated backup folder

📜 License

This project is licensed under the MIT License.
See the included LICENSE
 file for details.

💡 Credits

Developed by Nazar Zagriychuk
Inspired by the idea of creating a simple, open-source solution to diagnose and clean Minecraft modpacks automatically.
