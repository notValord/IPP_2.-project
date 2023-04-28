import re
import sys
from sys import stderr
import xml.etree.ElementTree as ET      # for reading xml
from operator import attrgetter         # for getting an attribute for sorting


# Class with one class method to create an instruction with corresponding opcode.
# Each instruction is matched to its type by what sources it needs to execute.
class MakeInstruct:
    @classmethod
    def create(cls, opcode: str, order: int):
        code = str.upper(opcode)
        if code == "DEFVAR":
            return Defvar(order, 1)
        elif code == "MOVE":
            return Move(order, 1)
        elif code == "CREATEFRAME":
            return CreateFrame(order, 2)
        elif code == "PUSHFRAME":
            return PushFrame(order, 2)
        elif code == "POPFRAME":
            return PopFrame(order, 2)
        elif code == "CALL":
            return Call(order, 3)
        elif code == "RETURN":
            return Return(order, 3)
        elif code == "PUSHS":
            return Pushs(order, 4)
        elif code == "POPS":
            return Pops(order, 4)
        elif code == "ADD" or code == "SUB" or code == "MUL" or code == "IDIV":
            return ArOperations(order, code, 1)
        elif code == "LT" or code == "GT" or code == "EQ":
            return Comparison(order, code, 1)
        elif code == "AND" or code == "OR":
            return LogOperations(order, code, 1)
        elif code == "NOT":
            return Not(order, 1)
        elif code == "INT2CHAR":
            return Int2Char(order, 1)
        elif code == "STRI2INT":
            return Stri2Int(order, 1)
        elif code == "READ":
            return Read(order, 5)
        elif code == "WRITE":
            return Write(order, 1)
        elif code == "CONCAT":
            return Concat(order, 1)
        elif code == "STRLEN":
            return Strlen(order, 1)
        elif code == "GETCHAR":
            return Getchar(order, 1)
        elif code == "SETCHAR":
            return Setchar(order, 1)
        elif code == "TYPE":
            return Type(order, 1)
        elif code == "LABEL":
            return Label(order, 0)
        elif code == "JUMP":
            return Jump(order, 3)
        elif code == "JUMPIFEQ" or code == "JUMPIFNEQ":
            return JumpCond(order, code[6:], 6)
        elif code == "EXIT":
            return Exit(order, 1)
        elif code == "DPRINT":
            return Dprint(order, 1)
        elif code == "BREAK":
            return Break(order, 1)
        else:
            throw_error("Unknown instruction\n", 32)


# Class representing the whole program from the source file, contains a list of instructions.
class Program:
    def __init__(self):
        self.instr_list = list()

    # Add a new instruction with arguments in the correct order.
    # Checks whether the instruction has the correct number of arguments, without aby duplicates with correct indexes.
    def add_instruct(self, instr: 'Instruction'):
        instr.args.sort(key=attrgetter("index"))
        instr.check_args(instr.max_args)
        tmp = list()
        for arg in instr.args:
            if arg.index in tmp:
                throw_error("Arguments with the same index\n", 32)
            else:
                tmp.append(arg.index)
        self.instr_list.append(instr)

    # Sorts the instructions by their order
    def sort_instruct(self):
        self.instr_list.sort(key=attrgetter("order"))

    # Runs through all the instructions and all labels are added to the lable dictionary.
    # At the same time checks, whether there are no instructions with the same order.
    def load_labels(self, label_dict: 'LabelDict'):
        tmp = list()
        for instruct in self.instr_list:
            index: int = self.instr_list.index(instruct)
            if instruct.order in tmp:
                throw_error("Instructions with the same order\n", 32, instruct)
            else:
                tmp.append(instruct.order)

            if instruct.opcode == "LABEL":
                instruct.create_label(label_dict, index)

    # Opens the input file and executes the instructions by the instruction counter.
    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', label_dict: 'LabelDict', i_file: str):
        file = ""
        if i_file != sys.stdin:
            try:
                file = open(i_file, "r")
            except FileNotFoundError:
                throw_error("Couldn't open the input file\n", 11)
        else:
            file = i_file
        data_stack = list()

        while label_dict.get_counter() < len(self.instr_list):
            ex_type: int = self.instr_list[label_dict.get_counter()].get_ex_type()
            if ex_type == 0:
                self.instr_list[label_dict.get_counter()].execute()
            elif ex_type == 1:
                self.instr_list[label_dict.get_counter()].execute(glob_frame, frame_stack)
            elif ex_type == 2:
                self.instr_list[label_dict.get_counter()].execute(frame_stack)
            elif ex_type == 3:
                self.instr_list[label_dict.get_counter()].execute(label_dict)
            elif ex_type == 4:
                self.instr_list[label_dict.get_counter()].execute(glob_frame, frame_stack, data_stack)
            elif ex_type == 5:
                self.instr_list[label_dict.get_counter()].execute(glob_frame, frame_stack, file)
            else:
                self.instr_list[label_dict.get_counter()].execute(glob_frame, frame_stack, label_dict)
            label_dict.inc_counter()

        if file != i_file:
            file.close()

    # Debug function to print all of the instructions with its arguments.
    def print(self):
        for instr in self.instr_list:
            print("opcode: " + instr.opcode, end=" order: ")
            print(instr.order, end=" arg_nmb: ")
            print(instr.arg_nmb, end="\n\t")
            for arg in instr.args:
                print("type: " + arg.type, end=" value: ")
                print(arg.value)


