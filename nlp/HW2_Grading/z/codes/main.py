# How to run:
# Correct mode: python3.5 main.py probs.txt sents.txt
# Use multiplying instead of adding in Viterbi: python3.5 main.py probs.txt sents.txt a2m
# Don't normalize in Forward: python3.5 main.py probs.txt sents.txt xnor

import sys
import math

default_prob = 0.0001
tag_set = ['noun', 'verb', 'inf', 'prep']
tr_pr = {}
em_pr = {}
sentences = []

with open(sys.argv[1], 'r') as f:
    for l in f:
        if l.strip():
            l_lst = l.strip().split()
            if l_lst[0] in tag_set or l_lst[0] == 'phi':
                if l_lst[0] not in tr_pr:
                    tr_pr[l_lst[0]] = {}
                tr_pr[l_lst[0]][l_lst[1]] = float(l_lst[2])
            else:
                if l_lst[0] not in em_pr:
                    em_pr[l_lst[0]] = {}
                em_pr[l_lst[0]][l_lst[1]] = float(l_lst[2])

with open(sys.argv[2], 'r') as f:
    for l in f:
        if l.strip():
            sentences.append(l.strip())


def get_prob(word, tag, tag_previous, log):
    try:
        tr = tr_pr[tag][tag_previous]
    except:
        tr = default_prob
    try:
        em = em_pr[word][tag]
    except:
        em = default_prob
    if log:
        return math.log2(tr), math.log2(em)
    else:
        return tr, em


def viterbi(sentence):
    s = sentence.split()
    score = dict()
    backptr = {}
    score[0] = {}
    backptr[0] = {}
    for t in tag_set:
        tr, em = get_prob(s[0], t, 'phi', True)
        if len(sys.argv) > 3 and sys.argv[3] == 'a2m':
            score[0][t] = tr * em
        else:
            score[0][t] = tr + em
        backptr[0][t] = 'phi'
    for w in range(1, len(s)):
        score[w] = {}
        backptr[w] = {}
        for t in tag_set:
            max_t = ''
            max_score = -float('inf')
            for t_previous in tag_set:
                tr, em = get_prob(s[w], t, t_previous, True)
                if len(sys.argv) > 3 and sys.argv[3] == 'a2m':
                    if score[w-1][t_previous] * tr * em > max_score:
                        max_score = score[w-1][t_previous] * tr * em
                        max_t = t_previous
                else:
                    if score[w-1][t_previous] + tr + em > max_score:
                        max_score = score[w-1][t_previous] + tr + em
                        max_t = t_previous
            score[w][t] = max_score
            backptr[w][t] = max_t
    print('PROCESSING SENTENCE:', sentence)
    print()
    print('FINAL VITERBI NETWORK')
    for w in range(len(s)):
        for t in tag_set:
            print('P(%s=%s) = %.4f' % (s[w], t, score[w][t]))
    print()
    print('FINAL BACKPTR NETWORK')
    for w in range(1, len(s)):
        for t in tag_set:
            print('Backptr(%s=%s) = %s' % (s[w], t, backptr[w][t]))
    print()
    max_t = ''
    max_score = -float('inf')
    for t in tag_set:
        if score[len(s)-1][t] > max_score:
            max_score = score[len(s)-1][t]
            max_t = t
    print('BEST TAG SEQUENCE HAS LOG PROBABILITY = %.4f' % max_score)
    t = max_t
    for w in range(len(s)-1, -1, -1):
        print('%s -> %s' % (s[w], t))
        t = backptr[w][t]
    print()


def forward(sentence):
    s = sentence.split()
    score = dict()
    score[0] = {}
    for t in tag_set:
        tr, em = get_prob(s[0], t, 'phi', False)
        score[0][t] = tr * em
    for w in range(1, len(s)):
        score[w] = {}
        for t in tag_set:
            sum_score = 0
            for t_previous in tag_set:
                tr, em = get_prob(s[w], t, t_previous, False)
                sum_score += score[w-1][t_previous] * tr * em
            score[w][t] = sum_score
    print('FORWARD ALGORITHM RESULTS')
    for w in range(len(s)):
        sum_score = sum(score[w][t] for t in tag_set)
        for t in tag_set:
            if len(sys.argv) > 3 and sys.argv[3] == 'xnor':
                print('P(%s=%s) = %.4f' % (s[w], t, score[w][t]))
            else:
                print('P(%s=%s) = %.4f' % (s[w], t, score[w][t]/sum_score))
    print()
    print()


def main():
    for sentence in sentences:
        viterbi(sentence)
        forward(sentence)


if __name__ == '__main__':
    main()
