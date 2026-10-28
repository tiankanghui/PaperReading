#!/bin/sh
# Build and push the public reading website; no force pushes or generated files.
set -eu
cd "$(dirname "$0")/.."
if [ "$(git remote get-url origin)" != 'https://github.com/tiankanghui/PaperReading.git' ]; then
  echo '远端地址不符合预期，已停止。' >&2
  exit 1
fi
if [ "$(git symbolic-ref --short HEAD)" != main ]; then
  echo '请在 main 分支发布，已停止。' >&2
  exit 1
fi
if ! git diff --cached --quiet; then
  echo '暂存区已有改动，请先检查并提交这些改动，再运行发布脚本。' >&2
  exit 1
fi
python3 scripts/build.py
python3 scripts/check_site.py
git fetch origin main
if ! git merge-base --is-ancestor origin/main HEAD; then
  echo '远端有尚未合入的更新，请先同步并解决冲突，已停止。' >&2
  exit 1
fi
git add .gitignore AGENTS.md README.md site.json scripts templates web .github
for paper_dir in papers/*/; do
  if [ -f "${paper_dir}metadata.json" ]; then
    git add "${paper_dir}metadata.json" "${paper_dir}notes.md" "${paper_dir}discussion.md"
    if [ -d "${paper_dir}images" ]; then
      find "${paper_dir}images" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) -exec git add -- '{}' +
    fi
  fi
done
if ! git diff --cached --quiet; then
  git -c user.name=tiankanghui -c user.email=tiankanghui@users.noreply.github.com \
    commit -m "Publish paper reading website"
fi
git push -u origin main
echo '已推送。请在 GitHub Actions 中查看 Publish reading notes 的部署结果。'
