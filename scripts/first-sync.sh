#!/bin/sh
# Run in your own terminal once, after configuring GitHub authentication.
set -eu
cd "$(dirname "$0")/.."

expected='https://github.com/tiankanghui/PaperReading.git'
if [ "$(git remote get-url origin)" != "$expected" ]; then
  echo '远端地址不符合预期，已停止。请检查 git remote -v。' >&2
  exit 1
fi
if [ "$(git symbolic-ref --short HEAD)" != main ]; then
  echo '当前分支不是 main，已停止。请先检查分支。' >&2
  exit 1
fi
remote_refs=$(git ls-remote origin)
if [ -n "$remote_refs" ]; then
  echo '远端已有内容，已停止首次同步，请将以下分支信息交给 Codex 检查：'
  printf '%s\n' "$remote_refs"
  exit 1
fi
python3 scripts/build.py
git add .gitignore AGENTS.md README.md papers scripts site.json templates web
if ! git diff --cached --quiet; then
  git -c user.name=tiankanghui -c user.email=tiankanghui@users.noreply.github.com \
    commit -m "Add private paper reading journal"
fi
git push -u origin main
echo '首次同步成功。后续更新请使用 sh scripts/publish.sh。'
