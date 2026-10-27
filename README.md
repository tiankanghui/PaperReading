# 论文阅读笔记

公开论文博客，整理方法、实验依据与值得继续研究的问题。

- 网站：<https://tiankanghui.github.io/PaperReading/>（完成 GitHub Pages 部署后可访问）
- 仓库：<https://github.com/tiankanghui/PaperReading>
- [SWE-Game 阅读文章](papers/swe-game/notes.md) · [问题与关键点](papers/swe-game/discussion.md)

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
  metadata.json   题目、作者、年份、阅读日期、状态、标签、摘要、原文链接
  notes.md        阅读文章
  discussion.md   文章式问题与关键点
```

目录名使用小写英文、数字、连字符或下划线。日期为 YYYY-MM-DD，状态可为待读、在读、已读、待复现。项目规则在 `AGENTS.md`。

## 本地查看（可选）

```sh
python3 scripts/build.py
python3 scripts/check_site.py
```

直接在浏览器打开 `_site/index.html` 即可，不必启动服务。页面使用白底、黑灰配色，中文优先使用本机楷体，英文使用 Times New Roman；未安装楷体时回退至衬线字体。不加载外部字体、统计服务或脚本。

支持基础 Markdown：标题、段落、粗体、行内代码、链接、无序列表、引用和代码块。暂不提供表格、图片和公式排版，LaTeX 公式保留为文本。
