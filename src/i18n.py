# -*- coding: utf-8 -*-
"""
i18n.py — 中英双语字典与切换机制
=================================

用法::

    from i18n import t, set_lang, get_lang

    set_lang("en")
    label.config(text=t("apply_skin"))

字典里的每个键都有 zh / en 两种翻译。缺 en 时回退到 zh 并在 stderr 提示，
所以新增文案时不会静默漏译。
"""
import sys

# 当前语言：zh / en
_LANG = "zh"

# 简体 / English
LANG_LABELS = {
    "zh": "简体中文",
    "en": "English",
}

# ---------------------------------------------------------------- 字典
# key: 中文值, value: 英文值
STRINGS = {
    # ---- 窗口 / 标题 ----
    "app_title":        ("CS 1.6 换肤工具",                    "CS 1.6 Skin Tool"),
    "header_title":     ("CS 1.6 武器换肤系统",                "CS 1.6 Weapon Skin System"),
    "ready":            ("就绪",                              "Ready"),

    # ---- 左侧：武器列表 ----
    "weapon_list":      ("武器列表",                          "Weapons"),
    "randomize_all":    ("一键随机全部",                      "Randomize All"),
    "cat_gun":          ("枪械",                              "Firearm"),
    "cat_knife":        ("刀",                                "Knife"),
    "log_panel":        ("操作日志",                          "Log"),

    # ---- 右侧：皮肤选择 ----
    "skin_select":      ("皮肤选择",                          "Skin"),
    "avail_skins":      ("可用皮肤: {n}",                     "Available skins: {n}"),
    "apply_skin":       ("应用皮肤",                          "Apply"),
    "random_weapon":    ("随机本武器",                        "Randomize This"),
    "search":           ("搜索:",                             "Search:"),

    # ---- 手套 ----
    "glove_skins":      ("手套皮肤",                          "Glove skins"),
    "clear":            ("清除",                              "Clear"),
    "randomize_gloves": ("一键手套全部",                      "Randomize All Gloves"),
    "glove_missing":    ("请先在手套列表中选一个手套皮肤",    "Select a glove skin first"),
    "glove_confirm":    ("将手套应用到所有武器?\n原文件将被直接覆盖!",
                          "Apply this glove to all weapons?\nOriginal files will be overwritten!"),
    "glove_no_tex":     ("无手套纹理",                        "no glove texture"),
    "glove_apply_ok":   ("手套应用完成!",                     "Gloves applied!"),
    "glove_done_all":   ("一键手套全部完成!\n成功: {ok}\n共: {total}",
                          "Randomize All Gloves done!\nSucceeded: {ok}\nTotal: {total}"),

    # ---- 贴纸 ----
    "stickers":         ("贴纸",                              "Stickers"),
    "channel":          ("通道:",                             "Channel:"),
    "apply_current":    ("应用到当前",                        "Apply to Current"),
    "randomize_all_ch": ("随机全部",                          "Randomize All"),
    "clear_transparent":("全清透明",                          "Clear All (Transparent)"),
    "sticker_missing":  ("请先选一个贴纸",                    "Select a sticker first"),
    "sticker_no_ch":    ("请至少选一个贴纸通道(A/B/C/D)",     "Select at least one sticker channel (A/B/C/D)"),
    "sticker_unsupported": ("当前武器({name})没有贴花通道，不支持贴纸替换",
                          "Current weapon ({name}) has no decal channel; stickers are unsupported"),
    "sticker_ok":       ("贴纸已应用: 通道{ch}",              "Sticker applied: channel {ch}"),
    "sticker_fail":     ("贴纸失败!",                         "Sticker failed!"),
    "sticker_random_done": ("贴纸随机完成! 成功: {ok}, 共: {total}",
                          "Sticker randomization done! Succeeded: {ok}, Total: {total}"),
    "sticker_random_all": ("贴纸随机完成!",                   "Sticker randomization done!"),
    "sticker_not_found": ("没有找到贴纸资源",                 "No sticker assets found"),
    "sticker_no_weapon": ("没有可贴纸的武器",                 "No weapons support stickers"),
    "sticker_confirm":  ("将为 {n} 个武器随机分配贴纸(ABCD四通道)?\n原文件将被直接覆盖!",
                          "Assign random stickers to {n} weapons (all 4 channels)?\nOriginal files will be overwritten!"),
    "sticker_random_all_done": ("贴纸随机完成!\n成功: {ok}\n共: {total}",
                          "Sticker randomization done!\nSucceeded: {ok}\nTotal: {total}"),
    "clear_transparent_hint": ("一键把当前武器所有 decal_a/b/c/d 通道全部替换为透明 BMP",
                          "Replace every decal_a/b/c/d channel of the current weapon with a transparent BMP"),
    "sticker_bmp_missing": ("找不到透明贴纸 BMP:\n{path}\n\n请把 transparent_sticker.bmp 放到贴纸目录下",
                          "Transparent sticker BMP not found:\n{path}\n\nPlease put transparent_sticker.bmp in the sticker directory"),
    "sticker_cleared":  ("{name} 贴纸已全部清空",             "All stickers cleared on {name}"),

    # ---- 状态 / 日志 ----
    "loading_models":   ("加载武器模型...",                    "Loading weapon models..."),
    "no_texture":       ("无贴图",                            "no texture"),
    "unknown":          ("未知",                              "Unknown"),
    "found_models":     ("找到 {n} 个武器模型",               "Found {n} weapon models"),
    "info_line":        ("武器: {dname}\n贴图: {tex}\n大小: {size}KB",
                          "Weapon: {dname}\nTexture: {tex}\nSize: {size}KB"),
    "read_error":       ("武器: {dname}\n读取错误: {e}",        "Weapon: {dname}\nRead error: {e}"),
    "applied":          ("已应用: {name}",                    "Applied: {name}"),
    "apply_failed":     ("失败!",                              "Failed!"),
    "random_all_confirm": ("一键随机所有武器的皮肤?\n原文件将被直接覆盖!",
                          "Randomize the skin of every weapon?\nOriginal files will be overwritten!"),
    "random_done":      ("完成! 成功: {ok}, 跳过: {skip}, 共: {total}",
                          "Done! Succeeded: {ok}, Skipped: {skip}, Total: {total}"),
    "random_all_done":  ("全部完成!",                          "All done!"),

    # ---- 原始刀 ----
    "original_knife":   ("原始刀",                            "Original knife"),

    "random_done_all":  ("一键随机皮肤完成!\n成功: {ok}\n跳过: {skip}\n共: {total}",
                          "Randomize All Skins done!\nSucceeded: {ok}\nSkipped: {skip}\nTotal: {total}"),
    "skip_no_tex":      ("跳过(无贴图)",                        "skipped (no texture)"),
    "glove_colon":      ("手套:{name}",                        "glove: {name}"),
    "glove_only":       ("只换手套",                            "gloves only"),
    "error_colon":      ("错误: {e}",                          "error: {e}"),

    # ---- 贴纸补充 ----
    "sticker_ch":       ("贴纸 [通道{ch}]",                    "sticker [channel {ch}]"),
    "sticker_error":    ("贴纸错误: {e}",                      "sticker error: {e}"),
    "sticker_no_decal": ("当前武器({name})没有贴花通道",       "Current weapon ({name}) has no decal channel"),
    "sticker_cleared_log": ("所有贴纸通道已清空 (透明)",        "all sticker channels cleared (transparent)"),
    "clear_sticker_error": ("清空贴纸错误: {e}",                "clear sticker error: {e}"),
    "clear_sticker_fail": ("清空贴纸失败!",                    "Failed to clear stickers!"),
    "sticker_random_log": ("随机贴纸x4",                        "4 random stickers"),
    "sticker_random_done": ("贴纸随机完成! 成功: {ok}, 共: {total}",
                          "Sticker randomization done! Succeeded: {ok}, Total: {total}"),

    # ---- 语言 ----
    "lang_switched":    ("语言已切换为 {lang}",                "Language switched to {lang}"),
    "glove_done_log":   ("完成! 成功: {ok}, 共: {total}",      "Done! Succeeded: {ok}, Total: {total}"),

    # ---- 对话框 ----
    "hint":             ("提示",                              "Notice"),
    "confirm":          ("确认",                              "Confirm"),
    "error":            ("错误",                              "Error"),
    "done":             ("完成",                              "Done"),
    "select_weapon":    ("请先在左侧选一把武器",              "Select a weapon on the left first"),

    # ---- 刀型提示 ----
    "knife_deploy_title": ("刀型部署提示",                    "Knife deployment"),
    "knife_deploy_msg": ("「{name}」是一把CSGO刀型，应用时将自动：\n"
                         "① 把该刀MDL复制到游戏读取位置\n"
                         "② 再注入皮肤贴图\n\n继续吗？",
                         "「{name}」is a CS:GO knife type. Applying it will automatically:\n"
                         "① Copy the knife MDL to the game's model path\n"
                         "② Then inject the skin texture\n\nContinue?"),
}


