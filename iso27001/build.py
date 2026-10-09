#!/usr/bin/env python3
"""Assemble les pages HTML autonomes du quiz ISO/IEC 27001 LI.

    python3 build.py             # construit toutes les éditions
    python3 build.py scenarios   # une seule édition

Éditions :
  quiz       -> quiz-iso27001.html            les 164 questions des 27 quiz (fiche + corrigé)
  scenarios  -> quiz-iso27001-scenarios.html  6 scénarios, 45 questions sur les domaines < 70 %

Chaque page a deux modes commutables (Entraînement / Corrigé) et intègre son
CSS et son JS : aucune ressource externe, aucun réseau requis.
"""
import argparse
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# Champs conservés dans la page. data/quiz.json garde en plus les variantes de
# formulation du corrigé (questionKey / optionsKey), inutiles à l'affichage.
FIELDS = ('n', 'quiz', 'quizTitle', 'scenario', 'scenarioText',
          'question', 'options', 'correct', 'explanation')
OPTIONAL = ('domain',          # domaine d'examen, utilisé par la synthèse par domaine
            'groupTag', 'groupShort', 'scenarioLabel')   # libellés de série facultatifs

EDITIONS = {
    'quiz': {
        'data': 'data/quiz.json',
        'out': 'quiz-iso27001.html',
        'title': 'Quiz ISO 27001 Lead Implementer',
        'description': ('Les 164 questions des 27 quiz de la formation ISO/IEC 27001 Lead '
                        'Implementer, une par diapositive : mode entraînement avec verdict '
                        'immédiat, mode corrigé avec la bonne réponse en vert, les mauvaises '
                        'en rouge et l’explication.'),
        'mark': '27001 LI',
        'brand': 'Certified ISO/IEC 27001 Lead Implementer',
        'sheet': 'Les 27 quiz',
        'config': {},
    },
    'scenarios': {
        'data': 'data/scenarios.json',
        'out': 'quiz-iso27001-scenarios.html',
        'title': 'Scénarios ISO 27001 ciblés',
        'description': ('6 scénarios et 45 questions au format de l’examen PECB ISO/IEC 27001 '
                        'Lead Implementer, ciblés sur les domaines obtenus sous 70 %, avec '
                        'comparaison domaine par domaine au résultat d’examen.'),
        'mark': 'Scénarios',
        'brand': 'Domaines 1, 2, 3, 4 et 6 — sous 70 % à l’examen',
        'sheet': 'Les 6 scénarios',
        'config': {
            'store': 'iso27001-scenarios-v2',
            # navigation par scenario (champ quiz), synthese par domaine (champ domain)
            'group': 'Scénario',
            'groups': 'scénarios',
            'groupPad': 1,
            'scenarioChip': False,
            'reportBy': 'domain',
            'target': 70,
            'reportTitle': 'Vos domaines, avant et après',
            'domains': {
                '1': 'Principes et concepts fondamentaux d’un SMSI',
                '2': 'Système de management de la sécurité de l’information (SMSI)',
                '3': 'Planification de la mise en œuvre d’un SMSI selon ISO/IEC 27001',
                '4': 'Mise en œuvre d’un SMSI selon ISO/IEC 27001',
                '6': 'Amélioration continue d’un SMSI selon ISO/IEC 27001',
            },
            # résultat de l'examen ISO/IEC 27001 LI, par domaine de compétence
            'baseline': {'1': 53.33, '2': 50, '3': 55.56, '4': 57.14, '6': 66.67},
        },
    },
}

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

<div class="sheet" id="sheet" data-open="false" role="dialog" aria-modal="true" aria-label="{sheet}">
  <div class="sheet__panel">
    <div class="sheet__head">
      <h2 class="sheet__title">{sheet}</h2>
      <span class="topbar__spacer"></span>
      <button class="iconbtn" type="button" id="sheetClose">Fermer</button>
    </div>
    <div class="sheet__grid" id="sheetGrid"></div>
  </div>
</div>

<script>
var CONFIG = {config};
var QUESTIONS = {data};
</script>
<script>
{js}
</script>
"""


def as_js(value):
    # </script> dans une chaîne JSON casserait le bloc script : on l'échappe.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def build(name):
    ed = EDITIONS[name]
    raw = json.loads((HERE / ed['data']).read_text(encoding='utf-8'))
    data = [dict({k: q[k] for k in FIELDS}, **{k: q[k] for k in OPTIONAL if k in q})
            for q in raw]

    html = PAGE.format(
        title=ed['title'],
        description=ed['description'],
        mark=ed['mark'],
        brand=ed['brand'],
        sheet=ed['sheet'],
        config=as_js(ed['config']),
        data=as_js(data),
        css=(HERE / 'assets' / 'deck.css').read_text(encoding='utf-8'),
        js=(HERE / 'assets' / 'deck.js').read_text(encoding='utf-8'),
    )
    path = HERE / ed['out']
    path.write_text(html, encoding='utf-8')
    print('%-32s %6.1f Ko  (%d questions)' % (path.name, path.stat().st_size / 1024, len(data)))


def main():
    ap = argparse.ArgumentParser()
    # pas de choices= ici : avec nargs='*', argparse rejette la liste vide
    ap.add_argument('editions', nargs='*', help='parmi : %s (par défaut : toutes)' % ', '.join(EDITIONS))
    args = ap.parse_args()
    unknown = [e for e in args.editions if e not in EDITIONS]
    if unknown:
        ap.error('édition inconnue : %s (choix : %s)' % (', '.join(unknown), ', '.join(EDITIONS)))
    for name in args.editions or EDITIONS:
        build(name)


if __name__ == '__main__':
    main()
