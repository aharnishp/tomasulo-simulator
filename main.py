import numpy as np

# Simlulation Parameters

# Instruction Queue
## Format [[indx, Operation, storeTo, input1, input2, queuedStatus],]
instQueue = [
    [0, "add", 2, 1, 0, 0],
    [1, "mul", 3, 2, 1, 0],
    [2, "sub", 5, 1, 0, 0],
]

# Architecture of core distribution
## Format: [[["list of ","operations supported"], #number of rows in Reservation Table]]
cores = [[["add", "adi", "sub", "subi", "and", "or_", "xor", "not"],3], [["mul", "div"],3], [["mul", "div"],3]]

# Register File
## Format [data,] starting from 0
regF = [2.72, 3.14, -0.27, 5.0]


# R.A.Table
## Format: [None, None, 3, None]
rat = [None]


# GLOBAL STATE VARIABLES



# Main Memory
mainMemory = []

def storeToReg(addr, value):
    # increase length of list if list is short
    if(len(regF) < addr):
        for _ in range(addr - len(regF)+1):
            regF.append(0)
    regF[addr] = value

def getReg(addr):
    # increase length of list if list is short
    if(len(regF) < addr):
        for _ in range(addr - len(regF) + 1):
            regF.append(0)
    return(regF[addr])

def lookUpRAT(addr):
    if(len(rat) < addr):
        for _ in range(addr - len(rat) + 1):
            rat.append(None)
    if(type(rat[addr])==None):
        return -1
    else:
        return rat[addr]


def dependencyFinder(instQue):
    # format: [[InstructionWritingToRegister, registerUsingInstruction, InputNumberOfReader]]
    raw = []
    
    # table of which instruction generates value for register
    ## Format: [[registerIndex, LastInstructionStoredIndex]]
    rut = []

    # listing all outputs that are inputs to next instructions
    for ins in instQue:
        rut.append([(ins[2]), ins[0]])


def issueInstructions():
    pc = 0  ## program counter for pointing to Instruction Queue

    # find an instruction that has no dependency and queue it and is not marked complete
    for ins in instQueue:
        if(ins[6] == 0):    ## check if it is not already sent to a table
            pass


    # # fetch instruction
    # ins = instQ[pc]



def main():
    # 
    instLft = instQueue.copy()

    # Start issuing
    issueInstructions()

if(__name__ == "__main__"):
    main()