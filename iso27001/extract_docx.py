#!/usr/bin/env python3
"""Extrait les quiz ISO/IEC 27001 LI depuis la fiche et le corrigé Word (.docx).

Usage:
    python3 extract_docx.py <fiche.docx> <corrige.docx> [-o data/quiz.json]

Les deux documents partagent la meme structure et le meme ordre de questions :
  - paragraphe en gras, non numerote, "Quiz N : titre"        -> nouvelle section
  - paragraphe en gras, non numerote, "Quiz base sur le scenario N :" -> section scenario
  - paragraphe en gras + numerote                             -> enonce de question
  - paragraphe non gras + numerote                            -> option de reponse
  - "Reponse correcte : X" / "Explication : ..."              -> corrige uniquement
"""
import argparse
import json
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

RE_QUIZ = re.compile(r'^Quiz\s*(\d+)\s*:\s*(.+)$')
RE_SCEN = re.compile(r'^Quiz\s+bas[ée]\s+sur\s+le\s+sc[ée]nario\s*(\d+)?\s*:?\s*(.*)$', re.I)
RE_ANS = re.compile(r'^R[ée]ponse\s+correcte\s*:\s*(.+)$', re.I)
RE_EXP = re.compile(r'^Explication\s*:\s*(.*)$', re.I)
RE_LEAD = re.compile(r'r[ée]pondez\s+aux\s+questions', re.I)


def norm(text):
    return re.sub(r'\s+', ' ', text).strip()


def read_paragraphs(docx_path):
    """Retourne [{text, bold, numbered}] dans l'ordre du document."""
    with zipfile.ZipFile(docx_path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    paras = []
    for p in root.iter(W + 'p'):
        chunks = []
        for node in p.iter():
            if node.tag == W + 't':
                chunks.append(node.text or '')
            elif node.tag in (W + 'tab', W + 'br'):
                chunks.append(' ')
        text = norm(''.join(chunks))
        if not text:
            continue
        bold = False
        for r in p.iter(W + 'r'):
            if not ''.join(n.text or '' for n in r.iter(W + 't')).strip():
                continue
            rpr = r.find(W + 'rPr')
            if rpr is not None and rpr.find(W + 'b') is not None:
                bold = True
        ppr = p.find(W + 'pPr')
        numbered = ppr is not None and ppr.find(W + 'numPr') is not None
        paras.append({'text': text, 'bold': bold, 'numbered': numbered})
    return paras


def parse(paras):
    questions = []
    quiz_n = quiz_title = None
    scen_n = None
    scen_text = []
    q = None
    mode = None

    for p in paras:
        t, bold, numbered = p['text'], p['bold'], p['numbered']

        if not numbered:
            m = RE_QUIZ.match(t)
            if m:
                quiz_n, quiz_title = int(m.group(1)), m.group(2).strip()
                scen_n, scen_text, q, mode = None, [], None, None
                continue
            m = RE_SCEN.match(t)
            if m:
                scen_n = int(m.group(1)) if m.group(1) else (scen_n or 0) + 1
                scen_text, q, mode = [], None, 'scenario'
                continue

        if quiz_n is None:
            continue

        if q is not None:
            m = RE_ANS.match(t)
            if m:
                q['answer'] = m.group(1).strip().rstrip('.')
                mode = 'answer'
                continue
            m = RE_EXP.match(t)
            if m:
                q['explanation'] = m.group(1).strip()
                mode = 'explanation'
                continue

        if bold and numbered:
            q = {
                'quiz': quiz_n,
                'quizTitle': quiz_title,
                'scenario': scen_n,
                'scenarioText': list(scen_text),
                'question': t,
                'options': [],
                'answer': None,
                'explanation': '',
            }
            questions.append(q)
            mode = 'question'
            continue

        if numbered and not bold and q is not None and mode in ('question', 'option'):
            q['options'].append(t)
            mode = 'option'
            continue

        if mode == 'scenario' and not numbered:
            if not RE_LEAD.search(t):
                scen_text.append(t)
            continue
        if mode == 'explanation' and q is not None:
            q['explanation'] += ' ' + t
            continue
        if mode == 'question' and q is not None:
            q['question'] += ' ' + t

    return questions


def slug(text):
    text = unicodedata.normalize('NFKD', text.lower())
    return re.sub(r'[^a-z0-9]', '', text)


def merge(worksheet, key):
    """Fusionne les deux documents, alignes position par position."""
    if len(worksheet) != len(key):
        sys.exit('Nombre de questions different : fiche=%d corrige=%d'
                 % (len(worksheet), len(key)))

    merged = []
    for i, (w, k) in enumerate(zip(worksheet, key), start=1):
        letter = k['answer'].strip().upper()
        if not re.fullmatch(r'[A-Z]', letter):
            sys.exit('Q%d : lettre de reponse inattendue %r' % (i, k['answer']))
        correct = ord(letter) - ord('A')
        if not 0 <= correct < len(k['options']):
            sys.exit('Q%d : reponse %s hors des %d options' % (i, letter, len(k['options'])))
        if len(w['options']) != len(k['options']):
            sys.exit('Q%d : nombre d options different entre les deux documents' % i)
        if slug(w['question'])[:40] != slug(k['question'])[:40]:
            print('avertissement Q%d : enonces divergents entre fiche et corrige' % i,
                  file=sys.stderr)

        merged.append({
            'n': i,
            'quiz': k['quiz'],
            'quizTitle': k['quizTitle'],
            'scenario': k['scenario'],
            'scenarioText': k['scenarioText'],
            'correct': correct,
            'explanation': k['explanation'],
            # enonce/options tels qu ils apparaissent dans chaque document
            'question': w['question'],
            'options': w['options'],
            'questionKey': k['question'],
            'optionsKey': k['options'],
        })
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('worksheet', help='fiche des quiz (.docx)')
    ap.add_argument('key', help='corrige des quiz (.docx)')
    ap.add_argument('-o', '--out', default='data/quiz.json')
    args = ap.parse_args()

    ws = parse(read_paragraphs(args.worksheet))
    ky = parse(read_paragraphs(args.key))
    data = merge(ws, ky)

    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    quizzes = sorted({q['quiz'] for q in data})
    print('%d questions, %d quiz -> %s' % (len(data), len(quizzes), args.out))


if __name__ == '__main__':
    main()
