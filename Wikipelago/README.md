# Wikipelago

Wikipelago is an Archipelago custom world inspired by The Wiki Game.
You navigate Wikipedia articles to hit generated round targets, collect progression, and clear your goal.

## What This Repo Contains

- `world/` - APWorld source + build scripts
- `yaml/` - player YAML templates
- `bridge/` - cloud/local bridge backend (connects web client to AP server)
- `web/` - browser client UI

## Requirements

- Archipelago 0.6.6 (recommended for this project)
- Windows PowerShell (for provided scripts)
- Python (for bridge and pool builder)
- Chrome/Edge/Firefox for web client

## Host Setup (Generator / Organizer)

### 1) Build article pool (optional but recommended)

```powershell
cd world
.\build_article_pool.ps1 -TargetCount 10000 -Replace -RandomShare 0.5
```

Notes:
- Higher `TargetCount` = broader round variety.
- After rebuilding pool, rebuild `.apworld`.

### 2) Build the APWorld

```powershell
cd world
.\build_apworld.ps1
```

Output:
- `world\APWorld\Wikipelago.apworld`

### 3) Install APWorld for local generation

```powershell
Copy-Item -Force ".\world\APWorld\Wikipelago.apworld" "C:\ProgramData\Archipelago\custom_worlds\Wikipelago.apworld"
```

### 4) Generate seed

Use your normal Archipelago generation flow with your player YAML(s).

## Player YAML

Use the template in `world\Wiki.yaml` (or files in `yaml\`).

Important options:
- `check_count`
- `required_fragments`
- `start_rounds_unlocked`
- `rounds_per_unlock`
- `random_goal_article`
- `goal_article_preset`
- `progression_balancing`

## How Players Join

For syncs (including Bananium-style setups), each Wikipelago player should have:
- their Wikipelago YAML
- matching `Wikipelago.apworld` installed in Archipelago custom worlds
- server address + slot name (+ password if needed)
- web app URL

## Web App / Bridge

## Hosted (recommended)

Deploy this repo as a Python web service (Render supported):

- Build command:
  - `pip install -r bridge/requirements.txt`
- Start command:
  - `python bridge/bridge.py --host 0.0.0.0 --port $PORT`

Then share the deployed URL with players.

## Local (optional)

```powershell
cd bridge
python bridge.py --host 127.0.0.1 --port 5000
```

Open:
- `http://127.0.0.1:5000`

## Gameplay Logic Summary

- Round checks are generated procedurally from article pairs.
- Goal article is selectable by preset or random mode.
- Goal requires Knowledge Fragments (and current progression conditions from slot data).
- Round unlocking is gated by `Round Access` items.
- Co-op support: other games can send your fragments/progression items.

## Troubleshooting

### Tracker does not show complete
- Ensure updated `bridge/bridge.py` is deployed/restarted.
- Reconnect slot and trigger a page check once.

### Web changes not visible
- Hard refresh (`Ctrl+Shift+R`) and clear site cache.
- Verify deployed commit is current.

### `No functional world found` / YAML errors
- Confirm game name is exactly `Wikipelago`.
- Confirm `Wikipelago.apworld` is installed in custom worlds.
- Validate YAML indentation and option names.

### Repeats / narrow article feel
- Rebuild pool with higher `TargetCount` and `-Replace`, then rebuild `.apworld`.

## Release Checklist

1. Rebuild pool (if changed)
2. Rebuild `.apworld`
3. Install updated `.apworld`
4. Generate test seed and verify playthrough
5. Deploy bridge/web update
6. Push all files and tag release

## Credits

Built for Archipelago custom multiworld play with a browser-first Wikipelago experience.
