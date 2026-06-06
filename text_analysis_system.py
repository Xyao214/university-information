# -*- coding: utf-8 -*-
"""
文本分析系统 - 集多格式文本导入、中文分词、停用词过滤、词频统计、词云可视化于一体
系统要求：Windows 11, PyCharm Community Edition 2024.3.3
依赖库：jieba, wordcloud, pillow, python-docx, PyPDF2, numpy, matplotlib
"""

import os
import re
import io
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from collections import Counter
from typing import List, Dict, Tuple, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import jieba
import wordcloud
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

# ============================================================
# 内置常用中文停用词表
# ============================================================
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
    "不断", "不仅", "不管", "不论", "不是", "不同", "不如", "不然", "不如",
    "不过", "不要", "不仅", "不管", "不论", "不是", "不同", "不如", "不然",
    "不如", "不过", "不要", "东西", "事情", "问题", "时候", "地方", "方面",
    "些", "啊", "吧", "吗", "呢", "哦", "嗯", "呀", "哪", "哇", "哈",
    "么", "嘛", "哎", "唉", "喂", "啦", "噢", "哟", "咳", "哼", "呵",
    "来", "去", "做", "干", "搞", "弄", "给", "让", "叫", "拿", "打",
    "走", "跑", "吃", "喝", "看", "听", "想", "说", "写", "读", "用",
}
# 补充更多常用停用词
BUILTIN_STOP_WORDS.update({
    "其中", "其他", "所有", "有些", "许多", "各个", "各种", "每", "某",
    "二", "三", "四", "五", "六", "七", "八", "九", "十", "百", "千", "万",
    "第", "次", "回", "种", "类", "样", "点", "些", "边", "面", "头",
    "里", "外", "中", "内", "前", "后", "左", "右", "上", "下",
    "大", "小", "多", "少", "高", "低", "长", "短", "新", "旧",
    "年", "月", "日", "时", "分", "秒", "今", "明", "昨", "现",
    "很", "太", "更", "最", "极", "较", "非常", "十分", "特别",
    "通过", "根据", "按照", "经过", "对于", "关于", "由于", "为了",
    "随着", "除了", "作为", "进行", "使用", "利用", "采用", "实现",
    "提供", "表示", "发生", "产生", "出现", "发展", "形成", "建立",
    "具有", "存在", "影响", "作用", "关系", "条件", "情况", "结果",
    "过程", "方式", "方法", "方面", "程度", "范围", "部分", "内容",
    "目前", "现在", "以前", "以后", "以前", "当时", "之前", "之后",
    "以来", "以上", "以下", "以内", "以外", "之间", "之中", "之内",
})


# ============================================================
# 10组预设颜色方案
# ============================================================
PRESET_COLOR_SCHEMES: Dict[str, List[str]] = {
    "海洋蓝调": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087",
                "#f95d6a", "#ff7c43", "#ffa600"],
    "日落暖橙": ["#ff6b6b", "#ff8e72", "#ffa272", "#ffb672", "#ffca72",
                "#ffde72", "#ffe972", "#fff272"],
    "森林绿意": ["#1b4332", "#2d6a4f", "#40916c", "#52b788", "#74c69d",
                "#95d5b2", "#b7e4c7", "#d8f3dc"],
    "薰衣草紫": ["#3c096c", "#5a189a", "#7b2cbf", "#9d4edd", "#c77dff",
                "#e0aaff", "#e3d5ff", "#f2e8ff"],
    "烈焰红": ["#641220", "#6e1423", "#85182a", "#a11d33", "#a71e34",
              "#bd1f36", "#c71f37", "#da1e37"],
    "极光梦幻": ["#0b132b", "#1c2541", "#3a506b", "#5bc0be", "#6fffe9",
                "#80ffdb", "#72efdd", "#4ea8de"],
    "蜜桃粉彩": ["#ffcdb2", "#ffb4a2", "#e5989b", "#b5838d", "#6d6875",
                "#ffc8dd", "#ffafcc", "#bde0fe"],
    "霓虹都市": ["#f72585", "#b5179e", "#7209b7", "#560bad", "#480ca8",
                "#3a0ca3", "#3f37c9", "#4361ee"],
    "大地棕调": ["#ede0d4", "#e6ccb2", "#ddb892", "#b08968", "#7f5539",
                "#9c6644", "#b07d62", "#ceb5a7"],
    "冰霜银白": ["#e0fbfc", "#c2dfe3", "#9db4c0", "#5c6b73", "#253237",
                "#98c1d9", "#6b9ac4", "#3b5998"],
}


