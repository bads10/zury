/* ==========================================================================
   Quiz ISO/IEC 27001 LI — moteur de diapositives
   Un seul fichier, deux modes commutables a chaud :
     « entrainement » -> on repond, verdict vert / rouge, puis l'explication
     « corrige »      -> bonne reponse en vert, mauvaises en rouge, explication
   Les donnees (QUESTIONS) sont injectees avant ce script.
   ========================================================================== */
(function () {
  'use strict';

  var LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];
  var STORE = 'iso27001-quiz-v2';
  var TRAINING = 'entrainement';
  var KEY = 'corrige';
  var total = QUESTIONS.length;

  /* --- etat ------------------------------------------------------------- */
  var state = { pos: 0, answers: {}, mode: TRAINING };

  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || 'null');
    if (saved && typeof saved === 'object') {
      if (saved.mode === KEY || saved.mode === TRAINING) state.mode = saved.mode;
      if (typeof saved.pos === 'number') state.pos = Math.min(Math.max(saved.pos, 0), total);
      if (saved.answers && typeof saved.answers === 'object') state.answers = saved.answers;
    }
  } catch (e) { /* stockage indisponible : on continue sans reprise */ }

  function save() {
    try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) {}
  }

  function isTraining() { return state.mode === TRAINING; }

  /* La synthese n'existe qu'en entrainement : elle occupe la position
     total, juste apres la derniere question. */
  function maxPos() { return isTraining() ? total : total - 1; }

  /* --- index des quiz --------------------------------------------------- */
  var quizzes = [];
  var byQuiz = {};
  QUESTIONS.forEach(function (q, i) {
    if (!byQuiz[q.quiz]) {
      byQuiz[q.quiz] = { n: q.quiz, title: q.quizTitle, items: [] };
      quizzes.push(byQuiz[q.quiz]);
    }
    byQuiz[q.quiz].items.push(i);
  });

  /* --- raccourcis DOM --------------------------------------------------- */
  var $ = function (sel) { return document.querySelector(sel); };
  var stage = $('#stage');
  var fill = $('#progressFill');
  var counter = $('#counter');
  var scoreEl = $('#score');
  var ticksLabel = $('#ticksLabel');
  var ticksStrip = $('#ticksStrip');
  var sheet = $('#sheet');
  var sheetGrid = $('#sheetGrid');
  var keyhint = $('#keyhint');
  var btnPrev = $('#btnPrev');
  var btnNext = $('#btnNext');
  var btnReset = $('#btnReset');
  var modeBtns = [].slice.call(document.querySelectorAll('[data-mode]'));

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function pad(n, width) {
    var s = String(n);
    while (s.length < width) s = '0' + s;
    return s;
  }

  /* --- comptages -------------------------------------------------------- */
  function answered() { return Object.keys(state.answers).length; }

  function correctCount() {
    var c = 0;
    Object.keys(state.answers).forEach(function (k) {
      if (QUESTIONS[+k] && state.answers[k] === QUESTIONS[+k].correct) c++;
    });
    return c;
  }

  function quizStats(quiz) {
    var ok = 0, bad = 0;
    quiz.items.forEach(function (i) {
      var pick = state.answers[i];
      if (pick == null) return;
      if (pick === QUESTIONS[i].correct) ok++; else bad++;
    });
    return { ok: ok, bad: bad, done: ok + bad, total: quiz.items.length };
  }

  /* --- bloc explication ------------------------------------------------- */
  function explainBlock(q) {
    var box = el('div', 'explain');
    box.appendChild(el('div', 'explain__label', 'Explication'));
    box.appendChild(el('p', null, q.explanation));
    return box;
  }

  /* --- rendu d'une diapositive question --------------------------------- */
  function renderQuestion(index) {
    var q = QUESTIONS[index];
    var training = isTraining();
    var pick = state.answers[index];
    var revealed = !training || pick != null;

    var slide = el('div', 'slide');
    slide.setAttribute('role', 'group');
    slide.setAttribute('aria-label', 'Question ' + q.n + ' sur ' + total);

    /* bandeau de reperage */
    var eyebrow = el('div', 'slide__eyebrow');
    eyebrow.appendChild(el('span', 'chip chip--quiz', 'Quiz ' + pad(q.quiz, 2)));
    if (q.scenario) {
      eyebrow.appendChild(el('span', 'chip chip--scenario', 'Scénario ' + q.scenario));
    }
    eyebrow.appendChild(el('span', 'slide__topic', q.quizTitle));
    slide.appendChild(eyebrow);

    /* dossier de scenario : ouvert sur la premiere question, replie ensuite */
    if (q.scenarioText && q.scenarioText.length) {
      var siblings = QUESTIONS.reduce(function (acc, item, i) {
        if (item.quiz === q.quiz && item.scenario === q.scenario) acc.push(i);
        return acc;
      }, []);
      var isFirst = siblings[0] === index;

      var det = el('details', 'scenario');
      det.open = isFirst;
      det.appendChild(el('summary', null, 'Scénario ' + q.scenario + ' — contexte'
        + (isFirst ? '' : ' (replié)')));

      var body = el('div', 'scenario__body');
      var prose = el('div', 'scenario__prose');
      q.scenarioText.forEach(function (para) { prose.appendChild(el('p', null, para)); });
      body.appendChild(prose);

      var jump = el('nav', 'scenario__jump');
      jump.setAttribute('aria-label', 'Questions du scénario ' + q.scenario);
      jump.appendChild(el('span', 'scenario__jump-label', siblings.length + ' questions'));
      siblings.forEach(function (i) {
        var b = el('button', 'jumpbtn', 'Question ' + pad(QUESTIONS[i].n, 3));
        b.type = 'button';
        if (i === index) b.setAttribute('aria-current', 'true');
        b.addEventListener('click', function () { go(i); });
        jump.appendChild(b);
      });
      body.appendChild(jump);

      det.appendChild(body);
      slide.appendChild(det);
    }

    /* enonce */
    var qBlock = el('div', 'question');
    qBlock.appendChild(el('div', 'question__index mono', pad(q.n, 3)));
    qBlock.appendChild(el('h1', 'question__text', q.question));
    slide.appendChild(qBlock);

    /* verdict immediat (entrainement, apres reponse) */
    if (training && pick != null) {
      var good = pick === q.correct;
      var bar = el('div', 'verdictbar');
      bar.setAttribute('data-verdict', good ? 'ok' : 'bad');
      bar.setAttribute('role', 'status');
      bar.appendChild(el('span', null, good ? '✓ Bonne réponse' : '✗ Mauvaise réponse'));
      if (!good) {
        bar.appendChild(el('small', null, 'La bonne réponse est ' + LETTERS[q.correct] + '.'));
      }
      slide.appendChild(bar);
    }

    /* options */
    var list = el('ul', 'options');
    q.options.forEach(function (text, i) {
      var li = el('li');
      var btn = el('button', 'option');
      btn.type = 'button';
      btn.style.setProperty('--delay', (i * 0.045) + 's');
      btn.appendChild(el('span', 'option__key', LETTERS[i]));
      btn.appendChild(el('span', 'option__label', text));
      var verdict = el('span', 'option__verdict');
      btn.appendChild(verdict);

      if (revealed) {
        var good = i === q.correct;
        btn.setAttribute('data-verdict', good ? 'ok' : 'bad');
        btn.disabled = true;
        if (good) {
          verdict.textContent = '✓ Bonne réponse';
        } else if (training && pick === i) {
          verdict.textContent = '✗ Votre réponse';
        } else {
          verdict.textContent = '✗ Mauvaise réponse';
        }
        if (training && pick === i) btn.setAttribute('data-picked', 'true');
      } else {
        btn.addEventListener('click', function () { answer(index, i); });
      }

      li.appendChild(btn);
      list.appendChild(li);
    });
    slide.appendChild(list);

    /* explication : d'emblee en corrige, apres la reponse en entrainement */
    if (revealed && q.explanation) slide.appendChild(explainBlock(q));

    /* invitation a repondre, tant que rien n'est coche */
    if (!revealed) {
      var hint = el('p', 'prompt', 'Choisissez une réponse pour voir le verdict et l’explication.');
      slide.appendChild(hint);
    }

    return slide;
  }

  /* --- rendu de la diapositive de synthese ------------------------------ */
  function renderReport() {
    var wrap = el('div', 'slide wrap');
    var done = answered();
    var ok = correctCount();
    var bad = done - ok;
    var pct = done ? Math.round((ok / done) * 100) : 0;

    var eyebrow = el('div', 'slide__eyebrow');
    eyebrow.appendChild(el('span', 'chip chip--quiz', 'Synthèse'));
    eyebrow.appendChild(el('span', 'slide__topic', total + ' questions · 27 quiz'));
    wrap.appendChild(eyebrow);

    wrap.appendChild(el('h1', 'wrap__title', 'Résultats des 27 quiz'));
    wrap.appendChild(el('p', 'wrap__lede', done === total
      ? 'Vous avez répondu à l’ensemble des ' + total + ' questions. Le détail par quiz indique où concentrer vos révisions avant l’examen.'
      : 'Vous avez répondu à ' + done + ' des ' + total + ' questions. Le détail par quiz indique où concentrer vos révisions.'));

    var metrics = el('div', 'metrics');
    [
      ['metric metric--accent', pct + ' %', 'Taux de réussite'],
      ['metric metric--ok', String(ok), 'Bonnes réponses'],
      ['metric metric--bad', String(bad), 'Mauvaises réponses'],
      ['metric', done + ' / ' + total, 'Questions traitées']
    ].forEach(function (m) {
      var card = el('div', m[0]);
      card.appendChild(el('div', 'metric__value mono', m[1]));
      card.appendChild(el('div', 'metric__label', m[2]));
      metrics.appendChild(card);
    });
    wrap.appendChild(metrics);

    var tw = el('div', 'tablewrap');
    var table = el('table', 'report');
    var thead = el('thead');
    var hr = el('tr');
    ['Quiz', 'Thème', 'Traitées', 'Justes', 'Fausses', 'Score'].forEach(function (h, i) {
      hr.appendChild(el('th', i === 1 ? null : 'num', h));
    });
    thead.appendChild(hr);
    table.appendChild(thead);

    var tbody = el('tbody');
    quizzes.forEach(function (quiz) {
      var s = quizStats(quiz);
      var tr = el('tr');
      tr.appendChild(el('td', 'num', pad(quiz.n, 2)));

      var tdTitle = el('td', 'title');
      var link = el('button', 'linkbtn', quiz.title);
      link.type = 'button';
      link.addEventListener('click', function () { go(quiz.items[0]); });
      tdTitle.appendChild(link);
      tr.appendChild(tdTitle);

      tr.appendChild(el('td', 'num', s.done + ' / ' + s.total));

      var tdOk = el('td', 'num');
      tdOk.appendChild(el('span', s.ok ? 'ok' : null, String(s.ok)));
      tr.appendChild(tdOk);

      var tdBad = el('td', 'num');
      tdBad.appendChild(el('span', s.bad ? 'bad' : null, String(s.bad)));
      tr.appendChild(tdBad);

      tr.appendChild(el('td', 'num', s.done ? Math.round((s.ok / s.done) * 100) + ' %' : '—'));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    tw.appendChild(table);
    wrap.appendChild(tw);

    var actions = el('div', 'wrap__actions');

    var again = el('button', 'navbtn navbtn--primary', 'Recommencer');
    again.type = 'button';
    again.addEventListener('click', reset);
    actions.appendChild(again);

    var review = el('button', 'navbtn', 'Passer au corrigé complet');
    review.type = 'button';
    review.addEventListener('click', function () { setMode(KEY, 0); });
    actions.appendChild(review);

    /* raccourci vers les questions manquees */
    var missed = Object.keys(state.answers).filter(function (k) {
      return state.answers[k] !== QUESTIONS[+k].correct;
    }).map(Number).sort(function (a, b) { return a - b; });

    if (missed.length) {
      var toMissed = el('button', 'navbtn',
        'Revoir la 1re erreur (question ' + pad(QUESTIONS[missed[0]].n, 3) + ')');
      toMissed.type = 'button';
      toMissed.addEventListener('click', function () { go(missed[0]); });
      actions.appendChild(toMissed);
    }

    wrap.appendChild(actions);
    return wrap;
  }

  /* --- appareillage : compteurs, jauge, releve -------------------------- */
  var HINT_TRAINING = '<span><kbd>A</kbd><kbd>B</kbd><kbd>C</kbd> répondre</span>'
    + '<span><kbd>&#8592;</kbd><kbd>&#8594;</kbd> naviguer</span>'
    + '<span><kbd>M</kbd> mode</span><span><kbd>S</kbd> sommaire</span>';
  var HINT_KEY = '<span><kbd>&#8592;</kbd><kbd>&#8594;</kbd> naviguer</span>'
    + '<span><kbd>M</kbd> revenir à l’entraînement</span><span><kbd>S</kbd> sommaire</span>';

  function renderChrome() {
    var training = isTraining();
    var onReport = training && state.pos >= total;
    var q = onReport ? null : QUESTIONS[state.pos];

    modeBtns.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.mode === state.mode));
    });

    keyhint.innerHTML = training ? HINT_TRAINING : HINT_KEY;

    counter.innerHTML = '';
    if (onReport) {
      counter.appendChild(el('span', null, 'Synthèse'));
    } else {
      counter.appendChild(el('b', null, pad(q.n, 3)));
      counter.appendChild(document.createTextNode(' / ' + total));
    }

    scoreEl.hidden = !training;
    btnReset.hidden = !training;
    if (training) {
      scoreEl.innerHTML = '';
      scoreEl.appendChild(el('b', null, String(correctCount())));
      scoreEl.appendChild(document.createTextNode(' justes / ' + answered() + ' traitées'));
    }

    var shown = onReport ? total : state.pos;
    fill.style.width = ((shown / total) * 100).toFixed(2) + '%';

    /* releve du quiz courant */
    ticksStrip.innerHTML = '';
    if (onReport) {
      ticksLabel.textContent = 'Fin du parcours';
      return;
    }
    var quiz = byQuiz[q.quiz];
    var s = quizStats(quiz);
    ticksLabel.textContent = 'Quiz ' + pad(quiz.n, 2) + ' · ' +
      (training ? s.done + '/' + s.total + ' traitées' : s.total + ' questions');

    quiz.items.forEach(function (i) {
      var t = el('button', 'tick');
      t.type = 'button';
      var label = 'Question ' + QUESTIONS[i].n;
      var pick = state.answers[i];
      if (pick != null) {
        var good = pick === QUESTIONS[i].correct;
        t.setAttribute('data-state', good ? 'ok' : 'bad');
        label += good ? ' — juste' : ' — fausse';
      } else if (!training && i < state.pos) {
        t.setAttribute('data-state', 'seen');
      }
      if (i === state.pos) t.setAttribute('aria-current', 'true');
      t.setAttribute('aria-label', label);
      t.title = label;
      t.addEventListener('click', function () { go(i); });
      ticksStrip.appendChild(t);
    });
  }

  /* --- navigation ------------------------------------------------------- */
  function render() {
    stage.innerHTML = '';
    stage.appendChild(isTraining() && state.pos >= total
      ? renderReport()
      : renderQuestion(state.pos));
    stage.scrollTop = 0;
    renderChrome();
    btnPrev.disabled = state.pos === 0;
    btnNext.disabled = state.pos >= maxPos();
    save();
  }

  function go(pos) {
    state.pos = Math.min(Math.max(pos, 0), maxPos());
    closeSheet();
    render();
  }

  function answer(index, choice) {
    state.answers[index] = choice;
    save();
    render();
  }

  /* Bascule de mode. La position est conservee : on reste sur la meme
     question en passant de l'entrainement au corrige et inversement. */
  function setMode(mode, pos) {
    if (mode !== TRAINING && mode !== KEY) return;
    var wasOnReport = isTraining() && state.pos >= total;
    state.mode = mode;
    if (pos != null) state.pos = pos;
    /* depuis la synthese, le corrige reprend au debut plutot que de retomber
       sur la derniere question par simple recadrage */
    else if (wasOnReport && mode === KEY) state.pos = 0;
    state.pos = Math.min(Math.max(state.pos, 0), maxPos());
    closeSheet();
    render();
  }

  function toggleMode() { setMode(isTraining() ? KEY : TRAINING); }

  function reset() {
    if (!window.confirm('Effacer toutes vos réponses et repartir de la question 1 ?')) return;
    state.answers = {};
    state.pos = 0;
    state.mode = TRAINING;
    save();
    render();
  }

  /* --- sommaire --------------------------------------------------------- */
  function buildSheet() {
    sheetGrid.innerHTML = '';
    quizzes.forEach(function (quiz) {
      var card = el('button', 'quizcard');
      card.type = 'button';
      if (QUESTIONS[state.pos] && QUESTIONS[state.pos].quiz === quiz.n) {
        card.setAttribute('aria-current', 'true');
      }
      card.appendChild(el('span', 'quizcard__n', pad(quiz.n, 2)));
      card.appendChild(el('span', 'quizcard__title', quiz.title));

      var meta = el('span', 'quizcard__meta');
      var s = quizStats(quiz);
      meta.appendChild(document.createTextNode(quiz.items.length + ' questions'));
      if (s.done) {
        meta.appendChild(document.createTextNode(' · '));
        meta.appendChild(el('span', 'ok', s.ok + ' justes'));
        meta.appendChild(document.createTextNode(' · '));
        meta.appendChild(el('span', 'bad', s.bad + ' fausses'));
      }
      card.appendChild(meta);

      card.addEventListener('click', function () { go(quiz.items[0]); });
      sheetGrid.appendChild(card);
    });
  }

  function openSheet() {
    buildSheet();
    sheet.setAttribute('data-open', 'true');
    var current = sheetGrid.querySelector('[aria-current="true"]') || sheetGrid.firstChild;
    if (current) current.focus();
  }

  function closeSheet() { sheet.setAttribute('data-open', 'false'); }

  function toggleSheet() {
    if (sheet.getAttribute('data-open') === 'true') closeSheet(); else openSheet();
  }

  /* --- branchements ----------------------------------------------------- */
  btnPrev.addEventListener('click', function () { go(state.pos - 1); });
  btnNext.addEventListener('click', function () { go(state.pos + 1); });
  btnReset.addEventListener('click', reset);
  $('#btnIndex').addEventListener('click', toggleSheet);
  $('#sheetClose').addEventListener('click', closeSheet);
  sheet.addEventListener('click', function (ev) { if (ev.target === sheet) closeSheet(); });

  modeBtns.forEach(function (b) {
    b.addEventListener('click', function () { setMode(b.dataset.mode); });
  });

  document.addEventListener('keydown', function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var tag = (ev.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;

    if (ev.key === 'Escape') {
      if (sheet.getAttribute('data-open') === 'true') { closeSheet(); ev.preventDefault(); }
      return;
    }

    /* sommaire ouvert : on laisse le clavier au sommaire */
    if (sheet.getAttribute('data-open') === 'true') return;

    /* un bouton a le focus : Entree et Espace lui appartiennent */
    var onControl = tag === 'button' || tag === 'summary' || tag === 'a';
    if (onControl && (ev.key === 'Enter' || ev.key === ' ')) return;

    switch (ev.key) {
      case 'ArrowRight': case 'PageDown': case ' ': case 'Enter':
        go(state.pos + 1); ev.preventDefault(); return;
      case 'ArrowLeft': case 'PageUp':
        go(state.pos - 1); ev.preventDefault(); return;
      case 'Home':
        go(0); ev.preventDefault(); return;
      case 'End':
        go(maxPos()); ev.preventDefault(); return;
    }

    var k = ev.key.toLowerCase();
    if (k === 's') { toggleSheet(); ev.preventDefault(); return; }
    if (k === 'm') { toggleMode(); ev.preventDefault(); return; }

    if (isTraining() && state.pos < total && state.answers[state.pos] == null) {
      var q = QUESTIONS[state.pos];
      var idx = -1;
      if (ev.key >= '1' && ev.key <= '9') idx = +ev.key - 1;
      else if (k >= 'a' && k <= 'f') idx = k.charCodeAt(0) - 97;
      if (idx >= 0 && idx < q.options.length) { answer(state.pos, idx); ev.preventDefault(); }
    }
  });

  render();
})();
