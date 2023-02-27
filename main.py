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



# TODO:
# Dispatch out of order



# import numpy as np

##### INPUT VARIABLES #####


# Instruction Queue
#                     0        1         2        3         4              5
## Format {indx: [Operation, storeTo, input1, input2, immediateData, queuedStatus],}
instQueue = {
    # indx 0  1  2  3  4   5
    0:["load",6, 2, 0,34, 0],
    1:["load",2, 3, 0,45, 0],
    2:["mul", 0, 2, 4, 0, 0],
    3:["sub", 8, 2, 6, 0, 0],
    4:["div",10, 0, 6, 0, 0],
    5:["add", 6, 8, 2, 0, 0],
}

## RAT table
# Format => {2:"i5"}
rat = {}

# Architecture of core distribution
## Format: [[["list of ","operations supported"], #number of rows in Reservation Table, [executionDuration]]]
cores = [
            [["add", "adi", "sub", "subi", "and", "or", "xor", "not", "load"],3,[2,2,2,2,2,2,2,2,2]], ## coreID 0
            [["mul", "div"],3,[10,40]],     ## coreID = 1
            [["mul", "div"],3,[10,40]]      ## coreID = 2
        ]


## Dictionary of register file
regF = {
    0:0,
    1:0,
    2:100,
    3:200,
    4:2.5,
}


## Memory to load data from
memory = {
    134: 256,
    245: 512,
}





##### PARAMETERS #####
writeback_delay = 1






### Telemetries:    has 3 levels = {0, 1, 2}
issueTelemetry = 1
dispatchTelemetry = 1
broadcastTelemetry = 2

warningTelemetry = 1

##### OPERATIONAL VARIABLES #####


## Creating reservation table
# Format = {
#   coreID: [        Vj = float         Qj = pointer stored as string
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, DispatchedStageClockCycle],
#   ],
#   coreID: [0   1      2     3   4   5   6     7
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, DispatchedStageClockCycle],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, DispatchedStageClockCycle],
#   ]
# }

# Examples of Qj
# Qj = r12 pointing to regF[12]
# Qj = i7 pointing to output of instructionId 7


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




##### INITIALIZATIONS #####
##### INITIALIZATIONS #####
##### INITIALIZATIONS #####

print("Empty reservation station:", resst)


# print("adding dummy data to reservation table")
# resst[0].append([2, 1, "add", 56, 34, None, None, None])


##### FUNCTIONS #####
##### FUNCTIONS #####
##### FUNCTIONS #####


def exec(opc, Val1, Val2, immediateData = 0):
    if(opc == "add"):
        return Val1 + Val2
    elif(opc == "adi"):
        return Val1 + Val2 + immediateData
    elif(opc == "sub"):
        return Val1 - Val2
    elif(opc == "subi"):
        return Val1 + Val2 + immediateData
    elif(opc == "and"):
        return Val1 & Val2
    elif(opc == "andi"):
        return Val1 & immediateData
    elif(opc == "or"):
        return Val1 | Val2
    elif(opc == "xor"):
        return (Val1 ^ Val2)
    elif(opc == "not"):
        # val2 can be None
        return not(Val1)
    elif(opc == "mul"):
        return Val1 * Val2
    elif(opc == "muli"):
        return Val1 * immediateData
    elif(opc == "div"):
        return Val1 / Val2
    elif(opc == "load"):
        addr = immediateData + Val1
        if(addr in (memory.keys())):
            return memory[addr]
        else:   
            return 0
    # elif(opc == "store"):
    #     addr = immediateData + Val1
        
    #     return None

def evaluatePointer(inPointer):
    if(inPointer[0]== 'r'):
        return regF[inPointer[1:]]  ## return value from register file after removing 'r'
    elif(inPointer[0]=="i"):
        print("Un-updated pointer value was dispatched for execution.")
        return None

def broadcast(insID, outputValue):
    RegtoStore = (instQueue[insID][2])
    # regF[RegtoStore] = outputValue
    # print(insID, outputValue)
    
    # storing addr of instruction to delete later 
    delCoreID = -1
    delInsIndex = -1

    # replace existing pointers in reservation table to execute.    
    for coreID in resst:
        for indx, ins in enumerate(resst[coreID]):
            if(outputValue is not None):
                Qj = ins[5]
                Qk = ins[6]
                if(Qj == "i"+str(insID)):
                    ins[5] = outputValue
                    if(broadcastTelemetry == 2): print("replaced i"+str(insID), "with", outputValue, "for operand 1 in insID =", insID, "for core=", coreID)

                if(Qk == "i"+str(insID)):
                    ins[6] = outputValue
                    if(broadcastTelemetry == 2): print("replaced i"+str(insID), "with", outputValue, "for operand 2 in insID =", insID, "for core=", coreID)
                
            # searching for insID in resst
            if(insID == ins[0]):
                if(broadcastTelemetry): print("Matched Inst. to delete")
                delCoreID = coreID
                delInsIndex = indx


    # remove from reservation table
    executedIns = resst[delCoreID].pop(delInsIndex)
    if(broadcastTelemetry): print("Instruction Broadcasted =", executedIns)

    # remove from RAT able
    ## verify RAT table pointer was not over-written
    if(insID[1] in rat.keys()):
        if(rat[insID[1]] == "i"+str(insID)):
            if(broadcastTelemetry): print("deleting pointer in rat for insID =", insID)
            del rat[insID[1]]
        else:
            if(broadcastTelemetry): print("mismatched pointer in RAT, not deleted")
    else:
        if(broadcastTelemetry): print("Not found in RAT insID =", insID)

    # remove from broadcast queue
    if(clock in broadcastQueue.keys()):
        if(len(broadcastQueue[clock]) > 1):     # multiple broadcast at sametime
            for i in range(len(broadcastQueue[clock])):
                if(broadcastQueue[clock][i][0] == insID):
                    broadcastQueue[clock].pop(i)
        elif(len(broadcastQueue[clock]) == 1):
            broadcastQueue[clock] = []
        else:
            if(warningTelemetry): print("WARNING: broadcastQueue was already cleared.")


