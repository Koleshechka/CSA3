# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=import-error
# pylint: disable=too-many-branches, too-many-statements, too-many-instance-attributes
# pylint: disable=invalid-name

import sys
import logging
from enum import Enum
from constants.isa import Opcode


class SelTOS(Enum):
    ARG = 0
    ALU = 1
    MEM = 2


class SelSP(Enum):
    INC = 0
    DEC = 1


class SelIP(Enum):
    INC = 0
    ARG = 1


class SelOP(Enum):
    OPCODE = 0
    L_PASS = 1
    R_PASS = 2


class SelBR(Enum):
    TOS = 0
    BR = 1


class ControlUnit:
    def __init__(self, path, data_path, mem_size):
        self.mem: list[dict[str, [Opcode, int]]] = [0] * mem_size
        self.ip: int = 0
        self.tc: int = 0
        self.data_path: DataPath = data_path
        self.var_linker: dict = {}
        self.link_linker: dict = {}
        self.arg: int = 0
        self.parse_variable_and_links(path)
        self.parse_program_mem(path)
        self.ip = 0

    def parse_variable_and_links(self, path):
        self.var_linker.update({0: 0})
        self.var_linker.update({1: 1})
        self.var_linker.update({2: 2})

        line_counter = 0
        with open(path, "rb") as file:
            while True:
                command = file.read(1)

                if command:
                    if command == Opcode.VAR.value.to_bytes(1, 'big'):
                        var = file.read(4)
                        var = int.from_bytes(var, 'big')
                        self.var_linker[var] = self.data_path.reserve_var()

                    elif command == Opcode.LINK.value.to_bytes(1, 'big'):
                        link = file.read(4)
                        link = int.from_bytes(link, 'big')
                        self.link_linker[link] = line_counter
                    else:
                        line_counter += 1
                    if command == Opcode.PUSH.value.to_bytes(1, 'big'):
                        file.read(4)

                    if command == Opcode.POP.value.to_bytes(1, 'big'):
                        file.read(4)
                    if command == Opcode.JMP.value.to_bytes(1, 'big') \
                            or command == Opcode.BZ.value.to_bytes(1, 'big') \
                            or command == Opcode.BNZ.value.to_bytes(1, 'big') \
                            or command == Opcode.GET.value.to_bytes(1, 'big'):
                        file.read(4)

                else:
                    break

    def parse_program_mem(self, path):
        with open(path, "rb") as file:
            while True:
                arg = 0
                command = int.from_bytes(file.read(1), 'big')
                if command:
                    if command == Opcode.VAR.value:
                        file.read(4)
                        continue
                    if command == Opcode.PUSH.value:
                        arg = file.read(4)
                        arg = int.from_bytes(arg, 'big')
                    elif command == Opcode.POP.value:
                        arg = int.from_bytes(file.read(4), 'big')
                        arg = self.var_linker[arg]
                    elif command in [Opcode.ADD.value,
                                     Opcode.SUB.value,
                                     Opcode.MUL.value,
                                     Opcode.DIV.value,
                                     Opcode.MOD.value,
                                     Opcode.GR.value,
                                     Opcode.LESS.value,
                                     Opcode.EQ.value,
                                     Opcode.DROP.value,
                                     Opcode.DUP.value,
                                     Opcode.DUP_D.value,
                                     Opcode.EXIT.value]:
                        arg = 0
                    elif command == Opcode.LINK.value:
                        file.read(4)
                        continue
                    if command in [Opcode.JMP.value, Opcode.BZ.value, Opcode.BNZ.value]:
                        arg = file.read(4)
                        arg = self.link_linker[int.from_bytes(arg, 'big')]
                    elif command == Opcode.GET.value:
                        arg = file.read(4)
                        arg = self.var_linker.get(int.from_bytes(arg, 'big'))
                    self.create_command_from_bytes(self.parse_opcode_from_int(command), arg)
                else:
                    self.create_command_from_bytes(self.parse_opcode_from_int(command), arg)
                    break

    def parse_opcode_from_int(self, val):
        for opcode in Opcode:
            if opcode.value == val:
                return opcode
        return None

    def create_command_from_bytes(self, opcode, arg):  # читает одну команду и возвращает
        # конвертировать биты в команду
        command = {}
        command["opcode"] = opcode
        command["arg"] = arg
        self.mem[self.ip] = command
        self.ip += 1

    def tick(self) -> None:
        self.tc += 1

    def decode_and_execute_instruction(self) -> bool:
        command = self.mem[self.ip]
        opcode = command["opcode"]
        self.arg = command["arg"]
        self.data_path.arg = self.arg

        if opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD] or opcode in [Opcode.GR, Opcode.LESS,
                                                                                                Opcode.EQ]:
            self.data_path.sel_op(SelOP.OPCODE, opcode=opcode)
            self.data_path.latch_ds()
            self.tick()
            self.data_path.latch_sp(SelSP.DEC)
            self.tick()

        if opcode == Opcode.PUSH:
            self.data_path.latch_sp(SelSP.INC)
            self.tick()
            self.data_path.latch_tos(SelTOS.ARG)
            self.tick()

        if opcode == Opcode.POP:
            self.data_path.latch_dp()
            self.tick()
            self.data_path.latch_mem()
            self.tick()
            self.data_path.latch_sp(SelSP.DEC)
            self.tick()

        if opcode == Opcode.DUP:
            self.data_path.latch_sp(SelSP.INC)
            self.tick()
            self.data_path.sel_op(SelOP.L_PASS)
            self.data_path.latch_tos()
            self.tick()

        if opcode == Opcode.DUP_D:
            self.data_path.latch_br()
            self.tick()
            self.data_path.latch_sp(SelSP.INC)
            self.tick()
            self.data_path.sel_op(SelOP.R_PASS, sel_br=SelBR.BR)
            self.data_path.latch_tos()
            self.tick()
            self.data_path.latch_br()
            self.tick()
            self.data_path.latch_sp(SelSP.INC)
            self.tick()
            self.data_path.sel_op(SelOP.R_PASS, sel_br=SelBR.BR)
            self.data_path.latch_tos()
            self.tick()

        if opcode == Opcode.GET:
            self.data_path.latch_dp()
            self.tick()
            self.data_path.latch_sp(SelSP.INC)
            self.tick()
            self.data_path.latch_tos(SelTOS.MEM)
            self.tick()

        if opcode == Opcode.JMP:
            self.latch_ip()
            self.tick()
        elif opcode == Opcode.BZ:
            if self.data_path.zero():
                self.latch_ip()
            else:
                self.latch_ip(SelIP.INC)
            self.tick()
            self.data_path.latch_sp(SelSP.DEC)
        elif opcode == Opcode.BNZ:
            if not self.data_path.zero():
                self.latch_ip()
            else:
                self.latch_ip(SelIP.INC)
            self.tick()
            self.data_path.latch_sp(SelSP.DEC)
        else:
            self.latch_ip(SelIP.INC)

        if opcode == Opcode.EXIT:
            return False
        return True

    def latch_ip(self, sel_ip: SelIP = SelIP.ARG):
        assert sel_ip in [SelIP.INC, SelIP.ARG], "Invalid sel"
        if sel_ip == SelIP.INC:
            self.ip += 1
        elif sel_ip == SelIP.ARG:
            self.ip = self.arg

    def __repr__(self):
        state = f"TICK: {self.tc}, IP: {self.ip}, ADDR: {self.data_path.dp}, TOS: {self.data_path.stack[self.data_path.sp]}, DS: {self.data_path.stack[self.data_path.sp - 1]}"

        instr = self.mem[self.ip]
        opcode = instr["opcode"]

        action = f"{opcode.name} {instr['arg']}"

        return f"{action} {state}"


