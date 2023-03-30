# pylint: disable=missing-class-docstring, missing-module-docstring

from enum import Enum

a_operations = {"+", "-", "*", "=", ">", "<", "mod", "div"}
operations = {"variable", "begin", "drop", "if", "else",
              "endif", "until", ".", "dup_d", "dup", "exit", ","}
variable_op = {"@", "!"}


class Opcode(Enum):
    EXIT = 0b00000000
    ADD = 0b00000010
    SUB = 0b00000100
    MUL = 0b00000110
    DIV = 0b00001000
    MOD = 0b00001010
    GR = 0b00001100
    LESS = 0b00001110
    EQ = 0b00010000
    DROP = 0b00010010
    DUP = 0b00010100
    DUP_D = 0b00010110
    PUSH = 0b00011000
    POP = 0b00011011
    GET = 0b00011101
    JMP = 0b00011111
    BZ = 0b00100001
    BNZ = 0b00100011
    VAR = 0b00100101
    LINK = 0b00100111
