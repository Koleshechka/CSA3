# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=import-error
# pylint: disable=line-too-long
"""Интеграционные тесты транслятора и машины
"""

import unittest

import translator
from constants.isa import Opcode


class TestTranslator(unittest.TestCase):

    def test_translation(self):
        with open("examples/cat.forth", "rt", encoding="utf-8") as file:
            text = file.read()

        code, _, link_counter = translator.translate(text)
        print(code)
        self.assertEqual(([(Opcode.LINK.value.to_bytes(1, 'big'), int(1).to_bytes(4, 'big')),
                           (Opcode.GET.value.to_bytes(1, 'big'), int(2).to_bytes(4, 'big')),
                           (Opcode.DUP.value.to_bytes(1, 'big'), False),
                           (Opcode.POP.value.to_bytes(1, 'big'), int(0).to_bytes(4, 'big')),
                           (Opcode.PUSH.value.to_bytes(1, 'big'), int(0).to_bytes(4, 'big')),
                           (Opcode.EQ.value.to_bytes(1, 'big'), False),
                           (Opcode.BZ.value.to_bytes(1, 'big'), int(1).to_bytes(4, 'big'))]),
                         code)
        self.assertEqual(7, link_counter)