def parse_opcode_from_int(val):
    for opcode in Opcode:
        if opcode.value == val:
            return opcode
    return None


class DataPath:
    def __init__(self, data_memory_size, stack_size, input_buffer):
        assert data_memory_size > 0, "Negative data size"
        self.mem: list[int] = [0] * data_memory_size
        self.dp: int = 3
        self.br: int = 0
        self.stack: list[int] = [0] * stack_size
        self.sp: int = 0
        self.input_buffer: list[str] = input_buffer
        self.output_buffer: list = []
        self.arg: int = 0
        self.alu: int = 0
        self.alu_ops: dict = \
            {
                Opcode.DIV: lambda left, right: left / right,
                Opcode.MOD: lambda left, right: left % right,
                Opcode.ADD: lambda left, right: left + right,
                Opcode.SUB: lambda left, right: left - right,
                Opcode.MUL: lambda left, right: left * right,
                Opcode.GR: lambda left, right: (int)(left > right),
                Opcode.LESS: lambda left, right: (int)(left < right),
                Opcode.EQ: lambda left, right: (int)(left == right)
            }

    def reserve_var(self) -> int:
        self.dp += 1
        return self.dp

    def zero(self) -> bool:
        """Флаг"""
        return self.stack[self.sp] == 0

    def latch_dp(self) -> None:
        self.dp = self.arg

    def latch_br(self) -> None:
        assert self.sp > 0, "Out of stack"
        self.br = self.stack[self.sp - 1]  # DS

    def latch_tos(self, sel_tos: SelTOS = SelTOS.ALU) -> None:
        assert sel_tos in [SelTOS.ALU, SelTOS.ARG, SelTOS.MEM], "Invalid sel"
        if sel_tos == SelTOS.ALU:
            self.stack[self.sp] = self.alu
        if sel_tos == SelTOS.ARG:
            self.stack[self.sp] = self.arg
        if sel_tos == SelTOS.MEM:
            if self.dp == 2:
                if len(self.input_buffer) == 0:
                    raise EOFError
                self.stack[self.sp] = self.input_buffer.pop()  # MEMORY-MAPPED INPUT
            else:
                self.stack[self.sp] = self.mem[self.dp]

    def latch_ds(self) -> None:
        self.stack[self.sp - 1] = self.alu

    def latch_sp(self, sel_sp: SelSP = SelSP.INC) -> None:
        assert sel_sp in [SelSP.INC, SelSP.DEC], "Invalid sel"
        if sel_sp == SelSP.INC:
            self.sp += 1
        elif sel_sp == SelSP.DEC:
            self.sp -= 1

    def sel_op(self, sel_op: SelOP, opcode: Opcode = Opcode.ADD, sel_br: SelBR = SelBR.TOS) -> None:
        right = 0
        left = self.stack[self.sp - 1]
        if sel_br == SelBR.TOS:
            right = self.stack[self.sp]
        elif sel_br == SelBR.BR:
            right = self.br
        if sel_op == SelOP.R_PASS:
            self.alu = right
        elif sel_op == SelOP.L_PASS:
            self.alu = left
        elif sel_op == SelOP.OPCODE:
            self.alu = self.alu_ops[opcode](left, right)

    def latch_mem(self) -> None:
        if self.dp == 0:
            self.output_buffer.append(self.stack[self.sp])  # MEMORY-MAPPED OUTPUT
        elif self.dp == 1:
            self.output_buffer.append(chr(self.stack[self.sp]))  # MEMORY-MAPPED CHAR OUTPUT
        else:
            self.mem[self.dp] = self.stack[self.sp]


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
    return ''.join(list(map(str, data_path.output_buffer))), instr_counter, control_unit.tc


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
