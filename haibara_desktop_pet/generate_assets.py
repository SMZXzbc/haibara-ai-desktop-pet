# -*- coding: utf-8 -*-
"""
占位图片生成脚本
用 Pillow 生成灰原哀 Q 版角色轮廓占位图，方便后续替换为真实素材。
运行：python generate_assets.py
"""
# 需要安装: pip install Pillow

import os
from PIL import Image, ImageDraw, ImageFont

# 输出目录
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# 图片尺寸
WIDTH, HEIGHT = 200, 250

# 各状态配色（主体色, 高光色, 阴影色）
STATE_COLORS = {
    "idle":    ((173, 216, 230), (130, 180, 210)),  # 浅蓝
    "talk":    ((144, 238, 144), (100, 190, 100)),   # 浅绿
    "think":   ((255, 255, 224), (220, 200, 150)),   # 浅黄
    "tired":   ((216, 191, 216), (180, 150, 180)),   # 浅紫
    "serious": ((255, 182, 193), (220, 130, 150)),   # 浅红
}


def draw_haibara(draw, state, w, h):
    """绘制灰原哀 Q 版轮廓"""
    main_color, accent_color = STATE_COLORS[state]
    cx, cy = w // 2, h // 2  # 中心点

    # === 头发（棕色短发）===
    hair_color = (120, 80, 50)
    # 头发主体 - 椭圆
    draw.ellipse([cx - 55, cy - 95, cx + 55, cy - 15], fill=hair_color)
    # 左侧刘海
    draw.polygon([
        (cx - 55, cy - 60), (cx - 65, cy - 30), (cx - 40, cy - 20),
        (cx - 45, cy - 50)
    ], fill=hair_color)
    # 右侧刘海
    draw.polygon([
        (cx + 55, cy - 60), (cx + 65, cy - 30), (cx + 40, cy - 20),
        (cx + 45, cy - 50)
    ], fill=hair_color)
    # 额前碎发
    draw.polygon([
        (cx - 20, cy - 90), (cx - 10, cy - 70), (cx, cy - 85),
        (cx + 10, cy - 70), (cx + 20, cy - 90)
    ], fill=hair_color)

    # === 脸部 ===
    skin_color = (255, 228, 196)
    draw.ellipse([cx - 40, cy - 75, cx + 40, cy - 10], fill=skin_color)

    # === 眼睛 ===
    eye_color = (70, 130, 180)  # 蓝色
    eye_y = cy - 50

    if state == "tired":
        # 困倦 - 闭眼（横线）
        draw.line([(cx - 25, eye_y), (cx - 10, eye_y)], fill=(50, 50, 50), width=2)
        draw.line([(cx + 10, eye_y), (cx + 25, eye_y)], fill=(50, 50, 50), width=2)
    elif state == "serious":
        # 认真 - 锐利眼神
        draw.ellipse([cx - 28, eye_y - 8, cx - 12, eye_y + 8], fill=eye_color)
        draw.ellipse([cx + 12, eye_y - 8, cx + 28, eye_y + 8], fill=eye_color)
        # 瞳孔
        draw.ellipse([cx - 23, eye_y - 4, cx - 17, eye_y + 4], fill=(30, 30, 30))
        draw.ellipse([cx + 17, eye_y - 4, cx + 23, eye_y + 4], fill=(30, 30, 30))
        # 眉毛下压
        draw.line([(cx - 30, eye_y - 14), (cx - 10, eye_y - 10)], fill=(80, 50, 30), width=2)
        draw.line([(cx + 10, eye_y - 10), (cx + 30, eye_y - 14)], fill=(80, 50, 30), width=2)
    else:
        # 普通眼睛
        draw.ellipse([cx - 28, eye_y - 8, cx - 12, eye_y + 8], fill=eye_color)
        draw.ellipse([cx + 12, eye_y - 8, cx + 28, eye_y + 8], fill=eye_color)
        # 瞳孔
        draw.ellipse([cx - 22, eye_y - 4, cx - 16, eye_y + 4], fill=(30, 30, 30))
        draw.ellipse([cx + 16, eye_y - 4, cx + 22, eye_y + 4], fill=(30, 30, 30))
        # 高光
        draw.ellipse([cx - 20, eye_y - 3, cx - 17, eye_y], fill=(255, 255, 255))
        draw.ellipse([cx + 18, eye_y - 3, cx + 21, eye_y], fill=(255, 255, 255))

    # === 嘴巴 ===
    mouth_y = cy - 30
    if state == "talk":
        # 说话 - 嘴巴微张
        draw.ellipse([cx - 8, mouth_y - 4, cx + 8, mouth_y + 6], fill=(200, 100, 100))
    elif state == "tired":
        # 困倦 - 打哈欠
        draw.ellipse([cx - 10, mouth_y - 6, cx + 10, mouth_y + 8], fill=(200, 100, 100))
    elif state == "think":
        # 思考 - 嘴巴闭合略偏
        draw.arc([cx - 8, mouth_y - 4, cx + 8, mouth_y + 4], 0, 180, fill=(180, 100, 100), width=2)
    else:
        # 普通 - 平静嘴巴
        draw.line([(cx - 8, mouth_y), (cx + 8, mouth_y)], fill=(180, 100, 100), width=2)

    # === 身体（外套）===
    coat_color = main_color
    # 身体梯形
    draw.polygon([
        (cx - 35, cy - 5), (cx + 35, cy - 5),
        (cx + 45, cy + 80), (cx - 45, cy + 80)
    ], fill=coat_color)
    # 衣领
    draw.polygon([
        (cx - 15, cy - 5), (cx, cy + 15), (cx + 15, cy - 5)
    ], fill=(255, 255, 255))

    # === 手 ===
    hand_color = skin_color
    if state == "think":
        # 思考 - 单手托腮
        draw.ellipse([cx + 30, cy - 45, cx + 50, cy - 25], fill=hand_color)
    elif state == "idle":
        # 待机 - 双手插兜
        draw.ellipse([cx - 50, cy + 40, cx - 35, cy + 55], fill=hand_color)
        draw.ellipse([cx + 35, cy + 40, cx + 50, cy + 55], fill=hand_color)
    elif state == "serious":
        # 认真 - 双臂交叉
        draw.rectangle([cx - 45, cy + 20, cx + 45, cy + 30], fill=coat_color)
    else:
        # 默认 - 自然下垂
        draw.ellipse([cx - 50, cy + 30, cx - 35, cy + 50], fill=hand_color)
        draw.ellipse([cx + 35, cy + 30, cx + 50, cy + 50], fill=hand_color)

    # === 腿 ===
    leg_color = (60, 60, 80)
    draw.rectangle([cx - 25, cy + 75, cx - 10, cy + 110], fill=leg_color)
    draw.rectangle([cx + 10, cy + 75, cx + 25, cy + 110], fill=leg_color)

    # === 鞋 ===
    shoe_color = (80, 60, 50)
    draw.ellipse([cx - 30, cy + 105, cx - 5, cy + 120], fill=shoe_color)
    draw.ellipse([cx + 5, cy + 105, cx + 30, cy + 120], fill=shoe_color)


def generate_image(state):
    """生成指定状态的占位图片"""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_haibara(draw, state, WIDTH, HEIGHT)
    return img


def main():
    """生成所有状态图片"""
    os.makedirs(ASSETS_DIR, exist_ok=True)

    for state in STATE_COLORS:
        filename = f"haibara_{state}.png"
        filepath = os.path.join(ASSETS_DIR, filename)
        img = generate_image(state)
        img.save(filepath, "PNG")
        print(f"已生成: {filename}")

    print(f"\n所有图片已保存到: {ASSETS_DIR}")
    print("可将这些占位图替换为真实素材（保持 200x250 PNG 透明背景）")


if __name__ == "__main__":
    main()
