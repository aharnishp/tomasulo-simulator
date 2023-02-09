import numpy as np


# Simlulation Parameters

# Instruction Queue
## Format [[indx, Operation, storeTo, input1, input2, queuedStatus],]
# instQueue = {
#     0:["add", 2, 1, 0, 0],
#     1:["mul", 3, 2, 1, 0],
#     2:["sub", 5, 1, 0, 0],
# }
instQueue = {
    0:["add", 2, 4, 1, 0],
    1:["div", 1, 2, 1, 0],
    2:["sub", 4, 1, 2, 0],
    3:["add", 1, 2, 3, 0],
}
# instQueue = {
#     0:["add", 2, 4, 1, 0],
#     1:["div", 1, 2, 1, 0],
#     2:["sub", 4, 1, 2, 0],
#     3:["add", 1, 2, 3, 0],
# }

# Architecture of core distribution
## Format: [[["list of ","operations supported"], #number of rows in Reservation Table]]
cores = [[["add", "adi", "sub", "subi", "and", "or", "xor", "not"],3], [["mul", "div"],3], [["mul", "div"],3]]

# Register File
## Format [data,] starting from 0
regF = [2.72, 3.14, -0.27, 5.0]


# R.A.Table
## Format: [None, None, 3, None]
rat = [None]


# GLOBAL STATE VARIABLES


# Telemetry Settings
dependencyTelemetry = 1



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
    # Table of which instruction generates value for register
    ## Format: registerIndex: LastInstructionStoredIndex
    rut = {}
    
    # List of all RAW dependencies in the instruction queue
    ## Format: [[RegisterNumber, InstructionWritingToRegister, registerUsingInstruction, InputNumberOfReader]]
    raw = []

    # List of register values that were assigned just as an intermediate value
    # Stale value?
    ## Format: 
    intermediaries = []

    # List of all WAW dependencies in the instruction queue
    ## Format = [[RegisterNumber, 1st inst. writing, 2nd inst. writing]]
    waw = []

    # listing all outputs that are inputs to next instructions
    for indx in instQue:
        # check if this instruction has dependency on previous
        in1 = instQue[indx][2]
        in2 = instQue[indx][3]
        # input 1 of current inst depends on previous
        if(in1 in rut.keys()):
            raw.append([in1, rut[in1], indx, 0])
        if(in2 in rut.keys()):
            raw.append([in2, rut[in2], indx, 1])
            
        # checking before assigning to test WAW
        # if(rut[(instQue[indx][1])] == indx):
        #     pass
        # assigning register with value of instruction index
        rut[(instQue[indx][1])] = indx

    return [rut, raw, intermediaries]


def issueInstructions():
    pc = 0  ## program counter for pointing to Instruction Queue

    output = (dependencyFinder(instQue=instQueue))
    if(dependencyTelemetry): print("Register Assignment Last", output[0])
    if(dependencyTelemetry): 
        for rawd in output[1]:
            print("RAW Dependency:")
            print("  Register #" ,rawd[0])
            print("  depends on instr.", rawd[1])
            print("  required by inst.", rawd[2], "for input", rawd[3])


def main():
    # 
    instLft = instQueue.copy()

    # Start issuing
    issueInstructions()

if(__name__ == "__main__"):
    main()