from enum import Enum

a_operations = {"+", "-", "*", "=", ">", "<", "mod", "div"}
operations = {"variable", "begin", "drop", "if", "else", "endif", "until", ".", "dup_d", "dup", "exit", ","}
variable_op = {"@", "!"}


"""
Opcode_dict = {
    #8й отвечает за адресная/неадресная
    "PUSH": "0000000 0", # + n  (n) (кладем число на стек)
    "POP": "0000000 1", # + адрес переменной (sum !, из стека убираем)
    "ADD": "0000010 0", # (+) (складываем числа на стеке, результат на стек, сами числа убили)


    "GR": "0000100 0", # (>) (сравниваем числа на стекеб результат на стек, сами числа убили)

    "MOD": "0000110 0", # (mod, результат на стек, сами числа убили)

    "EQ": "0001000 0", # (=) (сравниваем числа на стеке, результат на стек, сами числа убили)

    "DUP": "0001010 0", #дублируем верхний элем

    "GET": "0001110 1", # + адрес переменной (@)
    "JMP": "0010000 1", # + адрес метки
    #"PRINT": "0010010 0"
    "EXIT": "1111110 0",
    "DUP_D": "0010100 0", #дублируем 2 элемента стека
    "SUB": "0010101 0",
    "MUL": "0010110 0",
    "DIV": "0010111 0",
    "LESS": "0011000 0"
    "BZ": "0011010 1",
    "BNZ": "0011011 1",
    "VAR": "1011011 1",
    "LINK": "11011011 1"

#"ADD_INT": "000001 1 0", # + n (n +) (n в стек не кладем)
#"MORE_INT": "000010 1 0", # (n >)
#"MOD_INT":  "000011 1 0", # + n (n mod) (n в стек не кладем)
#"EQ_INT": "000100 1 0", # (n =)  (прроверки в if и until кастим сюда)
#"DROP": "0001100 0", #убиваем верхний элем
}
    #TODO а что с выводом
    
    """

class Opcode(Enum):
    EXIT = 0b00000000
    POP = 0b00000001
    ADD = 0b00000100
    #ADD_INT = "00000110"
    GR = 0b00001000
    #MORE_INT = "00001000"
    MOD = 0b00001100
    #MOD_INT = "00001110"
    EQ = 0b00010000
    #EQ_INT = "00010010"
    DUP = 0b00010100
    DROP = 0b00011000
    GET = 0b00011101
    #PRINT = "00100100"
    JMP = 0b00100001
    DUP_D = 0b00101000
    PUSH = 0b11111100
    SUB= 0b00101010
    MUL= 0b00101100
    DIV= 0b00101110
    LESS= 0b00110000
    BZ= 0b00110101
    BNZ= 0b00110111
    VAR= 0b10110111
    LINK= 0b11011011






