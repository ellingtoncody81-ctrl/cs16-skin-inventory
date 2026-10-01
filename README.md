# CS:GO Weapon Inventory for Counter-Strike 1.6

**把 CS:GO 的武器皮肤库存系统移植到 CS 1.6（GoldSrc）。**

配套一个 Windows 图形化换肤工具：解析 GoldSrc `.mdl` 模型文件，
把 BMP 贴图**直接写回模型内置纹理槽**，无需 HLMV、无需 studiomdl 重编译。

仓库结构与游戏目录一致 —— **整个 `cstrike\` 复制到游戏的 `Half-Life\` 即可直接使用。**

---

## 特性

- **零重编译换肤** —— 直接改写 `.mdl` 内嵌纹理，不碰骨骼/动画/碰撞体
- **3 类资源可换** —— 武器皮肤、匕首皮肤、手套、贴纸（印花）
- **一键随机** —— 单把随机 / 全部武器随机
- **贴图实时预览** —— BMP 直读，索引色 256 色
- **支持 34 把武器 + 19 种刀型**
- **零依赖单文件** —— 除 Pillow 外无其他 Python 依赖

---

## 安装

### 方式一：直接用打包好的 EXE（推荐）

1. 从 [Releases](https://github.com/<owner>/<repo>/releases) 下载，或直接用仓库根目录的 `cs_skin_gui.exe`
2. 把**整个仓库文件夹**放在任意位置（工具会自动定位同级 `cstrike\` 目录）
3. 双击运行

### 方式二：从源码运行

```bash
git clone <本仓库地址>
cd csgo-inventory-cs16
pip install -r requirements.txt
python src/cs_skin_gui.py
```

> **Python 3.8+** · Windows · 依赖仅 `Pillow`（`tkinter` 为标准库自带）

---

## 目录结构

```
csgo-inventory-cs16/
├── cs_skin_gui.exe              # 打包好的图形工具
├── src/
│   └── cs_skin_gui.py           # 源码（MIT）
├── cstrike/                     # ← 整个目录复制到游戏的 Half-Life\ 即可
│   ├── models/                  # 112 个 .mdl 武器模型
│   │   ├── v_ak47.mdl           #   第一人称
│   │   ├── p_ak47.mdl           #   第三人称
│   │   └── ...
│   ├── sound/                   # 208 个 .wav 武器音效
│   │   ├── ak47-1.wav           #   原版 CS1.6 音效
│   │   └── csgo/                #   CS:GO 移植音效
│   │       ├── ak47/
│   │       ├── awp/
│   │       └── ...
│   └── CSGO Texture Pack/       # 2,173 个 .bmp 贴图
│       ├── _gloves/             #   手套贴图（103）
│       ├── knives_textures/     #   匕首贴图（466）
│       ├── stickers/            #   印花贴图（549）
│       ├── AK-47/               #   武器贴图
│       ├── AWP/
│       └── ... 共 24 个武器目录
├── docs/
│   ├── 使用说明.md
│   └── 资源清单.md
├── LICENSE
├── requirements.txt
└── README.md
```

---

## 使用

1. 运行 `cs_skin_gui.exe`
2. 左侧选择武器（可切「枪械」/「刀」分类，可点「一键随机全部」）
3. 右侧从列表里挑皮肤，**贴图会实时预览**
4. 点「应用皮肤」—— 直接改写 `cstrike\models\` 下对应 `.mdl`
5. 启动游戏即可看到新皮肤

> **备份提醒**：首次使用前请自行备份 `cstrike\models\` 目录。
> 工具会直接覆盖模型文件。

---

## 工具是怎么工作的

GoldSrc 的 `.mdl` 文件里，每张贴图都是一个 **512×512 的 8 位索引色**数据块，
后面紧跟 **768 字节的 256 色调色板**。

工具的流程：

```
1. 读 .mdl → 校验 magic "IDST" + version == 10
2. 解析 header → 拿到 textureindex / numtextures
3. 遍历纹理表 → 每项 80 字节，得到纹理的 名字/宽/高/数据偏移
4. 用 Pillow 打开 BMP
   ├─ 索引色(P) → 直接取像素 + 调色板
   └─ 真彩色     → quantize(256, MEDIANCUT) 量化
5. 尺寸不符 → NEAREST 缩放到模型要求的宽高
6. 覆写 .mdl 里对应的像素块 + 调色板
7. 写回磁盘
```

**为什么不用 HLMV / studiomdl** —— 因为只换贴图不换几何。
`.mdl` 的骨骼、动画序列、碰撞体、命中盒全部保持原样，
所以直接二进制覆写是安全的，文件大小也不变。

---

## Credits

### 移植资源（本仓库 `cstrike/` 全部内容）

本项目 **不制作任何美术资源**。以下内容全部来自
**CS:GO Ports 工作室**（GameBanana 工作室，33 名成员）在
GameBanana 发布的 CS:GO → GoldSrc 移植作品：

| 资源 | 原作者 | 出处 |
|---|---|---|
| 武器贴图包 | **BDS** | [1424 CSGO's Texture Pack !!! By BDS](https://gamebanana.com/mods/228944) |
| 武器模型（低模 + CS1.6 手臂 + 检视动画） | **CS:GO Ports** | [CS:GO Weapons Pack - Update #3](https://gamebanana.com/mods/227269) |
| 上述两者的整合打包 | TheDoctor0 | [TheDoctor0/CSGOMod](https://github.com/TheDoctor0/CSGOMod) |
| 工作室主页 | — | [CS:GO Ports @ GameBanana](https://gamebanana.com/studios/34724) |

原作者在发布页明确标注 **"Don't redistribute this as yours!!!!!"** ——
**请勿冒名转载**。本仓库严格遵守，仅做整理与工具化。

### 上游作品

- **Counter-Strike** 与 **CS:GO** — Valve Corporation
- **GoldSrc SDK** — Valve Corporation
- **[TheDoctor0/CSGOMod](https://github.com/TheDoctor0/CSGOMod)** — 本仓库的仓库结构、
  分发模式（贴图/模型直接入库、编译产物 gitignore）均参照该先例

### 本项目

- 换肤工具 `src/cs_skin_gui.py` — 本仓库贡献者，MIT License

---

## License

- **`src/` 源码** — [MIT](LICENSE)
- **`cstrike/` 资源** — 版权归原移植者与 Valve 所有，**不适用 MIT**，
  遵循原作者的授权条款

> 本项目与 Valve Corporation 无任何关联。
> Counter-Strike 是 Valve Corporation 的注册商标。

---

## Disclaimer

本项目仅用于技术学习与个人Mod制作交流。
使用者需自行确保符合所在地法律与相关版权协议，
并自行承担使用第三方资源的全部责任。
