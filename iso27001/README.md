# Quiz ISO/IEC 27001 Lead Implementer — diapositives interactives

**`quiz-iso27001.html`** — un seul fichier, les 164 questions des 27 quiz de la
formation *Certified ISO/IEC 27001 Lead Implementer* (V10.0 FR), une question
par diapositive.

Le fichier est entièrement autonome : CSS et JS intégrés, aucune ressource
externe, aucun réseau requis. Il suffit de l'ouvrir dans un navigateur ou de
l'envoyer par e-mail.

## Deux modes, commutables depuis la page

| Mode | Comportement |
| --- | --- |
| **Entraînement** | Vous répondez. Le verdict s'affiche aussitôt — **bonne réponse en vert, mauvaise en rouge** — puis l'explication du corrigé se dévoile. Score suivi quiz par quiz, synthèse finale. |
| **Corrigé** | Tout est révélé d'emblée : **bonne réponse en vert, mauvaises en rouge**, avec l'explication sur chaque diapositive. |

Le sélecteur est dans la barre haute (ou touche <kbd>M</kbd>). La bascule
conserve la question courante : on peut vérifier un point dans le corrigé puis
revenir exactement là où on en était. Les réponses déjà données restent
marquées dans les deux modes.

## Contenu couvert

- 27 quiz, 164 questions
- 4 quiz basés sur un scénario (YoMedia, DetSearch, Ecovista Energy Global, Markt).
  Le contexte du scénario est déplié sur sa première question puis replié sur les
  suivantes, avec un renvoi direct vers les questions rattachées.

## Utilisation

- <kbd>A</kbd> <kbd>B</kbd> <kbd>C</kbd> (ou <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd>) — répondre
- <kbd>←</kbd> <kbd>→</kbd>, <kbd>Espace</kbd>, <kbd>Page↑</kbd> <kbd>Page↓</kbd> — naviguer
- <kbd>Début</kbd> / <kbd>Fin</kbd> — première question / synthèse
- <kbd>M</kbd> — changer de mode, <kbd>S</kbd> — sommaire des 27 quiz, <kbd>Échap</kbd> — fermer

Le mode, la progression et les réponses sont conservés dans le navigateur : on
peut fermer la page et reprendre où l'on s'était arrêté. Le bouton
« Recommencer » efface tout.

Thèmes clair et sombre selon le réglage du système. Mise en page vérifiée de
320 px à 1440 px.

## Régénérer

```bash
# 1. extraire les questions des deux .docx  ->  data/quiz.json
python3 extract_docx.py \
  05_27001LI_Quizzes_Worksheet_V10.0_FR.DOCX \
  06_27001LI_Quizzes_Correction_Key_V10.0_FR.DOCX \
  -o data/quiz.json

# 2. assembler la page HTML
python3 build.py
```

`extract_docx.py` n'a besoin que de la bibliothèque standard : il lit
`word/document.xml` dans l'archive `.docx` et s'appuie sur la mise en forme
(gras, numérotation) pour distinguer les titres de quiz, les énoncés, les
options, la réponse correcte et l'explication. Les deux documents sont ensuite
alignés position par position ; toute divergence de structure interrompt
l'extraction plutôt que de produire un corrigé décalé.

Trois questions (40, 55, 81) sont formulées différemment dans la fiche et dans
le corrigé — même question, autre tournure. `data/quiz.json` conserve les deux
versions (`question` / `questionKey`) ; la page affiche celle de la fiche.

## Organisation

```
extract_docx.py     extraction .docx -> JSON
build.py            JSON + assets -> quiz-iso27001.html
data/quiz.json      les 164 questions (énoncé, options, bonne réponse, explication)
assets/deck.css     feuille de style (thèmes clair et sombre)
assets/deck.js      moteur de diapositives et bascule de mode
quiz-iso27001.html  le livrable, autonome
```
