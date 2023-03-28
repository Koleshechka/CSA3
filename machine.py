import sys
import logging
from enum import Enum
from isa import Opcode


class Sel_tos(Enum):
    ARG = 0,
    ALU = 1,
    MEM = 2


class Sel_sp(Enum):
    INC = 0,
    DEC = 1


class Sel_ip(Enum):
    INC = 0,
    ARG = 1


class Sel_op(Enum):
    OPCODE = 0,
    L_PASS = 1,
    R_PASS = 2


class Sel_br(Enum):
    TOS = 0,
    BR = 1


class ControlUnit:
    def __init__(self, path, dataPath, mem_size):
        self.mem: list[dict[str, [Opcode, int]]] = [0] * mem_size
        self.IP: int = 0
        self.TC: int = 0
        self.dataPath: DataPath = dataPath
        self.var_linker: dict = dict()
        self.link_linker: dict = dict()
        self.arg: int = 0
        self.parse_variable_and_links(path)
        self.parse_program_mem(path)
        self.IP = 0

    def parse_variable_and_links(self, path):
        self.var_linker.update({0: 0})
        self.var_linker.update({1: 1})
        self.var_linker.update({2: 2})

        line_counter = 0
        with open(path, "rb") as f:
            while True:
                command = f.read(1)

                if command:
                    if command == Opcode.VAR.value.to_bytes(1, 'big'):
                        var = f.read(4)
                        var = int.from_bytes(var, 'big')
                        self.var_linker[var] = self.dataPath.reserve_var()

                    elif command == Opcode.LINK.value.to_bytes(1, 'big'):
                        link = f.read(4)
                        link = int.from_bytes(link, 'big')
                        self.link_linker[link] = line_counter


                    else:
                        line_counter += 1
                    if command == Opcode.PUSH.value.to_bytes(1, 'big'):
                        arg = f.read(4)

                    if command == Opcode.POP.value.to_bytes(1, 'big'):
                        arg = f.read(4)
                    if command == Opcode.JMP.value.to_bytes(1, 'big') \
                            or command == Opcode.BZ.value.to_bytes(1, 'big') \
                            or command == Opcode.BNZ.value.to_bytes(1, 'big') \
                            or command == Opcode.GET.value.to_bytes(1, 'big'):
                        arg = f.read(4)

                else:
                    break

    def parse_program_mem(self, path):
        with open(path, "rb") as f:
            while True:
                arg = 0
                command = int.from_bytes(f.read(1), 'big')
                if command:
                    if command == Opcode.VAR.value:
                        f.read(4)
                        continue
                    elif command == Opcode.PUSH.value:
                        arg = f.read(4)
                        arg = int.from_bytes(arg, 'big')
                    elif command == Opcode.POP.value:
                        arg = int.from_bytes(f.read(4), 'big')
                        arg = self.var_linker[arg]
                    elif command == Opcode.ADD.value \
                        or command == Opcode.SUB.value\
                        or command == Opcode.MUL.value \
                        or command == Opcode.DIV.value \
                        or command == Opcode.MOD.value \
                        or command == Opcode.GR.value \
                        or command == Opcode.LESS.value \
                        or command == Opcode.EQ.value \
                        or command == Opcode.DROP.value \
                        or command == Opcode.DUP.value \
                        or command == Opcode.DUP_D.value \
                        or command == Opcode.EXIT.value \
                            :
                                arg = 0
                    elif command == Opcode.LINK.value:
                        f.read(4)
                        continue
                    elif command == Opcode.JMP.value \
                            or command == Opcode.BZ.value \
                            or command == Opcode.BNZ.value :
                        arg = f.read(4)
                        arg = self.link_linker[int.from_bytes(arg, 'big')]
                    elif command == Opcode.GET.value:
                        arg = f.read(4)
                        arg = self.var_linker.get(int.from_bytes(arg, 'big'))
                    self.create_command_from_bytes(self.parse_opcode_from_int(command), arg)
                else:
                    self.create_command_from_bytes(self.parse_opcode_from_int(command), arg)
                    break


    def parse_opcode_from_int(self, val):
        for opcode in Opcode:
            if opcode.value == val:
                return opcode

    def create_command_from_bytes(self, opcode, arg):  # читает одну команду и возвращает
        # конвертировать биты в команду
        command = {}
        command["opcode"] = opcode
        command["arg"] = arg
        self.mem[self.IP] = command
        self.IP += 1


        """
        {
            "opcode" : Opcode.JMP,
            "arg" : 5,
        }
        """

    def tick(self) -> None:
        self.TC += 1

    def decode_and_execute_instruction(self) -> bool:
        command = self.mem[self.IP]
        opcode = command["opcode"]
        self.arg = command["arg"]
        self.dataPath.arg = self.arg

        if opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD] or opcode in [Opcode.GR, Opcode.LESS, Opcode.EQ]:
            self.dataPath.sel_op(Sel_op.OPCODE, opcode=opcode)
            self.dataPath.latch_DS()
            self.tick()
            self.dataPath.latch_SP(Sel_sp.DEC)
            self.tick()

        if opcode == Opcode.PUSH:
            self.dataPath.latch_SP(Sel_sp.INC)
            self.tick()
            self.dataPath.latch_TOS(Sel_tos.ARG)
            self.tick()

        if opcode == Opcode.POP:
            self.dataPath.latch_DP()
            self.tick()
            self.dataPath.latch_mem()
            self.tick()
            self.dataPath.latch_SP(Sel_sp.DEC)
            self.tick()

        if opcode == Opcode.DUP:
            self.dataPath.latch_SP(Sel_sp.INC)
            self.tick()
            self.dataPath.sel_op(Sel_op.L_PASS)
            self.dataPath.latch_TOS()
            self.tick()

        if opcode == Opcode.DUP_D:
            self.dataPath.latch_BR()
            self.tick()
            self.dataPath.latch_SP(Sel_sp.INC)
            self.tick()
            self.dataPath.sel_op(Sel_op.R_PASS, sel_br=Sel_br.BR)
            self.dataPath.latch_TOS()
            self.tick()
            self.dataPath.latch_BR()
            self.tick()
            self.dataPath.latch_SP(Sel_sp.INC)
            self.tick()
            self.dataPath.sel_op(Sel_op.R_PASS, sel_br=Sel_br.BR)
            self.dataPath.latch_TOS()
            self.tick()

        if opcode == Opcode.GET:
            self.dataPath.latch_DP()
            self.tick()
            self.dataPath.latch_SP(Sel_sp.INC)
            self.tick()
            self.dataPath.latch_TOS(Sel_tos.MEM)
            self.tick()

        if opcode == Opcode.JMP:
            self.latch_IP()
            self.tick()
        elif opcode == Opcode.BZ:
            if self.dataPath.zero():
                self.latch_IP()

            else:
                self.latch_IP(Sel_ip.INC)

            self.tick()
            self.dataPath.latch_SP(Sel_sp.DEC)
        elif opcode == Opcode.BNZ:
            if not self.dataPath.zero():
                self.latch_IP()

            else:
                self.latch_IP(Sel_ip.INC)

            self.tick()
            self.dataPath.latch_SP(Sel_sp.DEC)
        else:
            self.latch_IP(Sel_ip.INC)

        if opcode == Opcode.EXIT:
            return False
        return True


    def latch_IP(self, sel_ip: Sel_ip = Sel_ip.ARG):
        assert sel_ip in [Sel_ip.INC, Sel_ip.ARG], "Invalid sel"
        if sel_ip == Sel_ip.INC:
            self.IP += 1
        elif sel_ip == Sel_ip.ARG:
            self.IP = self.arg


    def __repr__(self):
        state = "TICK: {}, IP: {}, ADDR: {}, TOS: {}, DS: {}".format(
            self.TC,
            self.IP,
            self.dataPath.DP,
            self.dataPath.stack[self.dataPath.SP],
            self.dataPath.stack[self.dataPath.SP-1],
        )

        instr = self.mem[self.IP]
        opcode = instr["opcode"]

        action = "{} {}".format(opcode.name, instr["arg"])

        return "{} {}".format(action, state)


