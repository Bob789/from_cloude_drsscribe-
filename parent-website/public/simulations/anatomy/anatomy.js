(function() {
  'use strict';
  const organs = window.ORGANS;
  const sims = window.ORGAN_SIM;
  const bodyWrap = document.getElementById('bodyWrap');
  const organLayer = document.getElementById('organLayer');
  const organListEl = document.getElementById('organList');
  const infoNum = document.getElementById('infoNum');
  const infoTitle = document.getElementById('infoTitle');
  const infoSub = document.getElementById('infoSub');
  const infoRole = document.getElementById('infoRole');
  const infoDesc = document.getElementById('infoDesc');
  const infoFacts = document.getElementById('infoFacts');
  const infoStats = document.getElementById('infoStats');
  const simBtn = document.getElementById('simBtn');
  const resetBtn = document.getElementById('resetBtn');

  let currentMode = 'normal';
  let activeKey = 'brain';
  let simulating = null;

  // Explode positions (spread out)
  const EXPLODE = {
    brain:'178,10','heart':'80,200','lungs-l':'20,160','lungs-r':'330,160',
    'liver':'290,290','stomach':'90,300','intestine':'140,450',
    'kidney-l':'40,380','kidney-r':'360,380','bladder':'180,570'
  };

  function renderOrgans(mode) {
    organLayer.innerHTML = '';
    const dropHTML = organs.map(o => {
      return `<div class="drop-zone" data-target="${o.key}" style="left:${o.x}px;top:${o.y}px;width:${o.w}px;height:${o.h}px"></div>`;
    }).join('');
    organLayer.innerHTML = dropHTML;

    organs.forEach(o => {
      const el = document.createElement('div');
      el.className = 'organ';
      el.dataset.key = o.key;
      let x = o.x, y = o.y;
      if (mode === 'exploded') {
        const [ex, ey] = EXPLODE[o.key].split(',').map(Number);
        x = ex; y = ey;
      }
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      el.innerHTML = o.svg + `<div class="organ-badge">${o.num}</div>`;
      organLayer.appendChild(el);
      if (currentMode !== 'exploded') makeDraggable(el, o);
      el.addEventListener('click', (e) => {
        if (el._wasDragging) { el._wasDragging = false; return; }
        selectOrgan(o.key);
      });
    });
  }

  function makeDraggable(el, data) {
    let startX, startY, startLeft, startTop, moved = false;

    function onDown(e) {
      e.preventDefault();
      const ev = e.touches ? e.touches[0] : e;
      startX = ev.clientX; startY = ev.clientY;
      startLeft = parseFloat(el.style.left); startTop = parseFloat(el.style.top);
      moved = false;
      el.classList.add('dragging');
      bodyWrap.parentElement.classList.add('dragging-active');
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
      document.addEventListener('touchmove', onMove, { passive: false });
      document.addEventListener('touchend', onUp);
    }
    function onMove(e) {
      e.preventDefault();
      const ev = e.touches ? e.touches[0] : e;
      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;
      if (Math.abs(dx) + Math.abs(dy) > 3) moved = true;
      el.style.left = (startLeft + dx) + 'px';
      el.style.top = (startTop + dy) + 'px';
      // check drop-zone hover
      const cx = parseFloat(el.style.left) + data.w/2;
      const cy = parseFloat(el.style.top) + data.h/2;
      document.querySelectorAll('.drop-zone').forEach(z => {
        const zx = parseFloat(z.style.left) + parseFloat(z.style.width)/2;
        const zy = parseFloat(z.style.top) + parseFloat(z.style.height)/2;
        const dist = Math.hypot(cx-zx, cy-zy);
        z.classList.toggle('hover', z.dataset.target === data.key && dist < 40);
      });
    }
    function onUp(e) {
      el.classList.remove('dragging');
      bodyWrap.parentElement.classList.remove('dragging-active');
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('touchend', onUp);
      // snap back if near original
      const cx = parseFloat(el.style.left);
      const cy = parseFloat(el.style.top);
      const dist = Math.hypot(cx-data.x, cy-data.y);
      if (dist < 50) {
        el.style.transition = 'left 0.3s ease, top 0.3s ease';
        el.style.left = data.x + 'px';
        el.style.top = data.y + 'px';
        setTimeout(() => { el.style.transition = ''; el.classList.add('in-place'); setTimeout(()=>el.classList.remove('in-place'), 400); }, 10);
      }
      document.querySelectorAll('.drop-zone').forEach(z => z.classList.remove('hover'));
      if (moved) el._wasDragging = true;
    }

    el.addEventListener('mousedown', onDown);
    el.addEventListener('touchstart', onDown, { passive: false });
  }

  function renderOrganList() {
    organListEl.innerHTML = organs.map(o =>
      `<div class="organ-item ${o.key===activeKey?'active':''}" data-key="${o.key}">
        <div class="organ-num">${o.num}</div>
        <div style="flex:1"><div class="organ-name">${o.name}</div><div class="organ-name-en">${o.nameEn}</div></div>
      </div>`
    ).join('');
    organListEl.querySelectorAll('.organ-item').forEach(it => {
      it.addEventListener('click', () => selectOrgan(it.dataset.key));
    });
  }

  function selectOrgan(key) {
    activeKey = key;
    const o = organs.find(x => x.key === key);
    if (!o) return;

    infoNum.textContent = o.num;
    infoTitle.textContent = o.name;
    infoSub.textContent = o.nameEn.toUpperCase() + ' · איבר מס׳ ' + o.num;
    infoRole.textContent = o.role;
    infoDesc.innerHTML = o.desc;
    infoFacts.innerHTML = o.facts.map(f => `<li>${f}</li>`).join('');
    infoStats.innerHTML = o.stats.map(([v,l]) => `<div class="stat-box"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');

    // highlight in list & on body
    organListEl.querySelectorAll('.organ-item').forEach(it => it.classList.toggle('active', it.dataset.key === key));
    organLayer.querySelectorAll('.organ').forEach(el => el.classList.toggle('highlighted', el.dataset.key === key));
    // Fade info card
    document.getElementById('infoCard').animate(
      [{ opacity: 0.5, transform: 'translateX(-6px)' }, { opacity: 1, transform: 'translateX(0)' }],
      { duration: 280, easing: 'ease-out' }
    );
    // Stop any running sim unless matches
    stopSim();
  }

  function stopSim() {
    if (simulating) {
      organLayer.querySelectorAll('.organ').forEach(el => el.classList.remove('simulating'));
      simBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> הפעל סימולציה';
      simulating = null;
    }
  }

  simBtn.addEventListener('click', () => {
    if (simulating === activeKey) { stopSim(); return; }
    stopSim();
    simulating = activeKey;
    const el = organLayer.querySelector(`.organ[data-key="${activeKey}"]`);
    if (el) el.classList.add('simulating');
    simBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/></svg> עצור סימולציה';
    // Flash a toast-like hint? Just update desc briefly
    const origDesc = infoDesc.innerHTML;
    const msg = sims[activeKey];
    if (msg) {
      infoDesc.innerHTML = '<strong style="color:var(--gold)">' + msg + '</strong><br/><br/>' + origDesc;
    }
  });

  // Mode buttons
  document.querySelectorAll('.mode-btn').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('.mode-btn').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      currentMode = b.dataset.mode;
      bodyWrap.classList.toggle('exploded', currentMode === 'exploded');
      renderOrgans(currentMode);
      selectOrgan(activeKey);
    });
  });

  resetBtn.addEventListener('click', () => {
    currentMode = 'normal';
    document.querySelectorAll('.mode-btn').forEach(x => x.classList.toggle('active', x.dataset.mode==='normal'));
    bodyWrap.classList.remove('exploded');
    renderOrgans('normal');
    selectOrgan(activeKey);
  });

  // INIT
  renderOrganList();
  renderOrgans('normal');
  selectOrgan('brain');
})();
