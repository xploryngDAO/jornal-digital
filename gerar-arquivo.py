import json
import os
import re
import sqlite3
from html import unescape
from pathlib import Path

root = Path(__file__).resolve().parent
db = root.parent / 'jornal-acervo.sqlite3'

def text(html):
    return ' '.join(unescape(re.sub(r'<[^>]*>', ' ', html)).split())

def extract(page):
    """Pautas de uma edição, sem contar os links do arquivo para a própria edição."""
    for topic, section in re.findall(r'<section id="(mundo|politica|economia|tecnologia|saude|ciencia|esporte|cultura|social)"[^>]*>(.*?)</section>', page, re.S):
        for card in re.findall(r'<article class=["\']card[^>]*?>(.*?)</article>', section, re.S):
            title = re.search(r'<h3[^>]*>(.*?)</h3>', card, re.S)
            if title:
                body = ' '.join(map(text, re.findall(r'<p[^>]*>(.*?)</p>', card, re.S)))
                yield text(title[1]), body, topic

stories = []
editions = {}
# A capa vigente entra na busca pelo próprio index.html; cada relatório publicado vale como edição.
if (root / 'index.html').exists():
    editions['__capa__'] = (root / 'index.html').read_text(encoding='utf-8')
for edition in sorted((root / 'edicoes').glob('????-??-??-????.html'), reverse=True):
    editions[edition.stem] = edition.read_text(encoding='utf-8')

# O acervo no SQLite é a fonte oficial; a capa vigente também entra na busca.
if db.exists():
    con = sqlite3.connect(db)
    try:
        for eid, html in con.execute('select id, html from edicoes order by id desc'):
            if eid not in editions and html and html.strip():
                editions[eid] = html
    finally:
        con.close()

capa_html = editions.get('__capa__', '').strip()
for eid in sorted(editions, reverse=True):
    if eid == '__capa__':
        capa = editions.pop('__capa__')
        for title, body, topic in extract(capa):
            stories.append(dict(title=title, body=body, topic=topic, date='capa vigente', url=f'#{topic}'))
        continue
    if capa_html and editions[eid].strip() == capa_html:
        # a edição já está na capa; evita pauta duplicada na busca
        continue
    year, month, day, hour = eid.split('-')
    date = f'{day}/{month}/{year} às {hour[:2]}:{hour[2:]}'
    for title, body, topic in extract(editions[eid]):
        stories.append(dict(title=title, body=body, topic=topic, date=date, url=f'edicoes/{eid}.html#{topic}'))

assert stories, 'Nenhuma pauta encontrada'
(root / 'arquivo-dados.js').write_text('window.pautasArquivadas = ' + json.dumps(stories, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'{len(stories)} pautas de {len(editions)} edições')
