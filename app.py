"""
Main Flask application for Yurt Radio.

This is the entry point for the backend server.
Run this file to start the server: python app.py
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.routes import api_bp
from backend.models import init_db
from scripts.scan_music import rescan_music_directory
import config
import os
import re
import markdown


app = Flask(__name__, static_folder='static')

app.config.from_object(config)

CORS(app)

# This will create the database file and tables if they don't exist
init_db()

# This connects all the API routes from backend/routes.py
app.register_blueprint(api_bp, url_prefix='/api')


# ==================== PAGE ROUTES ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the WebGL home page."""
    return send_from_directory('static', 'index.html')


@app.route('/radio', methods=['GET'])
def radio():
    """Serve the Yurt Radio player."""
    return send_from_directory('static', 'radio.html')


@app.route('/worlds', methods=['GET'])
def worlds():
    """Serve the game projects listing page."""
    return send_from_directory('static', 'worlds.html')


@app.route('/worlds/<slug>', methods=['GET'])
def world_detail(slug):
    """Serve individual game detail pages."""
    if not re.match(r'^[a-zA-Z0-9-]+$', slug):
        return 'Not found', 404
    filename = f'worlds/{slug}.html'
    if not os.path.exists(os.path.join('static', filename)):
        return 'Not found', 404
    return send_from_directory('static', filename)


@app.route('/tools', methods=['GET'])
def tools():
    """Serve the tools listing page."""
    return send_from_directory('static', 'tools.html')


@app.route('/imagery', methods=['GET'])
def imagery():
    """Serve the image gallery page."""
    return send_from_directory('static', 'imagery.html')


# ==================== NOTES ROUTES ====================

NOTES_DIR = os.path.join(os.path.dirname(__file__), 'notes', 'posts')


def _parse_frontmatter(text):
    """
    Strip and parse a --- delimited YAML frontmatter block from a markdown file.
    Returns (meta_dict, body_text).
    """
    meta = {}
    body = text
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            fm_block = text[3:end].strip()
            body = text[end + 3:].strip()
            for line in fm_block.splitlines():
                if ':' in line:
                    key, _, val = line.partition(':')
                    meta[key.strip()] = val.strip()
    return meta, body


def _notes_page(title, body_html):
    """Minimal HTML wrapper for notes pages."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Yurt Tech</title>
    <link rel="stylesheet" href="/css/site.css">
    <link rel="icon" type="image/x-icon" href="/resources/favicon.ico">
</head>
<body class="has-nav">
    <nav class="site-nav">
        <span class="nav-brand">YURT TECH</span>
        <a href="/">HOME</a>
        <a href="/worlds">WORLDS</a>
        <a href="/tools">TOOLS</a>
        <a href="/imagery">IMAGERY</a>
        <a href="/radio">RADIO</a>
        <a href="/notes">NOTES</a>
    </nav>
    <div class="page-wrapper">
        {body_html}
    </div>
    <script src="/js/nav.js"></script>
</body>
</html>"""


@app.route('/notes', methods=['GET'])
def notes_index():
    """Render the notes listing page from markdown files in notes/posts/."""
    os.makedirs(NOTES_DIR, exist_ok=True)

    entries = []
    for fname in sorted(os.listdir(NOTES_DIR), reverse=True):
        if not fname.endswith('.md'):
            continue
        slug = fname[:-3]
        fpath = os.path.join(NOTES_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        meta, _ = _parse_frontmatter(text)
        entries.append({
            'slug': slug,
            'title': meta.get('title', slug.replace('-', ' ').title()),
            'date':  meta.get('date', ''),
            'author': meta.get('author', '')
        })

    rows = ''.join(
        f'<li class="notes-item">'
        f'<a href="/notes/{e["slug"]}" class="notes-link">{e["title"]}</a>'
        f'<span class="notes-author">{e['author']}</span>'
        f'<span class="notes-date">{e["date"]}</span>'
        f'</li>'
        for e in entries
    ) or '<li class="notes-item notes-empty">No notes yet.</li>'

    body_html = f'<h1 class="page-title">Notes</h1><ul class="notes-list">{rows}</ul>'
    return _notes_page('Notes', body_html), 200


@app.route('/notes/<slug>', methods=['GET'])
def notes_detail(slug):
    """Render a single note from its markdown file."""
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        return 'Not found', 404

    fpath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.exists(fpath):
        return 'Not found', 404

    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    meta, body = _parse_frontmatter(text)
    title = meta.get('title', slug.replace('-', ' ').title())
    date  = meta.get('date', '')
    author = meta.get('author', '')

    html_body = markdown.markdown(body, extensions=['fenced_code', 'tables', 'toc'])

    date_span = f'&nbsp;&mdash;&nbsp; {date}' if date else ''
    author_span = f"&nbsp; {author}" if author else ''
    body_html = (
        f'<a href="/notes" class="back-link">&larr; NOTES</a>'
        f'<div class="entry-meta">{author_span}</div>'
        f'<div class="entry-meta">{date_span}</div>'
        f'<h1 class="page-title">{title}</h1>'
        f'<div class="markdown-body">{html_body}</div>'
    )
    return _notes_page(title, body_html), 200


# ==================== STATIC FILE WILDCARD ====================

@app.route('/<path:path>')
def static_files(path):
    """
    Serve static files (CSS, JS, images, etc.)
    All explicit page routes above take priority over this wildcard.
    """
    return send_from_directory('static', path)


if __name__ == '__main__':
    # Only rescan in development mode
    if config.DEBUG:
        rescan_music_directory()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
