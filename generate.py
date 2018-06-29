#!/usr/bin/python
# -*- coding: utf-8 -*-

# requirement: python 2 (for pattern.en)
import sys
import os
import random
import argparse
import ConfigParser
import spacy
from pattern.en import singularize, pluralize, lemma, conjugate

class generator:
    def __init__(self, config):
        self.config = config
        # print config
        #for k in config.sections():
        #    for _item in config.items(k):
        #        print(_item)

        # setting
        self.drop_all_func = config.getboolean("general", "drop_all_func")
        self.error_overall = config.getboolean("general", "error_overall")
        self.prep_list = config.get("preposition", "target_preposition").split('|')
        self.determiner_list = config.get("determiner", "target_determiner").split('|')
        self.func_tag_noun = config.get("noun-number", "target_noun").split('|')
        self.func_tag_verb = config.get("verb-form", "target_verb").split('|')
        self.func_tag_det = "DT"
        self.func_tag_prep = "IN"

        # spacy
        self.nlp = spacy.load("en_core_web_sm")

    def generate(self, src):
        # parse src
        parsed_sent = self.nlp(src.rstrip().decode('utf-8'))
        ug_src = []

        # Option 1: drop all morpho-syntactic features
        if self.drop_all_func:
            for tok in parsed_sent:
                #print(tok.text.lower())
                if tok.tag_ == self.func_tag_det and tok.text.lower() in self.determiner_list:
                    pass
                elif tok.tag_ == self.func_tag_prep and tok.text.lower() in self.prep_list:
                    pass
                elif tok.tag_ in self.func_tag_noun:
                    ug_src.append(singularize(tok.text))
                elif tok.tag_ in self.func_tag_verb:
                    ug_src.append(lemma(tok.text))
                else:
                    ug_src.append(tok.text)

        # Option 2: inject errors according to an overall probability
        elif self.error_overall:
            prob = 1. - self.config.getfloat("general", "error_rate_overall")

            for _i, tok in enumerate(parsed_sent):
                rand = random.random()
                # rare errors
                """
                if rand >= 0.95 and len(tok.text) > 3:
                    typo = tok.text[0] + "".join(random.sample(tok.text[1:-1], len(tok.text[1:-1]))) + tok.text[-1]
                    ug_src.append(typo)
                """

                if rand >= 0.98 and 0 < len(ug_src) and 1 < _i < len(parsed_sent)-1:
                    # swap
                    ug_pop = ug_src.pop()
                    ug_src.append(tok.text)
                    ug_src.append(ug_pop)
                if True:
                #else:
                    if rand >= prob and tok.tag_ == self.func_tag_det and tok.text.lower() in self.determiner_list:
                        rand2 = random.random()
                        if rand2 <= 0.25:
                            ug_src.append('a')
                        elif rand2 <= 0.50:
                            ug_src.append('an')
                        elif rand2 <= 0.75:
                            ug_src.append('the')
                        else:
                            pass

                    elif rand >= prob and tok.tag_ == self.func_tag_prep and tok.text.lower() in self.prep_list:
                        rand2 = random.random()
                        if rand2 <= 0.5:
                            ug_src.append(random.sample(self.prep_list, 1)[0])
                        else:
                            pass
                    elif rand >= prob and tok.tag_ in self.func_tag_noun:
                        rand2 = random.random()
                        if rand2 <= 0.5:
                            ug_src.append(singularize(tok.text))
                        else:
                            ug_src.append(pluralize(tok.text))

                    elif rand >= prob and tok.tag_ in self.func_tag_verb:
                        vb_tag = random.sample(self.func_tag_verb, 1)[0]
                        if vb_tag == "VB":
                            ug_src.append(lemma(tok.text))
                        elif vb_tag == "VBP":
                            ug_src.append(conjugate(tok.text, '1sg'))
                        elif vb_tag == "VBZ":
                            ug_src.append(conjugate(tok.text, '3sg'))
                        elif vb_tag == "VBG":
                            ug_src.append(conjugate(tok.text, 'part'))
                        elif vb_tag == "VBD":
                            ug_src.append(conjugate(tok.text, 'p'))
                        elif vb_tag == "VBN":
                            ug_src.append(conjugate(tok.text, 'ppart'))
                        else:
                            raise
                    else:
                        ug_src.append(tok.text)


        else:
            #TODO: individual error rates
            pass

        try:
            return (" ".join([t for t in ug_src if t is not None]).encode('utf-8'))
        except:
            print(src)
            print(ug_src)
            exit()

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, required=True,
                        help='input source text file')
    parser.add_argument('--drop_all_func', dest="drop_all_func", action='store_true',
                        help='drop all morpho-syntactic information')
    parser.add_argument('--error_rate_overall', type=float,
                        help='overall error injection rate (overwrite config.ini)')
    args = parser.parse_args()
    if args.error_rate_overall and args.drop_all_func:
        print("drop_all_func and error_rate_overall can't be used simultaneously.")
        exit(1)
    elif args.drop_all_func:
        config.set("general", "drop_all_func", 'True')
    elif args.error_rate_overall:
        config.set("general", "error_overall", 'True')
        config.set("general", "error_rate_overall", args.error_rate_overall)

    ug = generator(config)

    """# unit test
    src = "This is an example sentence in this file."
    for i in range(2000):
        src_ug = ug.generate(src)
        print("-----")
        print(src)
        print(src_ug)

    """
    # main
    for line in open(args.source, 'r'):
        src = line.rstrip()
        src_ug = ug.generate(src)
        print(src_ug)
