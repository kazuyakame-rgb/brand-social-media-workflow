#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mode A 后期叠字（PIL）—— 把文案与 logo 精确压到留白底图上，中文零错字、改字秒级。

用法:
  python overlay_text.py overlay.json
  python overlay_text.py overlay.json --preview     # 只打印布局，不写文件

JSON 配置:
{
  "base":   "base.png",          // 无文字底图
  "output": "out.png",
  "logo": {                      // 可选
    "path": "logo.png",
    "x": 0.06, "y": 0.05,        // 相对宽/高的比例，指 logo 左上角
    "width_ratio": 0.18          // logo 宽度 = 图宽 * 该比例
  },
  "blocks": [
    {
      "text": "主标题文字",
      "font": "msyhbd.ttc",      // 文件名（自动到系统字体目录找）或绝对路径
      "size_ratio": 0.05,        // 字号 = 图宽 * 该比例
      "color": "#1B3A5C",
      "letter_spacing": 0.06,    // 字距 = 字号 * 该比例（中文建议 0.04-0.10）
      "line_gap": 0.35,          // 行距 = 字号 * 该比例
      "x": 0.5, "y": 0.30,       // 该文字块中心点（相对比例）
      "align": "center",         // center | left | right
      "max_width_ratio": 0.82,   // 超宽自动缩字号
      "underline": {"color": "#C8A86B", "height_ratio": 0.06, "offset": 0.10, "width_ratio": 1.0}
    }
  ]
}

