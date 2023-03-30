# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring
# pylint: disable=import-error
# pylint: disable=line-too-long

import unittest

import translator


class TestValidator(unittest.TestCase):

    def test_names(self):
        translator.validate("+", {}, 2)
        translator.validate("drop", {"1": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("sveta", {"1": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("add", {"1": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("dup drop", {"1": "1"}, 2)

    def test_variables(self):
        translator.validate("variable sum", {}, 2)
        translator.validate("variable var", {}, 2)
        translator.validate("sum !", {"sum": "1"}, 2)
        translator.validate("sum @", {"sum": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("variable", {"1": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("variable sum sum", {"1": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("variable sum", {"sum": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("sum", {"sum": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("sum", {"sum": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("sum!", {"sum": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("sum@", {"sum": "1"}, 2)
        with self.assertRaises(AssertionError):
            translator.validate("sum +", {"sum": "1"}, 2)
