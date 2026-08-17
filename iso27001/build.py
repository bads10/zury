#!/usr/bin/env python3
"""Assemble les deux fichiers HTML autonomes du quiz ISO/IEC 27001 LI.

    python3 build.py            # lit data/quiz.json, ecrit les deux .html

Sortie :
  quiz-iso27001-questions.html -> 164 questions interactives (verdict vert/rouge)
  quiz-iso27001-corrige.html   -> memes questions, bonne reponse en vert,
                                  mauvaises en rouge, avec l'explication

Chaque fichier est autonome : CSS et JS sont integres, aucune ressource externe.
"""
import argparse
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

PAGE = """<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<style>
{css}
</style>

<div class="app">
  <header class="topbar">
    <div class="topbar__row">
      <div class="brand">
        <span class="brand__mark">{mark}</span>
        <span class="brand__name">{brand}</span>
      </div>
      <span class="topbar__spacer"></span>
      <span class="counter mono" id="counter"></span>
      {score_markup}
      <button class="iconbtn" type="button" id="btnIndex" aria-haspopup="dialog">Sommaire</button>
      {reset_markup}
    </div>
    <div class="progress" role="progressbar" aria-label="Progression">
      <div class="progress__fill" id="progressFill"></div>
    </div>
    <div class="ticks">
      <div class="ticks__row">
        <span class="ticks__label" id="ticksLabel"></span>
        <div class="ticks__strip" id="ticksStrip"></div>
      </div>
    </div>
  </header>

  <main class="stage" id="stage"></main>

  <footer class="navbar">
    <div class="navbar__row">
      <button class="navbtn" type="button" id="btnPrev">&#8592; Précédent</button>
      <p class="keyhint">{keyhint}</p>
      <button class="navbtn navbtn--primary" type="button" id="btnNext">Suivant &#8594;</button>
    </div>
  </footer>
</div>

<div class="sheet" id="sheet" data-open="false" role="dialog" aria-modal="true" aria-label="Sommaire des quiz">
  <div class="sheet__panel">
    <div class="sheet__head">
      <h2 class="sheet__title">Les 27 quiz</h2>
      <span class="topbar__spacer"></span>
      <button class="iconbtn" type="button" id="sheetClose">Fermer</button>
    </div>
    <div class="sheet__grid" id="sheetGrid"></div>
  </div>
</div>

<script>
var MODE = {mode};
var QUESTIONS = {data};
</script>
<script>
{js}
</script>
"""

KEYHINT_QUIZ = (
    '<span><kbd>A</kbd><kbd>B</kbd><kbd>C</kbd> répondre</span>'
    '<span><kbd>&#8592;</kbd><kbd>&#8594;</kbd> naviguer</span>'
    '<span><kbd>S</kbd> sommaire</span>'
)
KEYHINT_KEY = (
    '<span><kbd>&#8592;</kbd><kbd>&#8594;</kbd> naviguer</span>'
    '<span><kbd>S</kbd> sommaire</span>'
    '<span><kbd>Début</kbd> revenir au début</span>'
)

VARIANTS = {
    'questions': {
        'file': 'quiz-iso27001-questions.html',
        'mode': 'quiz',
        'title': 'Quiz ISO 27001 Lead Implementer',
        'mark': 'Fiche des quiz',
        'brand': 'Formation Certified ISO/IEC 27001 Lead Implementer',
        'description': ('Les 164 questions des 27 quiz de la formation ISO/IEC 27001 '
                        'Lead Implementer, une par diapositive, avec verdict immédiat '
                        'et suivi du score.'),
        'keyhint': KEYHINT_QUIZ,
        'score': True,
        'reset': True,
    },
    'corrige': {
        'file': 'quiz-iso27001-corrige.html',
        'mode': 'corrige',
        'title': 'Corrigé ISO 27001 Lead Implementer',
        'mark': 'Corrigé des quiz',
        'brand': 'Formation Certified ISO/IEC 27001 Lead Implementer',
        'description': ('Corrigé des 164 questions de la formation ISO/IEC 27001 Lead '
                        'Implementer : bonne réponse en vert, mauvaises en rouge, '
                        'explication à chaque diapositive.'),
        'keyhint': KEYHINT_KEY,
        'score': False,
        'reset': False,
    },
}

SCORE_MARKUP = '<span class="score mono" id="score"></span>'
RESET_MARKUP = '<button class="iconbtn" type="button" id="btnReset">Recommencer</button>'


def build(variant, data, css, js, outdir):
    v = VARIANTS[variant]
    # </script> dans une chaine JSON casserait le bloc script : on l echappe.
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')) \
        .replace('</', '<\\/')
    html = PAGE.format(
        title=v['title'],
        description=v['description'],
        mark=v['mark'],
        brand=v['brand'],
        keyhint=v['keyhint'],
        score_markup=SCORE_MARKUP if v['score'] else '',
        reset_markup=RESET_MARKUP if v['reset'] else '',
        mode=json.dumps(v['mode']),
        data=payload,
        css=css,
        js=js,
    )
    path = outdir / v['file']
    path.write_text(html, encoding='utf-8')
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--data', default=str(HERE / 'data' / 'quiz.json'))
    ap.add_argument('-o', '--outdir', default=str(HERE))
    args = ap.parse_args()

    data = json.loads(pathlib.Path(args.data).read_text(encoding='utf-8'))
    css = (HERE / 'assets' / 'deck.css').read_text(encoding='utf-8')
    js = (HERE / 'assets' / 'deck.js').read_text(encoding='utf-8')
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for variant in VARIANTS:
        path = build(variant, data, css, js, outdir)
        print('%-32s %6.1f Ko' % (path.name, path.stat().st_size / 1024))


if __name__ == '__main__':
    main()
