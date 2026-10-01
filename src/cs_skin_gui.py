"""
CS 1.6 武器换肤工具 - 图形界面版
完全独立,无需依赖其他文件
"""
import struct, os, sys, random, threading
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_exe_dir()
MODELS_DIR = os.path.join(BASE_DIR, "cstrike", "models")
TEXTURES_DIR = os.path.join(BASE_DIR, "cstrike", "CSGO Texture Pack")
GLOVES_DIR = os.path.join(TEXTURES_DIR, "_gloves")
KNIEFES_DIR = os.path.join(TEXTURES_DIR, "knives_textures")
STICKERS_DIR = os.path.join(TEXTURES_DIR, "stickers")

# (显示名, ct_knife 下的目录名, 贴图子文件夹)
KNIFE_ENTRIES = [
    ("Bayonet",       "Bayonet",         "bayonet"),
    ("Bowie",         "Bowie",           "bowie"),
    ("Butterfly",     "Butterfly",       "butterfly"),
    ("CounterTerrorist","CounterTerrorist","classic"),
    ("CSS",           "css",             "classic_css"),
    ("Flip",          "Flip",            "flip"),
    ("Gut",           "Gut",             "gut"),
    ("Huntsman",      "Huntsman",        "huntsman"),
    ("Karambit",      "Karambit",        "karambit"),
    ("M9 Bayonet",    "M9Bayonet",       "m9 bayonet"),
    ("Navaja",        "Navaja",          "navaja"),
    ("Nomad",         "Nomad",           "nomad"),
    ("Paracord",      "Paracord",        "paracord"),
    ("Shadow Daggers","ShadowDaggers",   "shadow daggers"),
    ("Skeleton",      "Skeleton",        "skeleton"),
    ("Stiletto",      "Stiletto",        "stiletto"),
    ("Survival",      "Survival",        "survival"),
    ("Talon",         "Talon",           "talon"),
    ("Terrorist",     "Terrorist",       "classic_t"),
    ("Ursus",         "Ursus_1st",       "ursus"),
]

EXCLUDE_WEAPONS = {
    "v_bizon.mdl", "v_cz75.mdl", "v_m4a1s.mdl", "v_mag7.mdl", "v_negev.mdl",
    "v_p2000.mdl", "v_r8.mdl", "v_sawedoff.mdl", "v_tec9.mdl",
    "v_knife_r.mdl", "v_shield_r.mdl", "v_augscope.mdl", "v_sigscope.mdl",
    "v_knife.mdl",
}

WEAPON_MAP = {
    "v_ak47.mdl":   ("AK-47",       "AK-47"),
    "v_aug.mdl":    ("AUG",         "AUG"),
    "v_awp.mdl":    ("AWP",         "AWP"),
    "v_deagle.mdl": ("Desert Eagle","Desert Eagle"),
    "v_elite.mdl":  ("Dual Elites", "Dual Elites"),
    "v_famas.mdl":  ("FAMAS",       "FAMAS"),
    "v_fiveseven.mdl":("Five-SeveN","Fiveseven"),
    "v_g3sg1.mdl":  ("G3SG1",       "G3SG1"),
    "v_galil.mdl":  ("Galil",       "Galil"),
    "v_glock18.mdl":("Glock 18",    "Glock 18"),
    "v_m249.mdl":   ("M249",        "M249"),
    "v_m3.mdl":     ("M3",          "Nova"),
    "v_m4a1.mdl":   ("M4A1",        "M4A1-s"),
    "v_mac10.mdl":  ("MAC-10",      "MAC10"),
    "v_mp5.mdl":    ("MP5",         "MP7"),
    "v_p90.mdl":    ("P90",         "P90"),
    "v_p228.mdl":   ("P228",        "P250"),
    "v_scout.mdl":  ("Scout",       "Scout"),
    "v_sg550.mdl":  ("SG550",       "SG550"),
    "v_sg552.mdl":  ("SG552",       "SG553"),
    "v_tmp.mdl":    ("TMP",         "MP9"),
    "v_ump45.mdl":  ("UMP-45",      "UMP-45"),
    "v_usp.mdl":    ("USP",         "USP-S"),
    "v_xm1014.mdl": ("XM1014",      "XM1014"),
}

TEX_ENTRY_SIZE = 80

def read_cstr(data, offset, maxlen=64):
    end = data.find(b'\x00', offset, offset + maxlen)
    if end == -1:
        end = offset + maxlen
    return data[offset:end].decode('ascii', errors='replace')

def parse_mdl(data):
    if data[0:4] != b'IDST':
        raise ValueError("Not a valid GoldSrc MDL file")
    version = struct.unpack_from('<I', data, 4)[0]
    if version != 10:
        raise ValueError(f"Unsupported MDL version: {version}")
    fields = ['numbones', 'boneindex', 'numbonecontrollers', 'bonecontrollerindex',
              'numhitboxes', 'hitboxindex', 'numseq', 'seqindex', 'numseqgroups', 'seqgroupindex',
              'numtextures', 'textureindex', 'texturedataindex',
              'numskinref', 'numskinfamilies', 'skinindex',
              'numbodyparts', 'bodypartindex',
              'numattachments', 'attachmentindex',
              'numtransitions', 'transitionindex']
    fmt = '<' + 'i' * len(fields)
    vals = struct.unpack_from(fmt, data, 140)
    info = dict(zip(fields, vals))
    info['name'] = read_cstr(data, 8, 64)
    info['length'] = struct.unpack_from('<I', data, 72)[0]
    return info

def get_textures(data, info):
    textures = []
    tex_off = info['textureindex']
    for i in range(info['numtextures']):
        off = tex_off + i * TEX_ENTRY_SIZE
        name = read_cstr(data, off, 64)
        flags = struct.unpack_from('<I', data, off + 64)[0]
        w = struct.unpack_from('<I', data, off + 68)[0]
        h = struct.unpack_from('<I', data, off + 72)[0]
        idx = struct.unpack_from('<I', data, off + 76)[0]
        textures.append({'index': i, 'name': name, 'flags': flags,
                         'width': w, 'height': h, 'data_offset': idx})
    return textures

