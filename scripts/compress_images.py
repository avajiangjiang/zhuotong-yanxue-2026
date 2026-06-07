#!/usr/bin/env python3
"""压缩网站图片，便于 GitHub 上传与网页加载"""
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
MAX_WIDTH = 1200
JPEG_QUALITY = 72


def compress(path):
    ext = os.path.splitext(path)[1].lower()
    with Image.open(path) as img:
        if ext in (".jpg", ".jpeg"):
            img = img.convert("RGB")
        else:
            img = img.convert("RGBA")
        w, h = img.size
        if w > MAX_WIDTH:
            img = img.resize((MAX_WIDTH, int(h * MAX_WIDTH / w)), Image.LANCZOS)

        before = os.path.getsize(path)
        if ext in (".jpg", ".jpeg"):
            img.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        else:
            img.save(path, "PNG", optimize=True, compress_level=9)
        after = os.path.getsize(path)
        print(f"{os.path.basename(path):20s} {before/1024/1024:5.1f}MB -> {after/1024/1024:5.1f}MB")


if __name__ == "__main__":
    for root, _, files in os.walk(ROOT):
        for name in sorted(files):
            if name.lower().endswith((".png", ".jpg", ".jpeg")):
                compress(os.path.join(root, name))
