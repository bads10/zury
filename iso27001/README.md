# Quiz ISO/IEC 27001 Lead Implementer — diapositives interactives

Deux pages HTML autonomes, une question par diapositive :

| Fichier | Contenu | Origine |
| --- | --- | --- |
| **`quiz-iso27001.html`** | Les 164 questions des 27 quiz de la formation *Certified ISO/IEC 27001 Lead Implementer* (V10.0 FR) | Extraites de la fiche et du corrigé PECB (`.docx`) |
| **`quiz-iso27001-scenarios.html`** | 45 questions de scénario sur les domaines d'examen obtenus sous 70 %, avec comparaison au résultat d'examen | Rédigées pour ce dépôt (voir plus bas) |

Chaque fichier est entièrement autonome : CSS et JS intégrés, aucune ressource
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

## Édition « scénarios ciblés »

Construite à partir du résultat d'examen par domaine de compétence. Seuls les
domaines sous 70 % sont travaillés, pondérés selon l'écart :

| Domaine | Examen | Questions |
| --- | ---: | ---: |
| 1 — Principes et concepts fondamentaux d'un SMSI | 53,33 % | 10 |
| 2 — Système de management de la sécurité de l'information | 50 % | 10 |
| 3 — Planification de la mise en œuvre d'un SMSI | 55,56 % | 10 |
| 4 — Mise en œuvre d'un SMSI | 57,14 % | 10 |
| 6 — Amélioration continue d'un SMSI | 66,67 % | 5 |

Les domaines 5 (surveillance et mesure) et 7 (préparation à l'audit de
certification), obtenus à 80 %, ne sont pas repris.

Le format suit celui de l'examen PECB : six scénarios longs, chacun sous une
forme différente, qui mêlent plusieurs domaines comme à l'examen. Les questions
renvoient à un fait précis du récit (« Selon le scénario 3, … ») et demandent
souvent de juger une décision (« Oui, car… / Non, car… ») ou d'identifier une
mesure de l'Annexe A.

| Scénario | Forme | Questions |
| --- | --- | ---: |
| 1 — Aquila Pharma | Récit de lancement de projet | 8 |
| 2 — Terminal Rhône Conteneurs | Compte rendu de comité de pilotage (risques) | 8 |
| 3 — Kalia Pay | Chronologie horodatée d'un incident | 8 |
| 4 — Val-Vert Agglomération | Rapport d'audit interne et suites données | 7 |
| 5 — Pixelnord | Notes d'entretiens avec les responsables d'équipe | 7 |
| 6 — Hydréa | Décisions d'un comité de direction (NIS 2) | 7 |

La navigation se fait par scénario ; la synthèse compte par domaine et compare
chacun au score d'examen (colonnes *Examen* et *Écart*), avec le nombre de
domaines qui atteignent 70 %. Le rattachement de chaque question à un domaine
est une estimation de rédaction, PECB ne publiant pas cette correspondance.

**Ces 45 questions ne proviennent ni des supports PECB ni d'un recueil de
questions d'examen.** Elles sont rédigées pour ce dépôt à partir d'ISO/IEC
27001:2022, ISO/IEC 27002:2022, ISO/IEC 27000 et ISO/IEC 27005, et chaque
explication cite l'article ou la mesure en jeu. Les entreprises sont fictives.

Deux contrôles évitent que la forme des réponses ne trahisse la bonne :

- la bonne réponse est répartie à parts égales entre A, B et C (graine fixe) ;
- elle n'est la plus longue que dans un tiers des questions, comme le voudrait
  le hasard. Le script affiche ces deux mesures à chaque génération.

Pour refaire l'exercice après un nouvel examen, modifier `baseline` dans
l'édition `scenarios` de `build.py`, puis `python3 build.py scenarios`.

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

# 2. assembler les pages HTML (ou une seule : python3 build.py scenarios)
python3 build.py
```

Les questions de scénario se modifient dans `author_scenarios.py`, qui
régénère `data/scenarios.json` :

```bash
python3 author_scenarios.py data/scenarios.json && python3 build.py scenarios
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
extract_docx.py               extraction .docx -> data/quiz.json
build.py                      données + assets -> pages HTML (éditions quiz et scenarios)
data/quiz.json                les 164 questions extraites des supports
author_scenarios.py           source des 45 questions de scénario et contrôles de qualité
data/scenarios.json           les 45 questions de scénario, générées par author_scenarios.py
assets/deck.css               feuille de style (thèmes clair et sombre)
assets/deck.js                moteur de diapositives, bascule de mode, synthèse
quiz-iso27001.html            livrable : 164 questions
quiz-iso27001-scenarios.html  livrable : 6 scénarios, 45 questions ciblées
```
