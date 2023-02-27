# This is a python script to simulate execution of instructions in CPU using Tomasulo's Algorithm
# 
# Usage: Modify the "instQueue" variable for executing custom instructions, the format is provided
#
# WIP: To advance press enter to skip to next clock cycle.
# 
# 


# Notes: Broadcast and Write Back are used as different terms here:
#    -> Broadcast refers to the results availibility to other instructions
#               Hence simulating forwarding inside a CPU
#
#    -> WriteBack refers to the part when result is stored in the memory.
#          
#    -> In this simulator Write Back occurs after 1 cycle of Broadcasting.






import numpy as np

##### INPUT VARIABLES #####


# Instruction Queue
#            0        1         2        3      4          5
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


# Architecture of core distribution
## Format: [[["list of ","operations supported"], #number of rows in Reservation Table, [executionDuration]]]
cores = [
            [["add", "adi", "sub", "subi", "and", "or", "xor", "not"],3,[2,2,2,2,2,2,2,2]], ## coreID 0
            [["mul", "div"],3,[10,40]],     ## coreID = 1
            [["mul", "div"],3,[10,40]]      ## coreID = 2
        ]


## Dictionary of register file
regF = {
    0:2.72,
    1:3.14,
    2:-0.27,
    3:5.0,
}

##### PARAMETERS #####
writeback_delay = 1






### Telemetries  :    has 3 levels = {0, 1, 2}
issueTelemetry = 1
dispatchTelemetry = 1
broadcastTelemetry = 1

##### OPERATIONAL VARIABLES #####


## Creating reservation table
# Format = {
#   coreID: [        Vj = float         Qj = pointer stored as string
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle],
#   ],
#   coreID: [
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle],
#   ]
# }

# Qj examples
# Qj = r12 pointing to regF[12]
# Qj = c2i4 pointing to instruction stored in reservation table of Cth core and Ith instruction
# Qj = i7 pointing to output of instructionId == 7


# generate empty reservation tables
resst={}
coreCounter = 0
for core in cores:
    resst[coreCounter] = []
    coreCounter += 1



# queue to wait for the simulated execution to complete
# Format = {
#   clock1: [[insID, outputValue],[insID, outputValue]],
#   clock2: [[insID, outputValue]],
# }
broadcastQueue = {}
# similar use/format to above but occurs 1 clock late for each.
writeBackQueue = {}


# Format2 = [
#   [clock1,[[insID, outputValue],[insID, outputValue]]],
#   [clock2, [[insID, outputValue]]],
# ]
# broadcastQueue = []


##### INITIALIZATIONS #####
##### INITIALIZATIONS #####
##### INITIALIZATIONS #####

print("Empty reservation station:", resst)


print("adding dummy data to reservation table")
resst[0].append([2, 1, "add", 56, 34, None, None, None])


##### FUNCTIONS #####
##### FUNCTIONS #####
##### FUNCTIONS #####


def exec(opc, Val1, Val2):
    if(opc == "add"):
        return Val1 + Val2
    elif(opc == "adi"):
        return Val1 + Val2
    elif(opc == "sub"):
        return Val1 - Val2
    elif(opc == "subi"):
        return Val1 + Val2
    elif(opc == "and"):
        return Val1 & Val2
    elif(opc == "or"):
        return Val1 | Val2
    elif(opc == "xor"):
        return (Val1 ^ Val2)
    elif(opc == "not"):
        # val2 can be None
        return not(Val1)
    elif(opc == "mul"):
        return Val1 * Val2
    elif(opc == "div"):
        return Val1 / Val2

def evaluatePointer(inPointer):
    if(inPointer[0]== 'r'):
        return regF[inPointer[1:]]  ## return value from register file after removing 'r'
    elif(inPointer[0]=="i"):
        print("Un-updated pointer value was dispatched for execution.")
        return None

