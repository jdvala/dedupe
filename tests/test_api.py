import dedupe
import dedupe.api
import unittest
import itertools
import random
import numpy
import warnings
from collections import OrderedDict


def icfi(x):
    return list(itertools.chain.from_iterable(x))


DATA_SAMPLE = [({'age': '27', 'name': 'Kyle'},
                {'age': '50', 'name': 'Bob'}),
               ({'age': '27', 'name': 'Kyle'},
                {'age': '35', 'name': 'William'}),
               ({'age': '10', 'name': 'Sue'},
                {'age': '35', 'name': 'William'}),
               ({'age': '27', 'name': 'Kyle'},
                {'age': '20', 'name': 'Jimmy'}),
               ({'age': '75', 'name': 'Charlie'},
                {'age': '21', 'name': 'Jimbo'})]

data_dict = OrderedDict(((0, {'name': 'Bob', 'age': '51'}),
                         (1, {'name': 'Linda', 'age': '50'}),
                         (2, {'name': 'Gene', 'age': '12'}),
                         (3, {'name': 'Tina', 'age': '15'}),
                         (4, {'name': 'Bob B.', 'age': '51'}),
                         (5, {'name': 'bob belcher', 'age': '51'}),
                         (6, {'name': 'linda ', 'age': '50'})))

data_dict_2 = OrderedDict(((7, {'name': 'BOB', 'age': '51'}),
                           (8, {'name': 'LINDA', 'age': '50'}),
                           (9, {'name': 'GENE', 'age': '12'}),
                           (10, {'name': 'TINA', 'age': '15'}),
                           (11, {'name': 'BOB B.', 'age': '51'}),
                           (12, {'name': 'BOB BELCHER', 'age': '51'}),
                           (13, {'name': 'LINDA ', 'age': '50'})))


class ActiveMatch(unittest.TestCase):
    def setUp(self):
        self.field_definition = [{'field': 'name', 'type': 'String'},
                                 {'field': 'age', 'type': 'String'}]

    def test_initialize_fields(self):
        self.assertRaises(TypeError, dedupe.api.ActiveMatching)

        with self.assertRaises(ValueError):
            dedupe.api.ActiveMatching([],)

        with self.assertRaises(ValueError):
            dedupe.api.ActiveMatching([{'field': 'name', 'type': 'Custom', 'comparator': lambda x: 1}],)

        with self.assertRaises(ValueError):
            dedupe.api.ActiveMatching([{'field': 'name', 'type': 'Custom', 'comparator': lambda x: 1},
                                       {'field': 'age', 'type': 'Custom', 'comparator': lambda x: 1}],)

        dedupe.api.ActiveMatching([{'field': 'name', 'type': 'Custom', 'comparator': lambda x: 1},
                                   {'field': 'age', 'type': 'String'}],)

    def test_check_record(self):
        matcher = dedupe.api.ActiveMatching(self.field_definition)

        self.assertRaises(ValueError, matcher._checkRecordPair, ())
        self.assertRaises(ValueError, matcher._checkRecordPair, (1, 2))
        self.assertRaises(ValueError, matcher._checkRecordPair, (1, 2, 3))
        self.assertRaises(ValueError, matcher._checkRecordPair, ({}, {}))

        matcher._checkRecordPair(({'name': 'Frank', 'age': '72'},
                                  {'name': 'Bob', 'age': '27'}))

    def test_markPair(self):
        from collections import OrderedDict
        good_training_pairs = OrderedDict((('match', DATA_SAMPLE[3:5]),
                                           ('distinct', DATA_SAMPLE[0:3])))
        bad_training_pairs = {'non_dupes': DATA_SAMPLE[0:3],
                              'match': DATA_SAMPLE[3:5]}

        matcher = dedupe.api.ActiveMatching(self.field_definition)

        self.assertRaises(ValueError, matcher.mark_pairs, bad_training_pairs)

        matcher.mark_pairs(good_training_pairs)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            matcher.mark_pairs({'match': [], 'distinct': []})
            assert len(w) == 1
            assert str(
                w[-1].message) == "Didn't return any labeled record pairs"


class DedupeTest(unittest.TestCase):
    def setUp(self):
        random.seed(123)
        numpy.random.seed(456)

        field_definition = [{'field': 'name', 'type': 'String'},
                            {'field': 'age', 'type': 'String'}]

        self.deduper = dedupe.Dedupe(field_definition)

    def test_randomSample(self):

        random.seed(7)
        numpy.random.seed(7)
        self.deduper._sample(data_dict, 30, 1)

        correct_result = [({'age': '50', 'name': 'Linda'},
                           {'age': '51', 'name': 'bob belcher'}),
                          ({'age': '51', 'name': 'Bob'},
                           {'age': '51', 'name': 'Bob B.'}),
                          ({'age': '51', 'name': 'Bob'},
                           {'age': '51', 'name': 'bob belcher'}),
                          ({'age': '51', 'name': 'Bob B.'},
                           {'age': '51', 'name': 'bob belcher'}),
                          ({'age': '50', 'name': 'Linda'},
                           {'age': '50', 'name': 'linda '})]

        for pair in correct_result:
            assert pair in self.deduper.active_learner.candidates


if __name__ == "__main__":
    unittest.main()
