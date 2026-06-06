# -*- coding: utf-8 -*-
"""
文本分析系统 - 集多格式文本导入、中文分词、停用词过滤、词频统计、词云可视化于一体
开发环境：Windows 11, PyCharm Community Edition 2024.3.3
界面布局：左侧操作区 - 右侧整合显示区（文本、词频、词云同屏显示）
风格：白色科幻主题
"""

import os
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from collections import Counter
from typing import List, Dict, Tuple, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import jieba
import wordcloud
from wordcloud import WordCloud, ImageColorGenerator

# ========================================
# 全局样式常量 - 白色科幻风格
# ========================================
STYLE = {
    "MAIN_BG": "#ffffff",
    "LEFT_BG": "#f8faff",
    "RIGHT_BG": "#ffffff",
    "FRAME_BG": "#f0f5ff",
    "TITLE_BG": "#f0f5ff",
    "TITLE_FG": "#0f172a",
    "ACCENT_PRIMARY": "#0ea5e9",
    "ACCENT_SECONDARY": "#8b5cf6",
    "ACCENT_HIGHLIGHT": "#06b6d4",
    "ACCENT_GLOW": "#60a5fa",
    "TEXT_PRIMARY": "#0f172a",
    "TEXT_SECONDARY": "#475569",
    "TEXT_MUTED": "#94a3b8",
    "BORDER_COLOR": "#e2e8f0",
    "BORDER_LIGHT": "#f1f5f9",
    "BUTTON_BG": "#0f172a",
    "BUTTON_FG": "#ffffff",
    "BUTTON_HOVER": "#1e293b",
    "BUTTON_PRIMARY_BG": "#0ea5e9",
    "BUTTON_PRIMARY_HOVER": "#0284c7",
    "BUTTON_ACCENT_BG": "#8b5cf6",
    "BUTTON_ACCENT_HOVER": "#7c3aed",
    "INPUT_BG": "#ffffff",
    "PANEL_SHADOW": "",
    "SCROLL_BG": "#cbd5e1",
    "CARD_BG": "#ffffff",
    "CARD_BORDER": "#e2e8f0",
}

# ========================================
# 内置常用中文停用词表
# ========================================
BUILTIN_STOP_WORDS: set = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "所", "为", "所以", "因为", "但是", "然而", "而且", "虽然", "如果",
    "可以", "这个", "那个", "已经", "还是", "或者", "以及", "之", "与",
    "等", "从", "对", "被", "把", "向", "让", "将", "以", "及", "并",
    "而", "且", "但", "或", "又", "再", "后", "前", "能", "能够", "可能",
    "应该", "需要", "知道", "觉得", "认为", "出来", "起来", "过来", "过去",
    "就是", "的话", "还有", "只是", "大家", "什么", "怎么", "怎样", "这样",
    "那样", "因为", "所以", "如果", "虽然", "但是", "然而", "于是", "因此",
    "然后", "接着", "最后", "首先", "其次", "另外", "此外", "并且", "而且",
    "不过", "只是", "只有", "只要", "只能", "不可", "不用", "不能", "不会",
    "不断", "不仅", "不管", "不论", "不是", "不同", "不如", "不然",
    "不要", "东西", "事情", "问题", "时候", "地方", "方面",
    "啊", "吧", "吗", "呢", "哦", "嗯", "呀", "哪", "哇", "哈",
    "么", "嘛", "哎", "唉", "喂", "啦", "噢", "哟", "咳", "哼", "呵",
    "来", "去", "做", "干", "搞", "弄", "给", "让", "叫", "拿", "打",
    "其中", "其他", "所有", "有些", "许多", "各个", "各种", "每", "某",
    "二", "三", "四", "五", "六", "七", "八", "九", "十", "百", "千", "万",
    "第", "次", "回", "种", "类", "样", "点", "边", "面", "头",
    "里", "外", "中", "内", "大", "小", "多", "少", "高", "低", "长", "短", "新", "旧",
    "年", "月", "日", "时", "分", "秒", "今", "明", "昨", "现",
    "很", "太", "更", "最", "极", "较", "非常", "十分", "特别",
    "通过", "根据", "按照", "经过", "对于", "关于", "由于", "为了",
    "随着", "除了", "作为", "进行", "使用", "利用", "采用", "实现",
    "提供", "表示", "发生", "产生", "出现", "发展", "形成", "建立",
    "具有", "存在", "影响", "作用", "关系", "条件", "情况", "结果",
    "过程", "方式", "方法", "方面", "程度", "范围", "部分", "内容",
    "目前", "现在", "以前", "以后", "当时", "之前", "之后", "以来",
    "以上", "以下", "以内", "以外", "之间", "之中", "之内",
}

