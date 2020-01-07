#!/usr/bin/env python

# We could try to decrypt the strings (figure out how is it printing the text
# adventure strings), thus getting the codes in a roundabout way...
# (THIS SEEMS TO BE THE EASIEST OPTION)
#
# Or we could try to solve the challenge itself: finding a r[7] value that works
# better with the verification procedure...
#
# Or we could try to skip the verification procedure somehow...
#
# Or we could understand and optimize the verification procedure...
#
# In any case we'll likely need to make a disassembler and IDA PRO-like viewer?

import struct
import sys
from vm_memory import Memory
from vm_stack import Stack
from vm_registers import Registers

##################################################

pc = 0
registers = Registers()
stack = Stack()
input_ = ''
inputs = [ 'doorway', 'north', 'north', 'bridge', 'continue', 'down', 'east', 'take empty lantern', 'west', 'west', 'passage', 'ladder', 'west', 'south', 'north', 'take can', 'use can', 'use lantern', 'west', 'ladder', 'darkness', 'continue', 'west', 'west', 'west', 'west', 'north', 'take red coin', 'north', 'west', 'take blue coin', 'up', 'take shiny coin', 'down', 'east', 'east', 'take concave coin', 'down', 'take corroded coin', 'up', 'west', 'use blue coin', 'use red coin', 'use shiny coin', 'use concave coin', 'use corroded coin', 'north', 'take teleporter' ]

##################################################

verbose = False

def log(color, *args, **kwargs):
    if verbose:
        #print(color, file=sys.stderr, end='')
        print(pc, *args, file=sys.stderr, **kwargs)
        #print('\033[0m', file=sys.stderr, end='')
        sys.stderr.flush()

def log1(*args, **kwargs): log('\033[93m', *args, **kwargs)
def log2(*args, **kwargs): log('\033[94m', *args, **kwargs)
def log3(*args, **kwargs): log('\033[95m', *args, **kwargs)
def log4(*args, **kwargs): log('\033[92m', *args, **kwargs)

##################################################

input_file = '../challenge.bin'

binary_data = []
blocksize = 2
with open(input_file, 'rb+') as f:
    while True:
        buf = f.read(blocksize)
        if not buf:
            break
        (value,) = struct.unpack_from("<H",buf)
        binary_data.append(value)

##################################################

def _(n):
    if n >= 2**15 + 8:
        raise ValueError
    elif n >= 2**15:
        register = n - 2**15
        return registers[register]
    else:
        return n

def reg_index(n):
    if 2**15 <= n < 2**15+8:
        return n - 2**15
    else:
        raise ValueError

memory = Memory(binary_data, _)

#vals = [(k,v) for k,v in memory.items()]
#for k,v in vals[1539-20:1539+20]:
#    print(k,v,sep=',')
#raise SystemExit

def raw(n):
    return memory.get_raw(n)

def set_to(where, value):
    try:
        registers[reg_index(raw(where))] = value
    except ValueError:
        memory[_(where)] = value


def get_input():
    global input_, inputs, registers
    if input_ == '':
        try:
            input_ = inputs[0] + '\n'
            inputs = inputs[1:]
        except IndexError:
            registers[7] = 1
            input_ = 'use teleporter\n'
    #while input_ == '':
    #    input_ = input() + '\n'

##################################################

def halt():
    log1('halt')
    raise SystemExit

def set_():
    log1(f'set {raw(pc+1)} {raw(pc+2)}')
    registers[reg_index(raw(pc+1))] = memory[pc+2]
    return pc+3

def push():
    log1(f'push {raw(pc+1)}')
    stack.append(memory[pc+1])
    return pc+2

def pop():
    log1(f'pop {raw(pc+1)}')
    set_to(pc+1, stack.pop())
    return pc+2

def eq():
    log1(f'eq {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    left = memory[pc+2]
    right = memory[pc+3]
    if left == right:
        value = 1
    else:
        value = 0
    set_to(pc+1, value)
    return pc+4

def gt():
    log1(f'gt {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    left = memory[pc+2]
    right = memory[pc+3]
    if left > right:
        value = 1
    else:
        value = 0
    set_to(pc+1, value)
    return pc+4

def jmp():
    log1(f'jmp {raw(pc+1)}')
    return memory[pc+1]

def jt():
    log1(f'jt {raw(pc+1)} {raw(pc+2)}')
    
    #############################
    if pc == 6027 or pc == 6035: # hax
        return memory[pc+2]
    #############################

    if memory[pc+1] != 0:
        return memory[pc+2]
    else:
        return pc+3

def jf():
    log1(f'jf {raw(pc+1)} {raw(pc+2)}')
    if memory[pc+1] == 0:
        return memory[pc+2]
    else:
        return pc+3

def add():
    log1(f'add {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    value = (memory[pc+2] + memory[pc+3]) % 2**15
    set_to(pc+1, value)
    return pc+4

def mult():
    log1(f'mult {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    value = (memory[pc+2] * memory[pc+3]) % 2**15
    set_to(pc+1, value)
    return pc+4

def mod():
    log1(f'mod {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    value = memory[pc+2] % memory[pc+3]
    set_to(pc+1, value)
    return pc+4

def and_():
    log1(f'and {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    value = memory[pc+2] & memory[pc+3]
    set_to(pc+1, value)
    return pc+4

def or_():
    log1(f'or {raw(pc+1)} {raw(pc+2)} {raw(pc+3)}')
    value = memory[pc+2] | memory[pc+3]
    set_to(pc+1, value)
    return pc+4

def not_():
    log1(f'not {raw(pc+1)} {raw(pc+2)}')
    value = memory[pc+2] ^ 0b111111111111111
    set_to(pc+1, value)
    return pc+3

def rmem():
    log1(f'rmem {raw(pc+1)} {raw(pc+2)}')
    value = memory[memory[pc+2]]
    set_to(pc+1, value)
    return pc+3

def wmem():
    log1(f'wmem {raw(pc+1)} {raw(pc+2)}')
    value = memory[pc+2]
    addr = memory[pc+1]
    memory[addr] = value
    return pc+3

def call():
    log1(f'call {raw(pc+1)}')
    stack.append(pc+2)
    return memory[pc+1]

def ret():
    log1(f'ret')
    return stack.pop()

def out():
    log1(f'out {raw(pc+1)}')
    print(chr(memory[pc+1]), end='')
    sys.stdout.flush()
    return pc+2

def in_():
    global input_
    log1(f'in {raw(pc+1)}')
    get_input()
    first = input_[0]
    input_ = input_[1:]
    set_to(pc+1, ord(first))
    return pc+2

def noop():
    log1('noop')
    return pc+1

ops = {
    0: halt,
    1: set_,
    2: push,
    3: pop,
    4: eq,
    5: gt,
    6: jmp,
    7: jt,
    8: jf,
    9: add,
    10: mult,
    11: mod,
    12: and_,
    13: or_,
    14: not_,
    15: rmem,
    16: wmem,
    17: call,
    18: ret,
    19: out,
    20: in_,
    21: noop
}

def step():
    global pc
    op = memory[pc]
    fn = ops[op]
    pc = fn()
    return pc

##################################################

def op_name(op):
    try:
        return ops[op].__name__
    except:
        return ''

if __name__ == "__main__":
    while True:
        step()