class DataPath:
    def __init__(self, data_memory_size, stack_size, input_buffer):
        assert data_memory_size > 0, "Negative data size"
        self.mem: list[int] = [0] * data_memory_size
        self.DP: int = 3
        self.BR: int = 0
        self.stack: list[int] = [0] * stack_size
        self.SP: int = 0
        self.input_buffer: list[str] = input_buffer
        self.output_buffer: list = []
        self.arg: int = 0
        self.alu: int = 0
        self.alu_ops: dict =\
        {
            Opcode.DIV: lambda left, right: left / right,
            Opcode.MOD: lambda left, right: left % right,
            Opcode.ADD: lambda left, right: left + right,
            Opcode.SUB: lambda left, right: right - left,
            Opcode.MUL: lambda left, right: left * right,
            Opcode.GR: lambda left, right: (int)(left > right),
            Opcode.LESS: lambda left, right: (int)(left < right),
            Opcode.EQ: lambda left, right: (int)(left == right)
        }

    def reserve_var(self) -> int:
        self.DP += 1
        return self.DP

    def zero(self) -> bool:
        """Флаг"""
        return self.stack[self.SP] == 0

    def latch_DP(self) -> None:
        self.DP = self.arg

    def latch_BR(self) -> None:
        assert self.SP > 0, "Out of stack"
        self.BR = self.stack[self.SP - 1]  # DS

    def latch_TOS(self, sel_tos: Sel_tos = Sel_tos.ALU) -> None:
        assert sel_tos in [Sel_tos.ALU, Sel_tos.ARG, Sel_tos.MEM], "Invalid sel"
        if sel_tos == Sel_tos.ALU:
            self.stack[self.SP] = self.alu
        if sel_tos == Sel_tos.ARG:
            self.stack[self.SP] = self.arg
        if sel_tos == Sel_tos.MEM:
            if self.DP == 2:
                if len(self.input_buffer) == 0:
                    raise EOFError
                self.stack[self.SP] = self.input_buffer.pop()  # MEMORY-MAPPED INPUT
            else:
                self.stack[self.SP] = self.mem[self.DP]

    def latch_DS(self) -> None:
        self.stack[self.SP - 1] = self.alu

    def latch_SP(self, sel_sp: Sel_sp = Sel_sp.INC) -> None:
        assert sel_sp in [Sel_sp.INC, Sel_sp.DEC], "Invalid sel"
        if sel_sp == Sel_sp.INC:
            self.SP += 1
        elif sel_sp == Sel_sp.DEC:
            self.SP -= 1

    def sel_op(self, sel_op: Sel_op, opcode: Opcode = Opcode.ADD, sel_br: Sel_br = Sel_br.TOS) -> None:
        right = 0
        left = self.stack[self.SP - 1]
        if sel_br == Sel_br.TOS:
            right = self.stack[self.SP]
        elif sel_br == Sel_br.BR:
            right = self.BR
        if sel_op == Sel_op.R_PASS:
            self.alu = right
        elif sel_op == Sel_op.L_PASS:
            self.alu = left
        elif sel_op == Sel_op.OPCODE:
            self.alu = self.alu_ops[opcode](left, right)

    def latch_mem(self) -> None:
        if self.DP == 0:
            self.output_buffer.append(self.stack[self.SP])  # MEMORY-MAPPED OUTPUT
        elif self.DP == 1:
            self.output_buffer.append(self.stack[self.SP])  # MEMORY-MAPPED CHAR OUTPUT
        else:
            self.mem[self.DP] = self.stack[self.SP]


def simulation(code, input_tokens, data_memory_size, limit):
    """Запуск симуляции процессора.

    Длительность моделирования ограничена количеством выполненных инструкций.
    """
    data_path = DataPath(data_memory_size, data_memory_size, input_tokens)
    control_unit = ControlUnit(code, data_path, data_memory_size)
    instr_counter = 0

    try:
        logging.debug('%s', control_unit)
        while control_unit.decode_and_execute_instruction():
            assert limit > instr_counter, "Too long execution"
            instr_counter += 1
            logging.debug('%s', control_unit)
    except EOFError:
        logging.warning('Input buffer is empty!')
    logging.info('output_buffer: %s', repr(''.join(list(map(str, data_path.output_buffer)))))
    return ''.join(list(map(str, data_path.output_buffer))), instr_counter, control_unit.TC


def main(args):
    assert len(args) == 2, "Wrong arguments: machine.py <code_file> <input_file>"
    code_file, input_file = args

    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter, ticks = simulation(code_file,
                                              input_tokens=input_token,
                                              data_memory_size=256, limit=1500)

    print(''.join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
