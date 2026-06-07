#!/usr/bin/env python3
"""将图片统一转为 JPG 并更新 routes 数据中的路径"""
import json
import os
import re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "images")
MAX_WIDTH = 1200
QUALITY = 70


def to_jpg(path):
    base, _ = os.path.splitext(path)
    out = base + ".jpg"
    with Image.open(path) as img:
        img = img.convert("RGB")
        w, h = img.size
        if w > MAX_WIDTH:
            img = img.resize((MAX_WIDTH, int(h * MAX_WIDTH / w)), Image.LANCZOS)
        img.save(out, "JPEG", quality=QUALITY, optimize=True)
    if out != path and os.path.exists(path):
        os.remove(path)
    return out


def fix_paths(obj):
    if isinstance(obj, dict):
        return {k: fix_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_paths(v) for v in obj]
    if isinstance(obj, str) and "assets/images/" in obj:
        return re.sub(r"\.(png|jpeg)$", ".jpg", obj, flags=re.I)
    return obj


if __name__ == "__main__":
    total_before = 0
    total_after = 0
    for dirpath, _, files in os.walk(IMG_DIR):
        for name in sorted(files):
            if not name.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            src = os.path.join(dirpath, name)
            total_before += os.path.getsize(src)
            dst = to_jpg(src)
            total_after += os.path.getsize(dst)

    routes_path = os.path.join(ROOT, "data", "routes.json")
    with open(routes_path, encoding="utf-8") as f:
        data = fix_paths(json.load(f))
    with open(routes_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    js_path = os.path.join(ROOT, "js", "data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.ROUTES_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

    print(f"images: {total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB")
    print("updated data/routes.json and js/data.js")