def broadcast(insID, outputValue):
    RegtoStore = (instQueue[insID][2])
    regF[RegtoStore] = outputValue
    # print(insID, outputValue)
    
    # replace existing pointers in reservation table to execute.
    for coreID in resst:
        for ins in resst[coreID]:
            Qj = ins[5]
            Qk = ins[6]
            if(Qj == "i"+str(insID)):
                ins[5] = outputValue
                if(broadcastTelemetry == 2): print("replaced i"+str(insID), "with", outputValue, "for operand 1 in insID =", insID, "for core=", coreID)

            if(Qk == "i"+str(insID)):
                ins[6] = outputValue
                if(broadcastTelemetry == 2): print("replaced i"+str(insID), "with", outputValue, "for operand 2 in insID =", insID, "for core=", coreID)

def writeback(regAddr, value):
    regF[regAddr] = value

def dispatch(coreID, insNum):
    ins = resst[coreID][insNum]
    insId = ins[0]
    insOp = ins[2]
    
    Vj = ins[3]
    Vk = ins[4]

    Qj = ins[5]
    Qk = ins[6]

    ## operate according to OpCode
    ### checking if core supports that operation
    if(not(insOp in cores[coreID][0])):
        print("Operation not supported by core.")
        return -1
    
    # getting appropriate inputs for operation.
    if(type(Vj) != type(None)):
        Val1 = Vj
    elif(type(Qj) != type(None)):
        Val1 = evaluatePointer(Qj)
    else:
        Val1 = None

    if(type(Vk) != type(None)):
        Val2 = Vk
    elif(type(Qk) != type(None)):
        Val2 = evaluatePointer(Qk)
    else:
        Val2 = None


    # execution of instruction begins (as a simulator, the value is processed and waits for clock)
    outVal = exec(insOp, Val1, Val2)


    # find delay from the core properties
    delay = cores[coreID][2][(cores[coreID][0].index(insOp))]
    targetClock = clock + delay

    if(targetClock in broadcastQueue.keys()):
        broadcastQueue[targetClock].append([insId, outVal])
    else:
        broadcastQueue[targetClock] = [[insId, outVal]]
    
    ## adding to writeback queue
    if((targetClock+writeback_delay) in writeBackQueue.key()):  # checking if key already exists
        print("Multiple writebacks in", (targetClock + writeback_delay), "clock cycle.")
        writeBackQueue[targetClock+writeback_delay].append([insId, outVal])
    else:
        broadcastQueue[targetClock+writeback_delay] = [[insId, outVal]]



def findFreeCore(opCode):
    # finding fastest core capable of executing this instruction with least queue
    minDelay = -1
    minDelayCoreID = -1
    for coreID in resst:
        # check if core can exec the opcode
        if((opCode in cores[coreID][0])):
            delay = cores[coreID][2][(cores[coreID][0].index(opCode))]
            if(delay < minDelay or minDelay == -1): # uninitialized min delay
                minDelay = delay
                minDelayCoreID = coreID

            


def issue(clock):
    if(issueTelemetry): print("Issuing")
    
    # find the next instruction in instQueue without checking dependency
    for id in instQueue:
        if(instQueue[id][5]==0):
            ins = instQueue[id]
            resst[coreID]


##### MAIN #####
clock = 0

# calculate dependency penalty


while(True):
    print("clock cycle=", clock)

    ## Dispatch stage
    for core in resst:
        pass
        # for ins in resst[core]:
        #     print("pending core:", core, " > ",  ins)


    ## Broadcast Stage
    if(clock in broadcastQueue.keys()):
        pendingBrd = broadcastQueue[clock]

        if(broadcastTelemetry): print("pendingbroadcasts: ", pendingBrd)
        for brd in pendingBrd:
            broadcast(insID=brd[0], outputValue=[1])


    ## Issue Stage (written out of order as to run issued instruction in next cycle
    issue(clock)
        

    # for brd in broadcastQueue:

    # check for available broadcasts at this clock cycle

    break
    clock += 1