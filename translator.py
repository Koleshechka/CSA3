import sys
import re
from isa import a_operations, operations, variable_op, Opcode


def validate(line, variables_dict, link_counter):
    words = list(line.split(' '))

    if len(words) > 2: raise AssertionError
    elif re.fullmatch(r'[-+]?\d+', words[0]) or re.fullmatch(r'\D{1}', words[0]):
        if len(words) > 1:
            raise AssertionError
    elif words[0] == "variable":
        if len(words) != 2: raise AssertionError
        elif words[1] in variables_dict.keys(): raise AssertionError
        else:
            variables_dict.update({words[1]: link_counter})
            link_counter += 1
    elif words[0] not in operations and words[0] not in variables_dict.keys() and words[0] not in a_operations: raise AssertionError
    elif (words[0] in operations or words[0] in a_operations) and len(words) > 1: raise AssertionError

    elif words[0] in variables_dict.keys():
        if len(words) < 2 : raise AssertionError
        elif words[1] not in variable_op: raise AssertionError
    return link_counter



def parse(line, variable_dict, link_counter, link_dict, if_counter):
    words = list(line.split(' '))
    print(words[0])
    if re.fullmatch(r'[-+]?\d+', words[0]):
        parsed_line = Opcode.PUSH.value.to_bytes(1, 'big'), int(words[0]).to_bytes(4, 'big')
    elif words[0] == "=":
        print("eq!!!!!!!!")
        print(Opcode.EQ.value)
        print(Opcode.EQ.value.to_bytes(1, 'big'))
        parsed_line = Opcode.EQ.value.to_bytes(1, 'big'), False

    elif words[0] == "variable":
        var = int(variable_dict.get(words[1]))
        parsed_line = Opcode.VAR.value.to_bytes(1, 'big'), var.to_bytes(4, 'big')
    elif words[0] in variable_dict.keys():
        if words[1] == "!": parsed_line = Opcode.POP.value.to_bytes(1, 'big'), int(variable_dict.get(words[0])).to_bytes(4, 'big')
        else: parsed_line = Opcode.GET.value.to_bytes(1, 'big'), int(variable_dict.get(words[0])).to_bytes(4, 'big')
    elif words[0] == ".":
        parsed_line = Opcode.POP.value.to_bytes(1, 'big'), int(0).to_bytes(4, 'big')
    elif words[0] == ",":
        parsed_line = Opcode.POP.value.to_bytes(1, 'big'), int(1).to_bytes(4, 'big')
    elif words[0] == "+":
        parsed_line = Opcode.ADD.value.to_bytes(1, 'big'), False
    elif words[0] == "-":
        parsed_line = Opcode.SUB.value.to_bytes(1, 'big'), False
    elif words[0] == "*":
        parsed_line = Opcode.MUL.value.to_bytes(1, 'big'), False
    elif words[0] == "div":
        parsed_line = Opcode.DIV.value.to_bytes(1, 'big'), False
    elif words[0] == "mod":
        parsed_line = Opcode.MOD.value.to_bytes(1, 'big'), False
    elif words[0] == ">":
        parsed_line = Opcode.GR.value.to_bytes(1, 'big'), False
    elif words[0] == "<":
        parsed_line = Opcode.LESS.value.to_bytes(1, 'big'), False
    elif words[0] == "#":
        parsed_line = Opcode.GET.value.to_bytes(1, 'big'), int(2).to_bytes(4, 'big')
    elif re.fullmatch(r'\D{1}', words[0]):
        parsed_line = Opcode.PUSH.value.to_bytes(1, 'big'), ord(words[0]).to_bytes(4, 'big')

    elif words[0] == "dup":

        parsed_line = Opcode.DUP.value.to_bytes(1, 'big'), False
    elif words[0] == "dup_d":
        parsed_line = Opcode.DUP_D.value.to_bytes(1, 'big'), False
    elif words[0] == "drop":
        parsed_line = Opcode.DROP.value.to_bytes(1, 'big'), False
    elif words[0] == "begin":
        link_counter += 1
        link_dict.update({"begin": link_counter})

        parsed_line = Opcode.LINK.value.to_bytes(1, 'big'), int(link_counter).to_bytes(4, 'big')
    elif words[0] == "until":
        parsed_line = Opcode.BZ.value.to_bytes(1, 'big'), int(link_dict.get("begin")).to_bytes(4, 'big')
        link_dict.pop("begin")
    elif words[0] == "if":
        parsed_line = Opcode.BZ.value.to_bytes(1, 'big'), int(0).to_bytes(4, 'big')
        if_counter += 1
    elif words[0] == "endif":
        link_counter += 1
        link_dict.update({"endif": link_counter})
        if_counter -= 1

        parsed_line = Opcode.LINK.value.to_bytes(1, 'big'), int(link_counter).to_bytes(4, 'big')
    elif words[0] == "exit":
        parsed_line = Opcode.EXIT.value.to_bytes(1, 'big'), False

    return parsed_line, link_counter, if_counter


def translate(source):
    raw_code = list(source.split('\n'))
    code = []
    variables_dict = dict()
    link_counter = 3

    link_dict = dict()
    if_counter = 0
    if_line = -1
    line_counter = 0
    for line in raw_code:
        link_counter = validate(line, variables_dict, link_counter)
        parsed_line, link_counter, if_counter = parse(line, variables_dict, link_counter, link_dict, if_counter)
        if if_counter > 0 :
            if_line = line_counter
            if_counter = 0
        if if_counter == -1 and if_line > -1 :
            code[if_line] = Opcode.BZ.value.to_bytes(1, 'big'), (link_dict.get("endif")).to_bytes(4, 'big')
            link_dict.pop("endif")
            line_counter = -1
            if_counter = 0
        code.append(parsed_line)
        line_counter += 1
    return code, line_counter



def main(args):

    assert len(args) == 2, \
        "Wrong arguments: translator.py <forth_file> <target_file>"

    source_file, target_file,  = args

    with open(source_file, "rt", encoding="utf-8") as file:
        source_file = file.read()

    code, line_counter = translate(source_file)



    print("source LoC:", line_counter, "code instr:", len(code))
    with open(target_file, "wb") as file:
        for instr in code:

            file.write(instr[0])
            if instr[1]:
                file.write(instr[1])


if __name__ == '__main__':

    main(sys.argv[1:])