# ---------------------------------------------------------------- API
def set_lang(lang):
    """切换语言：'zh' 或 'en'。"""
    global _LANG
    if lang in LANG_LABELS:
        _LANG = lang
        return True
    return False


def get_lang():
    """返回当前语言代码。"""
    return _LANG


def toggle_lang():
    """在中英之间切换，返回切换后的语言代码。"""
    set_lang("en" if _LANG == "zh" else "zh")
    return _LANG


def t(key, **kwargs):
    """
    取译文。kwargs 会用 str.format 填进占位符。

    缺 key 或缺当前语言的译文时回退到另一种语言，并在 stderr 告警一次，
    避免静默漏译。同一 key 只告警一次。
    """
    global _WARNED
    entry = STRINGS.get(key)
    if entry is None:
        if key not in _WARNED:
            print(f"[i18n] 缺少 key: {key}", file=sys.stderr)
            _WARNED.add(key)
        return key

    idx = 1 if _LANG == "en" else 0
    text = entry[idx]
    if not text and len(entry) > 1 - idx:
        text = entry[1 - idx]
    if not text and key not in _WARNED:
        print(f"[i18n] key {key} 两种语言都缺译文", file=sys.stderr)
        _WARNED.add(key)
        return key

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError) as e:
            print(f"[i18n] key {key} 占位符错误: {e}", file=sys.stderr)
            return text
    return text


_WARNED = set()


def coverage_report():
    """返回 (完整键数, 缺 en 的键, 缺 zh 的键)。用于自检。"""
    missing_en, missing_zh = [], []
    for k, v in STRINGS.items():
        zh = v[0] if len(v) > 0 else ""
        en = v[1] if len(v) > 1 else ""
        if not zh:
            missing_zh.append(k)
        if not en:
            missing_en.append(k)
    return len(STRINGS), missing_en, missing_zh


if __name__ == "__main__":
    total, me, mz = coverage_report()
    print(f"字典键数 = {total}")
    print(f"缺 en = {len(me)}  {me}")
    print(f"缺 zh = {len(mz)}  {mz}")
    print()
    set_lang("zh")
    print("[zh]", t("avail_skins", n=117), "|", t("app_title"))
    set_lang("en")
    print("[en]", t("avail_skins", n=117), "|", t("app_title"))
