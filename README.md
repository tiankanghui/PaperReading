# 私人论文阅读博客

这是一个私人论文阅读博客，网页在本地查看，源文件和笔记同步到用户创建的私有仓库：<https://github.com/tiankanghui/PaperReading>。初版已完成首次同步；后续新增笔记需另行提交和推送。不启用公开网页部署。

## 本地查看

需要 Python 3.9 或更新版本，无第三方依赖。

```sh
python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

打开 <http://127.0.0.1:8000>。也可以直接用浏览器打开 `_site/index.html`。服务器仅监听本机；网页不加载外部脚本、字体或分析服务。`noindex` 只是爬虫提示，不提供访问权限保护；隐私依靠文件保留在本地。

## 每次读完怎样记录

可以在当前项目的 Codex 聊天中说：

> 把本次论文阅读整理成博客文章。把讨论提炼为文章中的问题与关键点，不保留聊天原句或对话轨迹；区分原文结论和推测，补充尚未解决的问题。先保存在本地。

项目的 `AGENTS.md` 提供记录约定。笔记保留整理后的知识与证据，不保存聊天原句、发言顺序、对话日期或理解变化的过程。其他聊天的内容可以先整理成文章要点，再带到本项目；网站不会自动采集聊天历史。

每篇论文一个目录：

```text
papers/paper-slug/
  metadata.json   题目、作者、年份、阅读日期、状态、标签和原文链接
  notes.md        整理后的阅读笔记
  discussion.md   文章式问题与关键点
```

从 `templates/` 复制这三个文件，文件夹名使用小写英文、数字、连字符或下划线。日期使用 YYYY-MM-DD。建议状态：待读、在读、已读、待复现。首页统计不计入“示例”记录。

支持基础 Markdown：标题、段落、粗体、行内代码、链接、无序列表、引用和代码块；暂不支持表格、图片和公式排版。LaTeX 公式会保留为文本。首页支持标题/作者/摘要/标签关键词搜索，以及主题、论文年份、阅读状态筛选。

## 同步 GitHub

私有仓库 `PaperReading` 只保存源文件和笔记，生成的 `_site/` 不提交。新增或更新笔记后，在本地构建查看，再提交并同步：

```sh
python3 scripts/build.py
git add papers site.json
git commit -m "Update paper reading notes"
git push origin main
```

首次连接需要完成 GitHub 身份验证。不要把密码、访问令牌或其他凭据写入项目文件。

当前项目已配置远端地址。首次同步可以在自己的终端执行：

```sh
sh scripts/first-sync.sh
```

脚本仅在远端没有任何引用、当前分支为 main 时提交并推送；已有远端内容时停止。首次提交使用 GitHub 用户名及 `tiankanghui@users.noreply.github.com` 作为提交身份，不修改全局 Git 配置。公开部署模板留在 `templates/` 中，不会触发部署。

私有仓库与私有网页是两回事。GitHub Pages 的访问权限取决于账户和组织方案；不能因为仓库是 Private 就认为网页也是私有的。现阶段继续用本地网页即可；需要在线私有访问时，先选择带登录控制的托管方式。

若以后决定公开，`templates/github-pages.yml` 提供 GitHub Pages 部署模板。届时将它移到 `.github/workflows/pages.yml`，检查公开内容、调整页面的本地标识，并在仓库 Settings → Pages 选择 GitHub Actions。公开网址通常为 `https://tiankanghui.github.io/PaperReading/`，以实际部署结果为准。
