# Dungeon RPG

A 2D dungeon RPG built with Python and Pygame. Explore random rooms, fight
enemies, collect gold, choose upgrades, and defeat the boss.

## Play the Windows version

1. Download [`main.exe`](https://github.com/faurc050/me/releases/latest).
2. Open the downloaded file to start the game.
3. If Windows shows a security warning, choose **More info** and then **Run anyway**.

## Run from source

Install Python 3.10 or newer, then run these commands in the project folder:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Windows Command Prompt:

```bat
venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

## Features
- WASD movement
- mouse aim
- left-click attacks
- dodge roll
- random room dungeon
- enemies, gold, upgrades, boss fight
- generated sounds
- menu + pause menu + game over + victory flow
- music toggle
- full 360-degree character aiming and weapon rotation

You can also double-click `run_game.bat` after installing the dependency.

## Controls
- Move: W A S D
- Aim: Mouse
- Attack: Left click
- Dodge: Space
- Upgrade choices: 1, 2, 3
- Enter door: E
- Pause: Esc
- Toggle music: M
- Restart: Enter
