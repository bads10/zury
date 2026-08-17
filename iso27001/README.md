# Quiz ISO/IEC 27001 Lead Implementer — diapositives interactives

Deux pages HTML autonomes générées depuis la fiche des quiz et le corrigé
de la formation *Certified ISO/IEC 27001 Lead Implementer* (V10.0 FR).

| Fichier | Contenu |
| --- | --- |
| `quiz-iso27001-questions.html` | Les 164 questions, une par diapositive. On répond, le verdict s'affiche aussitôt : **bonne réponse en vert, mauvaise en rouge**. Score suivi quiz par quiz, synthèse finale. |
| `quiz-iso27001-corrige.html` | Les mêmes 164 questions avec la **bonne réponse en vert**, les **mauvaises en rouge**, et l'explication du corrigé sur chaque diapositive. |

Chaque fichier est entièrement autonome : CSS et JS intégrés, aucune ressource
externe, aucun réseau requis. Il suffit de l'ouvrir dans un navigateur ou de
l'envoyer par e-mail.

## Contenu couvert

- 27 quiz, 164 questions
- 4 quiz basés sur un scénario (YoMedia, DetSearch, Ecovista Energy Global, Markt).
  Le contexte du scénario est déplié sur sa première question puis replié sur les
  suivantes, avec un renvoi direct vers les questions rattachées.

## Utilisation

- <kbd>A</kbd> <kbd>B</kbd> <kbd>C</kbd> (ou <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd>) — répondre
- <kbd>←</kbd> <kbd>→</kbd>, <kbd>Espace</kbd>, <kbd>Page↑</kbd> <kbd>Page↓</kbd> — naviguer
- <kbd>Début</kbd> / <kbd>Fin</kbd> — première question / synthèse
- <kbd>S</kbd> — sommaire des 27 quiz, <kbd>Échap</kbd> pour le fermer

La progression et les réponses sont conservées dans le navigateur : on peut
fermer la page et reprendre où l'on s'était arrêté. Le bouton « Recommencer »
efface tout.

## Régénérer

```bash
# 1. extraire les questions des deux .docx  ->  data/quiz.json
python3 extract_docx.py \
  05_27001LI_Quizzes_Worksheet_V10.0_FR.DOCX \
  06_27001LI_Quizzes_Correction_Key_V10.0_FR.DOCX \
  -o data/quiz.json

# 2. assembler les deux pages HTML
python3 build.py
```

`extract_docx.py` n'a besoin que de la bibliothèque standard : il lit
`word/document.xml` dans l'archive `.docx` et s'appuie sur la mise en forme
(gras, numérotation) pour distinguer les titres de quiz, les énoncés, les
options, la réponse correcte et l'explication. Les deux documents sont ensuite
alignés position par position ; toute divergence de structure interrompt
l'extraction plutôt que de produire un corrigé décalé.

## Organisation

```
extract_docx.py    extraction .docx -> JSON
build.py           JSON + assets -> les deux pages HTML
data/quiz.json     les 164 questions (énoncé, options, bonne réponse, explication)
assets/deck.css    feuille de style commune (thèmes clair et sombre)
assets/deck.js     moteur de diapositives commun aux deux modes
```

Les deux pages partagent le même CSS et le même JS ; c'est la variable `MODE`
injectée à la construction qui décide du comportement (`quiz` ou `corrige`).
