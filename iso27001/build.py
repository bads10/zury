#!/usr/bin/env python3
"""Assemble la page HTML autonome du quiz ISO/IEC 27001 LI.

    python3 build.py            # lit data/quiz.json, ecrit quiz-iso27001.html

Un seul fichier, deux modes commutables depuis la page :
  Entrainement -> on repond, verdict vert / rouge, puis l'explication
  Corrige      -> bonne reponse en vert, mauvaises en rouge, explication

CSS et JS sont integres : aucune ressource externe, aucun reseau requis.
"""
import argparse
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = 'quiz-iso27001.html'

TITLE = 'Quiz ISO 27001 Lead Implementer'
DESCRIPTION = ('Les 164 questions des 27 quiz de la formation ISO/IEC 27001 Lead '
               'Implementer, une par diapositive : mode entraînement avec verdict '
               'immédiat, mode corrigé avec la bonne réponse en vert, les mauvaises '
               'en rouge et l’explication.')

# Champs conserves dans la page. On laisse de cote les variantes de formulation
# du corrige (questionKey / optionsKey) : la page affiche l enonce de la fiche,
# et data/quiz.json garde les deux versions pour tracabilite.
FIELDS = ('n', 'quiz', 'quizTitle', 'scenario', 'scenarioText',
          'question', 'options', 'correct', 'explanation')

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
        <span class="brand__mark">27001 LI</span>
        <span class="brand__name">Certified ISO/IEC 27001 Lead Implementer</span>
      </div>

      <span class="topbar__spacer"></span>

      <div class="modeswitch" role="group" aria-label="Mode d’affichage">
        <button class="modeswitch__btn" type="button" data-mode="entrainement"
                aria-pressed="true">Entraînement</button>
        <button class="modeswitch__btn" type="button" data-mode="corrige"
                aria-pressed="false">Corrigé</button>
      </div>

      <span class="counter mono" id="counter"></span>
      <button class="iconbtn" type="button" id="btnIndex" aria-haspopup="dialog">Sommaire</button>
      <button class="iconbtn" type="button" id="btnReset">Recommencer</button>
    </div>

    <div class="progress" role="progressbar" aria-label="Progression">
      <div class="progress__fill" id="progressFill"></div>
    </div>

    <div class="ticks">
      <div class="ticks__row">
        <span class="ticks__label" id="ticksLabel"></span>
        <div class="ticks__strip" id="ticksStrip"></div>
        <span class="topbar__spacer"></span>
        <span class="score mono" id="score"></span>
      </div>
    </div>
  </header>

  <main class="stage" id="stage"></main>

  <footer class="navbar">
    <div class="navbar__row">
      <button class="navbtn" type="button" id="btnPrev">&#8592; Précédent</button>
      <p class="keyhint" id="keyhint"></p>
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
var QUESTIONS = {data};
</script>
<script>
{js}
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--data', default=str(HERE / 'data' / 'quiz.json'))
    ap.add_argument('-o', '--out', default=str(HERE / OUT))
    args = ap.parse_args()

    raw = json.loads(pathlib.Path(args.data).read_text(encoding='utf-8'))
    data = [{k: q[k] for k in FIELDS} for q in raw]

    # </script> dans une chaine JSON casserait le bloc script : on l echappe.
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')) \
        .replace('</', '<\\/')

    html = PAGE.format(
        title=TITLE,
        description=DESCRIPTION,
        data=payload,
        css=(HERE / 'assets' / 'deck.css').read_text(encoding='utf-8'),
        js=(HERE / 'assets' / 'deck.js').read_text(encoding='utf-8'),
    )

    path = pathlib.Path(args.out)
    path.write_text(html, encoding='utf-8')
    print('%-28s %6.1f Ko  (%d questions)' % (path.name, path.stat().st_size / 1024, len(data)))


if __name__ == '__main__':
    main()