# ========================================
# 10组预设颜色方案（要求：10组）
# ========================================
PRESET_COLORS: Dict[str, List[str]] = {
    "冰川蓝": ["#f0f9ff", "#e0f2fe", "#bae6fd", "#7dd3fc", "#38bdf8", "#0ea5e9", "#0284c7", "#0369a1"],
    "霓虹紫": ["#f5f3ff", "#ede9fe", "#ddd6fe", "#c4b5fd", "#a78bfa", "#8b5cf6", "#7c3aed", "#6d28d9"],
    "极光绿": ["#f0fdf4", "#dcfce7", "#bbf7d0", "#86efac", "#4ade80", "#22c55e", "#16a34a", "#15803d"],
    "落日橙": ["#fff7ed", "#ffedd5", "#fed7aa", "#fdba74", "#fb923c", "#f97316", "#ea580c", "#c2410c"],
    "玫瑰粉": ["#fdf2f8", "#fce7f3", "#fbcfe8", "#f9a8d4", "#f472b6", "#ec4899", "#db2777", "#be185d"],
    "暗夜": ["#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b", "#475569", "#0f172a"],
    "森林": ["#f0fdf0", "#e6f4ea", "#cce7d1", "#a3c9a8", "#75a085", "#588157", "#3a5a40", "#1b4332"],
    "日落": ["#fff1e6", "#ffd6a5", "#fdffb6", "#caffbf", "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff"],
    "钢铁灰": ["#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b", "#475569", "#1e293b"],
    "彩虹": ["#ef4444", "#f97316", "#f59e0b", "#84cc16", "#10b981", "#06b6d4", "#3b82f6", "#8b5cf6"],
}