# ============================================================
# 10个预设形状名称及对应的生成函数
# ============================================================
def _generate_circle_mask(size: int = 500) -> np.ndarray:
    """生成圆形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 10
    draw.ellipse([margin, margin, size - margin, size - margin], fill=255)
    return np.array(img)


def _generate_heart_mask(size: int = 500) -> np.ndarray:
    """生成心形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 20
    w, h = size - 2 * margin, size - 2 * margin
    # 使用多边形近似心形
    cx, cy = size / 2, size / 2
    points = []
    for i in range(360):
        t = np.radians(i)
        # 心形参数方程
        x = 16 * (np.sin(t) ** 3)
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        scale = min(w, h) / 34.0
        px = cx + x * scale
        py = cy - y * scale
        points.append((px, py))
    draw.polygon(points, fill=255)
    # 应用模糊使边缘平滑
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_star_mask(size: int = 500) -> np.ndarray:
    """生成五角星掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    outer_r = size / 2 - 15
    inner_r = outer_r * 0.4
    points = []
    for i in range(10):
        angle = np.radians(i * 36 - 90)
        r = outer_r if i % 2 == 0 else inner_r
        px = cx + r * np.cos(angle)
        py = cy + r * np.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_diamond_mask(size: int = 500) -> np.ndarray:
    """生成菱形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 20
    cx, cy = size / 2, size / 2
    r = size / 2 - margin
    points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_cloud_mask(size: int = 500) -> np.ndarray:
    """生成云朵形掩码（通过多个圆形叠加）"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 30
    cx, cy = size / 2, size / 2
    # 绘制重叠的圆形成云朵形状
    circles = [
        (cx - 80, cy + 20, 60),
        (cx - 20, cy - 20, 70),
        (cx + 60, cy + 10, 65),
        (cx + 120, cy + 40, 50),
        (cx + 20, cy + 50, 55),
        (cx - 50, cy + 60, 45),
        (cx + 40, cy - 40, 40),
        (cx, cy, 75),
    ]
    for (x, y, r) in circles:
        draw.ellipse([int(x - r), int(y - r), int(x + r), int(y + r)], fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=3))
    return np.array(img)


def _generate_triangle_mask(size: int = 500) -> np.ndarray:
    """生成三角形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 20
    cx, cy = size / 2, size / 2
    r = size / 2 - margin
    points = [(cx, cy - r), (cx + r * 0.866, cy + r * 0.5), (cx - r * 0.866, cy + r * 0.5)]
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_hexagon_mask(size: int = 500) -> np.ndarray:
    """生成六边形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size / 2 - 15
    points = []
    for i in range(6):
        angle = np.radians(i * 60 - 90)
        px = cx + r * np.cos(angle)
        py = cy + r * np.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_ellipse_mask(size: int = 500) -> np.ndarray:
    """生成椭圆形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 10
    draw.ellipse([margin, margin + 50, size - margin, size - margin - 50], fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_rounded_rect_mask(size: int = 500) -> np.ndarray:
    """生成圆角矩形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 20
    radius = 60
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius, fill=255
    )
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return np.array(img)


def _generate_speech_bubble_mask(size: int = 500) -> np.ndarray:
    """生成对话气泡形掩码"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    margin = 25
    tail_h = 60
    tail_w = 50
    # 主体圆角矩形
    body_rect = [margin, margin, size - margin, size - margin - tail_h - 10]
    draw.rounded_rectangle(body_rect, radius=50, fill=255)
    # 尾部三角形
    tail_points = [
        (size / 2 - tail_w / 2, size - margin - tail_h - 10),
        (size / 2 + tail_w / 2, size - margin - tail_h - 10),
        (size / 2, size - margin),
    ]
    draw.polygon(tail_points, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    return np.array(img)


# 形状名称到生成函数的映射
SHAPE_GENERATORS: Dict[str, callable] = {
    "圆形": _generate_circle_mask,
    "心形": _generate_heart_mask,
    "五角星": _generate_star_mask,
    "菱形": _generate_diamond_mask,
    "云朵": _generate_cloud_mask,
    "三角形": _generate_triangle_mask,
    "六边形": _generate_hexagon_mask,
    "椭圆形": _generate_ellipse_mask,
    "圆角矩形": _generate_rounded_rect_mask,
    "对话气泡": _generate_speech_bubble_mask,
}


# ============================================================
# 文本分析器
# ============================================================
class TextAnalyzer:
    """文本分析器：负责文本导入、分词、停用词过滤、词频统计"""

    def __init__(self):
        self._raw_text: str = ""
        self._words: List[str] = []
        self._word_freq: Counter = Counter()
        self._stop_words: set = BUILTIN_STOP_WORDS.copy()
        self._custom_stop_words: set = set()

    # ---------- 停用词管理 ----------
    @property
    def stop_words(self) -> set:
        return self._stop_words | self._custom_stop_words

    def add_stop_words(self, words: List[str]) -> None:
        for w in words:
            w = w.strip()
            if w:
                self._custom_stop_words.add(w)

    def remove_stop_words(self, words: List[str]) -> None:
        for w in words:
            w = w.strip()
            self._custom_stop_words.discard(w)
            self._stop_words.discard(w)

    def get_stop_words_list(self) -> List[str]:
        return sorted(self.stop_words)

    def get_custom_stop_words_list(self) -> List[str]:
        return sorted(self._custom_stop_words)

    # ---------- 文本导入 ----------
    @staticmethod
    def _read_txt(file_path: str) -> str:
        encodings = ["utf-8", "gbk", "gb2312", "utf-16", "latin-1"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise ValueError("无法识别的文本编码，已尝试 utf-8 / gbk / gb2312 / utf-16 / latin-1")

    @staticmethod
    def _read_docx(file_path: str) -> str:
        try:
            from docx import Document
        except ImportError:
            raise ImportError("请安装 python-docx 库：pip install python-docx")
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        # 优先使用 PyPDF2
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError("请安装 PyPDF2 库：pip install PyPDF2")

        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        result = "\n".join(text_parts).strip()

        # 如果 PyPDF2 提取效果不好，尝试 pdfplumber
        if not result or len(result) < 20:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    parts = []
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            parts.append(t)
                    result2 = "\n".join(parts).strip()
                    if len(result2) > len(result):
                        result = result2
            except ImportError:
                pass

        if not result:
            raise ValueError("无法从PDF中提取文本内容，PDF可能为扫描件或图片型PDF")
        return result

    def load_file(self, file_path: str) -> str:
        """导入文件并返回文本内容"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            text = self._read_txt(file_path)
        elif ext == ".docx":
            text = self._read_docx(file_path)
        elif ext == ".pdf":
            text = self._read_pdf(file_path)
        else:
            raise ValueError(f"不支持的文件格式：{ext}，仅支持 .txt / .docx / .pdf")
        self._raw_text = text
        return text

    # ---------- 分词 ----------
    def segment(self, text: str = None) -> List[str]:
        """中文分词，去除停用词"""
        if text is not None:
            self._raw_text = text
        if not self._raw_text:
            self._words = []
            self._word_freq = Counter()
            return []

        # 使用 jieba 精确模式分词
        words = jieba.lcut(self._raw_text)
        sw = self.stop_words

        # 过滤：至少2个字符，非纯数字/标点，非停用词，包含中文或字母
        filtered = []
        for w in words:
            w = w.strip()
            if len(w) < 2:
                continue
            if w in sw:
                continue
            # 保留包含中文、英文或数字的词汇
            if re.search(r'[\u4e00-\u9fff\uff00-\uffefa-zA-Z0-9]', w):
                filtered.append(w)

        self._words = filtered
        self._word_freq = Counter(filtered)
        return filtered

    # ---------- 词频统计 ----------
    def get_word_frequency(self, top_n: int = None) -> List[Tuple[str, int]]:
        """获取按频率降序排列的词频列表"""
        items = self._word_freq.most_common()
        if top_n is not None:
            items = items[:top_n]
        return items

    @property
    def raw_text(self) -> str:
        return self._raw_text

    @property
    def total_words(self) -> int:
        return len(self._words)

    @property
    def unique_words(self) -> int:
        return len(self._word_freq)


# ============================================================
# 词云生成器
# ============================================================
class WordCloudGenerator:
    """词云生成器：负责词云生成、形状处理、颜色配置、导出"""

    def __init__(self):
        self._wordcloud: Optional[WordCloud] = None
        self._mask_image: Optional[np.ndarray] = None
        self._current_shape: Optional[str] = None
        self._current_color_scheme: Optional[str] = None
        self._custom_mask_data: Optional[np.ndarray] = None
        self._use_image_colors: bool = False

    # ---------- 形状掩码 ----------
    def set_preset_shape(self, shape_name: str, size: int = 500) -> np.ndarray:
        """设置预设形状"""
        if shape_name not in SHAPE_GENERATORS:
            raise ValueError(f"未知形状：{shape_name}")
        self._current_shape = shape_name
        self._custom_mask_data = None
        self._use_image_colors = False
        mask = SHAPE_GENERATORS[shape_name](size)
        self._mask_image = mask
        return mask

    def load_custom_mask(self, image_path: str, size: int = 500) -> np.ndarray:
        """从图片加载自定义掩码"""
        img = Image.open(image_path).convert("L")
        img = img.resize((size, size), Image.LANCZOS)
        # 二值化处理
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0)
        mask = np.array(img)
        self._mask_image = mask
        self._custom_mask_data = mask
        self._current_shape = "自定义"
        return mask

    def load_custom_color_image(self, image_path: str, size: int = 500) -> np.ndarray:
        """加载自定义图片用于颜色提取和掩码"""
        img_color = Image.open(image_path).convert("RGB")
        img_color = img_color.resize((size, size), Image.LANCZOS)
        img_gray = img_color.convert("L")
        threshold = 128
        img_gray = img_gray.point(lambda p: 255 if p > threshold else 0)
        mask = np.array(img_gray)
        self._mask_image = mask
        self._custom_mask_data = mask
        self._current_shape = "自定义图片"
        self._use_image_colors = True
        self._color_image = np.array(img_color)
        return mask

    # ---------- 颜色方案 ----------
    @staticmethod
    def get_color_func(scheme_name: str):
        """根据颜色方案名称返回颜色函数"""
        if scheme_name in PRESET_COLOR_SCHEMES:
            colors = PRESET_COLOR_SCHEMES[scheme_name]

            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                idx = hash(word) % len(colors)
                return colors[idx]

            return color_func

        # matplotlib 内置 colormaps
        matplotlib_cmaps = [
            "viridis", "plasma", "inferno", "magma", "cividis",
            "twilight", "twilight_shifted", "turbo",
            "Blues", "Greens", "Oranges", "Reds", "Purples",
            "YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu", "BuPu",
            "GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn", "YlGn",
            "binary", "gist_yarg", "gist_gray", "gray", "bone",
            "pink", "spring", "summer", "autumn", "winter", "cool",
            "Wistia", "hot", "afmhot", "gist_heat", "copper",
        ]
        if scheme_name in matplotlib_cmaps:
            cmap = plt.get_cmap(scheme_name)

            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                rng = np.random.RandomState(hash(word) % (2 ** 32))
                return mcolors.rgb2hex(cmap(rng.random()))

            return color_func

        # 默认使用 viridis
        cmap = plt.get_cmap("viridis")

        def default_func(word, font_size, position, orientation, random_state=None, **kwargs):
            rng = np.random.RandomState(hash(word) % (2 ** 32))
            return mcolors.rgb2hex(cmap(rng.random()))

        return default_func

    def set_color_scheme(self, scheme_name: str) -> None:
        self._current_color_scheme = scheme_name

    def use_custom_colors(self, color_list: List[str]) -> None:
        """使用用户自定义颜色列表"""
        self._current_color_scheme = "__custom__"
        self._custom_colors = color_list

    # ---------- 生成词云 ----------
    def generate(
        self,
        word_freq: dict,
        width: int = 800,
        height: int = 600,
        font_path: str = None,
        background_color: str = "white",
        max_words: int = 200,
        max_font_size: int = None,
        min_font_size: int = 8,
        collocations: bool = False,
    ) -> WordCloud:
        """生成词云"""
        mask = self._mask_image

        # 设置字体
        if font_path is None:
            # 尝试常见的系统中文字体路径
            candidates = [
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/STKAITI.TTF",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            ]
            for fp in candidates:
                if os.path.exists(fp):
                    font_path = fp
                    break
            if font_path is None:
                font_path = "C:/Windows/Fonts/simhei.ttf"  # fallback

        # 确定颜色函数
        if self._use_image_colors and hasattr(self, '_color_image') and self._color_image is not None:
            color_func = ImageColorGenerator(self._color_image)
        else:
            color_func = self.get_color_func(self._current_color_scheme or "viridis")

        wc = WordCloud(
            width=width,
            height=height,
            font_path=font_path,
            background_color=background_color,
            mask=mask,
            max_words=max_words,
            max_font_size=max_font_size,
            min_font_size=min_font_size,
            color_func=color_func,
            collocations=collocations,
            random_state=42,
            prefer_horizontal=0.7,
        )
        wc.generate_from_frequencies(word_freq)
        self._wordcloud = wc
        return wc

    # ---------- 导出 ----------
    def export_image(self, file_path: str) -> None:
        """导出词云为图片"""
        if self._wordcloud is None:
            raise ValueError("请先生成词云")
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            file_path += ".png"

        # 使用 PIL 保存，wordcloud 直接提供了 to_image 方法
        img = self._wordcloud.to_image()
        # 如果掩码是自定义导入的且使用了图片颜色，保留透明背景
        img.save(file_path, quality=95)
        self._export_path = file_path

    def export_array(self) -> np.ndarray:
        """获取词云图像的 numpy 数组"""
        if self._wordcloud is None:
            raise ValueError("请先生成词云")
        return np.array(self._wordcloud.to_image())

    @property
    def wordcloud_obj(self) -> Optional[WordCloud]:
        return self._wordcloud


# ============================================================
# 主 GUI 应用程序
# ============================================================
class TextAnalysisApp:
    """文本分析系统 GUI 主程序 —— 白色科幻风格"""

    # ---------- 配色常量（白色科幻风格）----------
    BG_MAIN = "#ffffff"
    BG_LEFT = "#f5f7fa"
    BG_RIGHT = "#ffffff"
    BG_TITLE = "#1a1a2e"
    ACCENT_PRIMARY = "#0f3460"
    ACCENT_SECONDARY = "#16213e"
    ACCENT_HIGHLIGHT = "#e94560"
    TEXT_PRIMARY = "#1a1a2e"
    TEXT_SECONDARY = "#4a4a6a"
    TEXT_LIGHT = "#7a7a9a"
    BORDER_COLOR = "#e0e4e8"
    BUTTON_BG = "#16213e"
    BUTTON_FG = "#ffffff"
    BUTTON_HOVER = "#0f3460"
    INPUT_BG = "#ffffff"
    PANEL_BG = "#f8f9fb"
    TABLE_BG = "#ffffff"
    TABLE_HEADER_BG = "#16213e"
    TABLE_HEADER_FG = "#ffffff"
    TABLE_ROW_ALT = "#f5f7fa"
    SCROLL_BG = "#e0e4e8"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文本分析系统 - TextLens")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        self.root.configure(bg=self.BG_MAIN)

        # 初始化模块
        self.analyzer = TextAnalyzer()
        self.generator = WordCloudGenerator()

        # 状态变量
        self.current_file_path: Optional[str] = None
        self.current_preview_image: Optional[Image.Image] = None

        # 构建界面
        self._build_ui()

        # 设置默认形状和颜色
        self.generator.set_preset_shape("圆形")
        self.generator.set_color_scheme("海洋蓝调")
        self.shape_var.set("圆形")
        self.color_var.set("海洋蓝调")

        # 显示初始提示
        self._show_welcome()

    # ============================================================
    # UI 构建
    # ============================================================
    def _build_ui(self) -> None:
        """构建整体界面"""
        # 顶部标题栏
        self._build_title_bar()

        # 主内容区（左操作区 + 右显示区）
        self.main_paned = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL,
            bg=self.BORDER_COLOR, sashwidth=2, sashrelief=tk.FLAT
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 左侧操作面板
        self.left_frame = self._build_left_panel()
        # 右侧显示面板
        self.right_frame = self._build_right_panel()

        self.main_paned.add(self.left_frame, minsize=380, width=400)
        self.main_paned.add(self.right_frame, minsize=600, width=800)

        # 底部状态栏
        self._build_status_bar()

        # 设置 ttk 样式
        self._setup_ttk_styles()

    def _build_title_bar(self) -> None:
        """顶部标题栏"""
        title_frame = tk.Frame(self.root, bg=self.BG_TITLE, height=52)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="TEXTLENS · 文本分析系统",
            font=("Microsoft YaHei UI", 16, "bold"),
            fg="#ffffff",
            bg=self.BG_TITLE,
        )
        title_label.pack(side=tk.LEFT, padx=24, pady=10)

        subtitle_label = tk.Label(
            title_frame,
            text="多格式导入 · 中文分词 · 词频统计 · 词云可视化",
            font=("Microsoft YaHei UI", 9),
            fg="#8899aa",
            bg=self.BG_TITLE,
        )
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=15)

    def _setup_ttk_styles(self) -> None:
        """配置 ttk 样式"""
        style = ttk.Style()
        style.theme_use("clam")

        # 配置各个组件样式
        style.configure(
            "TNotebook",
            background=self.BG_MAIN,
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=self.PANEL_BG,
            foreground=self.TEXT_SECONDARY,
            padding=[18, 8],
            font=("Microsoft YaHei UI", 10),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.BG_MAIN)],
            foreground=[("selected", self.ACCENT_PRIMARY)],
            expand=[("selected", [0, 0, 0, 0])],
        )

        style.configure(
            "Treeview",
            background=self.TABLE_BG,
            foreground=self.TEXT_PRIMARY,
            rowheight=28,
            fieldbackground=self.TABLE_BG,
            borderwidth=0,
            font=("Microsoft YaHei UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=self.TABLE_HEADER_BG,
            foreground=self.TABLE_HEADER_FG,
            font=("Microsoft YaHei UI", 9, "bold"),
            borderwidth=0,
            padding=[8, 4],
        )
        style.map(
            "Treeview.Heading",
            background=[("active", self.ACCENT_PRIMARY)],
        )

        style.configure(
            "TLabelframe",
            background=self.BG_LEFT,
            borderwidth=0,
        )
        style.configure(
            "TLabelframe.Label",
            background=self.BG_LEFT,
            foreground=self.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10, "bold"),
        )

        style.configure(
            "TCombobox",
            padding=[8, 4],
            font=("Microsoft YaHei UI", 9),
        )

    def _create_section_label(self, parent: tk.Widget, text: str) -> tk.Frame:
        """创建区域分隔标题"""
        frame = tk.Frame(parent, bg=self.BG_LEFT, height=32)
        frame.pack(fill=tk.X, pady=(12, 4), padx=10)

        indicator = tk.Frame(frame, bg=self.ACCENT_HIGHLIGHT, width=3, height=18)
        indicator.pack(side=tk.LEFT, padx=(0, 8))

        label = tk.Label(
            frame,
            text=text,
            font=("Microsoft YaHei UI", 11, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_LEFT,
        )
        label.pack(side=tk.LEFT)
        return frame

    def _create_styled_button(
        self, parent: tk.Widget, text: str, command,
        width: int = None, accent: bool = False
    ) -> tk.Button:
        """创建统一样式的按钮"""
        bg = self.ACCENT_HIGHLIGHT if accent else self.BUTTON_BG
        fg = "#ffffff"

        btn = tk.Button(
            parent, text=text, command=command,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=bg, fg=fg,
            activebackground=self.ACCENT_PRIMARY,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16, pady=6,
            borderwidth=0,
            highlightthickness=0,
        )
        if width:
            btn.configure(width=width)

        # 悬停效果
        def on_enter(e):
            btn.configure(bg=self.ACCENT_PRIMARY)

        def on_leave(e):
            btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ============================================================
    # 左侧操作面板
    # ============================================================
    def _build_left_panel(self) -> tk.Frame:
        """构建左侧操作面板"""
        left = tk.Frame(self.root, bg=self.BG_LEFT, width=400)

        # Canvas + Scrollbar 实现滚动
        canvas = tk.Canvas(left, bg=self.BG_LEFT, highlightthickness=0)
        scrollbar = tk.Scrollbar(left, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.BG_LEFT)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", on_canvas_configure)

        # 鼠标滚轮支持
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- 区块 1: 文件导入 ---
        self._create_section_label(scrollable_frame, "📁 文件导入")
        import_frame = tk.Frame(scrollable_frame, bg=self.BG_LEFT, padx=10)
        import_frame.pack(fill=tk.X)

        btn_frame = tk.Frame(import_frame, bg=self.BG_LEFT)
        btn_frame.pack(fill=tk.X, pady=(2, 6))

        self.btn_open = self._create_styled_button(
            btn_frame, "打开文件", self._on_open_file, accent=True
        )
        self.btn_open.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_clear = self._create_styled_button(
            btn_frame, "清空文本", self._on_clear_text
        )
        self.btn_clear.pack(side=tk.LEFT)

        self.file_path_var = tk.StringVar(value="未选择文件")
        file_label = tk.Label(
            import_frame,
            textvariable=self.file_path_var,
            font=("Microsoft YaHei UI", 8),
            fg=self.TEXT_LIGHT,
            bg=self.BG_LEFT,
            anchor="w",
            wraplength=350,
        )
        file_label.pack(fill=tk.X, pady=(0, 4))

        # --- 区块 2: 分析与分词 ---
        self._create_section_label(scrollable_frame, "🔍 分析与分词")
        analysis_frame = tk.Frame(scrollable_frame, bg=self.BG_LEFT, padx=10)
        analysis_frame.pack(fill=tk.X)

        self.btn_analyze = self._create_styled_button(
            analysis_frame, "开始分析", self._on_analyze, accent=True
        )
        self.btn_analyze.pack(fill=tk.X, pady=(2, 4))

        # 分析参数
        param_frame = tk.Frame(analysis_frame, bg=self.BG_LEFT)
        param_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            param_frame, text="显示词数:", bg=self.BG_LEFT,
            fg=self.TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT)
        self.top_n_var = tk.StringVar(value="100")
        top_n_entry = tk.Entry(
            param_frame, textvariable=self.top_n_var,
            width=6, font=("Microsoft YaHei UI", 9),
            bg=self.INPUT_BG, relief=tk.SOLID,
            borderwidth=1, highlightthickness=0,
        )
        top_n_entry.pack(side=tk.LEFT, padx=(6, 0))

        # 统计信息
        self.stats_var = tk.StringVar(value="总词数: 0 | 独立词数: 0")
        stats_label = tk.Label(
            analysis_frame,
            textvariable=self.stats_var,
            font=("Microsoft YaHei UI", 8),
            fg=self.TEXT_LIGHT,
            bg=self.BG_LEFT,
            anchor="w",
        )
        stats_label.pack(fill=tk.X, pady=(0, 4))

        # --- 区块 3: 停用词管理 ---
        self._create_section_label(scrollable_frame, "🚫 停用词管理")
        stop_frame = tk.Frame(scrollable_frame, bg=self.BG_LEFT, padx=10)
        stop_frame.pack(fill=tk.X)

        stop_input_frame = tk.Frame(stop_frame, bg=self.BG_LEFT)
        stop_input_frame.pack(fill=tk.X, pady=(2, 4))
        tk.Label(
            stop_input_frame, text="添加:", bg=self.BG_LEFT,
            fg=self.TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT)
        self.stop_add_var = tk.StringVar()
        stop_add_entry = tk.Entry(
            stop_input_frame, textvariable=self.stop_add_var,
            font=("Microsoft YaHei UI", 9),
            bg=self.INPUT_BG, relief=tk.SOLID,
            borderwidth=1, highlightthickness=0,
        )
        stop_add_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 4))
        btn_add_stop = self._create_styled_button(
            stop_input_frame, "+", self._on_add_stop_word, width=3
        )
        btn_add_stop.pack(side=tk.RIGHT)

        # 自定义停用词列表显示
        self.stop_listbox = tk.Listbox(
            stop_frame, height=5,
            font=("Microsoft YaHei UI", 9),
            bg=self.INPUT_BG, fg=self.TEXT_PRIMARY,
            selectbackground=self.ACCENT_PRIMARY,
            selectforeground="#ffffff",
            relief=tk.SOLID, borderwidth=1,
            highlightthickness=0,
        )
        self.stop_listbox.pack(fill=tk.X, pady=(0, 2))

        stop_btn_frame = tk.Frame(stop_frame, bg=self.BG_LEFT)
        stop_btn_frame.pack(fill=tk.X, pady=(0, 4))
        btn_remove_stop = self._create_styled_button(
            stop_btn_frame, "移除选中", self._on_remove_stop_word
        )
        btn_remove_stop.pack(side=tk.LEFT, padx=(0, 4))
        btn_reset_stop = self._create_styled_button(
            stop_btn_frame, "恢复默认", self._on_reset_stop_words
        )
        btn_reset_stop.pack(side=tk.LEFT)

        # --- 区块 4: 词云形状 ---
        self._create_section_label(scrollable_frame, "⬡ 词云形状")
        shape_frame = tk.Frame(scrollable_frame, bg=self.BG_LEFT, padx=10)
        shape_frame.pack(fill=tk.X)

        tk.Label(
            shape_frame, text="预设形状:", bg=self.BG_LEFT,
            fg=self.TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)
        ).pack(anchor="w")

        self.shape_var = tk.StringVar()
        shape_combo = ttk.Combobox(
            shape_frame, textvariable=self.shape_var,
            values=list(SHAPE_GENERATORS.keys()),
            state="readonly", font=("Microsoft YaHei UI", 9),
        )
        shape_combo.pack(fill=tk.X, pady=(2, 4))
        shape_combo.bind("<<ComboboxSelected>>", self._on_shape_changed)

        tk.Label(
            shape_frame, text="自定义形状 (导入图片):", bg=self.BG_LEFT,
            fg=self.TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)
        ).pack(anchor="w")

        mask_btn_frame = tk.Frame(shape_frame, bg=self.BG_LEFT)
        mask_btn_frame.pack(fill=tk.X, pady=(2, 4))
        btn_load_mask = self._create_styled_button(
            mask_btn_frame, "导入形状图片", self._on_load_mask_image
        )
        btn_load_mask.pack(side=tk.LEFT, padx=(0, 4))
        btn_load_color_img = self._create_styled_button(
            mask_btn_frame, "导入彩色图片", self._on_load_color_image
        )
        btn_load_color_img.pack(side=tk.LEFT)

        self.mask_info_var = tk.StringVar(value="")
        mask_info_label = tk.Label(
            shape_frame, textvariable=self.mask_info_var,
            font=("Microsoft YaHei UI", 8),
            fg=self.TEXT_LIGHT, bg=self.BG_LEFT, anchor="w",
        )
        mask_info_label.pack(fill=tk.X, pady=(0, 4))

        # --- 区块 5: 颜色配置 ---
        self._create_section_label(scrollable_frame, "🎨 颜色配置")
        color_frame = tk.Frame(scrollable_frame, bg=self.BG_LEFT, padx=10)
        color_frame.pack(fill=tk.X)

        self.color_var = tk.StringVar()
        color_combo = ttk.Combobox(
            color_frame, textvariable=self.color_var,
            values=list(PRESET_COLOR_SCHEMES.keys()),
            state="readonly", font=("Microsoft YaHei UI", 9),
        )
        color_combo.pack(fill=tk.X, pady=(2, 4))
        color_combo.bind("<<ComboboxSelected>>", self._on_color_changed)

        # 自定义颜色
        tk.Label(
            color_frame, text="自定义颜色 (逗号分隔，#RRGGBB):", bg=self.BG_LEFT,
            fg=self.TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)
        ).pack(anchor="w")

        custom_color_frame = tk.Frame(color_frame, bg=self.BG_LEFT)
        custom_color_frame.pack(fill=tk.X, pady=(2, 4))
        self.custom_color_var = tk.StringVar()
        custom_color_entry = tk.Entry(
            custom_color_frame, textvariable=self.custom_color_var,
            font=("Microsoft YaHei UI", 9),
            bg=self.INPUT_BG, relief=tk.SOLID,
            borderwidth=1, highlightthickness=0,
        )
        custom_color_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        btn_apply_custom = self._create_styled_button(
            custom_color_frame, "应用", self._on_apply_custom_colors, width=6
        )
        btn_apply_custom.pack(side=tk.RIGHT)

        # --- 区块 6: 生成与导出 ---
        self._create_section_label(scrollable_frame, "📊 生成与导出")
        export_frame = tk.Frame(scrollable_frame, bg=self.BG_LEFT, padx=10)
        export_frame.pack(fill=tk.X)

        self.btn_generate = self._create_styled_button(
            export_frame, "生成词云", self._on_generate_wordcloud, accent=True
        )
        self.btn_generate.pack(fill=tk.X, pady=(2, 4))

        self.btn_export = self._create_styled_button(
            export_frame, "导出词云图片 (PNG/JPG)", self._on_export_image
        )
        self.btn_export.pack(fill=tk.X, pady=(0, 6))

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            export_frame, variable=self.progress_var,
            mode="indeterminate", length=350,
        )

        return left

    # ============================================================
    # 右侧显示面板
    # ============================================================
    def _build_right_panel(self) -> tk.Frame:
        """构建右侧显示面板（选项卡式）"""
        right = tk.Frame(self.root, bg=self.BG_MAIN)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Tab 1: 文本预览
        self.tab_text = self._build_text_tab()
        # Tab 2: 词频统计
        self.tab_freq = self._build_frequency_tab()
        # Tab 3: 词云预览
        self.tab_cloud = self._build_cloud_tab()

        self.notebook.add(self.tab_text, text="  文本预览  ")
        self.notebook.add(self.tab_freq, text="  词汇统计  ")
        self.notebook.add(self.tab_cloud, text="  词云预览  ")

        return right

    def _build_text_tab(self) -> tk.Frame:
        """文本预览选项卡"""
        frame = tk.Frame(self.notebook, bg=self.BG_MAIN)

        info_frame = tk.Frame(frame, bg=self.BG_MAIN, height=30)
        info_frame.pack(fill=tk.X, padx=10, pady=(6, 2))
        self.text_info_var = tk.StringVar(value="文本长度: 0 字符")
        tk.Label(
            info_frame, textvariable=self.text_info_var,
            font=("Microsoft YaHei UI", 9),
            fg=self.TEXT_LIGHT, bg=self.BG_MAIN,
        ).pack(side=tk.LEFT)

        text_container = tk.Frame(frame, bg=self.BG_MAIN)
        text_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        self.text_display = scrolledtext.ScrolledText(
            text_container,
            font=("Microsoft YaHei UI", 10),
            bg=self.BG_MAIN,
            fg=self.TEXT_PRIMARY,
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=0,
            insertbackground=self.ACCENT_PRIMARY,
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)

        # 设置内边距
        self.text_display.configure(padx=12, pady=10)

        return frame

    def _build_frequency_tab(self) -> tk.Frame:
        """词频统计选项卡"""
        frame = tk.Frame(self.notebook, bg=self.BG_MAIN)

        info_frame = tk.Frame(frame, bg=self.BG_MAIN, height=30)
        info_frame.pack(fill=tk.X, padx=10, pady=(6, 2))
        self.freq_info_var = tk.StringVar(value="共 0 个词汇")
        tk.Label(
            info_frame, textvariable=self.freq_info_var,
            font=("Microsoft YaHei UI", 9),
            fg=self.TEXT_LIGHT, bg=self.BG_MAIN,
        ).pack(side=tk.LEFT)

        # Treeview 词频表
        tree_container = tk.Frame(frame, bg=self.BORDER_COLOR)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        columns = ("rank", "word", "frequency")
        self.freq_tree = ttk.Treeview(
            tree_container, columns=columns,
            show="headings", selectmode="browse",
        )
        self.freq_tree.heading("rank", text="序号")
        self.freq_tree.heading("word", text="词汇")
        self.freq_tree.heading("frequency", text="频次")

        self.freq_tree.column("rank", width=60, anchor="center")
        self.freq_tree.column("word", width=320, anchor="w")
        self.freq_tree.column("frequency", width=80, anchor="center")

        # 滚动条
        tree_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL,
            command=self.freq_tree.yview,
        )
        self.freq_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.freq_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 行颜色交替
        self.freq_tree.tag_configure("even", background=self.TABLE_ROW_ALT)
        self.freq_tree.tag_configure("odd", background=self.TABLE_BG)

        return frame

    def _build_cloud_tab(self) -> tk.Frame:
        """词云预览选项卡"""
        frame = tk.Frame(self.notebook, bg=self.BG_MAIN)

        info_frame = tk.Frame(frame, bg=self.BG_MAIN, height=30)
        info_frame.pack(fill=tk.X, padx=10, pady=(6, 2))
        self.cloud_info_var = tk.StringVar(value="尚未生成词云")
        tk.Label(
            info_frame, textvariable=self.cloud_info_var,
            font=("Microsoft YaHei UI", 9),
            fg=self.TEXT_LIGHT, bg=self.BG_MAIN,
        ).pack(side=tk.LEFT)

        # 词云显示画布
        cloud_container = tk.Frame(frame, bg=self.BORDER_COLOR)
        cloud_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        self.cloud_canvas = tk.Canvas(
            cloud_container,
            bg=self.BG_MAIN,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.cloud_canvas.pack(fill=tk.BOTH, expand=True)

        return frame

    def _build_status_bar(self) -> None:
        """底部状态栏"""
        status_frame = tk.Frame(self.root, bg=self.BG_TITLE, height=26)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value="就绪 - 等待操作...")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Microsoft YaHei UI", 8),
            fg="#8899aa",
            bg=self.BG_TITLE,
            anchor="w",
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, padx=16, pady=3)

        self.status_icon_var = tk.StringVar(value="●")
        icon_label = tk.Label(
            status_frame,
            textvariable=self.status_icon_var,
            font=("Microsoft YaHei UI", 8),
            fg="#4ecdc4",
            bg=self.BG_TITLE,
        )
        icon_label.pack(side=tk.RIGHT, padx=16, pady=3)

    # ============================================================
    # 事件处理
    # ============================================================
    def _set_status(self, text: str, color: str = "#4ecdc4") -> None:
        self.status_var.set(text)
        self.status_icon_var.set("●")
        self.root.update_idletasks()

    def _show_welcome(self) -> None:
        """显示欢迎信息"""
        self.text_display.delete("1.0", tk.END)
        welcome_msg = (
            "欢迎使用 TextLens 文本分析系统\n"
            "══════════════════════════════\n\n"
            "操作步骤:\n"
            "  1. 点击「打开文件」导入文本文件（支持 .txt / .docx / .pdf）\n"
            "  2. 点击「开始分析」进行中文分词和词频统计\n"
            "  3. 选择词云形状和颜色方案\n"
            "  4. 点击「生成词云」查看可视化结果\n"
            "  5. 点击「导出词云图片」保存结果\n\n"
            "提示：\n"
            "  · 可在「停用词管理」中添加或删除停用词\n"
            "  · 支持导入图片作为自定义形状\n"
            "  · 支持自定义颜色方案\n"
        )
        self.text_display.insert("1.0", welcome_msg)
        self.text_display.configure(state=tk.NORMAL)

    # --- 文件导入 ---
    def _on_open_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[
                ("文本文件", "*.txt;*.docx;*.pdf"),
                ("TXT 文件", "*.txt"),
                ("Word 文档", "*.docx"),
                ("PDF 文件", "*.pdf"),
                ("所有文件", "*.*"),
            ],
        )
        if not file_path:
            return

        self._set_status("正在导入文件...", "#f9ca24")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))
        self.progress_bar.start()

        def _load():
            try:
                text = self.analyzer.load_file(file_path)
                self.current_file_path = file_path
                self.file_path_var.set(os.path.basename(file_path))

                self.root.after(0, lambda: self._on_file_loaded(text, file_path))
            except Exception as e:
                self.root.after(0, lambda: self._on_load_error(str(e)))

        threading.Thread(target=_load, daemon=True).start()

    def _on_file_loaded(self, text: str, file_path: str) -> None:
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # 显示文本预览
        self.text_display.delete("1.0", tk.END)
        preview_len = min(len(text), 10000)
        self.text_display.insert("1.0", text[:preview_len])
        if len(text) > 10000:
            self.text_display.insert(tk.END, f"\n\n... (文本过长，仅显示前 10000 字符，共 {len(text)} 字符)")

        self.text_info_var.set(f"文本长度: {len(text)} 字符 | 文件: {os.path.basename(file_path)}")
        self._set_status(f"文件导入成功: {os.path.basename(file_path)}")
        self.notebook.select(self.tab_text)

    def _on_load_error(self, error: str) -> None:
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        messagebox.showerror("导入错误", f"文件导入失败：\n{error}")
        self._set_status(f"导入失败: {error}", "#e94560")

    def _on_clear_text(self) -> None:
        self.analyzer = TextAnalyzer()
        self.generator = WordCloudGenerator()
        self.current_file_path = None
        self.file_path_var.set("未选择文件")
        self.text_display.delete("1.0", tk.END)
        self.text_info_var.set("文本长度: 0 字符")

        # 清空词频表
        for item in self.freq_tree.get_children():
            self.freq_tree.delete(item)
        self.freq_info_var.set("共 0 个词汇")
        self.stats_var.set("总词数: 0 | 独立词数: 0")

        # 清空词云
        self.cloud_canvas.delete("all")
        self.cloud_info_var.set("尚未生成词云")
        self.current_preview_image = None

        # 恢复默认形状和颜色
        self.generator.set_preset_shape("圆形")
        self.generator.set_color_scheme("海洋蓝调")
        self.mask_info_var.set("")
        self._show_welcome()
        self._set_status("已清空所有内容")

    # --- 分析与分词 ---
    def _on_analyze(self) -> None:
        if not self.analyzer.raw_text:
            messagebox.showwarning("提示", "请先导入文本文件")
            return

        self._set_status("正在进行中文分词和词频统计...", "#f9ca24")

        def _analyze():
            try:
                words = self.analyzer.segment()
                freq = self.analyzer.get_word_frequency()
                self.root.after(0, lambda: self._on_analysis_done(words, freq))
            except Exception as e:
                self.root.after(0, lambda: self._on_analysis_error(str(e)))

        threading.Thread(target=_analyze, daemon=True).start()

    def _on_analysis_done(self, words: List[str], freq: List[Tuple[str, int]]) -> None:
        # 更新统计信息
        self.stats_var.set(f"总词数: {self.analyzer.total_words} | 独立词数: {self.analyzer.unique_words}")

        # 更新词频表
        for item in self.freq_tree.get_children():
            self.freq_tree.delete(item)

        try:
            top_n = int(self.top_n_var.get())
        except ValueError:
            top_n = 100

        display_freq = freq[:top_n]
        for i, (word, count) in enumerate(display_freq):
            tag = "even" if i % 2 == 0 else "odd"
            self.freq_tree.insert("", tk.END, values=(i + 1, word, count), tags=(tag,))

        self.freq_info_var.set(f"共 {len(freq)} 个词汇，显示前 {len(display_freq)} 个")
        self._set_status(f"分析完成: {self.analyzer.total_words} 个词汇, {self.analyzer.unique_words} 个独立词")
        self.notebook.select(self.tab_freq)

    def _on_analysis_error(self, error: str) -> None:
        messagebox.showerror("分析错误", f"分词失败：\n{error}")
        self._set_status(f"分析失败: {error}", "#e94560")

    # --- 停用词管理 ---
    def _on_add_stop_word(self) -> None:
        word = self.stop_add_var.get().strip()
        if not word:
            return
        self.analyzer.add_stop_words([word])
        self._refresh_stop_list()
        self.stop_add_var.set("")
        self._set_status(f"已添加停用词: {word}")

    def _on_remove_stop_word(self) -> None:
        selection = self.stop_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要移除的停用词")
            return
        words = [self.stop_listbox.get(idx) for idx in selection]
        self.analyzer.remove_stop_words(words)
        self._refresh_stop_list()
        self._set_status(f"已移除停用词: {', '.join(words)}")

    def _on_reset_stop_words(self) -> None:
        self.analyzer = TextAnalyzer()
        self._refresh_stop_list()
        self._set_status("已恢复默认停用词表")

    def _refresh_stop_list(self) -> None:
        self.stop_listbox.delete(0, tk.END)
        for word in self.analyzer.get_custom_stop_words_list():
            self.stop_listbox.insert(tk.END, word)

    # --- 形状选择 ---
    def _on_shape_changed(self, event=None) -> None:
        shape_name = self.shape_var.get()
        try:
            self.generator.set_preset_shape(shape_name)
            self.mask_info_var.set(f"当前形状: {shape_name}")
            self._set_status(f"已选择形状: {shape_name}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _on_load_mask_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="选择形状图片（黑白轮廓效果最佳）",
            filetypes=[
                ("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("所有文件", "*.*"),
            ],
        )
        if not file_path:
            return
        try:
            self.generator.load_custom_mask(file_path)
            self.mask_info_var.set(f"当前形状: 自定义 ({os.path.basename(file_path)})")
            self.shape_var.set("自定义")
            self._set_status(f"已加载自定义形状: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载形状图片失败：\n{e}")

    def _on_load_color_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="选择彩色图片（将提取形状和颜色）",
            filetypes=[
                ("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("所有文件", "*.*"),
            ],
        )
        if not file_path:
            return
        try:
            self.generator.load_custom_color_image(file_path)
            self.mask_info_var.set(f"当前: 自定义彩色 ({os.path.basename(file_path)})")
            self.shape_var.set("自定义图片")
            self._set_status(f"已加载彩色图片: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载彩色图片失败：\n{e}")

    # --- 颜色选择 ---
    def _on_color_changed(self, event=None) -> None:
        scheme_name = self.color_var.get()
        self.generator.set_color_scheme(scheme_name)
        self._set_status(f"已选择颜色方案: {scheme_name}")

    def _on_apply_custom_colors(self) -> None:
        raw = self.custom_color_var.get().strip()
        if not raw:
            messagebox.showwarning("提示", "请输入颜色值")
            return
        colors = [c.strip() for c in raw.split(",") if c.strip()]
        if not colors:
            messagebox.showwarning("提示", "请输入有效的颜色值（#RRGGBB 格式，逗号分隔）")
            return
        # 验证颜色格式
        for c in colors:
            if not re.match(r'^#[0-9a-fA-F]{6}$', c):
                messagebox.showwarning("颜色格式错误", f"无效的颜色值: {c}\n请使用 #RRGGBB 格式")
                return
        self.generator.use_custom_colors(colors)
        self.color_var.set("自定义")
        self._set_status(f"已应用自定义颜色: {len(colors)} 种颜色")

    # --- 生成词云 ---
    def _on_generate_wordcloud(self) -> None:
        if not self.analyzer._word_freq:
            messagebox.showwarning("提示", "请先导入文本并进行分析")
            return

        self._set_status("正在生成词云，请稍候...", "#f9ca24")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))
        self.progress_bar.start()

        def _generate():
            try:
                freq_dict = dict(self.analyzer.get_word_frequency(200))
                wc = self.generator.generate(
                    word_freq=freq_dict,
                    width=800,
                    height=600,
                    background_color="white",
                    max_words=200,
                )
                self.root.after(0, lambda: self._on_cloud_generated(wc))
            except Exception as e:
                self.root.after(0, lambda: self._on_cloud_error(str(e)))

        threading.Thread(target=_generate, daemon=True).start()

    def _on_cloud_generated(self, wc: WordCloud) -> None:
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # 在画布上显示
        img = wc.to_image()
        self.current_preview_image = img

        # 缩放以适应画布
        canvas_w = self.cloud_canvas.winfo_width()
        canvas_h = self.cloud_canvas.winfo_height()

        if canvas_w < 100:
            canvas_w = 750
        if canvas_h < 100:
            canvas_h = 550

        img_w, img_h = img.size
        ratio = min(canvas_w / img_w, canvas_h / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)

        # 使用 PIL 缩放
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # 转换为 PhotoImage
        self._tk_image = self._pil_to_tk(resized)

        # 更新画布
        self.cloud_canvas.delete("all")
        self.cloud_canvas.create_image(
            canvas_w // 2, canvas_h // 2,
            image=self._tk_image, anchor=tk.CENTER,
        )

        shape_name = self.generator._current_shape or "默认"
        color_name = self.generator._current_color_scheme or "默认"
        self.cloud_info_var.set(
            f"词云已生成 | 形状: {shape_name} | 颜色: {color_name} | "
            f"词汇数: {self.analyzer.unique_words}"
        )
        self._set_status("词云生成成功！")
        self.notebook.select(self.tab_cloud)

    def _on_cloud_error(self, error: str) -> None:
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        messagebox.showerror("生成错误", f"词云生成失败：\n{error}")
        self._set_status(f"生成失败: {error}", "#e94560")

    # --- 导出图片 ---
    def _on_export_image(self) -> None:
        if self.generator.wordcloud_obj is None:
            messagebox.showwarning("提示", "请先生成词云")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出词云图片",
            defaultextension=".png",
            filetypes=[
                ("PNG 图片", "*.png"),
                ("JPEG 图片", "*.jpg;*.jpeg"),
            ],
        )
        if not file_path:
            return

        try:
            self.generator.export_image(file_path)
            self._set_status(f"词云已导出: {os.path.basename(file_path)}")
            messagebox.showinfo("导出成功", f"词云图片已保存至:\n{file_path}")
        except Exception as e:
            messagebox.showerror("导出错误", f"导出失败：\n{e}")

    # ============================================================
    # 工具方法
    # ============================================================
    @staticmethod
    def _pil_to_tk(image: Image.Image) -> tk.PhotoImage:
        """将 PIL Image 转换为 Tkinter PhotoImage"""
        from io import BytesIO
        buf = BytesIO()
        image.save(buf, format="PNG")
        return tk.PhotoImage(data=buf.getvalue())

    def run(self) -> None:
        """启动应用程序"""
        self.root.mainloop()


# ============================================================
# 主入口
# ============================================================
def main():
    """程序入口"""
    # 检查依赖
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
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")

    if missing:
        print("缺少必要的依赖库，请运行以下命令安装：")
        print(f"pip install {' '.join(missing)}")
        print("\n或者一次性安装所有依赖：")
        print("pip install jieba wordcloud pillow numpy matplotlib python-docx PyPDF2 pdfplumber")
        sys.exit(1)

    # 对于 docx 和 PDF 支持库给出友好提示
    try:
        from docx import Document
    except ImportError:
        print("[提示] 如需导入 .docx 文件，请安装：pip install python-docx")
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("[提示] 如需导入 .pdf 文件，请安装：pip install PyPDF2")
        print("[提示] 为提高 PDF 提取质量，推荐同时安装：pip install pdfplumber")

    app = TextAnalysisApp()
    app.run()


if __name__ == "__main__":
    main()