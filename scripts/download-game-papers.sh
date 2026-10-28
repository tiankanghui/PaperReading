#!/bin/sh
# Download the arXiv papers cited by SWE-Game into the local papers folder.
set -eu
cd "$(dirname "$0")/.."
mkdir -p papers
paper_temp=''
trap 'if [ -n "$paper_temp" ]; then rm -f "$paper_temp"; fi' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

download_paper() {
  paper_title=$1
  paper_id=$2
  paper_path=$3
  if [ -f "$paper_path" ]; then
    if [ "$(head -c 5 "$paper_path")" = '%PDF-' ]; then
      echo "$paper_title 已存在：$paper_path"
      return
    fi
    echo "$paper_path 已存在但不是 PDF，已停止以避免覆盖。" >&2
    exit 1
  fi
  paper_temp=$(mktemp)
  curl --fail --location --retry 2 --max-time 120 \
    "https://arxiv.org/pdf/$paper_id" --output "$paper_temp"
  if [ "$(head -c 5 "$paper_temp")" != '%PDF-' ]; then
    echo "$paper_title 下载结果不是 PDF，未保存。" >&2
    exit 1
  fi
  mv "$paper_temp" "$paper_path"
  paper_temp=''
  echo "$paper_title 下载完成：$paper_path"
}

download_paper 'GameDevBench' '2602.11103' 'papers/gamedevbench.pdf'
download_paper 'GameCraft-Bench' '2606.17861' 'papers/gamecraft-bench.pdf'
