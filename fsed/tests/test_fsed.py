#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_fsed.py
(c) Will Roberts  12 December, 2015

Test the ``fsed`` module.
'''

from __future__ import absolute_import, print_function, unicode_literals
from .. import ahocorasick
from .. import fsed
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
import unittest

class CMStringIO(StringIO):
    '''StringIO object with context manager.'''

    def __init__(self, *args, **kwargs):
        '''Ctor.'''
        StringIO.__init__(self, *args, **kwargs)

    def __enter__(self):
        self.seek(0)
        return self

    def __exit__(self, _type, _value, _tb):
        pass

PATTERN_TSV = b'''\\bMarco Polo\tMarco_Polo
Kublai Khan\tKublai_Khan
Christopher Columbus\tChristopher_Columbus
and uncle\tand_uncle'''

PATTERN_SED = b'''s/\\bMarco Polo/Marco_Polo/
s/Kublai Khan/Kublai_Khan/
s.Christopher Columbus.Christopher_Columbus.
s/and uncle/and_uncle/'''

INPUT_TEXT = '''and uncle
sand uncle
s and uncle
Kublai Khan
bKublai Khan
Marco Polo
bMarco Polo'''

# without --words
WITHOUT_WORDS_OUTPUT = '''and_uncle
sand_uncle
s and_uncle
Kublai_Khan
bKublai_Khan
Marco_Polo
bMarco Polo'''

# with --words
WITH_WORDS_OUTPUT = '''and_uncle
sand uncle
s and_uncle
Kublai_Khan
bKublai Khan
Marco_Polo
bMarco Polo'''

class TestFsed(unittest.TestCase):
    '''
    Unit tests for the `fsed` module.
    '''

    def test_detect_format(self):
        '''
        Checks the fsed.detect_pattern_format function.
        '''
        pattern_file = CMStringIO(PATTERN_TSV)
        self.assertEqual(fsed.detect_pattern_format(pattern_file, 'utf-8', False),
                         (True, True))
        pattern_file = CMStringIO(PATTERN_SED)
        self.assertEqual(fsed.detect_pattern_format(pattern_file, 'utf-8', False),
                         (False, True))

    def test_rewriting_tsv(self):
        '''
        Tests the fsed.rewrite_str_with_trie function.
        '''
        pattern_file = CMStringIO(PATTERN_TSV)
        trie, boundaries = fsed.build_trie(pattern_file, 'tsv', 'utf-8', False)
        self.assertTrue(boundaries)
        self.assertEqual(fsed.rewrite_str_with_trie(INPUT_TEXT, trie, boundaries),
                         WITHOUT_WORDS_OUTPUT)
        trie, boundaries = fsed.build_trie(pattern_file, 'tsv', 'utf-8', True)
        self.assertTrue(boundaries)
        self.assertEqual(fsed.rewrite_str_with_trie(INPUT_TEXT, trie, boundaries),
                         WITH_WORDS_OUTPUT)

    def test_rewriting_sed(self):
        '''
        Tests the fsed.rewrite_str_with_trie function.
        '''
        pattern_file = CMStringIO(PATTERN_SED)
        trie, boundaries = fsed.build_trie(pattern_file, 'sed', 'utf-8', False)
        self.assertTrue('C' in trie.root)
        self.assertTrue(boundaries)
        self.assertEqual(fsed.rewrite_str_with_trie(INPUT_TEXT, trie, boundaries),
                         WITHOUT_WORDS_OUTPUT)
        trie, boundaries = fsed.build_trie(pattern_file, 'sed', 'utf-8', True)
        self.assertTrue(boundaries)
        self.assertEqual(fsed.rewrite_str_with_trie(INPUT_TEXT, trie, boundaries),
                         WITH_WORDS_OUTPUT)

    def test_slow(self):
        '''
        Tests the fsed.rewrite_str_with_trie function with the ``slow``
        flag on.
        '''
        trie = ahocorasick.AhoCorasickTrie()
        trie['a'] = '(a)'
        trie['ab'] = '(ab)'
        trie['bab'] = '(bab)'
        trie['bc'] = '(bc)'
        trie['bca'] = '(bca)'
        trie['c'] = '(c)'
        trie['caa'] = '(caa)'
        self.assertEqual(fsed.rewrite_str_with_trie('abccab', trie, slow=False),
                         '(a)(bc)(c)(a)b')
        self.assertEqual(fsed.rewrite_str_with_trie('abccab', trie, slow=True),
                         '(a)(bc)(c)(ab)')

if __name__ == '__main__':
    unittest.main()
