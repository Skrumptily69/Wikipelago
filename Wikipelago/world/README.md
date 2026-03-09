APWorld source lives in `APWorldSource`.

Build APWorld:

```powershell
.\build_apworld.ps1
```

Output:

`APWorld\Wikipelago.apworld`

Build or expand article pool (broad + diverse):

```powershell
# Build to 5,000 titles (keeps existing and expands)
.\build_article_pool.ps1 -TargetCount 5000

# Rebuild from scratch to 20,000 titles
.\build_article_pool.ps1 -TargetCount 20000 -Replace
```

Optional tuning:

```powershell
# Increase random sampling share (0.0 to 1.0)
.\build_article_pool.ps1 -TargetCount 10000 -RandomShare 0.5

# Deterministic shuffle source
.\build_article_pool.ps1 -TargetCount 10000 -Seed 4242
```

Notes:
- New pool builder mixes many topic categories (games, tech, music, sports, geography, history, science, etc.) plus random pages.
- It filters out many low-value pages (disambiguations, list/index pages, namespace pages).
- After rebuilding pool, run `build_apworld.ps1` again and copy the new `.apworld` into Archipelago custom worlds.
