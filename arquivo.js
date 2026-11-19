(() => {
  const form = document.querySelector('#busca-arquivo');
  const term = document.querySelector('#arquivo-termo');
  const topic = document.querySelector('#arquivo-tema');
  const status = document.querySelector('#arquivo-status');
  const results = document.querySelector('#arquivo-resultados');
  const editions = [...document.querySelectorAll('#edicoes a[href$=".html"]')];
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  const topics = [...topic.options].slice(1).map(option => option.value);
  let stories = [], failures = 0;
  function render() {
    const query = normalize(term.value.trim());
    const matches = stories.filter(story => (!topic.value || story.topic === topic.value) && story.search.includes(query));
    status.textContent = `${matches.length} pautas no arquivo${failures ? ` · ${failures} edição(ões) indisponível(is)` : ''}.`;
    results.replaceChildren(...matches.map(story => {
      const row = document.createElement('li');
      const detail = document.createElement('details');
      const title = document.createElement('summary');
      title.textContent = `${story.title} · ${story.date}`;
      const body = document.createElement('p');
      body.textContent = story.body;
      const link = document.createElement('a');
      link.href = story.url;
      link.textContent = 'Abrir edição e consultar fontes';
      detail.append(title, body, link);
      row.append(detail);
      return row;
    }));
  }
  form.hidden = false;
  status.textContent = 'Carregando o índice de pautas…';
  Promise.allSettled(editions.map(async edition => {
    const response = await fetch(edition.href);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const page = new DOMParser().parseFromString(await response.text(), 'text/html');
    const date = `${edition.closest('details').querySelector('summary').textContent}, ${edition.textContent.split(' — ')[0]}`;
    return topics.flatMap(topic => [...page.querySelectorAll(`section#${topic} .card`)].flatMap(card => {
      const title = card.querySelector('h3')?.textContent.trim();
      if (!title) return [];
      const body = [...card.querySelectorAll('p')].map(p => p.textContent.trim()).join(' ');
      return [{ title, body, topic, date, url: `${edition.href}#${topic}`, search: normalize(`${title} ${body} ${date}`) }];
    }));
  })).then(entries => {
    stories = entries.flatMap(entry => entry.status === 'fulfilled' ? entry.value : []);
    failures = entries.filter(entry => entry.status === 'rejected').length;
    render();
  });
  term.addEventListener('input', render);
  topic.addEventListener('change', render);
})();
