# CS16 Skin Inventory

**The CS:GO weapon skin inventory system, ported to Counter-Strike 1.6 (GoldSrc).**

A Windows GUI that parses GoldSrc `.mdl` model files and writes BMP textures
**directly into the model's embedded texture slots** - no HLMV, no studiomdl,
no recompilation.

The repository layout mirrors the game directory: **copy `cstrike\` into your
`Half-Life\` folder and you're done.**

[简体中文](docs/README.zh-CN.md) | [使用说明](docs/使用说明.md) | [资源清单](docs/资源清单.md)

---

## Features

- **Zero-recompile skinning** - overwrites the texture in place; bones, animation
  sequences, hitboxes and file size all stay untouched
- **Four resource types** - weapon skins, knives, gloves, stickers
- **One-click randomize** - per weapon, or every weapon at once
- **Live texture preview** - reads indexed-colour BMPs directly
- **34 firearms + 19 knife types**
- **Bilingual UI** - switch between Simplified Chinese and English at runtime
- **Single-file tool** - Pillow is the only dependency

---

## Install

### Option 1 - use the prebuilt EXE (recommended)

1. Grab `cs_skin_gui.exe` from the repository root, or from the Releases page
2. Keep the whole repository folder together - the tool locates `cstrike\`
   next to itself
3. Double-click to run

### Option 2 - run from source

```bash
git clone https://github.com/ellingtoncody81-ctrl/cs16-skin-inventory.git
cd cs16-skin-inventory
pip install -r requirements.txt
python src/cs_skin_gui.py
```

> Requires **Python 3.8+** on Windows. `tkinter` ships with the official
> installer; Pillow is the only pip dependency.

---

## Interface language

The GUI ships with both Simplified Chinese and English. Click the language badge
in the top-right corner of the title bar to switch - the change is instant and
applies to every label, button, status line and dialog.

All translatable strings live in `src/i18n.py`. To add a language, append a
third entry to each tuple:

```python
"apply_skin": ("应用皮肤", "Apply", "Votre texte"),
```

The tool warns on `stderr` when a key is missing a translation, so nothing
fails silently. Run `python src/i18n.py` to print a coverage report.

---

## Layout

```
cs16-skin-inventory/
|-- cs_skin_gui.exe              # prebuilt GUI
|-- src/
|   |-- cs_skin_gui.py           # source (MIT)
|   `-- i18n.py                  # bilingual string table
|-- cstrike/                     # copy this into Half-Life\
|   |-- models/                  # 112 .mdl weapon models
|   |   |-- v_ak47.mdl           #   first person
|   |   |-- p_ak47.mdl           #   third person
|   |   `-- ...
|   |-- sound/                   # 208 .wav weapon sounds
|   |   |-- ak47-1.wav           #   vanilla CS 1.6
|   |   `-- csgo/                #   ported CS:GO sounds
|   |       |-- ak47/
|   |       |-- awp/
|   |       `-- ...
|   `-- CSGO Texture Pack/       # 2,173 .bmp textures
|       |-- _gloves/             #   103 glove textures
|       |-- knives_textures/     #   466 knife textures
|       |-- stickers/            #   549 sticker textures
|       `-- AK-47/ AWP/ ...      #   24 weapon folders
|-- docs/
|   |-- README.zh-CN.md          # Chinese readme
|   |-- 使用说明.md              # usage guide (Chinese)
|   `-- 资源清单.md              # asset manifest (Chinese)
|-- LICENSE
|-- requirements.txt
`-- README.md
```

---

## Usage

1. Run `cs_skin_gui.exe`
2. Pick a weapon on the left - filter by **Firearm** / **Knife**, or hit
   **Randomize All**
3. Pick a skin on the right; the texture preview updates live
4. Hit **Apply** - the matching `.mdl` in `cstrike\models\` is rewritten
5. Launch the game

> **Warning: back up `cstrike\models\` first.** The tool overwrites model
> files in place and has no undo.

---

## How it works

Every texture in a GoldSrc `.mdl` is an **8-bit indexed** pixel block (typically
512x512) followed by a **768-byte, 256-colour palette**.

```text
1. Read .mdl -> validate magic "IDST" and version == 10
2. Parse header -> locate textureindex / numtextures
3. Walk the texture table (80 bytes per entry) -> name, width, height, data offset
4. Load the BMP with Pillow
   |-- indexed (P) -> take pixels and palette as-is
   `-- truecolour  -> quantize(256, MEDIANCUT)
5. Resize with NEAREST if dimensions don't match the model's
6. Overwrite the pixel block and palette inside the .mdl
7. Write back to disk
```

**Why no HLMV or studiomdl?** Because only the texture changes, never the
geometry. Bones, animation sequences, collision hulls and hitboxes stay
identical, so a binary overwrite is safe and the file size never changes.

---

## Credits

### Ported assets - everything under `cstrike/`

This project **creates no art assets**. Everything below was ported from CS:GO
to GoldSrc by the **CS:GO Ports** studio (33 members) and published on
GameBanana:

| Asset | Author | Source |
|---|---|---|
| Weapon texture pack | **BDS** | [1424 CSGO's Texture Pack !!! By BDS](https://gamebanana.com/mods/228944) |
| Weapon models (low-poly, CS 1.6 hand rig, inspect animations) | **CS:GO Ports** | [CS:GO Weapons Pack - Update #3](https://gamebanana.com/mods/227269) |
| Packaging reference | TheDoctor0 | [TheDoctor0/CSGOMod](https://github.com/TheDoctor0/CSGOMod) |
| Studio home | - | [CS:GO Ports @ GameBanana](https://gamebanana.com/studios/34724) |

The original author states: **"Don't redistribute this as yours!!!!!"** - do
not rebrand it. This repository credits them and claims nothing else.

### Upstream

- **Counter-Strike** / **CS:GO** - Valve Corporation
- **GoldSrc SDK** - Valve Corporation
- **[TheDoctor0/CSGOMod](https://github.com/TheDoctor0/CSGOMod)** - this
  repository's structure and distribution model follow that precedent

### This project

- `src/cs_skin_gui.py` and `src/i18n.py` - contributors of this repository,
  MIT License

---

## License

- **Source code under `src/`** - [MIT](LICENSE)
- **Assets under `cstrike/`** - copyright of the original porters and Valve,
  **not covered by the MIT License**. Follow the original authors' terms.

This project is not affiliated with Valve Corporation.
Counter-Strike is a registered trademark of Valve Corporation.

---

## Disclaimer

For educational use and personal modding only. You are responsible for complying
with applicable law and the relevant copyright agreements, and for any
consequences arising from your use of third-party assets.
