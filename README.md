# 论文阅读笔记

公开论文博客，整理动机、核心 insight、方法、实验依据与值得继续研究的问题。首页支持全文搜索、主题、年份、阅读状态、日期范围和日期排序。文章包含作者单位、版本、核心要点、目录、论文截图与对照表。

- 网站：<https://tiankanghui.github.io/PaperReading/>
- 仓库：<https://github.com/tiankanghui/PaperReading>
- [SWE-Game 阅读文章](papers/swe-game/notes.md) · [问题与关键点](papers/swe-game/discussion.md)
- [GameDevBench 阅读文章](papers/gamedevbench/notes.md) · [问题与关键点](papers/gamedevbench/discussion.md)
- [GameCraft-Bench 阅读文章](papers/gamecraft-bench/notes.md) · [问题与关键点](papers/gamecraft-bench/discussion.md)

## 首次发布

仓库已经改为公开。本项目使用 `.github/workflows/pages.yml` 构建和发布，无第三方 Python 依赖。

1. 在 GitHub 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
2. 提交并推送本项目的发布配置。Actions 中的 **Publish reading notes** 会自动运行；也可选择 **Run workflow** 手动触发。
3. 工作流成功后，上方网站地址即可直接访问。每次推送到 `main` 都会更新网站，无需本地启动服务。

在文章目录设置 `metadata.json` 的 `"published": false` 可不生成该篇网页；但公开仓库中的源文件仍然可见。“示例”状态的记录默认不生成网页。

## 更新与同步

整理完成后，在终端运行：

```sh
sh scripts/publish.sh
```

该脚本检查构建、页面链接和远端分支，再提交并推送网站源文件。不会提交 `_site/` 或 papers 根目录里下载的 PDF，也不会强制推送。访问令牌需有该仓库 Contents 写入权限；上传 `.github/workflows/` 文件还需工作流写入权限（Fine-grained token 的 Workflows: Read and write，或 classic token 的 workflow scope）。不要把令牌写进文件或发到聊天中。

## 整理下一篇论文

可以对 Codex 说：

> 把本次论文阅读整理成博客文章。将讨论提炼为问题与关键点，不保留聊天原句和对话轨迹；区分原文结论与推测，注明证据，列出未解决的问题。

每篇论文一个目录，复制 `templates/` 中的三个文件：

```text
papers/paper-slug/
  metadata.json   题目、作者单位、版本、阅读日期、状态、标签、摘要、insight、原文链接
  notes.md        阅读文章
  discussion.md   文章式问题与关键点
  images/         论文图表截图，随源文件提交
```

目录名使用小写英文、数字、连字符或下划线。日期为 YYYY-MM-DD，状态可为待读、在读、已读、待复现。项目规则在 `AGENTS.md`。

## 本地查看（可选）

```sh
python3 scripts/build.py
python3 scripts/check_site.py
```

直接在浏览器打开 `_site/index.html` 即可，不必启动服务。页面使用白底、黑灰配色，中文优先使用本机楷体，英文使用 Times New Roman；未安装楷体时回退至衬线字体。不加载外部字体、统计服务或脚本。

支持基础 Markdown：标题、段落、粗体、行内代码、链接、无序列表、引用、代码块、管道表格和独立图片。图片可点击打开大图；图注包含来源，图后解释读图要点。LaTeX 公式保留为文本。

文章按 Motivation、Insight、Method、Experiments、结论边界、开放问题组织。metadata 的 `display_title` 用问题式中文标题，`title` 保留原论文题目；`affiliations`、`insights` 为字符串列表，`cover` 为 `images/overview.png` 一类相对路径。阅读日期与论文版本日期分别记录。

论文截图已作为 PNG 保存，构建无需 PDF 工具。需要重新提取时，可选运行 `scripts/extract_figures.py`（需要本地原 PDF、Pillow 与 Poppler）；每张图在文章中标明原论文图表编号和 PDF 页码。