# ========================================
# 10个预设形状（要求：10个）
# ========================================
def shape_circle(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 8
    draw.ellipse((margin, margin, size - margin, size - margin), fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def shape_heart(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    scale = size / 36
    points = []
    for i in range(360):
        t = np.radians(i)
        x = 16 * (np.sin(t) ** 3)
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        px = int(cx + x * scale)
        py = int(cy - y * scale)
        points.append((px, py))
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(2))
    return np.array(img)

def shape_star(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    outer = size // 2 - 10
    inner = outer * 0.4
    points = []
    for i in range(10):
        angle = np.radians(i * 36 - 90)
        r = outer if i % 2 == 0 else inner
        px = int(cx + r * np.cos(angle))
        py = int(cy + r * np.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def shape_cloud(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    circles = [
        (cx - 90, cy + 20, 70), (cx - 30, cy - 30, 80), (cx + 70, cy + 10, 75),
        (cx + 130, cy + 40, 55), (cx + 20, cy + 60, 65), (cx - 60, cy + 70, 50),
        (cx + 50, cy - 50, 45), (cx, cy, 85)
    ]
    for x, y, r in circles:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=255)
    img = img.filter(ImageFilter.GaussianBlur(3))
    return np.array(img)

def shape_diamond(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = size // 2 - 20
    points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def shape_triangle(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = size // 2 - 20
    points = [(cx, cy - r), (cx + r * 0.866, cy + r * 0.5), (cx - r * 0.866, cy + r * 0.5)]
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def shape_hexagon(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = size // 2 - 15
    points = []
    for i in range(6):
        angle = np.radians(i * 60 - 90)
        px = int(cx + r * np.cos(angle))
        py = int(cy + r * np.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def shape_oval(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 10
    draw.ellipse((margin, margin + 60, size - margin, size - margin - 60), fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def shape_bubble(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 25
    tail_h, tail_w = 70, 60
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin - tail_h - 10),
        radius=60, fill=255
    )
    cx = size // 2
    tail = [(cx - tail_w // 2, size - margin - tail_h - 10),
            (cx + tail_w // 2, size - margin - tail_h - 10),
            (cx, size - margin)]
    draw.polygon(tail, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(2))
    return np.array(img)

def shape_rounded_rect(size: int = 512) -> np.ndarray:
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 25
    draw.rounded_rectangle((margin, margin, size - margin, size - margin), radius=50, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

SHAPES: Dict[str, callable] = {
    "圆形": shape_circle,
    "心形": shape_heart,
    "五角星": shape_star,
    "云朵": shape_cloud,
    "菱形": shape_diamond,
    "三角形": shape_triangle,
    "六边形": shape_hexagon,
    "椭圆形": shape_oval,
    "对话气泡": shape_bubble,
    "圆角矩形": shape_rounded_rect,
}

# ========================================
# 文本分析核心类
# ========================================
class TextAnalyzer:
    def __init__(self):
        self.raw_text = ""
        self.words = []
        self.word_counts = Counter()
        self._stop_words = BUILTIN_STOP_WORDS.copy()
        self.custom_stop_words = set()

    @property
    def all_stop_words(self):
        return self._stop_words | self.custom_stop_words

    def add_custom_stops(self, words: List[str]):
        for w in words:
            w = w.strip()
            if w:
                self.custom_stop_words.add(w)

    def remove_custom_stops(self, words: List[str]):
        for w in words:
            self.custom_stop_words.discard(w.strip())

    def reset_stops(self):
        self.custom_stop_words.clear()

    @staticmethod
    def _read_txt(path: str) -> str:
        encodings = ["utf-8", "gbk", "gb2312", "utf-16", "latin-1"]
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError("无法识别文本编码，请确认文件为UTF-8或GBK格式")

    @staticmethod
    def _read_docx(path: str) -> str:
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    @staticmethod
    def _read_pdf(path: str) -> str:
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text.append(t)
        result = "\n".join(text).strip()
        if not result:
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    text = []
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text.append(t)
                    result = "\n".join(text).strip()
            except ImportError:
                pass
        if not result:
            raise ValueError("无法提取PDF文本，文件可能为扫描件")
        return result

    def load_file(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".txt":
            self.raw_text = self._read_txt(path)
        elif ext == ".docx":
            self.raw_text = self._read_docx(path)
        elif ext == ".pdf":
            self.raw_text = self._read_pdf(path)
        else:
            raise ValueError(f"不支持的格式 {ext}，仅支持 .txt .docx .pdf")
        return self.raw_text

    def process(self) -> List[str]:
        if not self.raw_text:
            return []
        words = jieba.lcut(self.raw_text)
        stops = self.all_stop_words
        filtered = []
        for w in words:
            w = w.strip()
            if len(w) < 2:
                continue
            if w in stops:
                continue
            if re.search(r'[\u4e00-\u9ffa-zA-Z0-9]', w):
                filtered.append(w)
        self.words = filtered
        self.word_counts = Counter(filtered)
        return filtered

    def get_top_words(self, n: int = 100) -> List[Tuple[str, int]]:
        return self.word_counts.most_common(n)

    @property
    def total_words(self) -> int:
        return len(self.words)

    @property
    def unique_words(self) -> int:
        return len(self.word_counts)

# ========================================
# 词云生成器
# ========================================
class WordCloudEngine:
    def __init__(self):
        self.mask: Optional[np.ndarray] = None
        self.color_image: Optional[np.ndarray] = None
        self.current_shape: str = ""
        self.current_colors: str = ""
        self.use_image_colors: bool = False
        self.wc: Optional[WordCloud] = None

    def set_preset_shape(self, name: str, size: int = 512) -> np.ndarray:
        if name not in SHAPES:
            raise ValueError(f"未知形状 {name}")
        self.mask = SHAPES[name](size)
        self.current_shape = name
        self.color_image = None
        self.use_image_colors = False
        return self.mask

    def load_mask_from_image(self, path: str, size: int = 512) -> np.ndarray:
        img = Image.open(path).convert("L")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        img = img.point(lambda p: 255 if p > 128 else 0)
        self.mask = np.array(img)
        self.current_shape = f"自定义: {os.path.basename(path)}"
        self.use_image_colors = False
        return self.mask

    def load_mask_and_colors(self, path: str, size: int = 512) -> np.ndarray:
        img_rgb = Image.open(path).convert("RGB")
        img_rgb = img_rgb.resize((size, size), Image.Resampling.LANCZOS)
        img_gray = img_rgb.convert("L")
        img_gray = img_gray.point(lambda p: 255 if p > 128 else 0)
        self.mask = np.array(img_gray)
        self.color_image = np.array(img_rgb)
        self.current_shape = f"图片颜色: {os.path.basename(path)}"
        self.use_image_colors = True
        return self.mask

    def get_color_function(self, scheme_name: str):
        if self.use_image_colors and self.color_image is not None:
            return ImageColorGenerator(self.color_image)
        if scheme_name in PRESET_COLORS:
            colors = PRESET_COLORS[scheme_name]
            def _func(word, *args, **kwargs):
                idx = hash(word) % len(colors)
                return colors[idx]
            return _func
        def _default(word, *args, **kwargs):
            return "#0f172a"
        return _default

    def generate(self, freq: Dict[str, int], width: int = 800, height: int = 600,
                 bg: str = "white", max_words: int = 200) -> WordCloud:
        font_path = self._find_font()
        color_func = self.get_color_function(self.current_colors)
        wc = WordCloud(
            width=width, height=height,
            font_path=font_path,
            background_color=bg,
            mask=self.mask,
            max_words=max_words,
            max_font_size=None,
            min_font_size=8,
            color_func=color_func,
            collocations=False,
            random_state=42,
            prefer_horizontal=0.7
        )
        wc.generate_from_frequencies(freq)
        self.wc = wc
        return wc

    def _find_font(self) -> str:
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/STKAITI.TTF",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return "C:/Windows/Fonts/msyh.ttc"

    def save(self, path: str):
        if self.wc is None:
            raise ValueError("未生成词云")
        img = self.wc.to_image()
        img.save(path, quality=95)

    def to_image(self) -> Image.Image:
        if self.wc is None:
            raise ValueError("未生成词云")
        return self.wc.to_image()

# ========================================
# 主GUI应用
# ========================================
class TextAnalysisApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TextLens · 中文文本分析系统")
        self.root.geometry("1440x820")
        self.root.minsize(1200, 700)
        self.root.configure(bg=STYLE["MAIN_BG"])

        self.analyzer = TextAnalyzer()
        self.generator = WordCloudEngine()

        # 状态
        self.current_file = None
        self.tk_preview = None
        self.is_processing = False

        self._build_ui()
        self._setup_styles()

        # 默认选择
        self.shape_var.set("圆形")
        self.color_var.set("冰川蓝")
        self.generator.set_preset_shape("圆形")
        self.generator.current_colors = "冰川蓝"

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TNotebook", background=STYLE["RIGHT_BG"],
            borderwidth=0, tabmargins=[2, 5, 0, 0]
        )
        style.configure(
            "TNotebook.Tab", background=STYLE["FRAME_BG"],
            foreground=STYLE["TEXT_SECONDARY"],
            padding=[16, 6], font=("Microsoft YaHei UI", 10),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", STYLE["MAIN_BG"])],
            foreground=[("selected", STYLE["ACCENT_PRIMARY"])],
        )
        style.configure(
            "Treeview",
            background=STYLE["CARD_BG"],
            foreground=STYLE["TEXT_PRIMARY"],
            rowheight=26,
            fieldbackground=STYLE["CARD_BG"],
            font=("Microsoft YaHei UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=STYLE["BUTTON_BG"],
            foreground=STYLE["BUTTON_FG"],
            font=("Microsoft YaHei UI", 9, "bold"),
        )
        style.configure(
            "TLabelframe", background=STYLE["LEFT_BG"], borderwidth=0
        )
        style.configure(
            "TLabelframe.Label", background=STYLE["LEFT_BG"],
            foreground=STYLE["TEXT_PRIMARY"],
            font=("Microsoft YaHei UI", 10, "bold")
        )
        style.configure(
            "TProgressbar", troughcolor=STYLE["FRAME_BG"],
            background=STYLE["ACCENT_PRIMARY"], borderwidth=0
        )

    def _create_card(self, parent, title):
        frame = tk.Frame(parent, bg=STYLE["LEFT_BG"], padx=12, pady=8)
        frame.pack(fill=tk.X, pady=(0, 8))
        header = tk.Frame(frame, bg=STYLE["LEFT_BG"])
        header.pack(fill=tk.X, pady=(0, 6))
        indicator = tk.Frame(header, bg=STYLE["ACCENT_PRIMARY"], width=4, height=18)
        indicator.pack(side=tk.LEFT, padx=(0, 8))
        label = tk.Label(
            header, text=title,
            font=("Microsoft YaHei UI", 11, "bold"),
            fg=STYLE["TEXT_PRIMARY"], bg=STYLE["LEFT_BG"]
        )
        label.pack(side=tk.LEFT)
        return frame

    def _btn_primary(self, parent, text, command, **kwargs):
        btn = tk.Button(
            parent, text=text, command=command,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=STYLE["BUTTON_PRIMARY_BG"], fg=STYLE["BUTTON_FG"],
            activebackground=STYLE["BUTTON_PRIMARY_HOVER"],
            activeforeground=STYLE["BUTTON_FG"],
            relief=tk.FLAT, cursor="hand2",
            padx=16, pady=7, borderwidth=0, highlightthickness=0, **kwargs
        )
        def _enter(e):
            if not btn["state"] == tk.DISABLED:
                btn.config(bg=STYLE["BUTTON_PRIMARY_HOVER"])
        def _leave(e):
            if not btn["state"] == tk.DISABLED:
                btn.config(bg=STYLE["BUTTON_PRIMARY_BG"])
        btn.bind("<Enter>", _enter)
        btn.bind("<Leave>", _leave)
        return btn

    def _btn_secondary(self, parent, text, command, **kwargs):
        btn = tk.Button(
            parent, text=text, command=command,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=STYLE["BUTTON_BG"], fg=STYLE["BUTTON_FG"],
            activebackground=STYLE["BUTTON_HOVER"],
            activeforeground=STYLE["BUTTON_FG"],
            relief=tk.FLAT, cursor="hand2",
            padx=16, pady=7, borderwidth=0, highlightthickness=0, **kwargs
        )
        def _enter(e):
            if not btn["state"] == tk.DISABLED:
                btn.config(bg=STYLE["BUTTON_HOVER"])
        def _leave(e):
            if not btn["state"] == tk.DISABLED:
                btn.config(bg=STYLE["BUTTON_BG"])
        btn.bind("<Enter>", _enter)
        btn.bind("<Leave>", _leave)
        return btn

    def _build_ui(self):
        # 顶部标题栏
        self._build_top_bar()

        # 主区域 - 左侧操作栏 + 右侧整合显示区
        main = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL,
            bg=STYLE["BORDER_COLOR"], sashwidth=1,
            sashrelief=tk.FLAT
        )
        main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        main.add(left_panel, minsize=360, width=380)
        main.add(right_panel, minsize=800, width=1000)

        # 底部状态栏
        self._build_status_bar()

    def _build_top_bar(self):
        bar = tk.Frame(self.root, bg=STYLE["TITLE_BG"], height=56)
        bar.pack(fill=tk.X, side=tk.TOP)
        bar.pack_propagate(False)
        title = tk.Label(
            bar, text="⚡ TEXTLENS",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg=STYLE["TITLE_FG"], bg=STYLE["TITLE_BG"]
        )
        title.pack(side=tk.LEFT, padx=24, pady=10)
        subtitle = tk.Label(
            bar, text="中文文本分析 · 词频统计 · 词云可视化",
            font=("Microsoft YaHei UI", 10),
            fg=STYLE["TEXT_SECONDARY"], bg=STYLE["TITLE_BG"]
        )
        subtitle.pack(side=tk.LEFT, padx=16, pady=18)

    def _build_left_panel(self) -> tk.Frame:
        left = tk.Frame(self.root, bg=STYLE["LEFT_BG"], width=380)
        canvas = tk.Canvas(left, bg=STYLE["LEFT_BG"], highlightthickness=0)
        scroll = tk.Scrollbar(left, orient=tk.VERTICAL, command=canvas.yview)
        self.left_content = tk.Frame(canvas, bg=STYLE["LEFT_BG"])
        self.left_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.left_content, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        def _resize(e):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width)
        canvas.bind("<Configure>", _resize)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        left.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta/120), "units"))

        # 1. 文件导入
        card = self._create_card(self.left_content, "📁 文本导入")
        btn_row = tk.Frame(card, bg=STYLE["LEFT_BG"])
        btn_row.pack(fill=tk.X, pady=(2, 6))
        self.btn_open = self._btn_primary(btn_row, "打开文件", self._on_open_file, width=12)
        self.btn_open.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_clear = self._btn_secondary(btn_row, "清空重置", self._on_clear, width=10)
        self.btn_clear.pack(side=tk.LEFT)
        self.file_label = tk.Label(
            card, text="未选择文件",
            font=("Microsoft YaHei UI", 8),
            fg=STYLE["TEXT_MUTED"], bg=STYLE["LEFT_BG"],
            anchor="w", wraplength=330
        )
        self.file_label.pack(fill=tk.X)

        # 2. 分词分析
        card = self._create_card(self.left_content, "🔍 分词分析")
        param_row = tk.Frame(card, bg=STYLE["LEFT_BG"])
        param_row.pack(fill=tk.X, pady=(2, 6))
        tk.Label(
            param_row, text="显示词数:",
            font=("Microsoft YaHei UI", 9),
            fg=STYLE["TEXT_SECONDARY"], bg=STYLE["LEFT_BG"]
        ).pack(side=tk.LEFT)
        self.top_n_var = tk.StringVar(value="100")
        entry = tk.Entry(
            param_row, textvariable=self.top_n_var,
            width=6, font=("Microsoft YaHei UI", 9),
            bg=STYLE["INPUT_BG"], relief=tk.SOLID,
            borderwidth=1, highlightthickness=0
        )
        entry.pack(side=tk.LEFT, padx=(8, 0))
        self.btn_analyze = self._btn_primary(card, "开始分析", self._on_analyze)
        self.btn_analyze.pack(fill=tk.X, pady=(2, 4))
        self.stats_label = tk.Label(
            card, text="总词数: 0 | 独立词: 0",
            font=("Microsoft YaHei UI", 8),
            fg=STYLE["TEXT_MUTED"], bg=STYLE["LEFT_BG"],
            anchor="w"
        )
        self.stats_label.pack(fill=tk.X)

        # 3. 停用词
        card = self._create_card(self.left_content, "🚫 停用词")
        add_row = tk.Frame(card, bg=STYLE["LEFT_BG"])
        add_row.pack(fill=tk.X, pady=(2, 4))
        tk.Label(
            add_row, text="添加:",
            font=("Microsoft YaHei UI", 9),
            fg=STYLE["TEXT_SECONDARY"], bg=STYLE["LEFT_BG"]
        ).pack(side=tk.LEFT)
        self.stop_add_var = tk.StringVar()
        entry = tk.Entry(
            add_row, textvariable=self.stop_add_var,
            font=("Microsoft YaHei UI", 9),
            bg=STYLE["INPUT_BG"], relief=tk.SOLID,
            borderwidth=1, highlightthickness=0
        )
        entry.pack(side=tk.LEFT, fill=X, expand=True, padx=(6, 4))
        btn = self._btn_secondary(add_row, "+", self._on_add_stop, width=2)
        btn.pack(side=tk.RIGHT)
        self.stop_list = tk.Listbox(
            card, height=5, font=("Microsoft YaHei UI", 9),
            bg=STYLE["INPUT_BG"], fg=STYLE["TEXT_PRIMARY"],
            selectbackground=STYLE["ACCENT_PRIMARY"],
            selectforeground="white",
            relief=tk.SOLID, borderwidth=1, highlightthickness=0
        )
        self.stop_list.pack(fill=tk.X, pady=(0, 4))
        btn_row = tk.Frame(card, bg=STYLE["LEFT_BG"])
        btn_row.pack(fill=tk.X)
        self._btn_secondary(btn_row, "移除选中", self._on_remove_stop).pack(side=tk.LEFT, padx=(0, 6))
        self._btn_secondary(btn_row, "恢复默认", self._on_reset_stops).pack(side=tk.LEFT)

        # 4. 形状选择
        card = self._create_card(self.left_content, "⬡ 词云形状")
        self.shape_var = tk.StringVar()
        combo = ttk.Combobox(
            card, textvariable=self.shape_var,
            values=list(SHAPES.keys()),
            state="readonly", font=("Microsoft YaHei UI", 9)
        )
        combo.pack(fill=tk.X, pady=(2, 6))
        combo.bind("<<ComboboxSelected>>", self._on_shape_change)
        btn_row = tk.Frame(card, bg=STYLE["LEFT_BG"])
        btn_row.pack(fill=tk.X, pady=(0, 4))
        self._btn_secondary(btn_row, "导入形状", self._on_import_mask).pack(side=tk.LEFT, padx=(0, 6))
        self._btn_secondary(btn_row, "导入带色图片", self._on_import_colored).pack(side=tk.LEFT)
        self.shape_info = tk.Label(
            card, text="当前: 圆形",
            font=("Microsoft YaHei UI", 8),
            fg=STYLE["TEXT_MUTED"], bg=STYLE["LEFT_BG"],
            anchor="w"
        )
        self.shape_info.pack(fill=tk.X)

        # 5. 颜色方案
        card = self._create_card(self.left_content, "🎨 颜色方案")
        self.color_var = tk.StringVar()
        combo = ttk.Combobox(
            card, textvariable=self.color_var,
            values=list(PRESET_COLORS.keys()),
            state="readonly", font=("Microsoft YaHei UI", 9)
        )
        combo.pack(fill=tk.X, pady=(2, 6))
        combo.bind("<<ComboboxSelected>>", self._on_color_change)
        self.custom_color_var = tk.StringVar()
        tk.Label(
            card, text="自定义颜色 (#RRGGBB 逗号分隔):",
            font=("Microsoft YaHei UI", 9),
            fg=STYLE["TEXT_SECONDARY"], bg=STYLE["LEFT_BG"],
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 2))
        custom_row = tk.Frame(card, bg=STYLE["LEFT_BG"])
        custom_row.pack(fill=tk.X, pady=(0, 4))
        entry = tk.Entry(
            custom_row, textvariable=self.custom_color_var,
            font=("Microsoft YaHei UI", 9),
            bg=STYLE["INPUT_BG"], relief=tk.SOLID,
            borderwidth=1, highlightthickness=0
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self._btn_secondary(custom_row, "应用", self._on_apply_custom, width=6).pack(side=tk.RIGHT)

        # 6. 生成导出
        card = self._create_card(self.left_content, "🚀 生成导出")
        self.progress = ttk.Progressbar(card, mode="indeterminate", length=320)
        self.progress.pack(fill=tk.X, pady=(0, 6))
        self.progress.pack_forget()
        self.btn_generate = self._btn_primary(card, "生成词云", self._on_generate)
        self.btn_generate.pack(fill=tk.X, pady=(2, 4))
        self.btn_export = self._btn_secondary(card, "导出PNG/JPG", self._on_export)
        self.btn_export.pack(fill=tk.X, pady=(0, 2))

        return left

    def _build_right_panel(self) -> tk.Frame:
        right = tk.Frame(self.root, bg=STYLE["RIGHT_BG"], padx=16, pady=12)

        # 上方 - 文本 + 词频统计（左右分栏）
        top = tk.Frame(right, bg=STYLE["RIGHT_BG"])
        top.pack(fill=tk.X, pady=(0, 12))

        # 文本区域（左侧）
        text_card = self._create_right_card(top, "📝 原文预览", width_ratio=1)
        self.text_view = scrolledtext.ScrolledText(
            text_card,
            font=("Microsoft YaHei UI", 9.5),
            bg="#ffffff", fg=STYLE["TEXT_PRIMARY"],
            wrap=tk.WORD, relief=tk.FLAT, borderwidth=1,
            highlightthickness=0, padx=12, pady=10
        )
        self.text_view.pack(fill=tk.BOTH, expand=True)
        self.text_info = tk.Label(
            text_card, text=f"字符数: 0",
            font=("Microsoft YaHei UI", 8),
            fg=STYLE["TEXT_MUTED"], bg=STYLE["CARD_BG"],
            anchor="w"
        )
        self.text_info.pack(fill=tk.X)

        # 词频表格（右侧）
        freq_card = self._create_right_card(top, "📊 词频统计", width_ratio=1)
        columns = ("rank", "word", "count")
        self.freq_table = ttk.Treeview(
            freq_card, columns=columns, show="headings",
            selectmode="browse", height=10
        )
        self.freq_table.heading("rank", text="序号")
        self.freq_table.heading("word", text="词汇")
        self.freq_table.heading("count", text="频次")
        self.freq_table.column("rank", width=50, anchor="center")
        self.freq_table.column("word", width=180, anchor="w")
        self.freq_table.column("count", width=60, anchor="center")
        tree_scroll = ttk.Scrollbar(freq_card, orient=tk.VERTICAL, command=self.freq_table.yview)
        self.freq_table.configure(yscrollcommand=tree_scroll.set)
        self.freq_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.freq_info = tk.Label(
            freq_card, text=f"共 0 个词汇",
            font=("Microsoft YaHei UI", 8),
            fg=STYLE["TEXT_MUTED"], bg=STYLE["CARD_BG"],
            anchor="w"
        )
        self.freq_info.pack(fill=tk.X)

        # 下方 - 词云预览
        bottom_card = self._create_right_card(right, "🌌 词云预览", height=360)
        self.cloud_canvas = tk.Canvas(
            bottom_card,
            bg=STYLE["CARD_BG"],
            highlightthickness=0, relief=tk.FLAT,
        )
        self.cloud_canvas.pack(fill=tk.BOTH, expand=True)
        self.cloud_info = tk.Label(
            bottom_card, text="等待生成...",
            font=("Microsoft YaHei UI", 8),
            fg=STYLE["TEXT_MUTED"], bg=STYLE["CARD_BG"],
            anchor="w"
        )
        self.cloud_info.pack(fill=tk.X)

        return right

    def _create_right_card(self, parent, title, width_ratio=None, height=None):
        frame = tk.Frame(
            parent, bg=STYLE["CARD_BG"],
            relief=tk.SOLID, borderwidth=1,
            highlightthickness=0
        )
        if width_ratio == 1:
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        elif width_ratio == 2:
            frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        else:
            frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        if height:
            frame.configure(height=height)
            frame.pack_propagate(False)
        header = tk.Frame(frame, bg=STYLE["CARD_BG"], height=32)
        header.pack(fill=tk.X, padx=12, pady=(4, 0))
        tk.Label(
            header, text=title,
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=STYLE["TEXT_PRIMARY"], bg=STYLE["CARD_BG"],
        ).pack(side=tk.LEFT)
        container = tk.Frame(frame, bg=STYLE["CARD_BG"])
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 8))
        return container

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=STYLE["BUTTON_BG"], height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        self.status_text = tk.StringVar(value="就绪")
        label = tk.Label(
            bar, textvariable=self.status_text,
            font=("Microsoft YaHei UI", 8),
            fg="#cbd5e1", bg=STYLE["BUTTON_BG"],
            anchor="w"
        )
        label.pack(side=tk.LEFT, fill=tk.X, padx=20, pady=5)
        self.status_dot = tk.Label(
            bar, text="●",
            font=("Microsoft YaHei UI", 8),
            fg="#10b981", bg=STYLE["BUTTON_BG"]
        )
        self.status_dot.pack(side=tk.RIGHT, padx=20, pady=5)

    def _set_status(self, text, color="#10b981"):
        self.status_text.set(text)
        self.status_dot.config(fg=color)
        self.root.update_idletasks()

    # ========================================
    # 事件处理
    # ========================================
    def _on_open_file(self):
        path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[
                ("支持格式", "*.txt *.docx *.pdf"),
                ("文本文件", "*.txt"),
                ("Word 文档", "*.docx"),
                ("PDF 文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        if not path:
            return
        self.progress.pack(fill=tk.X, pady=(0, 6))
        self.progress.start()
        self._set_status("正在读取文件...", "#f59e0b")
        def _task():
            try:
                text = self.analyzer.load_file(path)
                self.current_file = path
                self.root.after(0, lambda: self._after_open(path, text))
            except Exception as e:
                self.root.after(0, lambda: self._error("读取失败", str(e)))
        threading.Thread(target=_task, daemon=True).start()

    def _after_open(self, path: str, text: str):
        self.progress.stop()
        self.progress.pack_forget()
        self.file_label.config(text=os.path.basename(path))
        self.text_view.delete(1.0, tk.END)
        preview = text[:10000]
        self.text_view.insert(1.0, preview)
        if len(text) > 10000:
            self.text_view.insert(tk.END, f"\n\n[...] 文本过长，仅显示前 10000 字符，总计 {len(text)} 字符")
        self.text_info.config(text=f"字符数: {len(text)}")
        self._set_status(f"已加载: {os.path.basename(path)}")

    def _on_clear(self):
        self.analyzer = TextAnalyzer()
        self.generator = WordCloudEngine()
        self.current_file = None
        self.file_label.config(text="未选择文件")
        self.text_view.delete(1.0, tk.END)
        self.text_info.config(text="字符数: 0")
        for item in self.freq_table.get_children():
            self.freq_table.delete(item)
        self.freq_info.config(text="共 0 个词汇")
        self.stats_label.config(text="总词数: 0 | 独立词: 0")
        self.cloud_canvas.delete("all")
        self.cloud_info.config(text="等待生成...")
        self.stop_list.delete(0, tk.END)
        self.generator.set_preset_shape("圆形")
        self.shape_var.set("圆形")
        self.shape_info.config(text="当前: 圆形")
        self.color_var.set("冰川蓝")
        self.generator.current_colors = "冰川蓝"
        self._set_status("已清空重置")

    def _on_analyze(self):
        if not self.analyzer.raw_text:
            messagebox.showwarning("提示", "请先导入文本文件")
            return
        self.progress.pack(fill=tk.X, pady=(0, 6))
        self.progress.start()
        self._set_status("正在分词统计...", "#f59e0b")
        def _task():
            try:
                self.analyzer.process()
                self.root.after(0, self._after_analyze)
            except Exception as e:
                self.root.after(0, lambda: self._error("分词失败", str(e)))
        threading.Thread(target=_task, daemon=True).start()

    def _after_analyze(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.stats_label.config(text=f"总词数: {self.analyzer.total_words} | 独立词: {self.analyzer.unique_words}")
        try:
            n = int(self.top_n_var.get())
        except ValueError:
            n = 100
        for item in self.freq_table.get_children():
            self.freq_table.delete(item)
        top = self.analyzer.get_top_words(n)
        for idx, (word, cnt) in enumerate(top, 1):
            tag = "even" if idx % 2 == 0 else "odd"
            self.freq_table.insert("", tk.END, values=(idx, word, cnt), tags=(tag,))
        self.freq_table.tag_configure("even", background="#f8fafc")
        self.freq_info.config(text=f"显示前 {len(top)} / {self.analyzer.unique_words} 个词汇")
        self._set_status(f"分析完成: {self.analyzer.total_words} 词")
        self._refresh_stop_list()

    def _on_add_stop(self):
        word = self.stop_add_var.get().strip()
        if not word:
            return
        self.analyzer.add_custom_stops([word])
        self.stop_add_var.set("")
        self._refresh_stop_list()
        self._set_status(f"已添加停用词: {word}")

    def _on_remove_stop(self):
        sel = self.stop_list.curselection()
        if not sel:
            messagebox.showwarning("提示", "请选择要移除的停用词")
            return
        words = [self.stop_list.get(i) for i in sel]
        self.analyzer.remove_custom_stops(words)
        self._refresh_stop_list()
        self._set_status(f"已移除: {', '.join(words)}")

    def _on_reset_stops(self):
        self.analyzer.reset_stops()
        self._refresh_stop_list()
        self._set_status("已恢复默认停用词表")

    def _refresh_stop_list(self):
        self.stop_list.delete(0, tk.END)
        for w in sorted(self.analyzer.custom_stop_words):
            self.stop_list.insert(tk.END, w)

    def _on_shape_change(self, e):
        name = self.shape_var.get()
        if name in SHAPES:
            self.generator.set_preset_shape(name)
            self.shape_info.config(text=f"当前: {name}")
            self._set_status(f"已选择形状: {name}")

    def _on_import_mask(self):
        path = filedialog.askopenfilename(
            title="导入形状图片（黑白轮廓效果最佳）",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有", "*.*")]
        )
        if not path:
            return
        try:
            self.generator.load_mask_from_image(path)
            self.shape_var.set("自定义")
            self.shape_info.config(text=f"当前: 自定义 - {os.path.basename(path)}")
            self._set_status(f"已导入形状: {os.path.basename(path)}")
        except Exception as e:
            self._error("导入失败", str(e))

    def _on_import_colored(self):
        path = filedialog.askopenfilename(
            title="导入彩色图片（提取形状和颜色）",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有", "*.*")]
        )
        if not path:
            return
        try:
            self.generator.load_mask_and_colors(path)
            self.shape_var.set("图片颜色")
            self.shape_info.config(text=f"当前: {os.path.basename(path)} (带颜色)")
            self._set_status(f"已导入带色图片: {os.path.basename(path)}")
        except Exception as e:
            self._error("导入失败", str(e))

    def _on_color_change(self, e):
        name = self.color_var.get()
        self.generator.current_colors = name
        self._set_status(f"已选择颜色: {name}")

    def _on_apply_custom(self):
        text = self.custom_color_var.get().strip()
        if not text:
            messagebox.showwarning("提示", "请输入颜色值")
            return
        colors = [c.strip() for c in text.split(",") if c.strip()]
        for c in colors:
            if not re.match(r'^#[0-9a-fA-F]{6}$', c):
                messagebox.showwarning("格式错误", f"无效颜色 {c}，请使用 #RRGGBB 格式")
                return
        PRESET_COLORS["自定义"] = colors
        self.generator.current_colors = "自定义"
        self.color_var.set("自定义")
        self._set_status(f"已应用自定义颜色: {len(colors)} 种")

    def _on_generate(self):
        if self.analyzer.unique_words == 0:
            messagebox.showwarning("提示", "请先导入文本并分析")
            return
        if not self.generator.mask:
            self.generator.set_preset_shape("圆形")
        self.progress.pack(fill=tk.X, pady=(0, 6))
        self.progress.start()
        self._set_status("正在生成词云...", "#f59e0b")
        def _task():
            try:
                freq_dict = dict(self.analyzer.get_top_words(200))
                self.generator.generate(freq_dict, 800, 600, "white", 200)
                self.root.after(0, self._after_generate)
            except Exception as e:
                self.root.after(0, lambda: self._error("生成失败", str(e)))
        threading.Thread(target=_task, daemon=True).start()

    def _after_generate(self):
        self.progress.stop()
        self.progress.pack_forget()
        img = self.generator.to_image()
        canvas_w = self.cloud_canvas.winfo_width()
        canvas_h = self.cloud_canvas.winfo_height()
        if canvas_w < 100:
            canvas_w, canvas_h = 700, 320
        iw, ih = img.size
        ratio = min(canvas_w / iw, canvas_h / ih)
        new_w, new_h = int(iw * ratio), int(ih * ratio)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_preview = self._pil_to_tk(resized)
        self.cloud_canvas.delete("all")
        cx, cy = canvas_w // 2, canvas_h // 2
        self.cloud_canvas.create_image(cx, cy, image=self.tk_preview, anchor=tk.CENTER)
        shape = self.generator.current_shape or "默认"
        colors = self.generator.current_colors or "默认"
        self.cloud_info.config(text=f"形状: {shape} | 颜色: {colors} | 词汇数: {self.analyzer.unique_words}")
        self._set_status("词云生成完成")

    def _on_export(self):
        if self.generator.wc is None:
            messagebox.showwarning("提示", "请先生成词云")
            return
        path = filedialog.asksaveasfilename(
            title="导出词云",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg")]
        )
        if not path:
            return
        try:
            self.generator.save(path)
            self._set_status(f"已导出: {os.path.basename(path)}")
            messagebox.showinfo("导出成功", f"图片已保存到:\n{path}")
        except Exception as e:
            self._error("导出失败", str(e))

    def _error(self, title, msg):
        self.progress.stop()
        self.progress.pack_forget()
        messagebox.showerror(title, msg)
        self._set_status(f"{title}: {msg}", "#ef4444")

    def _pil_to_tk(self, img: Image.Image) -> tk.PhotoImage:
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return tk.PhotoImage(data=buf.getvalue())

    def run(self):
        self.root.mainloop()

# ========================================
# 入口
# ========================================
def check_deps():
    missing = []
    try:
        import jieba
    except ImportError:
        missing.append("jieba")
    try:
        from wordcloud import WordCloud
    except ImportError:
        missing.append("wordcloud")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    if missing:
        print("=" * 60)
        print("缺少依赖库，请先安装:")
        print()
        print("  pip install " + " ".join(missing))
        print()
        print("完整安装命令:")
        print("  pip install jieba wordcloud pillow numpy python-docx PyPDF2 pdfplumber")
        print("=" * 60)
        sys.exit(1)

def main():
    check_deps()
    root = tk.Tk()
    app = TextAnalysisApp(root)
    app.run()

if __name__ == "__main__":
    main()
