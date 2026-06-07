(function () {
  const data = window.ROUTES_DATA;
  if (!data) return;

  const routes = data.routes;
  let activeGrade = '全部';

  const gradeTabs = document.getElementById('gradeTabs');
  const routeGrid = document.getElementById('routeGrid');
  const routeCount = document.getElementById('routeCount');
  const heroStats = document.getElementById('heroStats');
  const contactBtn = document.getElementById('contactBtn');
  const menuToggle = document.getElementById('menuToggle');
  const nav = document.querySelector('.nav');

  if (contactBtn && data.contactPhone && !data.contactPhone.includes('咨询')) {
    contactBtn.href = 'tel:' + data.contactPhone.replace(/\s/g, '');
    contactBtn.textContent = '电话咨询：' + data.contactPhone;
  }

  menuToggle?.addEventListener('click', () => nav?.classList.toggle('open'));

  const grades = ['全部', ...new Set(routes.map(r => r.grade))];

  heroStats.innerHTML = [
    { value: routes.length, label: '精品线路' },
    { value: new Set(routes.map(r => r.destination)).size, label: '目的地' },
    { value: '1:10', label: '师生配比' },
    { value: '2026', label: '夏季营期' },
  ].map(s => `
    <div class="stat-item">
      <strong>${s.value}</strong>
      <span>${s.label}</span>
    </div>
  `).join('');

  function renderTabs() {
    gradeTabs.innerHTML = grades.map(g => `
      <button class="grade-tab${g === activeGrade ? ' active' : ''}" data-grade="${g}">${g}</button>
    `).join('');

    gradeTabs.querySelectorAll('.grade-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        activeGrade = btn.dataset.grade;
        renderTabs();
        renderRoutes();
      });
    });
  }

  function getCoverStyle(route) {
    if (route.cover) {
      return `background-image: linear-gradient(135deg, ${route.color}88, ${route.color}44), url('${route.cover}');`;
    }
    return `background: linear-gradient(135deg, ${route.color}, ${route.color}aa);`;
  }

  function truncate(text, len) {
    if (!text) return '';
    return text.length > len ? text.slice(0, len) + '…' : text;
  }

  function renderRoutes() {
    const filtered = activeGrade === '全部'
      ? routes
      : routes.filter(r => r.grade === activeGrade);

    routeCount.textContent = activeGrade === '全部'
      ? `共 ${filtered.length} 条精品线路`
      : `${activeGrade} · ${filtered.length} 条线路`;

    routeGrid.innerHTML = filtered.map(route => `
      <article class="route-card">
        <div class="route-card-cover" style="${getCoverStyle(route)}">
          <span class="route-card-badge">${route.grade}</span>
        </div>
        <div class="route-card-body">
          <div class="route-card-meta">
            <span class="tag">${route.destination}</span>
            <span class="tag">${route.duration}</span>
          </div>
          <h3>${route.title}</h3>
          <p>${truncate(route.destinationDesc || route.destinationTitle, 90)}</p>
          <div class="route-card-highlights">
            ${route.highlights.slice(0, 3).map(h => `
              <span class="highlight-chip">${h.title}</span>
            `).join('')}
          </div>
          <a class="route-card-link" href="route.html?id=${route.id}">
            查看详细行程 →
          </a>
        </div>
      </article>
    `).join('');
  }

  renderTabs();
  renderRoutes();
})();
