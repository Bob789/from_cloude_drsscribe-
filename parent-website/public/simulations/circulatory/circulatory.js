(function() {
  'use strict';

  // ============ SCENARIOS ============
  const SCENARIOS = {
    rest: {
      bpm: 72, bp: '120/80', o2: 98, flow: 5.0,
      particleCount: 28, vesselOpacity: 0.55, arteryWidth: 6, speedMult: 1,
      heartColor: '#d6243a', stress: 0,
      title: 'מצב מנוחה',
      desc: 'בזמן מנוחה, הלב פועם בקצב תקין של כ-<strong>72 פעימות בדקה</strong>. הדם זורם בקצב אחיד, מספק חמצן לכל תאי הגוף ומחזיר דו-תחמוצת הפחמן לריאות לפליטה.',
      facts: ['5 ליטר דם נשאבים בדקה', 'ריווי חמצן אידאלי (98%)', 'עורקים רפויים, פתוחים', 'צריכת אנרגיה מינימלית']
    },
    exercise: {
      bpm: 145, bp: '140/85', o2: 96, flow: 18.0,
      particleCount: 48, vesselOpacity: 0.8, arteryWidth: 7, speedMult: 2.2,
      heartColor: '#e53947', stress: 0.3,
      title: 'פעילות גופנית',
      desc: 'בעומס גופני, השרירים דורשים <strong>3-4 פעמים יותר חמצן</strong>. הלב מגביר את קצבו, כלי הדם ברגליים ובשרירים מתרחבים, ולחץ הדם הסיסטולי עולה כדי להעביר דם מהר יותר.',
      facts: ['זרימה עד 18 ל׳ לדקה', 'כלי דם מתרחבים בשרירים', 'לחץ סיסטולי עולה זמנית', 'חום גוף עולה – הזעה']
    },
    hyper: {
      bpm: 88, bp: '162/102', o2: 97, flow: 5.5,
      particleCount: 32, vesselOpacity: 0.95, arteryWidth: 4, speedMult: 1.4,
      heartColor: '#c62634', stress: 0.7,
      title: 'לחץ דם גבוה (יתר לחץ דם)',
      desc: 'בלחץ דם גבוה כרוני, דפנות העורקים <strong>מתקשות ומצטמצמות</strong>. הלב נאלץ לעבוד קשה יותר כדי לדחוף את הדם דרך צינורות צרים — מצב שמעמיס את שריר הלב ומגדיל סיכון לשבץ והתקף לב.',
      facts: ['עורקים מוצרים – התנגדות גבוהה', 'עומס יתר על שריר הלב', 'סיכון לפגיעה בכליות ובעיניים', 'יעד טיפול: מתחת ל-140/90']
    },
    hypo: {
      bpm: 58, bp: '88/58', o2: 95, flow: 3.2,
      particleCount: 18, vesselOpacity: 0.35, arteryWidth: 6, speedMult: 0.55,
      heartColor: '#9b1a24', stress: 0.2,
      title: 'לחץ דם נמוך (תת לחץ דם)',
      desc: 'בלחץ דם נמוך, הדם <strong>לא מגיע ביעילות</strong> לאיברים – במיוחד למוח. התוצאה: סחרחורת, עייפות, טשטוש ראייה, ולעיתים עילפון בקימה מהירה. לרוב קשור להתייבשות, תרופות או מצב קרדיאלי.',
      facts: ['זרימה איטית ודלילה', 'סחרחורת בעמידה חדה', 'מוח מקבל פחות חמצן', 'חיוור ועור קר']
    },
    attack: {
      bpm: 112, bp: '100/70', o2: 90, flow: 3.5,
      particleCount: 22, vesselOpacity: 0.75, arteryWidth: 5, speedMult: 1.2,
      heartColor: '#7a1118', stress: 1, blocked: true,
      title: 'התקף לב (MI)',
      desc: 'בהתקף לב, <strong>עורק כלילי נחסם</strong> – בדרך כלל על ידי קריש דם על פלאק טרשתי. חלק משריר הלב אינו מקבל חמצן ומתחיל להיפגע. זה מצב חירום הדורש טיפול מיידי (תוך דקות עד שעה).',
      facts: ['חסימה בעורק כלילי', 'כאב חד בחזה, בגב וביד שמאל', 'צורך מיידי בהזעקת 101', 'כל דקה שחולפת = פחות שריר לב']
    },
    sleep: {
      bpm: 55, bp: '108/68', o2: 97, flow: 4.2,
      particleCount: 22, vesselOpacity: 0.45, arteryWidth: 6, speedMult: 0.7,
      heartColor: '#b61e2a', stress: 0,
      title: 'שינה',
      desc: 'בשינה עמוקה, מערכת העצבים הפרה-סימפתטית <strong>מאטה את הלב</strong>, לחץ הדם יורד והגוף עובר למצב שחזור. זה הזמן בו תאים מתחדשים והמוח מעבד זיכרונות.',
      facts: ['קצב לב יורד ב-15-20%', 'לחץ דם יורד בכ-10%', 'שחרור הורמוני גדילה', 'מערכת החיסון פועלת במלואה']
    }
  };

  const ORGAN_INFO = {
    heart: {
      icon: '❤', title: 'הלב — המשאבה המרכזית', sub: 'איבר מס׳ 3 · שריר',
      desc: 'הלב הוא שריר חלול בגודל אגרוף, השואב כ-<strong>5 ליטר דם</strong> בדקה. הוא מורכב מארבעה חדרים — שני פרוזדורים ושני חדרים — הפועלים בסנכרון מושלם.',
      facts: ['פועם כ-100,000 פעמים ביום', 'שואב 7,000 ליטר דם בכל יממה', 'מופעל על ידי פולסים חשמליים (SA node)', 'מקבל חמצן מעורקים כליליים'],
      stats: [['~300', 'גרם משקל'], ['4', 'חדרי לב'], ['5L', 'דם לדקה'], ['~70', 'פעימות/דקה']],
      grad: 'linear-gradient(135deg, #e53947, #7a1118)'
    },
    brain: {
      icon: '🧠', title: 'המוח', sub: 'איבר מס׳ 1 · מרכז הבקרה',
      desc: 'המוח צורך <strong>20% מהחמצן</strong> בגוף אף שהוא רק 2% מהמשקל. כל קיצור זרימה של 5-10 שניות גורם לאיבוד הכרה — לכן הוא ראשון שמקבל דם ממערכת העורקים.',
      facts: ['זרימת דם קבועה: 750 מ״ל/דקה', '20% מכל צריכת החמצן של הגוף', 'מוגן על ידי מחסום דם-מוח', 'מכיל כ-86 מיליארד נוירונים'],
      stats: [['~1.4', 'ק״ג'], ['20%', 'חמצן'], ['86B', 'נוירונים'], ['750', 'מ״ל/דקה']],
      grad: 'linear-gradient(135deg, #d4a08a, #6b3a24)'
    },
    lungs: {
      icon: '🫁', title: 'הריאות', sub: 'איבר מס׳ 2 · חילוף גזים',
      desc: 'הריאות <strong>ממירות דם דל-חמצן לדם מחומצן</strong>. דרך מיליוני שקיקי אוויר זעירים (אלבאולי) מתבצע חילוף חמצן ↔ דו-תחמוצת הפחמן. זהו המחזור הריאתי.',
      facts: ['כ-300 מיליון אלבאולי בכל ריאה', 'שטח חילוף גזים ~ 70 מ״ר', '12-20 נשימות בדקה במנוחה', 'מקבלות דם דל-חמצן מהחדר הימני'],
      stats: [['6L', 'קיבולת אוויר'], ['300M', 'אלבאולי'], ['70m²', 'שטח חילוף'], ['16', 'נשימות/ד׳']],
      grad: 'linear-gradient(135deg, #e88499, #a84a5e)'
    },
    liver: {
      icon: '🫀', title: 'הכבד', sub: 'איבר מס׳ 4 · בית חרושת כימי',
      desc: 'הכבד מקבל <strong>כ-1.5 ליטר דם בדקה</strong> דרך וריד השער. הוא מנקה רעלים, מייצר חלבונים, אוחסן סוכר ומסייע בעיכול. אין איבר אחר שעושה יותר תפקידים.',
      facts: ['מבצע מעל 500 תפקידים שונים', 'מפרק תרופות ואלכוהול', 'מייצר מרה לעיכול שומנים', 'יכול להתחדש מ-25% מהמסה'],
      stats: [['1.5L', 'דם/דקה'], ['1.5kg', 'משקל'], ['500+', 'תפקידים'], ['25%', 'יכולת התחדשות']],
      grad: 'linear-gradient(135deg, #a84228, #3e1a15)'
    },
    kidneys: {
      icon: '🫘', title: 'הכליות', sub: 'איבר מס׳ 5 · מסננים',
      desc: 'שתי הכליות מסננות <strong>כ-180 ליטר דם ביום</strong> ומפרישות שתן. הן גם מווסתות את לחץ הדם (דרך הורמון רנין), את איזון המלחים ואת ייצור כדוריות הדם האדומות.',
      facts: ['מסננות 180 ליטר דם ביממה', 'מייצרות כ-1.5 ליטר שתן ביום', '1 מיליון נפרונים בכל כליה', 'מווסתות לחץ דם דרך רנין'],
      stats: [['180L', 'סינון/יום'], ['1M', 'נפרונים'], ['2', 'כליות'], ['1.5L', 'שתן/יום']],
      grad: 'linear-gradient(135deg, #a57cb8, #43264d)'
    }
  };

  // ============ STATE ============
  let state = {
    scenario: 'rest',
    playing: true,
    speed: 1,
    particles: [],
    lastTime: 0,
    progress: [] // per particle
  };

  const wrap = document.getElementById('circWrap');
  const playBtn = document.getElementById('playBtn');
  const playIcon = document.getElementById('playIcon');
  const speedSlider = document.getElementById('speed');
  const resetBtn = document.getElementById('resetBtn');
  const infoCard = document.getElementById('infoCard');

  // Paths for particles to follow
  const PATHS = ['pathBrain', 'pathBrainReturn', 'pathLungL', 'pathLungLOut', 'pathLungR', 'pathLungROut', 'pathLiver', 'pathLiverReturn', 'pathKidneyL', 'pathKidneyLReturn', 'pathKidneyR', 'pathKidneyRReturn'];
  const PATH_TYPES = { pathBrain: 'artery', pathBrainReturn: 'vein', pathLungL: 'artery', pathLungLOut: 'vein', pathLungR: 'artery', pathLungROut: 'vein', pathLiver: 'artery', pathLiverReturn: 'vein', pathKidneyL: 'artery', pathKidneyLReturn: 'vein', pathKidneyR: 'artery', pathKidneyRReturn: 'vein' };

  function createParticles(count) {
    // Remove existing
    wrap.querySelectorAll('.particle').forEach(p => p.remove());
    state.particles = [];
    state.progress = [];

    // Distribute across paths
    for (let i = 0; i < count; i++) {
      const pathId = PATHS[i % PATHS.length];
      const pathEl = document.getElementById(pathId);
      if (!pathEl) continue;
      const type = PATH_TYPES[pathId];
      const el = document.createElement('div');
      el.className = `particle ${type}`;
      wrap.appendChild(el);
      state.particles.push({ el, pathEl, length: pathEl.getTotalLength(), type, pathId });
      state.progress.push(Math.random()); // start offset
    }
  }

  function updateParticles(dt) {
    for (let i = 0; i < state.particles.length; i++) {
      const p = state.particles[i];
      // Speed: 0.25 full path per second at speedMult=1, flow=5
      const sc = SCENARIOS[state.scenario];
      let speed = 0.3 * sc.speedMult * state.speed;
      // If heart attack, block one specific path
      if (sc.blocked && p.pathId === 'pathLungR') speed *= 0.1;
      state.progress[i] += speed * dt / 1000;
      if (state.progress[i] > 1) state.progress[i] -= 1;

      // Get position via SVG path
      const len = p.length * state.progress[i];
      const pt = p.pathEl.getPointAtLength(len);
      // SVG viewBox is 0-560, wrap is 560x560
      p.el.style.transform = `translate(${pt.x}px, ${pt.y}px) translate(-50%, -50%)`;
    }
  }

  let rafId;
  function loop(t) {
    if (!state.lastTime) state.lastTime = t;
    const dt = t - state.lastTime;
    state.lastTime = t;
    if (state.playing) updateParticles(dt);
    rafId = requestAnimationFrame(loop);
  }

  function applyScenario(key) {
    const sc = SCENARIOS[key];
    state.scenario = key;

    // Active button
    document.querySelectorAll('.sim-btn').forEach(b => b.classList.toggle('active', b.dataset.sc === key));

    // Vitals
    document.getElementById('v-hr').innerHTML = `${sc.bpm}<span class="unit">BPM</span>`;
    document.getElementById('v-bp').innerHTML = `${sc.bp}<span class="unit">mmHg</span>`;
    document.getElementById('v-o2').innerHTML = `${sc.o2}<span class="unit">%</span>`;
    document.getElementById('v-flow').innerHTML = `${sc.flow}<span class="unit">ל׳/ד׳</span>`;

    // Heart BPM
    document.documentElement.style.setProperty('--bpm', sc.bpm);

    // Vessel opacity
    document.querySelectorAll('.vessels path').forEach(p => {
      p.style.opacity = sc.vesselOpacity;
      if (p.getAttribute('stroke') === 'url(#gArt)') p.style.strokeWidth = sc.arteryWidth;
    });

    // Particles count
    createParticles(sc.particleCount);

    // ECG speed
    const ecgDur = Math.max(0.5, 60 / sc.bpm * 2).toFixed(2);
    document.querySelector('.ecg-line svg').style.animationDuration = `${ecgDur}s`;

    // Heart attack visual
    document.querySelectorAll('.organ').forEach(o => o.classList.remove('attack-flash'));
    if (sc.blocked) {
      document.querySelector('.organ-lung-r').style.filter = 'grayscale(0.6) brightness(0.6)';
    } else {
      document.querySelectorAll('.organ').forEach(o => o.style.filter = '');
    }

    // High blood pressure: narrow arteries visual
    if (key === 'hyper') {
      wrap.style.filter = 'contrast(1.1) saturate(1.15)';
    } else if (key === 'hypo') {
      wrap.style.filter = 'brightness(0.85) saturate(0.8)';
    } else if (key === 'attack') {
      wrap.style.filter = 'saturate(1.2) contrast(1.05)';
    } else {
      wrap.style.filter = '';
    }

    // Info card
    updateInfoCard({
      icon: key === 'attack' ? '⚠️' : key === 'exercise' ? '🏃' : key === 'hyper' ? '🔺' : key === 'hypo' ? '🔻' : key === 'sleep' ? '😴' : '❤',
      title: sc.title,
      sub: 'תרחיש · ' + (key === 'attack' ? 'חירום רפואי' : 'מצב פיזיולוגי'),
      desc: sc.desc,
      facts: sc.facts,
      stats: [[sc.bpm, 'BPM'], [sc.bp, 'mmHg'], [sc.o2 + '%', 'חמצן'], [sc.flow + 'L', 'זרימה/ד׳']],
      grad: 'linear-gradient(135deg, ' + sc.heartColor + ', #7a1118)'
    });
  }

  function updateInfoCard(info) {
    document.getElementById('infoIcon').textContent = info.icon;
    document.getElementById('infoIcon').style.background = info.grad;
    document.getElementById('infoTitle').textContent = info.title;
    document.getElementById('infoSub').textContent = info.sub;
    document.getElementById('infoDesc').innerHTML = info.desc;
    document.getElementById('infoFacts').innerHTML = info.facts.map(f => `<li>${f}</li>`).join('');
    const sg = infoCard.querySelector('.stat-grid');
    sg.innerHTML = info.stats.map(([v, l]) => `<div class="stat-box"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');
    // subtle fade
    infoCard.animate([{ opacity: 0.4, transform: 'translateX(-6px)' }, { opacity: 1, transform: 'translateX(0)' }], { duration: 320, easing: 'ease-out' });
  }

  // ============ ORGAN CLICK ============
  document.querySelectorAll('.organ, .heart-core').forEach(el => {
    el.addEventListener('click', () => {
      const key = el.dataset.organ;
      document.querySelectorAll('.organ, .heart-core').forEach(o => o.classList.remove('active'));
      el.classList.add('active');
      const info = ORGAN_INFO[key];
      if (!info) return;
      updateInfoCard(info);
    });
  });

  // ============ CONTROLS ============
  playBtn.addEventListener('click', () => {
    state.playing = !state.playing;
    playIcon.innerHTML = state.playing
      ? '<rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/>'
      : '<polygon points="6,4 20,12 6,20"/>';
  });
  speedSlider.addEventListener('input', (e) => { state.speed = parseFloat(e.target.value); });
  resetBtn.addEventListener('click', () => {
    applyScenario('rest');
    speedSlider.value = 1;
    state.speed = 1;
  });

  // ============ SCENARIOS ============
  document.querySelectorAll('.sim-btn').forEach(btn => {
    btn.addEventListener('click', () => applyScenario(btn.dataset.sc));
  });

  // ============ INIT ============
  applyScenario('rest');
  rafId = requestAnimationFrame(loop);
})();
