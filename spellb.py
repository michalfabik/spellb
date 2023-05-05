#!/usr/bin/env python3

import argparse
import random
import re
import readline  # enables line editing features for input()
import sys

COMMANDS = [{'name': 'cheat', 'help': '', 'hidden': True},
            {'name': 'help', 'help': 'Show this help', 'hidden': False},
            {'name': 'list', 'help': 'Show words found so far', 'hidden': False},
            {'name': 'score', 'help': 'Show current score', 'hidden': False},
            {'name': 'show', 'help': 'Show available letters (in case they\'ve scrolled out of view)', 'hidden': False},
            {'name': 'shuffle', 'help': 'Shuffle letters, for inspiration', 'hidden': False},
            {'name': 'quit', 'help': 'Quit game', 'hidden': False},
            {'name': 'target', 'help': 'Show highest score and letter count possible for given set of letters', 'hidden': False}]

MASTER_WORD_LIST = '/usr/share/dict/words'

GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDCLR = '\033[0m'


def print_help():
    print('''
    Use the letters shown to create valid English words.
    - Each word has to be at least four letters long.
    - Each word must contain the yellow letter at least once.
    - A word can contain multiple occurrences of the same letter.
    - No proper names allowed.
    - A four-letter word counts for one point. Longer words count for one point per letter.
    - Bonus points for using all letters in a single word.

    Commands to control the game start with a colon. Non-ambiguous prefixes are allowed.
    ''')
    for command in COMMANDS:
        if not command['hidden']:
            print(f"    :{command['name']} - {command['help']}")


class SpellB():
    def __init__(self, pool=None):
        self.found_words = []
        self.letter_pool = ''
        self.score = 0
        if not pool:
            self.generate_letter_pool()
        else:
            self.validate_letter_pool(pool)
        self.prepare_word_list()
        self.best_possible_score = 0
        for word in self.word_list:
            self.best_possible_score += self.evaluate_word(word)[0]
        print('Type words. Type ":help" for more info. Type ":quit" to quit.')
        self.display_letter_pool()

    def execute_command(self, user_command):
        candidate_commands = []
        for command in COMMANDS:
            if not command['hidden']:
                if command['name'].startswith(user_command):
                    candidate_commands.append(command['name'])
            else:
                if command['name'] == user_command:
                    candidate_commands = [user_command]
                    break
        if not candidate_commands:
            print('Invalid command')
            return
        if len(candidate_commands) > 1:
            print(f'Ambiguous command: {", ".join(candidate_commands)}')
            return

        match candidate_commands[0]:
            case 'cheat':
                print(' '.join(self.word_list))
            case 'help':
                print_help()
            case 'list':
                print(f'{" ".join(sorted(self.found_words))}\n{len(self.found_words)} words')
            case 'score':
                print(self.score)
            case 'show':
                self.display_letter_pool()
            case 'shuffle':
                shuffled = ''.join(random.sample(self.letter_pool[1:], k=len(self.letter_pool[1:])))
                self.letter_pool = f'{self.letter_pool[0]}{shuffled}'
                self.display_letter_pool()
            case 'quit':
                sys.exit(0)
            case 'target':
                print(f'{len(self.word_list)} words, {self.best_possible_score} points')

    def display_letter_pool(self):
        print(f'{GREEN}  {self.letter_pool[1].upper()}   {self.letter_pool[2].upper()}{ENDCLR}\n'
              f'{GREEN}{self.letter_pool[3].upper()}   {YELLOW}{self.letter_pool[0].upper()}   {GREEN}{self.letter_pool[4].upper()}{ENDCLR}\n'
              f'{GREEN}  {self.letter_pool[5].upper()}   {self.letter_pool[6].upper()}{ENDCLR}\n')

    def evaluate_word(self, word):
        value = 0
        message = ''
        if not re.match(r'^[a-z]+$', word):
            return 0, 'Invalid characters in word'
        if self.letter_pool[0] not in word:
            return 0, 'Center letter not used'
        if len(word) < 4:
            return 0, 'Too short'
        if word not in self.word_list:
            return 0, 'Invalid word'
        if word in self.found_words:
            return 0, 'Already found'
        if len(word) == 4:
            value = 1
        else:
            value = len(word)
        if len(word) >= 7 and all(letter in word for letter in self.letter_pool):
            message = f'{GREEN}Pangram!{ENDCLR}'
            value += 7
        return value, message

    def generate_letter_pool(self):
        candidates = []
        with open(MASTER_WORD_LIST, 'r', encoding='utf-8') as file:
            try:
                while word := file.readline().strip():
                    if len(word) < 7:
                        continue
                    if len(set(word)) != 7:
                        continue
                    if not re.search(r'[aeiouy]', word):
                        continue
                    if re.search(r'[^a-z]', word):
                        continue
                    candidates.append(set(word))
            except EOFError:
                pass
        rnd_candidate = list(candidates[random.randint(0, len(candidates)-1)])
        self.letter_pool = ''.join(random.sample(rnd_candidate, k=len(rnd_candidate)))

    def validate_letter_pool(self, pool):
        if not pool.isalpha() or not pool.isascii():
            print('Invalid characters in letter pool. '
                  'Only English letters are allowed of which at most one can be uppercase.')
            sys.exit(1)
        caps = re.findall(r'[A-Z]', pool)
        if len(caps) > 1:
            print('Invalid letter pool format. At most one letter can be uppercase.')
            sys.exit(1)

        pool = pool.lower()
        if caps:
            center = caps[0].lower()
        else:
            center = pool[0]

        pool = set(pool)
        if len(pool) != 7:
            print('A letter pool must contain exactly seven unique letters.')
            sys.exit(1)

        pool.remove(center)

        self.letter_pool = f'{center}{"".join(list(pool))}'

    def prepare_word_list(self):
        self.word_list = []
        with open(MASTER_WORD_LIST, 'r', encoding='utf-8') as file:
            try:
                while word := file.readline().strip():
                    if len(word) < 4 or self.letter_pool[0] not in word:
                        continue
                    if not re.match(f'^[{self.letter_pool}]+$', word):
                        continue
                    # ad-hoc rules to filter out obscure words
                    if not re.search(r'[aeiouy]', word):
                        continue
                    self.word_list.append(word)
            except EOFError:
                pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        prog=__file__[__file__.rfind('/')+1:],
        description='''
            Spelling Bee game.
            Create as many English words as possible using a limited set of letters provided.
            Type ":help" for more info and in-game commands.
        '''
    )

    arg_parser.add_argument('-p', '--pool',
                            help='''
                            Use this letter pool. A letter pool must be a string containing exactly seven unique English letters.
                            If the string contains a capital letter, that letter will be used as the Center (mandatory) letter.
                            If the string only contains lowercase letters, the first letter will be used as Center.
                            ''')
    args = arg_parser.parse_args()
    game = SpellB(pool=args.pool)
    try:
        while user_input := input().lower():
            if user_input.startswith(':'):
                game.execute_command(user_input[1:])
                continue
            points, reason = game.evaluate_word(user_input)
            if points:
                game.score += points
                points = f'{GREEN}{points}{ENDCLR}'
                game.found_words.append(user_input)
            print(f'+{points} {reason}')
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
