import json
import re
from html import unescape
from pathlib import Path

root = Path(__file__).resolve().parent
stories = []
def text(html):
    return ' '.join(unescape(re.sub(r'<[^>]*>', ' ', html)).split())

for edition in sorted((root / 'edicoes').glob('????-??-??-????.html'), reverse=True):
    year, month, day, hour = edition.stem.split('-')
    date = f'{day}/{month}/{year} às {hour[:2]}:{hour[2:]}'
    page = edition.read_text(encoding='utf-8')
    for topic, section in re.findall(r'<section id="(mundo|politica|economia|tecnologia|social)"[^>]*>(.*?)</section>', page, re.S):
        for card in re.findall(r'<(?:article|div) class="card"[^>]*>(.*?)</(?:article|div)>', section, re.S):
            title = re.search(r'<h3[^>]*>(.*?)</h3>', card, re.S)
            if title:
                body = ' '.join(map(text, re.findall(r'<p[^>]*>(.*?)</p>', card, re.S)))
                stories.append(dict(title=text(title[1]), body=body, topic=topic, date=date, url=f'edicoes/{edition.name}#{topic}'))
assert stories, 'Nenhuma pauta encontrada'
(root / 'arquivo-dados.js').write_text('window.pautasArquivadas = ' + json.dumps(stories, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'{len(stories)} pautas')
