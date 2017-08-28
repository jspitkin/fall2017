""" jsp 08/25/17 - programming assignment 1 for CS-5340/6340 """
import math
import argparse


def main():
    """ program entry point. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('train_path', type=str, help='Training file path')
    arg_parser.add_argument('-test', type=str, help='Test file path')
    arg_parser.add_argument('-gen', type=str, help='Sentence generation seeds')
    args = arg_parser.parse_args()

    if args.test and args.gen:
        print('Either use -test or -gen, not both')
        return -1

    tokens, token_count, sentence_count = read_training_file(args.train_path)
    unigram_freq = get_unigram_freq(tokens)
    unigram_freq['phi'] = sentence_count
    bigram_freq = get_bigram_freq(tokens)

    if args.test:
        sentences = read_test_file(args.test)
        test_results = test_sentences(sentences, unigram_freq, bigram_freq, token_count)
        print_test_results(test_results)
        return 1
    elif args.gen:
        seeds = read_test_file(args.gen)
        gen_results = generate_sentences(seeds, unigram_freq, bigram_freq)
        print_gen_results(gen_results)
        return 1

def generate_sentences(seeds, unigram_freq, bigram_freq):
    gen_sentences = []
    for seed in seeds:
        gen_word_count = 0
        gen_sentence = ""
        prev_word = seed.lower()
        while gen_word_count < 10:
            next_word = get_next_gen_word(prev_word, unigram_freq, bigram_freq)
            if next_word == "":
                break
            gen_sentence = gen_sentence + " " + next_word
            prev_word = next_word
            gen_word_count += 1
        gen_sentences.append({ 'seed' : seed, 'gen_sentence' : gen_sentence})
    return gen_sentences


def test_sentences(sentences, unigram_freq, bigram_freq, token_count):
    results = []
    for sentence in sentences:
        result = {}
        result['sentence'] = sentence
        result['unigram'] = sentence_unigram_prob(sentence, unigram_freq, token_count)
        result['bigram'] = sentence_bigram_prob(sentence, bigram_freq, unigram_freq)
        result['smooth'] = sentence_bigram_prob_smoothing(sentence, bigram_freq, unigram_freq)
        results.append(result)
    return results


def get_next_gen_word(prev_word, unigram_freq, bigram_freq):
    next_word = ""
    next_word_prob = -math.inf
    for bigram, freq in bigram_freq.items():
        if bigram.split()[0] != prev_word:
            continue
        bigram_prob = math.log(bigram_freq[bigram] / unigram_freq[prev_word], 2)
        if bigram_prob > next_word_prob:
            next_word = bigram.split()[1]
            next_word_prob = bigram_prob
        elif bigram_prob == next_word_prob and  bigram.split()[1] > next_word:
            next_word = bigram.split()[1]
            next_word_prob = bigram_prob
    return next_word


def read_test_file(path):
    lines = []
    file = open(path, 'r')
    for line in file:
        lines.append(line.rstrip())
    return lines


def read_training_file(path):
    tokens = []
    token_count = 0
    sentence_count = 0
    file = open(path, 'r')   
    for line in file:
        sentence_count +=1
        prev_token = "phi"
        for token in line.split():
            entry = { 'token'      : token.lower(), 
                      'prev_token' : prev_token.lower(), }
            tokens.append(entry)
            prev_token = token
            token_count += 1
    return tokens, token_count, sentence_count
        

def get_unigram_freq(tokens):
    unigram_freq = {}
    for entry in tokens:
        key = entry['token']
        if key in unigram_freq:
            unigram_freq[key] += 1
        else:
            unigram_freq[key] = 1
    return unigram_freq


def get_bigram_freq(tokens):
    bigram_freq = {}
    for entry in tokens:
        key = entry['prev_token'] + " " + entry['token']
        if key in bigram_freq:
            bigram_freq[key] += 1
        else:
            bigram_freq[key] = 1
    return bigram_freq


def sentence_unigram_prob(sentence, unigram_freq, token_count):
    tokens = sentence.split()
    unigram_prob = 0
    for token in tokens:
        unigram_prob += math.log(unigram_freq[token.lower()] / token_count, 2)
    return round(unigram_prob, 4)


def sentence_bigram_prob(sentence, bigram_freq, unigram_freq):
    tokens = sentence.split()
    bigram_prob = 0
    previous_token = 'phi'
    for token in tokens:
       key = previous_token.lower() + " " + token.lower()
       if key in bigram_freq:
           bigram_prob += math.log(bigram_freq[key] / unigram_freq[previous_token], 2)
       else:
           return 0
       previous_token = token.lower()
    return round(bigram_prob, 4)


def sentence_bigram_prob_smoothing(sentence, bigram_freq, unigram_freq):
    vocab_size = len(unigram_freq) - 1
    tokens = sentence.split()
    bigram_prob = 0
    previous_token = 'phi'
    for token in tokens:
        key = previous_token.lower() + " " + token.lower()
        if key in bigram_freq:
           bigram_prob += math.log((bigram_freq[key] + 1) / (unigram_freq[previous_token] + vocab_size), 2)
        else:
           bigram_prob += math.log(1 / (unigram_freq[previous_token] + vocab_size), 2)
        previous_token = token.lower()
    return round(bigram_prob, 4) 


def print_test_results(results):
    for result in results:
        print('S =', result['sentence'])
        print('Unigrams: logprob(S) =', result['unigram'])
        if result['bigram'] == 0:
            print('Bigrams: logprob(S) = undefined')
        else:
            print('Bigrams: logprob(S) =', result['bigram'])
        print('Smoothed Bigrams: logprob(S) =', result['smooth'])
        print()


def print_gen_results(generated_sentences):
    for sentence in generated_sentences:
        print('Seed =', sentence['seed'], ':', 
                sentence['gen_sentence'])


if __name__ == "__main__":
    main()
    