# CS16 皮肤库存

**把 CS:GO 的武器皮肤库存系统移植到 Counter-Strike 1.6（GoldSrc）。**

一个 Windows 图形化工具：解析 GoldSrc 的 `.mdl` 模型文件，把 BMP 贴图
**直接写回模型内置的纹理槽** —— 不用 HLMV、不用 studiomdl、不用重新编译。

仓库结构与游戏目录一致：**把 `cstrike\` 整个复制到游戏的 `Half-Life\` 目录即可使用。**

[English](../README.md) | [使用说明](使用说明.md) | [资源清单](资源清单.md)

---

## 特性

- **零重编译换肤** —— 直接覆写贴图；骨骼、动画序列、碰撞体、文件大小全部不变
- **4 类资源可换** —— 武器皮肤、匕首、手套、贴纸
- **一键随机** —— 单把随机，或全部武器同时随机
- **贴图实时预览** —— 直接读取索引色 BMP
- **支持 34 把枪械 + 19 种刀型**
- **中英双语界面** —— 运行时一键切换
- **零依赖单文件** —— 除 Pillow 外无其他 Python 依赖

---

## 安装

### 方式一：直接用打包好的 EXE（推荐）

1. 从仓库根目录（或 Releases 页面）取 `cs_skin_gui.exe`
2. 保持整个仓库文件夹完整 —— 工具靠同级 `cstrike\` 定位资源
3. 双击运行

### 方式二：从源码运行

```bash
git clone https://github.com/ellingtoncody81-ctrl/cs16-skin-inventory.git
cd cs16-skin-inventory
pip install -r requirements.txt
python src/cs_skin_gui.py
```

> 需要 **Python 3.8+**，Windows 系统。`tkinter` 随官方安装包自带，
> Pillow 是唯一的 pip 依赖。

---

## 界面语言

工具内置简体中文和英文。**点标题栏右上角的语言徽章即可切换**，
所有标签、按钮、状态栏和对话框会立即更新。

所有可翻译文案集中在 `src/i18n.py`。要加第三种语言，给每个元组追加一项：

```python
"apply_skin": ("应用皮肤", "Apply", "Votre texte"),
```

缺翻译时工具会往 `stderr` 告警，**不会静默漏译**。
运行 `python src/i18n.py` 可以打印覆盖率报告。

---

## 目录结构

```
cs16-skin-inventory/
|-- cs_skin_gui.exe              # 打包好的图形工具
|-- src/
|   |-- cs_skin_gui.py           # 源码（MIT）
|   `-- i18n.py                  # 双语字符串表
|-- cstrike/                     # 整个目录复制到 Half-Life\
|   |-- models/                  # 112 个 .mdl 武器模型
|   |   |-- v_ak47.mdl           #   第一人称
|   |   |-- p_ak47.mdl           #   第三人称
|   |   `-- ...
|   |-- sound/                   # 208 个 .wav 武器音效
|   |   |-- ak47-1.wav           #   原版 CS 1.6
|   |   `-- csgo/                #   CS:GO 移植音效
|   |       |-- ak47/
|   |       |-- awp/
|   |       `-- ...
|   `-- CSGO Texture Pack/       # 2,173 个 .bmp 贴图
|       |-- _gloves/             #   103 个手套贴图
|       |-- knives_textures/     #   466 个匕首贴图
|       |-- stickers/            #   549 个贴纸贴图
|       `-- AK-47/ AWP/ ...      #   24 个武器目录
|-- docs/
|   |-- README.zh-CN.md          # 本文件
|   |-- 使用说明.md              # 详细使用说明
|   `-- 资源清单.md              # 资源清单
|-- LICENSE
|-- requirements.txt
`-- README.md
```

---

## 使用

1. 运行 `cs_skin_gui.exe`
2. 左侧选择武器 —— 可按 **枪械** / **刀** 筛选，或点 **一键随机全部**
3. 右侧挑皮肤，贴图预览实时更新
4. 点 **应用皮肤** —— `cstrike\models\` 下对应 `.mdl` 被改写
5. 启动游戏

> **注意：请先备份 `cstrike\models\`**。工具直接覆写模型文件，**没有撤销功能**。

---

## 原理

GoldSrc `.mdl` 里的每张贴图都是一个 **8 位索引色**像素块（通常 512x512），
后面紧跟 **768 字节的 256 色调色板**。

```text
1. 读 .mdl -> 校验 magic "IDST" 与 version == 10
2. 解析 header -> 定位 textureindex / numtextures
3. 遍历纹理表（每项 80 字节）-> 名字、宽、高、数据偏移
4. 用 Pillow 打开 BMP
   |-- 索引色 (P) -> 直接取像素与调色板
   `-- 真彩色     -> quantize(256, MEDIANCUT)
5. 尺寸不符 -> 用 NEAREST 缩放到模型要求的宽高
6. 覆写 .mdl 里的像素块与调色板
7. 写回磁盘
```

**为什么不用 HLMV / studiomdl？** 因为只换贴图，不换几何。骨骼、动画序列、
碰撞体、命中盒全部保持原样，所以二进制覆写是安全的，文件大小也不会变。

---

## 致谢

### 移植资源 —— `cstrike/` 下的全部内容

本项目 **不制作任何美术资源**。以下内容全部由 **CS:GO Ports** 工作室
（33 名成员）从 CS:GO 移植到 GoldSrc，并发布在 GameBanana：

| 资源 | 原作者 | 出处 |
|---|---|---|
| 武器贴图包 | **BDS** | [1424 CSGO's Texture Pack !!! By BDS](https://gamebanana.com/mods/228944) |
| 武器模型（低模、CS 1.6 手臂骨骼、检视动画） | **CS:GO Ports** | [CS:GO Weapons Pack - Update #3](https://gamebanana.com/mods/227269) |
| 打包方式参考 | TheDoctor0 | [TheDoctor0/CSGOMod](https://github.com/TheDoctor0/CSGOMod) |
| 工作室主页 | - | [CS:GO Ports @ GameBanana](https://gamebanana.com/studios/34724) |

原作者在发布页写明：**"Don't redistribute this as yours!!!!!"** ——
**请勿冒名转载**。本仓库严格署名，不主张任何其他权利。

### 上游作品

- **Counter-Strike** / **CS:GO** —— Valve Corporation
- **GoldSrc SDK** —— Valve Corporation
- **[TheDoctor0/CSGOMod](https://github.com/TheDoctor0/CSGOMod)** ——
  本仓库的结构与分发模式参照该先例

### 本项目

- `src/cs_skin_gui.py` 与 `src/i18n.py` —— 本仓库贡献者，MIT License

---

## 许可协议

- **`src/` 下的源码** —— [MIT](../LICENSE)
- **`cstrike/` 下的资源** —— 版权归原移植者与 Valve 所有，
  **不适用 MIT 协议**，请遵循原作者的授权条款

本项目与 Valve Corporation 无任何关联。
Counter-Strike 是 Valve Corporation 的注册商标。

---

## 免责声明

本项目仅用于技术学习与个人 Mod 制作交流。使用者需自行确保符合所在地法律
与相关版权协议，并自行承担使用第三方资源所产生的全部责任。
