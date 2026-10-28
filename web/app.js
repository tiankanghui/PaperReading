(() => {
  const search = document.getElementById('search');
  if (!search) return;
  const tag = document.getElementById('tag');
  const year = document.getElementById('year');
  const status = document.getElementById('status');
  const start = document.getElementById('date-start');
  const end = document.getElementById('date-end');
  const sort = document.getElementById('sort');
  const cards = document.querySelector('.cards');
  const papers = [...document.querySelectorAll('.paper')];
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const paper of papers) {
      const matches = paper.dataset.search.toLocaleLowerCase().includes(query)
        && (!tag.value || JSON.parse(paper.dataset.tags).includes(tag.value))
        && (!year.value || paper.dataset.year === year.value)
        && (!status.value || paper.dataset.status === status.value)
        && (!start.value || paper.dataset.date >= start.value)
        && (!end.value || paper.dataset.date <= end.value);
      paper.hidden = !matches;
      if (matches) count++;
    }
    [...papers].sort((a, b) => sort.value === 'asc'
      ? a.dataset.date.localeCompare(b.dataset.date)
      : b.dataset.date.localeCompare(a.dataset.date)).forEach(paper => cards.appendChild(paper));
    document.getElementById('result-count').textContent = `${count} 条记录`;
    document.getElementById('empty').hidden = count !== 0;
  }
  search.addEventListener('input', filter);
  for (const control of [tag, year, status, start, end, sort]) control.addEventListener('change', filter);
  document.getElementById('reset').addEventListener('click', () => {
    for (const control of [search, tag, year, status, start, end]) control.value = '';
    sort.value = 'desc';
    filter();
  });
})();