def read_bmp_texture(bmp_path, target_w, target_h):
    img = Image.open(bmp_path)
    if img.mode == 'P':
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.NEAREST)
        pixels = img.tobytes()
        palette = img.getpalette()
        if palette is None or len(palette) < 768:
            palette = palette + [0] * (768 - len(palette)) if palette else [0] * 768
        palette = bytes(palette[:768])
        return pixels, palette
    else:
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.NEAREST)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        quantized = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        pixels = quantized.tobytes()
        palette = quantized.getpalette()
        if palette is None or len(palette) < 768:
            palette = palette + [0] * (768 - len(palette)) if palette else [0] * 768
        palette = bytes(palette[:768])
        return pixels, palette

def replace_texture_in_mdl(mdl_data, tex_index, bmp_pixels, bmp_palette):
    info = parse_mdl(mdl_data)
    textures = get_textures(mdl_data, info)
    if tex_index < 0 or tex_index >= len(textures):
        raise ValueError(f"Invalid texture index")
    tex = textures[tex_index]
    expected_size = tex['width'] * tex['height']
    if len(bmp_pixels) != expected_size:
        raise ValueError(f"Pixel data size mismatch")
    new_data = bytearray(mdl_data)
    data_off = tex['data_offset']
    new_data[data_off:data_off + expected_size] = bmp_pixels
    new_data[data_off + expected_size:data_off + expected_size + 768] = bmp_palette
    return bytes(new_data)

def scan_skins(tex_folder):
    if tex_folder is None:
        return []
    if tex_folder.startswith("__knife__"):
        knife_type = tex_folder.split("__knife__", 1)[1]
        # classic_t（T方经典刀）的实际文件夹是 classic，只显示 knife_t.bmp
        if knife_type == "classic_t":
            tex_path = os.path.join(KNIEFES_DIR, "classic")
            if not os.path.exists(tex_path):
                return []
            skins = []
            for f in sorted(os.listdir(tex_path)):
                if f.lower() == "knife_t.bmp":
                    name = f[:-4]
                    skins.append((name, os.path.join(tex_path, f)))
            return skins
        # classic_css（CSS刀）的实际文件夹是 classic，显示所有通用贴图（排除 knife_ct 和 knife_t）
        if knife_type == "classic_css":
            tex_path = os.path.join(KNIEFES_DIR, "classic")
            if not os.path.exists(tex_path):
                return []
            skins = []
            for f in sorted(os.listdir(tex_path)):
                if not f.lower().endswith(".bmp"):
                    continue
                if f.lower() in ("knife_ct.bmp", "knife_t.bmp"):
                    continue
                name = f[:-4]
                skins.append((name, os.path.join(tex_path, f)))
            return skins
        tex_path = os.path.join(KNIEFES_DIR, knife_type)
        if not os.path.exists(tex_path):
            return []
        skins = []
        for f in sorted(os.listdir(tex_path)):
            if not f.lower().endswith(".bmp"):
                continue
            # CT classic 刀只显示 knife_ct.bmp
            if knife_type == "classic" and f.lower() != "knife_ct.bmp":
                continue
            name = f[:-4]
            skins.append((name, os.path.join(tex_path, f)))
        return skins
    folders = tex_folder.split('|')
    skins = []
    seen_names = set()
    for folder in folders:
        tex_path = os.path.join(TEXTURES_DIR, folder.strip())
        if not os.path.exists(tex_path):
            continue
        for f in sorted(os.listdir(tex_path)):
            if f.lower().endswith(".bmp"):
                name = f[:-4]
                if name not in seen_names:
                    seen_names.add(name)
                    skins.append((name, os.path.join(tex_path, f)))
    return skins

def scan_glove_skins():
    if not os.path.exists(GLOVES_DIR):
        return []
    skins = []
    for f in sorted(os.listdir(GLOVES_DIR)):
        if f.lower().endswith(".bmp"):
            name = f[:-4]
            skins.append((name, os.path.join(GLOVES_DIR, f)))
    return skins

def scan_stickers():
    if not os.path.exists(STICKERS_DIR):
        return []
    stickers = []
    for capsule in sorted(os.listdir(STICKERS_DIR)):
        capsule_path = os.path.join(STICKERS_DIR, capsule)
        if not os.path.isdir(capsule_path):
            continue
        for f in sorted(os.listdir(capsule_path)):
            if f.lower().endswith(".bmp"):
                name = f[:-4]
                display = f"[{capsule}] {name}"
                stickers.append((display, os.path.join(capsule_path, f)))
    return stickers

def get_deploy_path(dname, mdl_path, tex_folder):
    if tex_folder and tex_folder.startswith("__knife__"):
        return os.path.join(MODELS_DIR, "v_knife.mdl")
    return mdl_path

class SkinToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CS 1.6 换肤工具")
        self.root.geometry("1200x650")
        self.root.minsize(900, 550)
        self.root.resizable(True, True)

        self.weapons = []
        self.current_weapon = None
        self.current_skins = []
        self.glove_skins = []
        self.selected_glove = None
        self.stickers = []
        self.filtered_stickers = []
        self.selected_sticker = None
        self.preview_images = {}
        self.running = False
        self._weapon_index_map = {}

        self.setup_style()
        self.create_widgets()
        self.load_weapons()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('vista' if 'vista' in style.theme_names() else 'clam')
        style.configure('TLabel', font=("Microsoft YaHei", 10))
        style.configure('TButton', font=("Microsoft YaHei", 10))
        style.configure('TRadiobutton', font=("Microsoft YaHei", 10))
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelframe', font=("Microsoft YaHei", 10, "bold"))
        style.configure('Red.TButton', foreground='#cc3333')
        style.configure('Blue.TButton', foreground='#3366cc')

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部标题栏
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 12))

        container = tk.Frame(title_frame, bg='#2c3e50', height=60)
        container.pack(fill=tk.X)
        container.pack_propagate(False)

        tk.Label(container, text="CS 1.6 武器换肤系统", font=("Microsoft YaHei", 18, "bold"),
                 fg="white", bg='#2c3e50').pack(side=tk.LEFT, padx=20, pady=10)
        self.status_label = tk.Label(container, text="就绪",
                                      font=("Microsoft YaHei", 10),
                                      fg="#bdc3c7", bg='#2c3e50')
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # 内容区域
        self.content_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.content_pane.pack(fill=tk.BOTH, expand=True)

        # ========= 左侧: 武器列表 =========
        left_frame = ttk.LabelFrame(self.content_pane, text=" 武器列表 ", padding="8")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 工具栏：一键随机 + 分类筛选
        tab_frame = ttk.Frame(left_frame)
        tab_frame.pack(fill=tk.X, pady=(0, 4))

        ttk.Button(tab_frame, text="一键随机全部",
                   command=self.random_all_skins).pack(side=tk.LEFT, padx=3)

        sep = ttk.Separator(tab_frame, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # 分类筛选
        cat_frame = ttk.Frame(tab_frame)
        cat_frame.pack(side=tk.LEFT, padx=3)
        self.cat_var = tk.StringVar(value="gun")
        for txt, val in [("枪械", "gun"), ("刀", "knife")]:
            ttk.Radiobutton(cat_frame, text=txt, variable=self.cat_var,
                            value=val, command=self.filter_weapons).pack(side=tk.LEFT, padx=2)

        # 武器列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.weapon_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       font=("Consolas", 10), selectmode=tk.SINGLE,
                                       activestyle='none', borderwidth=1,
                                       highlightthickness=0)
        self.weapon_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.weapon_list.yview)
        self.weapon_list.bind('<<ListboxSelect>>', self.on_weapon_select)

        # 进度条（放在左侧底部）
        progress_frame = ttk.Frame(left_frame)
        progress_frame.pack(fill=tk.X, pady=(6, 0))

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                        mode='determinate', length=0)
        self.progress.pack(fill=tk.X, expand=True)

        # 日志区域（移到左侧武器列表下方）
        log_frame = ttk.LabelFrame(left_frame, text=" 操作日志 ", padding="6")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_frame, height=8, font=("Consolas", 9),
                                 state=tk.DISABLED, borderwidth=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        log_scrollbar.config(command=self.log_text.yview)

        # ========= 右侧: 皮肤选择 =========
        right_frame = ttk.LabelFrame(self.content_pane, text=" 皮肤选择 ", padding="8")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 当前武器信息
        info_container = tk.Frame(right_frame, bg='#ecf0f1', highlightbackground='#bdc3c7',
                                   highlightthickness=1, highlightcolor='#bdc3c7')
        info_container.pack(fill=tk.X, pady=(0, 8))

        self.info_text = tk.Text(info_container, height=4, font=("Consolas", 9),
                                  state=tk.DISABLED, wrap=tk.WORD,
                                  bg='#ecf0f1', borderwidth=0)
        self.info_text.pack(fill=tk.X, padx=8, pady=6)

        # 皮肤标签、搜索、应用按钮
        skin_toolbar = ttk.Frame(right_frame)
        skin_toolbar.pack(fill=tk.X)

        self.skin_count_label = tk.Label(skin_toolbar, text="可用皮肤: 0",
                                          font=("Microsoft YaHei", 10, "bold"),
                                          fg="#2c3e50")
        self.skin_count_label.pack(side=tk.LEFT)

        # 应用皮肤按钮（移到搜索框旁边，确保可见）
        self.apply_btn = ttk.Button(skin_toolbar, text="应用皮肤",
                                    command=self.apply_skin, state=tk.DISABLED, width=10)
        self.apply_btn.pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(skin_toolbar, text="随机本武器",
                   command=self.random_one, width=10).pack(side=tk.RIGHT, padx=(3, 0))

        search_frame = ttk.Frame(skin_toolbar)
        search_frame.pack(side=tk.RIGHT)
        tk.Label(search_frame, text="搜索:",
                 font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_skins)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                                       font=("Microsoft YaHei", 9), width=14)
        self.search_entry.pack(side=tk.LEFT)

        # 皮肤列表 + 手套列表（垂直可拖拽分割）
        self.vpane = ttk.PanedWindow(right_frame, orient=tk.VERTICAL)
        self.vpane.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        # -- 皮肤列表（上） --
        skin_pane = ttk.Frame(self.vpane)
        self.vpane.add(skin_pane, weight=3)

        skin_scrollbar = ttk.Scrollbar(skin_pane)
        skin_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.skin_listbox = tk.Listbox(skin_pane, yscrollcommand=skin_scrollbar.set,
                                        font=("Consolas", 10), selectmode=tk.SINGLE,
                                        activestyle='none', borderwidth=1,
                                        highlightthickness=0, exportselection=False)
        self.skin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        skin_scrollbar.config(command=self.skin_listbox.yview)
        self.skin_listbox.bind('<<ListboxSelect>>', self.on_skin_select)
        self.skin_listbox.bind('<Double-Button-1>', lambda e: self.apply_skin())

        # -- 手套皮肤（下） --
        glove_pane = ttk.Frame(self.vpane)
        self.vpane.add(glove_pane, weight=1)

        glove_header = ttk.Frame(glove_pane)
        glove_header.pack(fill=tk.X)
        tk.Label(glove_header, text="手套皮肤", font=("Microsoft YaHei", 10, "bold"),
                 fg="#2c3e50").pack(side=tk.LEFT)
        self.glove_count_label = tk.Label(glove_header, text="0", font=("Microsoft YaHei", 9), fg="#7f8c8d")
        self.glove_count_label.pack(side=tk.LEFT, padx=(4, 0))
        self.glove_clear_btn = tk.Label(glove_header, text=" ✕清除", font=("Microsoft YaHei", 9),
                                         fg="#e74c3c", cursor="hand2")
        self.glove_clear_btn.pack(side=tk.RIGHT, padx=(0, 2))
        self.glove_clear_btn.bind('<Button-1>', lambda e: self.clear_glove())

        self.glove_team_btn = ttk.Button(glove_header, text="一键手套全部",
                                          command=self.apply_glove_to_all, style='Blue.TButton')
        self.glove_team_btn.pack(side=tk.RIGHT, padx=(0, 4))

        glove_scrollbar = ttk.Scrollbar(glove_pane)
        glove_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.glove_listbox = tk.Listbox(glove_pane, yscrollcommand=glove_scrollbar.set,
                                         font=("Consolas", 9), selectmode=tk.SINGLE,
                                         activestyle='none', borderwidth=1,
                                         highlightthickness=0, exportselection=False)
        self.glove_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        glove_scrollbar.config(command=self.glove_listbox.yview)
        self.glove_listbox.bind('<<ListboxSelect>>', self.on_glove_select)

        # -- 贴纸（下） --
        sticker_pane = ttk.Frame(self.vpane)
        self.vpane.add(sticker_pane, weight=1)

        sticker_header = ttk.Frame(sticker_pane)
        sticker_header.pack(fill=tk.X)
        tk.Label(sticker_header, text="贴纸", font=("Microsoft YaHei", 10, "bold"),
                 fg="#2c3e50").pack(side=tk.LEFT)
        self.sticker_count_label = tk.Label(sticker_header, text="0", font=("Microsoft YaHei", 9), fg="#7f8c8d")
        self.sticker_count_label.pack(side=tk.LEFT, padx=(4, 0))

        # 紧凑布局：搜索框 + 通道选择 + 按钮 同一行
        sticker_ctrl_frame = ttk.Frame(sticker_pane)
        sticker_ctrl_frame.pack(fill=tk.X, pady=(2, 0))
        
        # 左侧：搜索框
        sticker_search_frame = ttk.Frame(sticker_ctrl_frame)
        sticker_search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.sticker_search_var = tk.StringVar()
        self.sticker_search_var.trace_add('write', self.filter_stickers)
        ttk.Entry(sticker_search_frame, textvariable=self.sticker_search_var,
                  font=("Microsoft YaHei", 8), width=15).pack(fill=tk.X)
        
        # 中间：通道选择
        decal_frame = ttk.Frame(sticker_ctrl_frame)
        decal_frame.pack(side=tk.LEFT, padx=(0, 4))
        tk.Label(decal_frame, text="通道:", font=("Microsoft YaHei", 8), fg="#555").pack(side=tk.LEFT)
        self.decal_var_a = tk.BooleanVar(value=True)
        self.decal_var_b = tk.BooleanVar(value=True)
        self.decal_var_c = tk.BooleanVar(value=True)
        self.decal_var_d = tk.BooleanVar(value=True)
        for ch, var in [("A", self.decal_var_a), ("B", self.decal_var_b),
                        ("C", self.decal_var_c), ("D", self.decal_var_d)]:
            ttk.Checkbutton(decal_frame, text=ch, variable=var,
                           style='Toolbutton').pack(side=tk.LEFT, padx=0)
        
        # 右侧：按钮
        sticker_btn_frame = ttk.Frame(sticker_ctrl_frame)
        sticker_btn_frame.pack(side=tk.RIGHT)
        ttk.Button(sticker_btn_frame, text="应用到当前",
                   command=self.apply_sticker_to_current, width=9).pack(side=tk.LEFT, padx=2)
        ttk.Button(sticker_btn_frame, text="随机全部",
                   command=self.random_stickers_to_all, style='Blue.TButton', width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(sticker_btn_frame, text="全清透明",
                   command=self.clear_stickers_on_current, style='Red.TButton', width=8).pack(side=tk.LEFT, padx=2)

        sticker_list_frame = ttk.Frame(sticker_pane)
        sticker_list_frame.pack(fill=tk.BOTH, expand=True)

        sticker_scrollbar = ttk.Scrollbar(sticker_list_frame)
        sticker_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.sticker_listbox = tk.Listbox(sticker_list_frame, yscrollcommand=sticker_scrollbar.set,
                                           font=("Consolas", 8), selectmode=tk.SINGLE,
                                           activestyle='none', borderwidth=1,
                                           highlightthickness=0, exportselection=False)
        self.sticker_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sticker_scrollbar.config(command=self.sticker_listbox.yview)
        self.sticker_listbox.bind('<<ListboxSelect>>', self.on_sticker_select)

        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # 延迟设置分割位置，确保组件完全初始化（兼容Tcl 9）
        self.root.after(100, self._set_sash_position)
    
    def _set_sash_position(self):
        try:
            self.content_pane.sash_place(0, 280, 0)
            # 垂直分割：皮肤列表高度约220px，给按钮留出空间
            self.vpane.sash_place(0, 0, 220)
        except Exception:
            pass

    def log(self, msg):
        def _log():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _log)

    def set_status(self, msg, color=None):
        def _set():
            self.status_label.config(text=msg)
            if color:
                self.status_label.config(fg=color)
            else:
                self.status_label.config(fg="#bdc3c7")
            self.root.update_idletasks()
        self.root.after(0, _set)

    def load_weapons(self):
        self.log("加载武器模型...")
        self.weapons = []
        skip_patterns = ['test', 'copy']

        def should_skip(name):
            for p in skip_patterns:
                if p in name.lower():
                    return True
            return False

        # 枪械：从 models/ 根目录加载（游戏读取位置）
        if os.path.exists(MODELS_DIR):
            for f in sorted(os.listdir(MODELS_DIR)):
                if (f.startswith("v_") and f.endswith(".mdl") and not should_skip(f)
                    and f not in EXCLUDE_WEAPONS):
                    mdl_path = os.path.join(MODELS_DIR, f)
                    if f in WEAPON_MAP:
                        name, tex_folder = WEAPON_MAP[f]
                        tex_label = tex_folder.replace("|", " + ") if tex_folder else "无贴图"
                        self.weapons.append((f, name, mdl_path, tex_folder, tex_label))
                    else:
                        self.weapons.append((f, f.replace('v_','').replace('.mdl','').upper(), mdl_path, None, "未知"))

        # CSGO刀（20把）：来自 ct_knife/，需部署到 models/v_knife.mdl
        ct_knife_dir = os.path.join(MODELS_DIR, "ct_knife")
        if os.path.exists(ct_knife_dir):
            for disp_name, ct_fld, tex_sub in KNIFE_ENTRIES:
                mdl_path = os.path.join(ct_knife_dir, ct_fld, "v_knife.mdl")
                if os.path.exists(mdl_path):
                    tex_folder = f"__knife__{tex_sub}"
                    self.weapons.append(("v_knife.mdl", disp_name, mdl_path, tex_folder, disp_name))

        self.log(f"找到 {len(self.weapons)} 个武器模型")
        self.filter_weapons()

    def filter_weapons(self):
        self.weapon_list.delete(0, tk.END)
        cat = self.cat_var.get()
        self._weapon_index_map = {}

        for i, (fname, dname, path, tex_folder, tex_label) in enumerate(self.weapons):
            # 分类筛选
            is_knife = tex_folder and tex_folder.startswith("__knife__")
            is_gun = not is_knife
            if cat == 'gun' and not is_gun:
                continue
            if cat == 'knife' and not is_knife:
                continue

            size = os.path.getsize(path) // 1024
            display = f"  {dname:18s} {size:4d}KB"
            self.weapon_list.insert(tk.END, display)
            self._weapon_index_map[self.weapon_list.size() - 1] = i

    def get_selected_weapon_index(self):
        sel = self.weapon_list.curselection()
        if not sel:
            return None
        return self._weapon_index_map.get(sel[0])

    def on_weapon_select(self, event):
        w_idx = self.get_selected_weapon_index()
        if w_idx is None or w_idx >= len(self.weapons):
            return

        weapon = self.weapons[w_idx]
        fname, dname, mdl_path, tex_folder, tex_label = weapon
        self.current_weapon = weapon

        # 显示信息
        try:
            with open(mdl_path, 'rb') as f:
                data = f.read()
            info = parse_mdl(data)
            textures = get_textures(data, info)
            size = len(data) // 1024

            tex_info = []
            for t in textures:
                tex_info.append(f"  [{t['index']}] {t['name']} ({t['width']}x{t['height']})")

            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete('1.0', tk.END)
            self.info_text.insert(tk.END, f"武器: {dname}  贴图: {tex_label}  大小: {size}KB\n")
            for ti in tex_info:
                self.info_text.insert(tk.END, ti + "\n")
            self.info_text.config(state=tk.DISABLED)
        except Exception as e:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete('1.0', tk.END)
            self.info_text.insert(tk.END, f"武器: {dname}\n读取错误: {e}")
            self.info_text.config(state=tk.DISABLED)

        # 加载皮肤列表
        self.current_skins = scan_skins(tex_folder)
        self.skin_count_label.config(text=f"可用皮肤: {len(self.current_skins)}")
        self.filter_skins()

        # 加载手套皮肤
        if not self.glove_skins:
            self.glove_skins = scan_glove_skins()
            self.glove_count_label.config(text=str(len(self.glove_skins)))
            self.glove_listbox.delete(0, tk.END)
            for name, path in self.glove_skins:
                try:
                    size = os.path.getsize(path) // 1024
                except:
                    size = 0
                self.glove_listbox.insert(tk.END, f"  {name:30s}  ({size}KB)")

        # 加载贴纸
        if not self.stickers:
            self.stickers = scan_stickers()
            self.sticker_count_label.config(text=str(len(self.stickers)))
            self.filter_stickers()

    def filter_skins(self, *args):
        self.skin_listbox.delete(0, tk.END)
        query = self.search_var.get().lower()
        for name, path in self.current_skins:
            if query and query not in name.lower():
                continue
            try:
                size = os.path.getsize(path) // 1024
            except:
                size = 0
            self.skin_listbox.insert(tk.END, f"  {name:30s}  ({size}KB)")

    def on_skin_select(self, event):
        has_skin = bool(self.skin_listbox.curselection())
        has_glove = self.selected_glove is not None
        self.apply_btn.config(state=tk.NORMAL if (has_skin or has_glove) else tk.DISABLED)

    def on_glove_select(self, event):
        sel = self.glove_listbox.curselection()
        if sel:
            self.selected_glove = self.glove_skins[sel[0]]
        has_skin = bool(self.skin_listbox.curselection())
        self.apply_btn.config(state=tk.NORMAL if (has_skin or self.selected_glove) else tk.DISABLED)

    def clear_glove(self):
        self.selected_glove = None
        self.glove_listbox.selection_clear(0, tk.END)
        # 如果武器无皮肤且无选中手套，检查皮肤列表是否有选中
        if self.current_weapon:
            fname, dname, mdl_path, tex_folder, tex_label = self.current_weapon
            if tex_folder is None:
                self.apply_btn.config(state=tk.DISABLED)
            elif not self.skin_listbox.curselection():
                self.apply_btn.config(state=tk.DISABLED)

    def apply_glove_to_all(self):
        if not self.selected_glove:
            messagebox.showwarning("提示", "请先在手套列表中选一个手套皮肤")
            return
        if self.running:
            return
        reply = messagebox.askyesno("确认", "将手套应用到所有武器?\n原文件将被直接覆盖!")
        if not reply:
            return

        self.running = True
        glove_name, glove_path = self.selected_glove

        def do_apply():
            # 手套直接在源文件上改，不部署（部署是换刀型时才需要）
            targets = [(dname, mdl_path) for fname, dname, mdl_path, tex_folder, tex_label in self.weapons]

            # 默认原始刀也应用手套（无论是否已被覆盖）
            knife_path = os.path.join(MODELS_DIR, "v_knife.mdl")
            if os.path.exists(knife_path):
                targets.append(("原始刀", knife_path))

            total = len(targets)
            success = 0
            self.progress_var.set(0)
            self.progress.config(maximum=total)

            for idx, (dname, mdl_path) in enumerate(targets):
                if not self.running:
                    break
                self.set_status(f"[{idx+1}/{total}] {dname}")
                try:
                    with open(mdl_path, 'rb') as f:
                        data = f.read()
                    info = parse_mdl(data)
                    textures = get_textures(data, info)
                    new_data = bytearray(data)
                    has_glove = False
                    for t in textures:
                        if 'glove' in t['name'].lower():
                            gp, gpal = read_bmp_texture(glove_path, t['width'], t['height'])
                            new_data = replace_texture_in_mdl(bytes(new_data), t['index'], gp, gpal)
                            new_data = bytearray(new_data)
                            has_glove = True
                    if has_glove:
                        with open(mdl_path, 'wb') as f:
                            f.write(bytes(new_data))
                        self.log(f"  ✅ [{idx+1}/{total}] {dname} -> 手套:{glove_name}")
                        success += 1
                    else:
                        self.log(f"  ⏭ [{idx+1}/{total}] {dname} -> 无手套纹理")
                except Exception as e:
                    self.log(f"  ❌ [{idx+1}/{total}] {dname} -> {e}")
                self.progress_var.set(idx + 1)

            self.running = False
            self.log(f"\n{'='*50}")
            self.log(f"完成! 成功: {success}, 共: {total}")
            self.log(f"{'='*50}")
            self.set_status("手套应用完成!")
            self.root.after(0, lambda: messagebox.showinfo("完成",
                f"一键手套全部完成!\n成功: {success}\n共: {total}"))

        threading.Thread(target=do_apply, daemon=True).start()

    def get_selected_skin(self):
        sel = self.skin_listbox.curselection()
        if not sel:
            return None
        # 从搜索后的列表中匹配
        query = self.search_var.get().lower()
        visible = [(name, path) for name, path in self.current_skins
                   if not query or query in name.lower()]
        if sel[0] < len(visible):
            return visible[sel[0]]
        return None

    def apply_skin(self, silent=False):
        if self.current_weapon is None:
            return
        skin = self.get_selected_skin()
        if skin is None and not self.selected_glove:
            return

        fname, dname, mdl_path, tex_folder, tex_label = self.current_weapon

        # CSGO刀：自动部署到游戏位置（silent模式不弹窗）
        if tex_folder and tex_folder.startswith("__knife__"):
            if not silent:
                reply = messagebox.askyesno("刀型部署提示",
                    f"「{dname}」是一把CSGO刀型，应用时将自动：\n"
                    f"① 把该刀MDL复制到游戏读取位置\n"
                    f"② 再注入皮肤贴图\n\n"
                    f"继续吗？")
                if not reply:
                    return

        skin_name = None
        skin_path = None
        if skin:
            skin_name, skin_path = skin

        def do_apply():
            nonlocal skin_name
            try:
                # CSGO刀：先部署到游戏位置
                deploy_path = get_deploy_path(dname, mdl_path, tex_folder)
                if deploy_path != mdl_path:
                    with open(mdl_path, 'rb') as f:
                        src_data = f.read()
                    with open(deploy_path, 'wb') as f:
                        f.write(src_data)
                    actual_path = deploy_path
                else:
                    actual_path = mdl_path

                with open(actual_path, 'rb') as f:
                    orig_data = f.read()

                info = parse_mdl(orig_data)
                textures = get_textures(orig_data, info)
                new_data = bytearray(orig_data)

                # 替换枪身贴图
                if skin_path:
                    tex_idx = -1
                    skip_keywords = ['arm', 'hand', 'glove', 'sleeve', 'finger', 'scope', 'shell',
                                     'decal', 'glass', 'watch', 'gold', 'ziel', 'gwiazd', 'switch']
                    for i, t in enumerate(textures):
                        name_lower = t['name'].lower()
                        is_skin = (all(k not in name_lower for k in skip_keywords)
                                   and t['width'] >= 128 and t['height'] >= 128)
                        if is_skin:
                            tex_idx = i
                    if tex_idx == -1:
                        tex_idx = len(textures) - 1

                    target_tex = textures[tex_idx]
                    bmp_pixels, bmp_palette = read_bmp_texture(skin_path, target_tex['width'], target_tex['height'])
                    new_data = replace_texture_in_mdl(bytes(new_data), tex_idx, bmp_pixels, bmp_palette)
                    new_data = bytearray(new_data)
                    # chrome 反光通道：用同样的刀皮缩小后替换
                    for t in textures:
                        if 'chrome' in t['name'].lower():
                            cp, cpal = read_bmp_texture(skin_path, t['width'], t['height'])
                            new_data = replace_texture_in_mdl(bytes(new_data), t['index'], cp, cpal)
                            new_data = bytearray(new_data)
                            break

                # 替换手套纹理
                if self.selected_glove:
                    glove_name, glove_path = self.selected_glove
                    for t in textures:
                        if 'glove' in t['name'].lower():
                            gp, gpal = read_bmp_texture(glove_path, t['width'], t['height'])
                            new_data = replace_texture_in_mdl(bytes(new_data), t['index'], gp, gpal)
                            new_data = bytearray(new_data)

                with open(actual_path, 'wb') as f:
                    f.write(bytes(new_data))
                out_size = len(new_data) // 1024
                parts = [dname]
                if skin_name:
                    parts.append(skin_name)
                if self.selected_glove:
                    parts.append(f"手套:{glove_name}")
                self.log(f"✅ {' -> '.join(parts)} ({out_size}KB)")
                self.set_status(f"已应用: {skin_name or '只换手套'}")
            except Exception as e:
                self.log(f"❌ {dname} 错误: {e}")
                self.set_status("失败!")

        threading.Thread(target=do_apply, daemon=True).start()

    def random_one(self):
        if self.current_weapon is None:
            return
        skins = self.current_skins
        if not skins:
            return
        skin = random.choice(skins)
        # 在列表中选中它
        query = self.search_var.get().lower()
        visible = [(name, path) for name, path in skins
                   if not query or query in name.lower()]
        for i, (name, path) in enumerate(visible):
            if name == skin[0]:
                self.skin_listbox.selection_clear(0, tk.END)
                self.skin_listbox.selection_set(i)
                self.skin_listbox.see(i)
                self.apply_btn.config(state=tk.NORMAL)
                break
        self.apply_skin(silent=True)

    def random_all_skins(self):
        if self.running:
            return
        reply = messagebox.askyesno("确认", "一键随机所有武器的皮肤?\n原文件将被直接覆盖!")
        if not reply:
            return

        self.running = True

        # 确保手套列表已加载
        if not self.glove_skins:
            self.glove_skins = scan_glove_skins()

        def do_random_all():
            # 构建完整武器列表：self.weapons + 默认原始刀
            weapons = list(self.weapons)
            seen = {mdl_path for _, _, mdl_path, _, _ in weapons}

            # 添加默认原始刀（无皮肤贴图但需要手套）
            default_knife = os.path.join(MODELS_DIR, "v_knife.mdl")
            if os.path.exists(default_knife) and default_knife not in seen:
                weapons.append(("v_knife.mdl", "原始刀", default_knife, None, "无贴图"))

            total = len(weapons)
            success = 0
            skipped = 0

            self.progress_var.set(0)
            self.progress.config(maximum=total)

            for idx, (fname, dname, mdl_path, tex_folder, tex_label) in enumerate(weapons):
                if not self.running:
                    break

                self.set_status(f"[{idx+1}/{total}] {dname}")

                # 如果没有皮肤也没有手套，跳过
                if tex_folder is None and not self.glove_skins:
                    self.log(f"  ⏭ [{idx+1}] {dname} -> 跳过(无贴图)")
                    skipped += 1
                    self.progress_var.set(idx + 1)
                    continue

                try:
                    # CSGO刀不部署：直接改 ct_knife/ 下的源文件
                    no_deploy = bool(tex_folder and tex_folder.startswith('__knife__'))

                    if no_deploy:
                        actual_path = mdl_path
                    else:
                        deploy_path = get_deploy_path(dname, mdl_path, tex_folder)
                        if deploy_path != mdl_path:
                            with open(mdl_path, 'rb') as f:
                                src_data = f.read()
                            with open(deploy_path, 'wb') as f:
                                f.write(src_data)
                            actual_path = deploy_path
                        else:
                            actual_path = mdl_path

                    with open(actual_path, 'rb') as f:
                        orig_data = f.read()
                    info = parse_mdl(orig_data)
                    textures = get_textures(orig_data, info)
                    new_data = bytearray(orig_data)

                    skin_name = None
                    # 有皮肤目录才应用皮肤
                    if tex_folder:
                        skins = scan_skins(tex_folder)
                        if skins:
                            skin = random.choice(skins)
                            skin_name, skin_path = skin

                            tex_idx = -1
                            skip_keywords = ['arm', 'hand', 'glove', 'sleeve', 'finger', 'scope', 'shell',
                                             'decal', 'glass', 'watch', 'gold', 'ziel', 'gwiazd', 'switch']
                            for i, t in enumerate(textures):
                                name_lower = t['name'].lower()
                                is_skin = (all(k not in name_lower for k in skip_keywords)
                                           and t['width'] >= 128 and t['height'] >= 128)
                                if is_skin:
                                    tex_idx = i
                            if tex_idx == -1:
                                tex_idx = len(textures) - 1

                            target_tex = textures[tex_idx]
                            bmp_pixels, bmp_palette = read_bmp_texture(skin_path, target_tex['width'], target_tex['height'])
                            new_data = replace_texture_in_mdl(bytes(new_data), tex_idx, bmp_pixels, bmp_palette)
                            new_data = bytearray(new_data)
                            # chrome 反光通道：用同样的刀皮缩小后替换
                            for t in textures:
                                if 'chrome' in t['name'].lower():
                                    cp, cpal = read_bmp_texture(skin_path, t['width'], t['height'])
                                    new_data = replace_texture_in_mdl(bytes(new_data), t['index'], cp, cpal)
                                    new_data = bytearray(new_data)
                                    break

                    # 随机选一个手套皮肤
                    gname = None
                    if self.glove_skins:
                        gskin = random.choice(self.glove_skins)
                        gname, gpath = gskin
                        for t in textures:
                            if 'glove' in t['name'].lower():
                                gp, gpal = read_bmp_texture(gpath, t['width'], t['height'])
                                new_data = replace_texture_in_mdl(bytes(new_data), t['index'], gp, gpal)
                                new_data = bytearray(new_data)

                    # 写回修改后的数据
                    with open(actual_path, 'wb') as f:
                        f.write(bytes(new_data))
                    # 如果是需要部署的武器，也写回源文件
                    if not no_deploy and deploy_path != mdl_path:
                        try:
                            with open(mdl_path, 'wb') as f:
                                f.write(bytes(new_data))
                        except Exception:
                            pass
                    parts = [dname]
                    if skin_name:
                        parts.append(skin_name)
                    if gname:
                        parts.append(f"手套:{gname}")
                    self.log(f"  ✅ [{idx+1}/{total}] {' -> '.join(parts)}")
                    success += 1
                except Exception as e:
                    self.log(f"  ❌ [{idx+1}/{total}] {dname} -> {e}")

                self.progress_var.set(idx + 1)

            self.running = False
            self.log(f"\n{'='*50}")
            self.log(f"完成! 成功: {success}, 跳过: {skipped}, 共: {total}")
            self.log(f"{'='*50}")
            self.set_status("全部完成!")
            self.root.after(0, lambda: messagebox.showinfo("完成",
                f"一键随机皮肤完成!\n成功: {success}\n跳过: {skipped}\n共: {total}"))

        threading.Thread(target=do_random_all, daemon=True).start()

    def filter_stickers(self, *args):
        self.sticker_listbox.delete(0, tk.END)
        query = self.sticker_search_var.get().lower()
        self.filtered_stickers = []
        for display, path in self.stickers:
            if query and query not in display.lower():
                continue
            self.filtered_stickers.append((display, path))
            self.sticker_listbox.insert(tk.END, f"  {display}")

    def on_sticker_select(self, event):
        sel = self.sticker_listbox.curselection()
        if sel and sel[0] < len(self.filtered_stickers):
            self.selected_sticker = self.filtered_stickers[sel[0]]

    def _apply_stickers_to_mdl(self, mdl_data, sticker_path, channels):
        info = parse_mdl(mdl_data)
        textures = get_textures(mdl_data, info)
        new_data = bytearray(mdl_data)
        for t in textures:
            name_lower = t['name'].lower().replace('.bmp', '').replace('.tga', '')
            for ch in channels:
                if name_lower in (f'decal_{ch}', f'decal{ch}'):
                    sp, spal = read_bmp_texture(sticker_path, t['width'], t['height'])
                    new_data = replace_texture_in_mdl(bytes(new_data), t['index'], sp, spal)
                    new_data = bytearray(new_data)
                    break
        return bytes(new_data)

    def apply_sticker_to_current(self):
        if self.current_weapon is None:
            return
        sel = self.sticker_listbox.curselection()
        if not sel or sel[0] >= len(self.filtered_stickers):
            messagebox.showwarning("提示", "请先选一个贴纸")
            return
        channels = []
        if self.decal_var_a.get(): channels.append('a')
        if self.decal_var_b.get(): channels.append('b')
        if self.decal_var_c.get(): channels.append('c')
        if self.decal_var_d.get(): channels.append('d')
        if not channels:
            messagebox.showwarning("提示", "请至少选一个贴纸通道(A/B/C/D)")
            return
        sticker_display, sticker_path = self.filtered_stickers[sel[0]]
        fname, dname, mdl_path, tex_folder, tex_label = self.current_weapon
        # 检查是否有decal通道
        is_knife = tex_folder and tex_folder.startswith('__knife__')
        is_grenade = fname in ("v_c4.mdl", "v_flashbang.mdl", "v_hegrenade.mdl", "v_smokegrenade.mdl")
        if is_knife or is_grenade:
            messagebox.showwarning("提示", f"当前武器({dname})没有贴花通道，不支持贴纸替换")
            return
        ch_str = ''.join(channels).upper()

        def do_apply():
            try:
                deploy_path = get_deploy_path(dname, mdl_path, tex_folder)
                if deploy_path != mdl_path:
                    with open(mdl_path, 'rb') as f:
                        src_data = f.read()
                    with open(deploy_path, 'wb') as f:
                        f.write(src_data)
                    actual_path = deploy_path
                else:
                    actual_path = mdl_path
                with open(actual_path, 'rb') as f:
                    orig_data = f.read()
                new_data = self._apply_stickers_to_mdl(orig_data, sticker_path, channels)
                with open(actual_path, 'wb') as f:
                    f.write(new_data)
                self.log(f"✅ {dname} -> 贴纸 [通道{ch_str}]")
                self.set_status(f"贴纸已应用: 通道{ch_str}")
            except Exception as e:
                self.log(f"❌ {dname} 贴纸错误: {e}")
                self.set_status("贴纸失败!")

        threading.Thread(target=do_apply, daemon=True).start()

    def clear_stickers_on_current(self):
        """一键把当前武器所有 decal_a/b/c/d 通道全部替换为透明 BMP"""
        if self.current_weapon is None:
            messagebox.showwarning("提示", "请先在左侧选一把武器")
            return

        fname, dname, mdl_path, tex_folder, tex_label = self.current_weapon

        # 刀、手雷、C4 没有 decal 通道
        is_knife = tex_folder and tex_folder.startswith('__knife__')
        is_grenade = fname in ("v_c4.mdl", "v_flashbang.mdl", "v_hegrenade.mdl", "v_smokegrenade.mdl")
        if is_knife or is_grenade:
            messagebox.showwarning("提示", f"当前武器({dname})没有贴花通道")
            return

        # 透明 BMP 路径 — 相对路径,放在贴纸资源包根目录
        transparent_bmp = os.path.join(STICKERS_DIR, "transparent_sticker.bmp")
        if not os.path.exists(transparent_bmp):
            messagebox.showerror("错误",
                f"找不到透明贴纸 BMP:\n{transparent_bmp}\n\n"
                f"请把 transparent_sticker.bmp 放到贴纸目录下")
            return

        def do_clear():
            try:
                deploy_path = get_deploy_path(dname, mdl_path, tex_folder)
                if deploy_path != mdl_path:
                    # 半指手套/全手套刀：先把 v_xxx.mdl 复制到 v_knife.mdl
                    with open(mdl_path, 'rb') as f:
                        src_data = f.read()
                    with open(deploy_path, 'wb') as f:
                        f.write(src_data)
                    actual_path = deploy_path
                else:
                    actual_path = mdl_path

                with open(actual_path, 'rb') as f:
                    orig_data = f.read()

                # 四个通道全部用透明 BMP
                channels = ['a', 'b', 'c', 'd']
                new_data = self._apply_stickers_to_mdl(orig_data, transparent_bmp, channels)

                with open(actual_path, 'wb') as f:
                    f.write(new_data)

                self.log(f"🧹 {dname} -> 所有贴纸通道已清空 (透明)")
                self.set_status(f"{dname} 贴纸已全部清空")
            except Exception as e:
                self.log(f"❌ {dname} 清空贴纸错误: {e}")
                self.set_status("清空贴纸失败!")

        threading.Thread(target=do_clear, daemon=True).start()

    def random_stickers_to_all(self):
        if not self.stickers:
            self.stickers = scan_stickers()
            if not self.stickers:
                messagebox.showwarning("提示", "没有找到贴纸资源")
                return
        channels = ['a', 'b', 'c', 'd']
        targets = []
        for fname, dname, mdl_path, tex_folder, tex_label in self.weapons:
            # 只处理真正的枪械：排除刀、手雷、C4（没有decal贴花通道）
            is_knife = tex_folder and tex_folder.startswith('__knife__')
            is_grenade = fname in ("v_c4.mdl", "v_flashbang.mdl", "v_hegrenade.mdl", "v_smokegrenade.mdl")
            if is_knife or is_grenade:
                continue
            deploy_path = get_deploy_path(dname, mdl_path, tex_folder)
            targets.append((dname, mdl_path, deploy_path))
        if not targets:
            messagebox.showwarning("提示", "没有可贴纸的武器")
            return
        reply = messagebox.askyesno("确认",
            f"将为 {len(targets)} 个武器随机分配贴纸(ABCD四通道)?\n原文件将被直接覆盖!")
        if not reply:
            return
        self.running = True

        def do_random():
            total = len(targets)
            success = 0
            self.progress_var.set(0)
            self.progress.config(maximum=total)
            for idx, (dname, src_path, actual_path) in enumerate(targets):
                if not self.running:
                    break
                self.set_status(f"[{idx+1}/{total}] {dname}")
                try:
                    if src_path != actual_path:
                        with open(src_path, 'rb') as f:
                            src_data = f.read()
                        with open(actual_path, 'wb') as f:
                            f.write(src_data)
                    with open(actual_path, 'rb') as f:
                        orig_data = f.read()
                    new_data = bytearray(orig_data)
                    for ch in channels:
                        sticker = random.choice(self.stickers)
                        _, sticker_path = sticker
                        new_data = self._apply_stickers_to_mdl(bytes(new_data), sticker_path, [ch])
                        new_data = bytearray(new_data)
                    with open(actual_path, 'wb') as f:
                        f.write(bytes(new_data))
                    self.log(f"  ✅ [{idx+1}/{total}] {dname} -> 随机贴纸x4")
                    success += 1
                except Exception as e:
                    self.log(f"  ❌ [{idx+1}/{total}] {dname} -> {e}")
                self.progress_var.set(idx + 1)
            self.running = False
            self.log(f"\n{'='*50}")
            self.log(f"贴纸随机完成! 成功: {success}, 共: {total}")
            self.log(f"{'='*50}")
            self.set_status("贴纸随机完成!")
            self.root.after(0, lambda: messagebox.showinfo("完成",
                f"贴纸随机完成!\n成功: {success}\n共: {total}"))

        threading.Thread(target=do_random, daemon=True).start()

def main():
    try:
        root = tk.Tk()
        app = SkinToolGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        with open(os.path.join(BASE_DIR, 'cs_skin_error.log'), 'w') as f:
            f.write(f"Error: {e}\n{traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main()
