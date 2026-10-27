#!/usr/bin/env python3
"""Check generated links and fragments, including the GitHub Pages subpath."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                raise ValueError('{}: duplicate id {}'.format(self.path, attrs['id']))
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def check():
    base = urlparse(json.loads((ROOT / 'site.json').read_text())['url'])
    pages = {}
    for path in SITE.rglob('*.html'):
        page = Page(path)
        page.feed(path.read_text())
        pages[path.resolve()] = page
    if not pages:
        raise ValueError('No built pages; run python3 scripts/build.py first')
    for page in pages.values():
        for link in page.links:
            url = urlparse(link)
            if url.scheme or url.netloc:
                if url.scheme not in ('http', 'https') or url.netloc != base.netloc:
                    continue
                if not url.path.startswith(base.path):
                    raise ValueError('Wrong GitHub Pages subpath: ' + link)
                target = SITE / unquote(url.path[len(base.path):])
            else:
                target = page.path.parent / unquote(url.path) if url.path else page.path
            if target.is_dir():
                target = target / 'index.html'
            target = target.resolve()
            if SITE.resolve() not in target.parents or not target.exists():
                raise ValueError('{}: missing local target {}'.format(page.path, link))
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                raise ValueError('{}: missing anchor {}'.format(page.path, link))
    sitemap = ET.parse(SITE / 'sitemap.xml')
    for loc in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        url = urlparse(loc.text)
        if url.netloc != base.netloc or not url.path.startswith(base.path):
            raise ValueError('Invalid sitemap URL: ' + loc.text)
        target = SITE / unquote(url.path[len(base.path):])
        if target.is_dir():
            target = target / 'index.html'
        if not target.exists():
            raise ValueError('Missing sitemap page: ' + loc.text)
    print('Verified {} pages: links, anchors, sitemap and GitHub Pages paths'.format(len(pages)))


if __name__ == '__main__':
    check()
