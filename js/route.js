(function () {
  const data = window.ROUTES_DATA;
  const main = document.getElementById('routeMain');
  const menuToggle = document.getElementById('menuToggle');
  const nav = document.querySelector('.nav');

  menuToggle?.addEventListener('click', () => nav?.classList.toggle('open'));

  if (!data || !main) return;

  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  const route = data.routes.find(r => r.id === id);

  if (!route) {
    main.innerHTML = `
      <div class="loading">
        <p>未找到该线路，请返回总览页选择。</p>
        <p style="margin-top:16px"><a href="index.html">← 返回线路总览</a></p>
      </div>
    `;
    return;
  }

  document.title = `${route.title} · 遂宁卓同2026夏季研学营`;

  const idx = data.routes.findIndex(r => r.id === id);
  const prev = data.routes[idx - 1];
  const next = data.routes[idx + 1];

  function listItems(items) {
    if (!items || !items.length) return '';
    return `<ul>${items.map(i => `<li>${i}</li>`).join('')}</ul>`;
  }

  function formatDayLabel(n) {
    const cn = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
    return n <= 10 ? `第${cn[n - 1]}天` : `第${n}天`;
  }

  function renderDay(day) {
    const blocks = [];

    if (day.schedule?.length) {
      blocks.push(`<div class="day-block"><h4>行程安排</h4>${listItems(day.schedule)}</div>`);
    }
    if (day.content?.length) {
      blocks.push(`<div class="day-block"><h4>活动详情</h4>${listItems(day.content)}</div>`);
    }
    if (day.courses?.length) {
      blocks.push(`<div class="day-block"><h4>课程内容</h4>${listItems(day.courses)}</div>`);
    }
    if (day.gains?.length) {
      blocks.push(`<div class="day-block"><h4>知识收获</h4>${listItems(day.gains)}</div>`);
    }
    if (day.activities?.length) {
      blocks.push(`<div class="day-block"><h4>特色活动</h4>${listItems(day.activities)}</div>`);
    }

    const info = day.info || {};
    const infoHtml = Object.keys(info).length
      ? `<div class="day-info">${Object.entries(info).map(([k, v]) => `<span>${k}：${v}</span>`).join('')}</div>`
      : '';

    const photoHtml = day.image
      ? `<div class="day-photo"><img src="${day.image}" alt="${day.title}" loading="lazy"></div>`
      : '';

    return `
      <article class="day-item${day.image ? ' has-photo' : ''}" style="--brand:${route.color}">
        <div class="day-body">
          <div class="day-head">
            <span class="day-num" style="background:${route.color};color:#fff">${formatDayLabel(day.day)}</span>
            <span class="day-title">${day.title}</span>
          </div>
          ${day.subtitle ? `<p class="day-subtitle">${day.subtitle}</p>` : ''}
          ${blocks.join('')}
          ${infoHtml}
        </div>
        ${photoHtml}
      </article>
    `;
  }

  const coverStyle = route.cover
    ? `background-image: linear-gradient(135deg, ${route.color}99, rgba(0,0,0,0.35)), url('${route.cover}');`
    : `background: linear-gradient(135deg, ${route.color}, #1a1a1a);`;

  main.innerHTML = `
    <section class="detail-hero">
      <div class="detail-hero-bg" style="${coverStyle}"></div>
      <div class="detail-hero-content">
        <span class="tag" style="background:rgba(255,255,255,0.2);color:#fff">${route.grade} · ${route.duration}</span>
        <h1>${route.title}</h1>
        <p class="detail-subtitle">${route.destinationTitle}</p>
        <div class="badges-row" style="margin-top:16px">
          <span class="tag" style="background:rgba(255,255,255,0.15);color:#fff">${route.destination}</span>
          ${(route.badges || []).map(b => `<span class="tag" style="background:rgba(255,255,255,0.15);color:#fff">${b}</span>`).join('')}
        </div>
      </div>
    </section>

    <section class="detail-section">
      <div class="container">
        <div class="info-grid">
          <div class="info-card">
            <h2 class="card-title">目的地介绍</h2>
            <p>${route.destinationDesc || route.destinationTitle}</p>
          </div>
          <div class="info-card">
            <h2 class="card-title">基本信息</h2>
            <ul class="info-list">
              <li><strong>适用年级：</strong>${route.grade}</li>
              <li><strong>行程天数：</strong>${route.duration}</li>
              <li><strong>目的地：</strong>${route.destination}</li>
              <li><strong>营期品牌：</strong>${data.brand}</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="detail-section alt">
      <div class="container">
        <h2>研学目标</h2>
        <div class="goals-grid">
          ${Object.entries(route.goals || {}).map(([k, v]) => `
            <article class="goal-card" style="border-left-color:${route.color}">
              <h3 style="color:${route.color}">${k}</h3>
              <p>${v}</p>
            </article>
          `).join('')}
        </div>
      </div>
    </section>

    <section class="detail-section">
      <div class="container">
        <h2>特色项目</h2>
        <div class="highlights-grid">
          ${route.highlights.map(h => `
            <article class="highlight-card">
              <h3>${h.title}</h3>
              <p>${h.detail || h.summary}</p>
            </article>
          `).join('')}
        </div>
      </div>
    </section>

    <section class="detail-section alt">
      <div class="container">
        <h2>每日行程安排</h2>
        <div class="timeline">
          ${route.days.map(renderDay).join('')}
        </div>
      </div>
    </section>

    ${route.images?.length ? `
    <section class="detail-section">
      <div class="container">
        <h2>线路图集</h2>
        <div class="gallery">
          ${route.images.map(img => `<img src="${img}" alt="${route.title}" loading="lazy">`).join('')}
        </div>
      </div>
    </section>` : ''}

    <section class="detail-section alt">
      <div class="container">
        <h2>服务保障</h2>
        <div class="service-grid">
          <article class="service-card">
            <div class="service-icon">🍽️</div>
            <h3>餐饮标准</h3>
            ${listItems(route.services.dining)}
          </article>
          <article class="service-card">
            <div class="service-icon">🏨</div>
            <h3>住宿标准</h3>
            ${listItems(route.services.lodging)}
          </article>
          <article class="service-card">
            <div class="service-icon">🛡️</div>
            <h3>安全保障</h3>
            <ul>
              ${route.services.safety.map(s => `<li><strong>${s.title}：</strong>${s.desc}</li>`).join('')}
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="container cta-box" style="background:linear-gradient(135deg, ${route.color}, ${route.color}cc)">
        <div>
          <h2>${route.destination.split('·')[0]}，等你出发</h2>
          <p>让每一次旅行都成为成长的礼物。欢迎联系学校研学负责人了解报名详情。</p>
        </div>
        <a href="index.html#contact" class="btn btn-light">立即咨询报名</a>
      </div>
    </section>

    <div class="container detail-nav">
      ${prev ? `<a href="route.html?id=${prev.id}">← ${prev.title}</a>` : '<span></span>'}
      ${next ? `<a href="route.html?id=${next.id}">${next.title} →</a>` : '<span></span>'}
    </div>
  `;

  document.querySelectorAll('.goal-card h3').forEach(el => {
    el.style.color = route.color;
  });
})();
