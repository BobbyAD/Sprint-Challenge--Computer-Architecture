"""CPU functionality."""

import sys
import re

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.registers = [0]*8 # SP = 7
        self.registers[7] = 0xFF # SP initialized to end of ram
        # I think these are wrong, I'll clean them up tomorrow :)
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0
        
        self.subroutines = {}

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        program = []
        try:
            with open(filename) as f:
                # Find functions
                # in_func = False
                # for line in f:
                #     l = line.replace("\n", "")
                #     l = l.split(";")
                #     l = l[0]
                #     if l.endswith(":"):
                #         print("Hey")
                #         print(l)
                #         in_func = True
                #     # Gets commands inside a command
                #     # Need to find out where to put them
                #     # Top of RAM? Put everything else below it?
                #     elif in_func == True:
                #         print("OY")
                #         print(l)
                #         if l.startswith("    "):
                #             print("yo")
                #         else:
                #             in_func = False
                for line in f:
                    #remove anything after #
                    # comment_split = line.split("#")
                    # These need to be swapped to # since it's python now, not C
                    comment_split = line.lstrip(' ')
                    comment_split = comment_split.replace("\n", "")
                    comment_split = comment_split.split(';')

                    commands = re.split('\W+', comment_split[0])

                    # print(comment_split[0])
                    #If I hit a command, I store its location. Not sure how I'd do this
                    if comment_split[0].endswith(":"):
                        self.subroutines[comment_split[0].strip(':')] = len(program)
                    elif commands[0] == "HLT":
                        program.append(0b00000001)
                    elif commands[0] == "LDI":
                        program.append(0b10000010)
                        program.append(int(commands[1].strip('R')))
                        if commands[2].isdigit():
                            program.append(int(commands[2]))
                        else:
                            program.append(commands[2])
                    elif commands[0] == "PRN":
                        program.append(0b01000111)
                        program.append(int(commands[1].strip('R')))
                    elif commands[0] == "MUL":
                        program.append(0b10100010)
                        program.append(int(commands[1].strip('R')))
                        program.append(int(commands[2].strip('R')))
                    elif commands[0] == "PUSH":
                        program.append(0b01000101)
                        program.append(int(commands[1].strip('R')))
                    elif commands[0] == "POP":
                        program.append(0b01000110)
                        program.append(int(commands[1].strip('R')))
                    elif commands[0] == "ADD":
                        program.append(0b10100000)
                        program.append(int(commands[1].strip('R')))
                        program.append(int(commands[2].strip('R')))
                    elif commands[0] == "CALL":
                        program.append(0b01010000)
                        program.append(int(commands[1].strip('R')))
                    elif commands[0] == "RET":
                        program.append(0b00010001)

                    
        except FileNotFoundError:
            print(f"{filename} not found")
            sys.exit(2)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, index, value):
        self.ram[index] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.pc = 0
        running = True
        while running:
            self.ir = self.ram[self.pc]
            operand_a = self.ram[self.pc+1]
            operand_b = self.ram[self.pc+2]
            if self.ir == 0b00000001:
                break
            elif self.ir == 0b10000010:
                if operand_b in self.subroutines:
                    self.registers[int(operand_a)] = self.subroutines[operand_b]
                else:
                    self.registers[int(operand_a)] = operand_b
                self.pc += 3
            elif self.ir == 0b01000111:
                print(self.registers[operand_a])
                self.pc += 2
            elif self.ir == 0b10100010:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            elif self.ir == 0b01000101:
                self.registers[7] -= 1
                self.ram[self.registers[7]] = self.registers[operand_a]
                self.pc += 2
            elif self.ir == 0b01000110:
                self.registers[operand_a] = self.ram[self.registers[7]]
                self.registers[7] += 1
                self.pc += 2
            elif self.ir == 0b10100000:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            elif self.ir == 0b01010000:
                self.registers[7] -= 1
                self.ram[self.registers[7]] = self.pc+2
                self.pc = self.registers[operand_a]
            elif self.ir == 0b00010001:
                self.pc = self.ram[self.registers[7]]
                self.registers[7] += 1
