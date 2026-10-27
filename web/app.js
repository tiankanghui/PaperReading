(() => {
  const search = document.getElementById('search');
  if (!search) return;
  const tag = document.getElementById('tag');
  const year = document.getElementById('year');
  const status = document.getElementById('status');
  const papers = [...document.querySelectorAll('.paper')];
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const paper of papers) {
      const matches = paper.dataset.search.toLocaleLowerCase().includes(query)
        && (!tag.value || JSON.parse(paper.dataset.tags).includes(tag.value))
        && (!year.value || paper.dataset.year === year.value)
        && (!status.value || paper.dataset.status === status.value);
      paper.hidden = !matches;
      if (matches) count++;
    }
    document.getElementById('result-count').textContent = `${count} 条记录`;
    document.getElementById('empty').hidden = count !== 0;
  }
  search.addEventListener('input', filter);
  for (const select of [tag, year, status]) select.addEventListener('change', filter);
})();
