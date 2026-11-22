(() => {
  const form = document.querySelector('#busca-arquivo');
  const term = document.querySelector('#arquivo-termo');
  const topic = document.querySelector('#arquivo-tema');
  const status = document.querySelector('#arquivo-status');
  const results = document.querySelector('#arquivo-resultados');
  const archiveBase = new URL('.', document.currentScript.src);
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  const stories = (window.pautasArquivadas || []).map(story => ({ ...story, search: normalize(`${story.title} ${story.body} ${story.date} ${story.topic}`) }));
  function render() {
    const query = normalize(term.value.trim());
    const matches = stories.filter(story => (!topic.value || story.topic === topic.value) && story.search.includes(query));
    status.textContent = `${matches.length} pautas no arquivo.`;
    results.replaceChildren(...matches.map(story => {
      const row = document.createElement('li');
      const detail = document.createElement('details');
      const title = document.createElement('summary');
      title.textContent = `${story.title} · ${story.date}`;
      const body = document.createElement('p');
      body.textContent = story.body;
      const link = document.createElement('a');
      link.href = new URL(story.url, archiveBase);
      link.textContent = story.url.startsWith('#') ? 'Ler na edição vigente' : 'Abrir edição e consultar fontes';
      detail.append(title, body, link);
      row.append(detail);
      return row;
    }));
  }
  form.hidden = false;
  render();
  term.addEventListener('input', render);
  topic.addEventListener('change', render);
})();