def writeback(regAddr, value):
    if(value is not None):
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



def findBestCore(opCode):
    # finding fastest core capable of executing this instruction with least queue
    minDelay = -1
    minDelayCoreID = -1
    for coreID in resst:
        # check if core can exec the opcode
        if((opCode in cores[coreID][0])):
            # counting number of entries in reservation table for that core.
            count = 0
            delay = 0
            for ins in resst[coreID]:   # summing delay for queues
                thisOpCode = ins[2]
                count += 1
                delay += cores[coreID][2][(cores[coreID][0].index(thisOpCode))]
            # adding required delay for current operation
            delay += cores[coreID][2][(cores[coreID][0].index(opCode))]
            if((delay < minDelay or minDelay == -1) and count < cores[coreID][1]): # uninitialized min delay
                minDelay = delay
                minDelayCoreID = coreID
                # BETA-ONLY:
    if(minDelayCoreID == -1):
        if(warningTelemetry): print("Warning: No free core supports the instruction:", opCode)
    return minDelayCoreID
#  FIXME:
            


def issue(clock):
    if(issueTelemetry): print("Issuing")
    
    # find the next instruction in instQueue without caring about dependency
    for id in instQueue:
        if(instQueue[id][5]==0):
            ins = instQueue[id]

            Vj = None
            Vk = None
            Qj = None
            Qk = None
            immediateData = ins[4]

            # find input sources according to the RAT table.

            # finding val1 in rat
            if(ins[2] in rat.keys() and rat[ins[2]][0] == "i"):
                # val1 = "i" + str(ins[2])
                Qj = "i" + str(ins[2])
            else: 
                # extract value from register at this clock
                if(ins[2] in regF.keys()):
                    Vj = regF[ins[2]]
                else:
                    if(warningTelemetry == 1): print("WARNING: no link in rat found & addr uninitialized in regF. insID =",id,"  clock =",clock,"  addr =", ins[2])
                    Vj = 0
                    regF[ins[2]] = 0

            # finding val2 in rat
            if(ins[3] in rat.keys() and rat[ins[3]][0] == "i"):
                # val1 = "i" + str(ins[3])
                Qk = "i" + str(ins[3])
            else: 
                # extract value from register at this clock
                if(ins[3] in regF.keys()):
                    Vk = regF[ins[3]]
                else:
                    if(warningTelemetry == 1): print("WARNING: no link in rat found & addr uninitialized in regF. insID =",id,"  clock =",clock,"  addr =", ins[3])
                    Vk = 0
                    regF[ins[3]] = 0

                   



            #                             [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle]
            bestCore = findBestCore(ins[0])
            if(bestCore > -1):
                resst[bestCore].append([id, 1, ins[0], Vj, Vk, Qj, Qk, immediateData, None])
            else:
                if(issueTelemetry): print("Reservation Table full / no core able to exec this.")
                continue

            # insert current output address to RAT Table with link
            rat[ins[1]] = "i"+str(id)

            # change issued flag to 1 in instQueue
            instQueue[id][5] = 1

            # TODO:
            return 0  # 0 if issued
            # break
    print("No instructions were issued")
    return 0      # 1 if unable to issue

##### MAIN #####
clock = 0


allInsIssued = 0
# calculate dependency penalty


while(True):
    print("clock cycle =", clock)

    print("Reservation Table = ")
    for core in resst:
        for ins in resst[core]:
            print("core:", core, " > ",  ins)

    
    ## Dispatch stage
    for core in resst:
        # find a suitable instruction to execute without dependencies
        for ins in resst[core]:
            pass
            # print("pending core:", core, " > ",  ins)


    ## Broadcast Stage      (and remove instruction itself from reservation station)
    if(clock in broadcastQueue.keys()):
        pendingBrd = broadcastQueue[clock]

        if(broadcastTelemetry): print("pendingbroadcasts: ", pendingBrd)
        for brd in pendingBrd:
            broadcast(insID=brd[0], outputValue=[1])

    # Writeback Queue 
    if(clock in writeBackQueue.keys()):
        pendingWB = writeBackQueue[clock]

        if(broadcastTelemetry): print("pending writeback: ", pendingWB)
        for wb in pendingWB:
            RegtoStore = (instQueue[wb[0]][2])
            writeback(regAddr=RegtoStore, value=wb[1])

        del writeBackQueue[clock]

    ## Issue Stage (written out of order as to run issued instruction in next cycle
    issue(clock)

    # checking if all instructions are executed
    allInsIssued = 1
    for  insID in instQueue:
        if(instQueue[insID][5] == 0):
            allInsIssued = 0



    # FIXME: Add exit condition
    if(len(broadcastQueue) == 0 and len(writeBackQueue) == 0 and allInsIssued == 1):
        break
    clock += 1