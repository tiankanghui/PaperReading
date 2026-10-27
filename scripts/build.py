#!/usr/bin/env python3
"""Build a dependency-free paper-reading website for GitHub Pages."""
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'


def esc(value):
    return html.escape(str(value), quote=True)


def safe_url(value):
    return value if urlparse(value).scheme in ('https', 'http') else ''


def inline(text):
    # Escape HTML and keep code and links out of later formatting passes.
    tokens = []

    def token(value):
        tokens.append(value)
        return '\x00{}\x00'.format(len(tokens) - 1)

    text = esc(text)
    text = re.sub(r'`([^`]+)`', lambda m: token('<code>' + m[1] + '</code>'), text)

    def link(m):
        url = safe_url(html.unescape(m[2]))
        return token('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format(esc(url), m[1])) if url else m[1]

    text = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', link, text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return re.sub('\x00(\\d+)\x00', lambda m: tokens[int(m[1])], text)


def markdown(source):
    output, paragraph, items, quote, code = [], [], [], [], []
    in_code = False

    def flush():
        if paragraph:
            output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
        if items:
            output.append('<ul>' + ''.join('<li>' + inline(x) + '</li>' for x in items) + '</ul>')
            items.clear()
        if quote:
            output.append('<blockquote>' + inline(' '.join(quote)) + '</blockquote>')
            quote.clear()

    for line in source.splitlines():
        if line.startswith('```'):
            flush()
            if in_code:
                output.append('<pre><code>' + esc('\n'.join(code)) + '</code></pre>')
                code.clear()
            in_code = not in_code
        elif in_code:
            code.append(line)
        elif not line.strip():
            flush()
        elif re.match(r'^#{1,6} ', line):
            flush()
            level = min(len(line.split(' ')[0]) + 1, 6)
            output.append('<h{0}>{1}</h{0}>'.format(level, inline(line.split(' ', 1)[1])))
        elif line.startswith('- '):
            if paragraph or quote:
                flush()
            items.append(line[2:])
        elif line.startswith('> '):
            if paragraph or items:
                flush()
            quote.append(line[2:])
        else:
            if items or quote:
                flush()
            paragraph.append(line)
    flush()
    if in_code:
        output.append('<pre><code>' + esc('\n'.join(code)) + '</code></pre>')
    return '\n'.join(output)


def shell(title, body, prefix='', description='', page=''):
    config = json.loads((ROOT / 'site.json').read_text())
    canonical = safe_url(config.get('url', '')).rstrip('/') + '/' + page
    repository = safe_url(config.get('repository', ''))
    description = description or config['subtitle']
    body = body.replace('<main>', '<main id="main-content">', 1)
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{description}"><meta name="author" content="{author}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="{ogtype}"><meta property="og:locale" content="zh_CN">
<link rel="stylesheet" href="{prefix}style.css"></head>
<body><a class="skip-link" href="#main-content">跳至正文</a><div class="layout"><header class="top"><a class="brand" href="{prefix}index.html"><span class="mark">P</span> PAPER READING</a><a class="site-label" href="{repository}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></header>{body}
<footer>以原文为依据 · 持续修订<span>{author} · 论文阅读笔记</span></footer></div><script src="{prefix}app.js"></script></body></html>'''.format(title=esc(title), body=body, prefix=prefix, description=esc(description), author=esc(config['author']), canonical=esc(canonical), repository=esc(repository), ogtype='article' if page.startswith('papers/') else 'website')


def article_html(source):
    rendered = markdown(source)
    entries = []

    def heading(match):
        identifier = 'section-{}'.format(len(entries) + 1)
        entries.append('<li><a href="#{0}">{1}</a></li>'.format(identifier, match[1]))
        return '<h3 id="{}">{}</h3>'.format(identifier, match[1])

    rendered = re.sub(r'<h3>(.*?)</h3>', heading, rendered)
    toc = '<nav class="contents" aria-label="文章目录"><details><summary>文章目录</summary><ol>{}</ol></details></nav>'.format(''.join(entries)) if entries else ''
    return toc + rendered


def discussion_html(source):
    rendered = markdown(source)
    headings = list(re.finditer(r'<h3>(.*?)</h3>', rendered))
    if not headings:
        return rendered
    output = [rendered[:headings[0].start()]]
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(rendered)
        output.append('<details class="qa"><summary>{}</summary><div class="qa-body">{}</div></details>'.format(
            heading[1], rendered[heading.end():end]))
    return '\n'.join(output)


def build():
    config = json.loads((ROOT / 'site.json').read_text())
    papers = []
    for directory in sorted((ROOT / 'papers').iterdir()):
        if directory.is_dir() and (directory / 'metadata.json').exists():
            metadata = json.loads((directory / 'metadata.json').read_text())
            for field in ('title', 'date', 'status', 'tags', 'summary'):
                if field not in metadata:
                    raise ValueError('{}: missing {}'.format(directory.name, field))
            if not isinstance(metadata['tags'], list) or not all(isinstance(t, str) for t in metadata['tags']):
                raise ValueError('{}: tags must be a list of strings'.format(directory.name))
            if not isinstance(metadata.get('published', True), bool):
                raise ValueError('{}: published must be true or false'.format(directory.name))
            if not metadata.get('published', metadata['status'] != '示例'):
                continue
            if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', directory.name):
                raise ValueError('Paper folder must use lowercase letters, numbers, hyphens or underscores')
            papers.append((directory, metadata))
    papers.sort(key=lambda item: item[1]['date'], reverse=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in ('style.css', 'app.js'):
        shutil.copyfile(ROOT / 'web' / name, OUT / name)
    cards = []
    for directory, p in papers:
        tags = ''.join('<span class="tag">{}</span>'.format(esc(t)) for t in p['tags'])
        search = ' '.join(str(p.get(k, '')) for k in ('title', 'authors', 'summary', 'year', 'venue')) + ' ' + ' '.join(p['tags'])
        search += ' ' + (directory / 'notes.md').read_text() + ' ' + (directory / 'discussion.md').read_text()
        search = ' '.join(search.split())
        cards.append('''<a class="paper" href="papers/{slug}.html" data-search="{search}" data-status="{status}" data-year="{year}" data-tags="{tagdata}">
<div class="paper-meta"><span>{date} · {venue}</span><span class="status">{status}</span></div><h2>{title}</h2><p>{summary}</p><div class="paper-bottom"><div>{tags}</div><span class="read">阅读笔记 ↗</span></div></a>'''.format(slug=directory.name, search=esc(search), status=esc(p['status']), year=esc(p.get('year', '')), tagdata=esc(json.dumps(p['tags'], ensure_ascii=False)), date=esc(p['date']), venue=esc(p.get('venue') or '未填写发表位置'), title=esc(p['title']), summary=esc(p['summary']), tags=tags))
        source = safe_url(p.get('url', ''))
        source_link = '<a class="source" href="{}" target="_blank" rel="noopener noreferrer">论文原文 ↗</a>'.format(esc(source)) if source else ''
        body = '''<main><a class="back" href="../index.html">← 所有阅读</a><div class="article-head"><div class="eyebrow">{date} / {status}</div><h1>{title}</h1><p class="authors">{authors} · {year} · {venue}</p><p class="abstract">{summary}</p><div class="article-links">{tags}{source_link}</div></div>
<nav class="tabs" aria-label="笔记类型"><a href="#notes">阅读笔记</a><a href="#discussion">问题与关键点</a></nav>
<div class="article-grid"><article id="notes"><div class="section-label">01 / READING NOTES</div>{notes}</article><aside id="discussion"><div class="section-label">02 / KEY POINTS</div>{discussion}</aside></div></main>'''.format(date=esc(p['date']), status=esc(p['status']), title=esc(p['title']), authors=esc(p.get('authors') or '作者待补充'), year=esc(p.get('year', '')), venue=esc(p.get('venue', '')), summary=esc(p['summary']), tags=tags, source_link=source_link, notes=article_html((directory / 'notes.md').read_text()), discussion=discussion_html((directory / 'discussion.md').read_text()))
        (OUT / 'papers').mkdir(exist_ok=True)
        (OUT / 'papers' / (directory.name + '.html')).write_text(shell(p['title'] + ' · ' + config['title'], body, '../', p['summary'], 'papers/' + directory.name + '.html'))

    def options(values):
        return ''.join('<option value="{0}">{0}</option>'.format(esc(v)) for v in sorted(set(values)))

    real = [p for _, p in papers if p['status'] != '示例']
    body = '''<main><section class="hero"><div class="eyebrow">PAPERS · METHODS · QUESTIONS</div><h1>论文阅读笔记</h1><p>{subtitle}</p><div class="hero-stats"><span><b>{count:02d}</b> 篇阅读</span><span><b>{topics:02d}</b> 个主题</span><span class="hero-note">论文笔记 / 问题与要点 / 阅读启发</span></div></section>
<section class="library"><div class="library-head"><div><div class="eyebrow">THE READING SHELF</div><h2>我的论文书架</h2></div><span id="result-count">{all_count} 条记录</span></div>
<div class="filters"><label class="search"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="搜索论文、主题或正文关键词" aria-label="搜索论文全文"></label><select id="tag" aria-label="主题"><option value="">所有主题</option>{tag_options}</select><select id="year" aria-label="论文年份"><option value="">所有年份</option>{year_options}</select><select id="status" aria-label="阅读状态"><option value="">所有状态</option>{status_options}</select></div>
<div class="cards">{cards}</div><div id="empty" class="empty" hidden>还没有匹配的笔记。试试其他关键词，或清空筛选。</div></section>
<section class="ritual"><span class="section-label">每篇论文，整理值得记住的问题</span><p>问题是什么 <span>→</span> 方法如何工作 <span>→</span> 证据是否充分 <span>→</span> 我还有哪些疑问</p></section></main>'''.format(subtitle=esc(config['subtitle']), count=len(real), topics=len(set(t for p in real for t in p['tags'])), all_count=len(papers), tag_options=options(t for _, p in papers for t in p['tags']), year_options=options(str(p['year']) for _, p in papers if p.get('year')), status_options=options(p['status'] for _, p in papers), cards='\n'.join(cards))
    (OUT / 'index.html').write_text(shell(config['title'], body))
    base = safe_url(config['url']).rstrip('/') + '/'
    urls = [base] + [base + 'papers/' + directory.name + '.html' for directory, _ in papers]
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>{}</loc></url>'.format(esc(url)) for url in urls) + '</urlset>')
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + base + 'sitemap.xml\n')
    (OUT / '404.html').write_text(shell('页面未找到 · ' + config['title'], '<main><section class="hero"><div class="eyebrow">404</div><h1>页面未找到</h1><p>这篇笔记可能已经移动，请回到论文列表查找。</p><a href="' + esc(base) + '">返回论文列表 →</a></section></main>', base, page='404.html'))
    (OUT / '.nojekyll').touch()
    print('Built {} records → {}'.format(len(papers), OUT))


if __name__ == '__main__':
    build()
