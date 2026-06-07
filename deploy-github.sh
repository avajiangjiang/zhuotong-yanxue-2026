#!/bin/bash
# 将网站推送到 GitHub，开启 Pages 后客户可访问
set -e
cd "$(dirname "$0")"
REPO="avajiangjiang/zhuotong-yanxue-2026"
URL="https://avajiangjiang.github.io/zhuotong-yanxue-2026/"

echo "======================================"
echo "  卓同研学 2026 · 网站部署"
echo "======================================"
echo ""

if ! gh auth status >/dev/null 2>&1; then
  echo "需要先登录 GitHub（会打开浏览器）："
  gh auth login -h github.com -p https -w
fi

git remote get-url origin >/dev/null 2>&1 || \
  git remote add origin "https://github.com/${REPO}.git"

echo "正在上传..."
git push -u origin main

echo ""
echo "上传完成！请在 GitHub 开启 Pages："
echo "  1. 打开 https://github.com/${REPO}/settings/pages"
echo "  2. Source 选 Deploy from a branch"
echo "  3. Branch 选 main，文件夹选 / (root)，点 Save"
echo ""
echo "约 1～2 分钟后访问："
echo "  ${URL}"