# Basic class for the instruction, contains its opcode, order, execution type, list of arguments
# and number of arguments. From this class are inherited  classes for each type of the instruction.
class Instruction:
    def __init__(self, opcode: str, order: int):
        if order <= 0:
            throw_error("Order out of range\n", 32)
        self.opcode = opcode
        self.order = order
        self.args = list()
        self.arg_nmb = 0
        self.ex_type = 0

    def add_arg(self, arg: 'Argument'):
        self.args.append(arg)
        self.arg_nmb += 1

    def get_ex_type(self):
        return self.ex_type

    def check_args(self, max_arg: int):
        if max_arg != self.arg_nmb:
            throw_error("Wrong number of arguments for instruction\n", 32, self)
        x: int = 1
        for arg in self.args:
            if arg.index != x:
                throw_error("Wrong index of argument for instruction\n", 32, self)
            x += 1


# Next are the classes for each type of instruction with its max(expected) number
# of arguments and a function for its execution.

# Creates an uninitialized variable within the given frame.
class Defvar(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("DEFVAR", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        frame = self.args[0].get_value()[0:2]
        if frame == "GF":
            glob_frame.input_var(self.args[0].get_value()[3:])
        elif frame == "LF":
            frame_stack.loc_frame.input_var(self.args[0].get_value()[3:])
        elif frame == "TF":
            frame_stack.temp_frame.input_var(self.args[0].get_value()[3:])


# Sets the given variable to given value.
class Move(Instruction):
    max_args = 2

    def __init__(self, order: int, ex_type: int):
        super().__init__("MOVE", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        value: str = ""
        typ: str = ""

        value = get_value(self.args[1], glob_frame, frame_stack)
        typ = get_type(self.args[1], glob_frame, frame_stack)

        set_value(self.args[0], glob_frame, frame_stack, value, typ)


# Creates a new temporary frame.
class CreateFrame(Instruction):
    max_args = 0

    def __init__(self, order: int, ex_type: int):
        super().__init__("CREATEFRAME", order)
        self.ex_type = ex_type

    def execute(self, frame_stack: 'FrameStack'):
        frame_stack.create_temp_frame()


# Pushes the temporary frame onto the frame stack. Local frame points at the top frame in the frame stack.
# Temporary frame is left uninitialized.
class PushFrame(Instruction):
    max_args = 0

    def __init__(self, order: int, ex_type: int):
        super().__init__("PUSHFRAME", order)
        self.ex_type = ex_type

    def execute(self, frame_stack: 'FrameStack'):
        frame_stack.add_frame()


# Pops the frame from the frame stack in the temporary frame. Local frame points at the top frame in the frame stack.
class PopFrame(Instruction):
    max_args = 0

    def __init__(self, order: int, ex_type: int):
        super().__init__("POPFRAME", order)
        self.ex_type = ex_type

    def execute(self, frame_stack: 'FrameStack'):
        frame_stack.remove_frame()


# Jumps to the given label with the possibility of returning. Index before jumping is stores in the call stack.
class Call(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("CALL", order)
        self.ex_type = ex_type

    def execute(self, label_dict: 'LabelDict'):
        label_dict.store_index()
        index: int = label_dict.get_label(self.args[0].get_value())
        label_dict.set_counter(index)


# Returns to the last call instruction.
class Return(Instruction):
    max_args = 0

    def __init__(self, order: int, ex_type: int):
        super().__init__("RETURN", order)
        self.ex_type = ex_type

    def execute(self, label_dict: 'LabelDict'):
        label_dict.pop_index()


# Pushes the value to the data stack.
class Pushs(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("PUSHS", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', data_stack: list):
        value: str = get_value(self.args[0], glob_frame, frame_stack)
        typ: str = get_type(self.args[0], glob_frame, frame_stack)

        data_stack.append((value, typ))


# Pops the value from data stack to given variable.
class Pops(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("POPS", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', data_stack: list):
        if len(data_stack) == 0:
            throw_error("Empty data stack\n", 56)

        value: str
        typ: str
        value, typ = data_stack.pop()
        set_value(self.args[0], glob_frame, frame_stack, value, typ)


# Executes the given arithmetic operation on the last two arguments storing the result in the first argument.
class ArOperations(Instruction):
    # ADD, SUB, MUL, IDIV
    max_args = 3

    def __init__(self, order: int, typ: str, ex_type: int):
        super().__init__("AR_OPERATION", order)
        self.type = typ
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if not check_type(self.args[1], self.args[2], glob_frame, frame_stack, "int"):
            throw_error("Wrong types of arguments\n", 53, self)

        val1: int = get_value(self.args[1], glob_frame, frame_stack)
        val2: int = get_value(self.args[2], glob_frame, frame_stack)
        result: int = 0

        if self.type == "ADD":
            result = val1 + val2
        elif self.type == "SUB":
            result = val1 - val2
        elif self.type == "MUL":
            result = val1 * val2
        elif self.type == "IDIV":
            try:
                result = val1 // val2
            except ZeroDivisionError:
                throw_error("Cannot divide by zero\n", 57, self)
        else:
            throw_error("Inner problem\n", 99, self)

        set_value(self.args[0], glob_frame, frame_stack, str(result), "int")


# Executes the given comparing operation on the last two arguments storing the result(bool value) in the first argument.
class Comparison(Instruction):
    # LT, GT, EQ
    max_args = 3

    def __init__(self, order: int, typ: str, ex_type: int):
        super().__init__("COMPARE", order)
        self.type = typ
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if not check_type(self.args[1], self.args[2], glob_frame, frame_stack) and \
             get_type(self.args[1], glob_frame, frame_stack) != "nil" and \
             get_type(self.args[2], glob_frame, frame_stack) != "nil":
            throw_error("Wrong types of arguments\n", 53, self)

        val1: str = get_value(self.args[1], glob_frame, frame_stack)
        val2: str = get_value(self.args[2], glob_frame, frame_stack)

        if self.type == "EQ":
            if val1 == val2:
                set_value(self.args[0], glob_frame, frame_stack, "true", "bool")
            else:
                set_value(self.args[0], glob_frame, frame_stack, "false", "bool")
        else:
            if get_type(self.args[1], glob_frame, frame_stack) == "nil" or \
                    get_type(self.args[2], glob_frame, frame_stack) == "nil":
                throw_error("Wrong types of arguments\n", 53, self)

            elif self.type == "LT":
                if val1 < val2:
                    set_value(self.args[0], glob_frame, frame_stack, "true", "bool")
                else:
                    set_value(self.args[0], glob_frame, frame_stack, "false", "bool")

            elif self.type == "GT":
                    if val1 > val2:
                        set_value(self.args[0], glob_frame, frame_stack, "true", "bool")
                    else:
                        set_value(self.args[0], glob_frame, frame_stack, "false", "bool")


# Executes the given logical operation on the last two arguments storing the result in the first argument.
class LogOperations(Instruction):
    # AND, OR
    max_args = 3

    def __init__(self, order: int, typ: str, ex_type: int):
        super().__init__("LOG_OPETARION", order)
        self.type = typ
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if not check_type(self.args[1], self.args[2], glob_frame, frame_stack, "bool"):
            throw_error("Wrong types of arguments\n", 53, self)

        first: bool = False
        second: bool = False
        result: bool = False
        if get_value(self.args[1], glob_frame, frame_stack) == "true":
            first = True
        elif get_value(self.args[1], glob_frame, frame_stack) == "false":
            first = False

        if get_value(self.args[2], glob_frame, frame_stack) == "true":
            second = True
        elif get_value(self.args[2], glob_frame, frame_stack) == "false":
            second = False

        if self.type == "AND":
            result = first and second
        elif self.type == "OR":
            result = first or second

        set_value(self.args[0], glob_frame, frame_stack, str(result).lower(), "bool")


# Executes the logical operation not on the given value storing the result in the first argument.
class Not(Instruction):
    max_args = 2

    def __init__(self, order: int, ex_type: int):
        super().__init__("NOT", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if get_type(self.args[1], glob_frame, frame_stack) != "bool":
            throw_error("Wrong type of arguments\n", 53, self)

        result: bool = False
        if get_value(self.args[1], glob_frame, frame_stack) == "true":
            result = True
        elif get_value(self.args[1], glob_frame, frame_stack) == "false":
            result = False

        result = not result
        set_value(self.args[0], glob_frame, frame_stack, str(result).lower(), "bool")


# Changes the integer value to a character by its ASCII value storing the result.
class Int2Char(Instruction):
    max_args = 2

    def __init__(self, order: int, ex_type: int):
        super().__init__("INT2CHAR", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if get_type(self.args[1], glob_frame, frame_stack) != "int":
            throw_error("Wrong types of arguments\n", 53, self)

        value: int = get_value(self.args[1], glob_frame, frame_stack)
        result: str = ""

        try:
            result = chr(value)
        except ValueError:
            throw_error("Value out of range while converting int to char\n", 58)
        set_value(self.args[0], glob_frame, frame_stack, str(result), "string")


# Changes the character on the given index in a string to an integer by its ASCII value storing the result.
class Stri2Int(Instruction):
    max_args = 3

    def __init__(self, order: int, ex_type: int):
        super().__init__("STRI2INT", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if get_type(self.args[1], glob_frame, frame_stack) != "string" or \
                get_type(self.args[2], glob_frame, frame_stack) != "int":
            throw_error("Wrong types of arguments\n", 53, self)

        index: int = get_value(self.args[2], glob_frame, frame_stack)
        if len(get_value(self.args[1], glob_frame, frame_stack)) <= index or index < 0:
            throw_error("Indexing out of range\n", 58, self)

        char: str = get_value(self.args[1], glob_frame, frame_stack)[index]
        result: int = ord(char)
        set_value(self.args[0], glob_frame, frame_stack, str(result), "int")


# Reads data of given type form the input on one line. If there are no such data, value is set to nil.
class Read(Instruction):
    max_args = 2

    def __init__(self, order: int, ex_type: int):
        super().__init__("READ", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', input_file):
        line = input_file.readline()
        line = line.strip("\n")
        line = line.strip("\r")

        value: str = ""
        if line == "":
            set_value(self.args[0], glob_frame, frame_stack, "nil", "nil")
            return

        val1: str = self.args[1].get_value()
        if val1 == "int":
            tmp = re.search('^(([+-]?\d+)|(0[xX][0-9a-fA-F]+)|(0[oO][0-7]+))$', line)
            if tmp is None:
                set_value(self.args[0], glob_frame, frame_stack, "nil", "nil")
                return
            value = tmp.group(0)
        elif val1 == "string":
            if re.search('^((\\\[0-9]{3})|[^#\\\])*$', line) is None:
                set_value(self.args[0], glob_frame, frame_stack, "nil", "nil")
                return
            line = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), line)
            value = line
        elif val1 == "bool":
            if line.upper() == "TRUE":
                value = "true"
            else:
                value = "false"
        else:
            throw_error("Inner error\n", 99)

        set_value(self.args[0], glob_frame, frame_stack, value, val1)
        return


# Prints the value fo variable to stdout, is the value is nil empty string is printed.
class Write(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("WRITE", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        output: str = ""
        if get_type(self.args[0], glob_frame, frame_stack) != "nil":
            output = get_value(self.args[0], glob_frame, frame_stack)

        print(output, end="")


# Concatenates two strings storing the result in the first argument.
class Concat(Instruction):
    max_args = 3

    def __init__(self, order: int, ex_type: int):
        super().__init__("CONCAT", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if not check_type(self.args[1], self.args[2], glob_frame, frame_stack, "string"):
            throw_error("Wrong types of operands\n", 53, self)

        result: str = get_value(self.args[1], glob_frame, frame_stack) + get_value(self.args[2], glob_frame, frame_stack)
        set_value(self.args[0], glob_frame, frame_stack, result, "string")


# Gets the length on the string and store it in the first argument.
class Strlen(Instruction):
    max_args = 2

    def __init__(self, order: int, ex_type: int):
        super().__init__("STRLEN", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if get_type(self.args[1], glob_frame, frame_stack) != "string":
            throw_error("Wrong types of operands\n", 53, self)

        length = str(len(get_value(self.args[1], glob_frame, frame_stack)))
        set_value(self.args[0], glob_frame, frame_stack, length, "int")


# Gets the character on the given index in the string, storing hte result in the first argument.
class Getchar(Instruction):
    max_args = 3

    def __init__(self, order: int, ex_type: int):
        super().__init__("GETCHAR", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if get_type(self.args[1], glob_frame, frame_stack) != "string" or \
                get_type(self.args[2], glob_frame, frame_stack) != "int":
            throw_error("Wrong types of arguments\n", 53, self)

        index: int = get_value(self.args[2], glob_frame,frame_stack)
        if len(get_value(self.args[1], glob_frame, frame_stack)) <= index or index < 0:
            throw_error("Indexing out of range\n", 58, self)

        char: str = get_value(self.args[1], glob_frame, frame_stack)[index]
        set_value(self.args[0], glob_frame, frame_stack, char, "string")


# Changes the character in the string on the given index to another one.
class Setchar(Instruction):
    max_args = 3

    def __init__(self, order: int, ex_type: int):
        super().__init__("SETCHAR", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        if get_type(self.args[0], glob_frame, frame_stack) != "string" or \
            get_type(self.args[1], glob_frame, frame_stack) != "int" or \
            get_type(self.args[2], glob_frame, frame_stack) != "string":
            throw_error("Wrong types of arguments\n", 53, self)

        string: str = get_value(self.args[0], glob_frame, frame_stack)
        index: int = get_value(self.args[1], glob_frame, frame_stack)
        replace: str = get_value(self.args[2], glob_frame, frame_stack)
        if len(string) <= index or index < 0 or len(replace) == 0:
            throw_error("Indexing out of range\n", 58, self)

        string = string[:index] + replace[0] + string[index+1:]
        set_value(self.args[0], glob_frame, frame_stack, string, "string")


# Gets and stores the type of the given variable.
class Type(Instruction):
    max_args = 2

    def __init__(self, order: int, ex_type: int):
        super().__init__("TYPE", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        typ: str = ""
        if self.args[1].get_type() != "var":
            typ: str = self.args[1].get_type()
        else:
            frame = self.args[1].get_value()[0:2]
            if frame == "GF":
                typ: str = glob_frame.get_type_undef(self.args[1].get_value()[3:])
            elif frame == "LF":
                typ: str = frame_stack.loc_frame.get_type_undef(self.args[1].get_value()[3:])
            elif frame == "TF":
                typ: str = frame_stack.temp_frame.get_type_undef(self.args[1].get_value()[3:])

        if typ == "undef":
            typ = ""
        set_value(self.args[0], glob_frame, frame_stack, typ, "string")


# Represents the label.
class Label(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("LABEL", order)
        self.ex_type = ex_type

    def create_label(self, label_dict: 'LabelDict', index: int):
        label_dict.add_label(self.args[0].get_value(), index + 1)

    def execute(self):
        return


# Jumps to the given label and continues the instructions from there.
class Jump(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("JUMP", order)
        self.ex_type = ex_type

    def execute(self, label_dict: 'LabelDict'):
        index: int = label_dict.get_label(self.args[0].get_value())
        label_dict.set_counter(index)


# Evaluates the condition and if it is satisfied, the jump is preformed.
class JumpCond(Instruction):
    max_args = 3

    def __init__(self, order: int, typ: str, ex_type: int):
        super().__init__("JUMP_COND", order)
        self.type = typ
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', label_dict: 'LabelDict'):
        if not check_type(self.args[1], self.args[2], glob_frame, frame_stack) and \
                get_type(self.args[1], glob_frame, frame_stack) != "nil" and \
                get_type(self.args[2], glob_frame, frame_stack) != "nil":
            throw_error("Wrong types of arguments\n", 53, self)

        val1: str = get_value(self.args[1], glob_frame, frame_stack)
        val2: str = get_value(self.args[2], glob_frame, frame_stack)
        index: int = label_dict.get_label(self.args[0].get_value())
        if self.type == "EQ":
            if val1 == val2:
                label_dict.set_counter(index)
        elif self.type == "NEQ":
            if val1 != val2:
                label_dict.set_counter(index)


# Exit the execution of the program with the given return value.
class Exit(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("EXIT", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        value: str = get_value(self.args[0], glob_frame, frame_stack)
        typ: str = get_type(self.args[0], glob_frame, frame_stack)
        if typ != "int":
            try:
                value: int = int(value)
            except ValueError:
                throw_error("Wrong types of arguments\n", 53, self)
        if value < 0 or value > 49:
            throw_error("Exit code out of range\n", 57, self)

        exit(value)


# Prints the value of the given variable to the stderr.
class Dprint(Instruction):
    max_args = 1

    def __init__(self, order: int, ex_type: int):
        super().__init__("DPRINT", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        value: str = get_value(self.args[0], glob_frame, frame_stack)
        stderr.write(value)


# Prints the actual instruction and the content all frames.
class Break(Instruction):
    max_args = 0

    def __init__(self, order: int, ex_type: int):
        super().__init__("BREAK", order)
        self.ex_type = ex_type

    def execute(self, glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
        stderr.write("Instruction number " + str(self.order) + " with opcode " + self.opcode + "\n")
        stderr.write("Global frame:\n")
        glob_frame.print_frame()
        stderr.write("Local frame:\n")
        frame_stack.loc_frame.print_frame()
        stderr.write("Temporary frame:\n")
        frame_stack.temp_frame.print_frame()


# Class representing an argument with its type, index and value.
class Argument:
    def __init__(self, typ: str, value: str, index: int):
        if index < 1 or index > 3:
            throw_error("Wrong xml format, argument index out of range\n", 32)
        self.type = typ
        self.index = index
        if typ == "string" and value is None:
            self.value = ""
        elif typ == "string":
            self.value = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), value)
        else:
            self.value = value

    def get_value(self):
        return self.value

    def get_type(self):
        return self.type

    def get_index(self):
        return self.index


# Class for the global frame, is inherited to the single frame class.
class GlobalFrame:
    def __init__(self):
        self.frame = dict()

    # Creates a new undefined value
    def input_var(self, var: str):
        if self.is_in_frame(var):
            throw_error("The variable already exist in the frame\n", 52)
        self.frame[var] = ["", "undef"]

    # Sets the variable to given value
    def set_value(self, var: str, value: str, typ: str):
        if not self.is_in_frame(var):
            throw_error("Variable does not exist\n", 54)
        if typ == "int":
            self.frame[var] = [int(value), typ]
        else:
            self.frame[var] = [value, typ]

    # Gets value of given variable
    def get_value(self, var: str):
        if not self.is_in_frame(var):
            throw_error("Variable does not exist\n", 54)
        if self.frame[var][1] == "undef":
            throw_error("Variable is not initialized\n", 56)
        return self.frame[var][0]

    # Gets type of given variable, if is the variable undefined, throws error
    def get_type(self, var: str):
        if not self.is_in_frame(var):
            throw_error("Variable does not exist\n", 54)
        if self.frame[var][1] == "undef":
            throw_error("Variable is not initialized\n", 56)
        return self.frame[var][1]

    # Gets type of given variable even if it is uninitialized(used by type instruction)
    def get_type_undef(self, var: str):
        if not self.is_in_frame(var):
            throw_error("Variable does not exist\n", 54)
        return self.frame[var][1]

    # Checks whether the variable is in the frame
    def is_in_frame(self, var: str):
        return var in self.frame.keys()

    def print_frame(self):
        for key in self.frame.keys():
            stderr.write(key + " has the value " + self.frame[key][0] + " ane type " + self.frame[key][1] + "\n")


# Class for a single frame(both local and temporary frame) with a flag, if it is initialized.
class SingleFrame(GlobalFrame):
    init = False

    def __init__(self):
        super().__init__()

    def is_init(self):
        return self.init is True

    def set_init(self):
        self.init = True

    def unset_init(self):
        self.init = False

    def input_var(self, var: str):
        if self.is_init():
            super().input_var(var)
        else:
            throw_error("Frame is not defined\n", 55)

    def set_value(self, var: str, value: str, typ: str):
        if self.is_init():
            super().set_value(var, value, typ)
        else:
            throw_error("Frame is not defined\n", 55)

    def get_value(self, var: str):
        if self.is_init():
            return super().get_value(var)
        else:
            throw_error("Frame is not defined\n", 55)

    def get_type(self, var: str):
        if self.is_init():
            return super().get_type(var)
        else:
            throw_error("Frame is not defined\n", 55)

    def get_type_undef(self, var: str):
        if self.is_init():
            return super().get_type_undef(var)
        else:
            throw_error("Frame is not defined\n", 55)


# Class for a frame stack with local and temporary frame.
class FrameStack:
    def __init__(self):
        self.stack = list()
        self.loc_frame = SingleFrame()
        self.temp_frame = SingleFrame()

    def create_temp_frame(self):
        self.temp_frame = SingleFrame()
        self.temp_frame.set_init()

    # Pushes a temporary frame to frame stack, local frame points to the top of the stack
    def add_frame(self):
        if not self.temp_frame.is_init():
            throw_error("Temporary frame not defined\n", 55)
        self.stack.append(self.temp_frame)
        self.temp_frame = SingleFrame()
        self.loc_frame = self.stack[-1]
        self.loc_frame.set_init()

    # Pops the frame from the stack to the temporary frame,  local frame points to the top of the stack
    def remove_frame(self):
        if not self.loc_frame.is_init():
            throw_error("Local frame is not defined\n", 55)
        self.temp_frame = self.loc_frame
        self.stack.pop()
        if len(self.stack) == 0:
            self.loc_frame = SingleFrame()
        else:
            self.loc_frame = self.stack[-1]


# Class for the label directory with the instruction counter and call stack.
class LabelDict:
    instruct_counter: int = 0

    def __init__(self):
        self.dict = dict()
        self.call_stack = list()

    def add_label(self, label: str, instr: int):
        if label in self.dict.keys():
            throw_error("The label already exists\n", 52)
        self.dict[label] = instr - 1

    def get_label(self, label: str):
        if label in self.dict:
            return self.dict[label]
        throw_error("Nonexistent label\n", 52)

    def store_index(self):
        self.call_stack.append(self.get_counter())

    def pop_index(self):
        if len(self.call_stack) == 0:
            throw_error("Empty call stack\n", 56)
        self.set_counter(self.call_stack[-1])
        self.call_stack.pop()

    def inc_counter(self):
        self.instruct_counter += 1

    def set_counter(self, nmbr: int):
        self.instruct_counter = nmbr

    def get_counter(self):
        return self.instruct_counter


# Return the type of the given argument.
def get_type(arg: 'Argument', glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
    if arg.get_type() != "var":
        return arg.get_type()

    frame = arg.get_value()[0:2]
    if frame == "GF":
        return glob_frame.get_type(arg.get_value()[3:])
    elif frame == "LF":
        return frame_stack.loc_frame.get_type(arg.get_value()[3:])
    elif frame == "TF":
        return frame_stack.temp_frame.get_type(arg.get_value()[3:])


# Return the value of the given argument.
def get_value(arg: 'Argument', glob_frame: 'GlobalFrame', frame_stack: 'FrameStack'):
    if arg.get_type() != "var":
        if arg.get_type() == "int":
            try:
                return int(arg.get_value())
            except ValueError:
                throw_error("Wrong type of argument\n", 32)
        else:
            return arg.get_value()

    frame = arg.get_value()[0:2]
    if frame == "GF":
        return glob_frame.get_value(arg.get_value()[3:])
    elif frame == "LF":
        return frame_stack.loc_frame.get_value(arg.get_value()[3:])
    elif frame == "TF":
        return frame_stack.temp_frame.get_value(arg.get_value()[3:])


# Sets the variable to a given value.
def set_value(arg: 'Argument', glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', value: str, typ: str):
    if arg.get_type() == "var":
        frame = arg.get_value()[0:2]
        if frame == "GF":
            glob_frame.set_value(arg.get_value()[3:], value, typ)
        elif frame == "LF":
            frame_stack.loc_frame.set_value(arg.get_value()[3:], value, typ)
        elif frame == "TF":
            frame_stack.temp_frame.set_value(arg.get_value()[3:], value, typ)
    else:
        throw_error("Wrong types of arguments\n", 53)


# Checks whether the arguments are the same value. If the parameter typ is given
# also checks if the arguments are the given type.
def check_type(arg1: 'Argument', arg2: 'Argument', glob_frame: 'GlobalFrame', frame_stack: 'FrameStack', typ: str = "undef"):
    typ1: str = get_type(arg1, glob_frame, frame_stack)
    typ2: str = get_type(arg2, glob_frame, frame_stack)

    if typ == "undef":
        return typ1 == typ2
    else:
        return (typ1 == typ2) and (typ2 == typ)


# Prints the error message to the stderr and exit the program with the given return value.
def throw_error(message: str, number: int, instr: 'Instruction' = None):
    if instr is not None:
        stderr.write("Instruction: " + instr.opcode + " " + str(instr.order) + "\n")
    stderr.write(message)
    exit(number)


# Parse the program arguments.
def parse_arguments():
    s_file = sys.stdin
    i_file = sys.stdin
    argc = len(sys.argv)

    if argc == 1 or argc > 3:
        throw_error("Wrong program arguments\n", 10)
    if "--help" in sys.argv:
        if argc != 2:
            throw_error("Wrong program arguments\n", 10)
        print("Usage: interpret.py [--input=\"filename\"] [--source=\"filename\"]")
        print("\t interpret.py [--help]")
        print("Program takes the source code (expected in an xml format) of IPPcode22 and executes it")
        print("\t --source  -  defines a file from which the source code will be taken,\n\t"
              " else the source code will be taken from the standard input.\n\t"
              "At least one of the  arguments (sourcefile, inputfile) must be given")
        print("\t --input  -  defines a file from which the input code (for READ instruction) will be taken,\n\t"
              " else the input code will be taken from the standard input.\n\t"
              "At least one of the  arguments (sourcefile, inputfile) must be given")
        print("\t --help  -  printing this help")
        exit(0)

    if sys.argv[1].startswith("--source="):
        if argc > 2:
            if sys.argv[1].startswith("--input="):
                throw_error("Wrong program arguments\n", 10)
            i_file = sys.argv[2].partition('=')[2]
        s_file = sys.argv[1].partition('=')[2]
        return i_file, s_file

    if sys.argv[1].startswith("--input="):
        if argc > 2:
            if sys.argv[1].startswith("--source="):
                throw_error("Wrong program arguments\n", 10)
            s_file = sys.argv[2].partition('=')[2]
        i_file = sys.argv[1].partition('=')[2]
        return i_file, s_file

    throw_error("Wrong program arguments\n", 10)


# Load the instructions from the source file, created program class is returned.
# Checks for the syntax error in the xml.
def get_instruction_tree(s_file):
    tree = ""
    try:
        tree = ET.parse(s_file)
    except FileNotFoundError:
        throw_error("Couldn't open the source file\n", 11)
    except ET.ParseError:
        throw_error("Wrong xml structure\n", 31)

    root = tree.getroot()

    if root.tag != "program":
        throw_error("Wrong xml format, missing the element program\n", 32)
    if root.attrib["language"] != "IPPcode22":
        throw_error("Wrong xml format, program attributes\n", 32)

    prog = Program()
    for element in root:
        if element.tag != "instruction":
            throw_error("Wrong xml format, missing element instruction\n", 32)

        arg_keys = list(element.attrib.keys())
        if ("opcode" not in arg_keys) or ("order" not in arg_keys) or len(arg_keys) != 2:
            throw_error("Wrong xml format, instruction attributes", 32)
        if not element.attrib["order"].isnumeric():
            throw_error("Order is not a number\n", 32)
        instruct = MakeInstruct.create(element.attrib["opcode"], int(element.attrib["order"]))
        for child in element:
            if child.tag[0:-1] != "arg" or "type" not in child.attrib.keys() or len(child.attrib.keys()) != 1:
                throw_error("Wrong xml format, attributes of attribute", 32)

            arg = Argument(child.attrib["type"], child.text, int(child.tag[-1]))
            instruct.add_arg(arg)

        prog.add_instruct(instruct)

    prog.sort_instruct()
    return prog


# Create global frame, frame stack, create and initialize label directory and execute the loaded program.
def execute_prog(prog, i_file):
    glob_frame = GlobalFrame()
    frame_stack = FrameStack()
    label_dict = LabelDict()
    prog.load_labels(label_dict)
    prog.execute(glob_frame, frame_stack, label_dict, i_file)


# Usage: interpret.py [--input=filename] [--source=filename]
#        interpret.py [--help]
if __name__ == '__main__':
    try:
        in_file, src_file = parse_arguments()
        program = get_instruction_tree(src_file)
        execute_prog(program, in_file)
    except Exception as e:
        print(e)
        throw_error("Inner error\n", 99)
    exit(0)