坐标约定: x/y 均为相对整图宽/高的 0-1 比例；y 指该文字块整体的垂直中心。
字体: 未安装指定字体时自动回退到系统默认字体（会在 stderr 提示）。
"""
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFont

FONT_DIRS = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    "/usr/share/fonts", "/usr/local/share/fonts",
    os.path.expanduser("~/Library/Fonts"), "/Library/Fonts", "/System/Library/Fonts",
]


def resolve_font(name, size):
    """按文件名或绝对路径解析字体；找不到则回退默认字体。"""
    if name and os.path.isabs(name) and os.path.exists(name):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    if name:
        for d in FONT_DIRS:
            hits = glob.glob(os.path.join(d, "**", name), recursive=True) if os.path.isdir(d) else []
            if hits:
                try:
                    return ImageFont.truetype(hits[0], size)
                except Exception:
                    continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def text_size(draw, s, font):
    """兼容新旧 Pillow 的通用测量。"""
    try:
        l, t, r, b = draw.textbbox((0, 0), s, font=font)
        return r - l, b - t
    except AttributeError:
        return draw.textsize(s, font=font)


def draw_spaced(draw, s, font, color, letter_px):
    """逐字绘制以支持字距；返回总宽度。"""
    x = 0.0
    for ch in s:
        draw.text((x, 0), ch, font=font, fill=color)
        w, _ = text_size(draw, ch, font)
        x += w + letter_px
    return max(0.0, x - letter_px)


def measure_spaced(draw, s, font, letter_px):
    total = 0.0
    for ch in s:
        w, _ = text_size(draw, ch, font)
        total += w + letter_px
    return max(0.0, total - letter_px)


def build_lines(draw, text, font, letter_px, max_w):
    """按 \n 分行；单行超宽则按 CJK 边界折行。"""
    lines, cur = [], ""
    for para in str(text).split("\n"):
        if not para:
            lines.append("")
            continue
        cur = para
        while cur and measure_spaced(draw, cur, font, letter_px) > max_w and len(cur) > 1:
            cut = len(cur)
            while cut > 1 and measure_spaced(draw, cur[:cut], font, letter_px) > max_w:
                cut -= 1
            lines.append(cur[:cut])
            cur = cur[cut:]
        lines.append(cur)
    return lines


def fit_font(draw, block, img_w, max_w):
    """超宽自动缩字号，返回 (font, letter_px, 实际字号)。"""
    base_size = max(8, int(img_w * block.get("size_ratio", 0.05)))
    ratio = block.get("letter_spacing", 0.06)
    name = block.get("font", "")
    for size in range(base_size, 7, -1):
        font = resolve_font(name, size)
        lp = size * ratio
        if measure_spaced(draw, block.get("text", ""), font, lp) <= max_w:
            return font, lp, size
    return resolve_font(name, 8), 8 * ratio, 8


def render(cfg, preview=False):
    base_path = cfg.get("base")
    if not base_path or not os.path.exists(base_path):
        sys.exit(f"底图不存在: {base_path}")
    img = Image.open(base_path).convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # ---- logo ----
    logo = cfg.get("logo")
    if logo and logo.get("path") and os.path.exists(logo["path"]):
        lg = Image.open(logo["path"]).convert("RGBA")
        lw = int(W * logo.get("width_ratio", 0.18))
        lg = lg.resize((lw, max(1, int(lw * lg.height / lg.width))), Image.LANCZOS)
        pos = (int(W * logo.get("x", 0.06)), int(H * logo.get("y", 0.05)))
        img.alpha_composite(lg, dest=pos)
        print(f"logo: {logo['path']} -> {lg.size} @{pos}")

    # ---- 文字块 ----
    for i, b in enumerate(cfg.get("blocks", [])):
        text = b.get("text", "")
        if not text:
            continue
        max_w = W * b.get("max_width_ratio", 0.82)
        font, lp, real_size = fit_font(draw, b, W, max_w)
        lines = build_lines(draw, text, font, lp, max_w)

        gap = real_size * b.get("line_gap", 0.35)
        heights = [text_size(draw, ln, font)[1] if ln else real_size for ln in lines]
        total_h = sum(heights) + gap * (len(lines) - 1)

        cy = H * b.get("y", 0.5)
        top = cy - total_h / 2
        align = b.get("align", "center")
        color = b.get("color", "#000000")
        widest, last_x0, last_w = 0, 0, 0

        for ln, h in zip(lines, heights):
            lw = measure_spaced(draw, ln, font, lp) if ln else 0
            if align == "left":
                x0 = W * b.get("x", 0.5)
            elif align == "right":
                x0 = W * b.get("x", 0.5) - lw
            else:
                x0 = W * b.get("x", 0.5) - lw / 2
            # draw_spaced 以 (0,0) 为原点，故用临时图层平移
            if ln:
                layer = Image.new("RGBA", (max(1, int(lw) + 4), int(h * 2) + 8), (0, 0, 0, 0))
                draw_spaced(ImageDraw.Draw(layer), ln, font, color, lp)
                img.alpha_composite(layer, dest=(int(x0), int(top)))
                last_x0, last_w = x0, lw
                widest = max(widest, lw)
            top += h + gap

        print(f"block[{i}] size={real_size}px lines={len(lines)} "
              f"w≈{int(widest)} y_center={b.get('y', 0.5)}")

        # ---- 下划线：默认跟随最后一行宽度 ----
        ul = b.get("underline")
        if ul:
            uh = max(1, int(real_size * ul.get("height_ratio", 0.06)))
            off = real_size * ul.get("offset", 0.10)
            ratio = ul.get("width_ratio", 1.0)
            uw = int((widest if ul.get("follow_text", True) else W) * ratio)
            ux = (last_x0 + last_w / 2) - uw / 2 if ul.get("follow_text", True) \
                else W * b.get("x", 0.5) - uw / 2
            uy = cy + total_h / 2 + off
            draw.rectangle([ux, uy, ux + uw, uy + uh], fill=ul.get("color", color))
            print(f"  underline @{int(ux)},{int(uy)} {uw}x{uh}")

    out = cfg.get("output", "out.png")
    if preview:
        print(f"[preview] 未写入文件。目标: {out} 画布: {img.size}")
        return
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    img.save(out)
    print(f"已保存: {out}  ({img.size[0]}x{img.size[1]})")


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = argv[0]
    if not os.path.exists(path):
        sys.exit(f"配置文件不存在: {path}")
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    render(cfg, preview="--preview" in argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
