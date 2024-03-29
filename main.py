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
# Block core till execution time is completed.



# import numpy as np

##### INPUT VARIABLES #####


# Instruction Queue
#                     0        1         2        3         4              5                6
## Format {indx: [Operation, storeTo, input1, input2, immediateData, queuedStatus, execution_Core_of_ins],}
    # execution_Core_of_ins = -1 means it can execute on any core cluster and will be given to sub core with minimum reservation queue.
instQueue = {
    # indx 0  1  2  3  4  5  6
    0:["load",6, 2, 0,34, 0, 0],
    1:["load",2, 3, 0,45, 0, 0],
    2:["mul", 0, 2, 4, 0, 0, 0],
    3:["sub", 8, 2, 6, 0, 0, 1],
    4:["div",10, 0, 6, 0, 0, 1],
    5:["add", 6, 8, 2, 0, 0, 1],
}

L1size = 3 # number of memory locations
L2size = 6 # number of memory locations
L3size = 9 # number of memory locations


## RAT table
# Format => {2:"i5"}
rat = {}

# Architecture of core distribution
## Format: [[["list of ","operations supported"], #number of rows in Reservation Table, [executionDuration]]]
cores = [
            # execution core 0
            [["add", "adi", "sub", "subi", "and", "or", "xor", "not", "load"],3,[2,2,2,2,2,2,2,2,2]], ## subcoreID 0
            [["mul", "div"],3,[10,40]],     ## subcoreID = 1

            # execution core 1
            [["add", "adi", "sub", "subi", "and", "or", "xor", "not", "load"],3,[2,2,2,2,2,2,2,2,2]], ## subcoreID 2
            [["mul", "div"],3,[10,40]]      ## subcoreID = 3
        ]

executionCoreCluster = [[0,1],[2,3]]    # [ ( execCore:0 [ 0, 1 ]) , ( execCore:1 [2, 3] ) ]

## Dictionary of register file ( FORMAT=> { Address: Value } )
regF = {
    0:0,
    1:0,
    2:100,
    3:200,
    4:2.5,
}


## Memory to load data from ( FORMAT=> { Address: Value } )
memory = {
    134: 256,
    245: 512,
}

l1cache = [] # [ (core0: { address: value}), (core1: {address: value}) ]
l2cache = [] # [ (core0: { address: value}), (core1: {address: value}) ]
l3cache = [] # [ (core0: { address: value}), (core1: {address: value}) ]


##### PARAMETERS #####
writeback_delay = 1


### Telemetries:    has 3 levels = {0, 1, 2}
issueTelemetry = 1
dispatchTelemetry = 1
broadcastTelemetry = 1

warningTelemetry = 1

##### OPERATIONAL VARIABLES #####


## Creating reservation table
# Format = {
#   coreID: [0   1      2     3   4   5   6         7           8        9          10
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, IssueCLK, DispCLK, WritebackCLK],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, IssueCLK, DispCLK, WritebackCLK],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, IssueCLK, DispCLK, WritebackCLK],
#   ],
#   coreID: [        Vj = float         Qj = pointer stored as string
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, IssueCLK, DispCLK, WritebackCLK],
#       [insID, Busy, OpCode, Vj, Vk, Qj, Qk, ImmediateData, IssueCLK, DispCLK, WritebackCLK],
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


# Store information about which core is executing an operation and which is not
coreFree = {}
for coreID in range(len(cores)):
    coreFree[coreID] = 1


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
        if(Val2 != 0):
            return Val1 / Val2
        else:
            print("FATAL ERROR: Divisin by zero. clock=",clock)
            return -1
    elif(opc == "load"):
        addr = immediateData + Val1
        if(addr in (memory.keys())):
            return memory[addr]
        else:   
            return 0
    # elif(opc == "store"):
    #     addr = immediateData + Val1
        
    #     return None

def getRegF(addr):
    return regF[addr]

def evaluatePointer(inPointer):
    if(inPointer[0]== 'r'):
        return getRegF(inPointer[1:])  ## return value from register file after removing 'r'
    elif(inPointer[0]=="i"):
        print("Un-updated pointer value was dispatched for execution.")
        return None

def broadcast(insID, outputValue):
    RegtoStore = (instQueue[insID][1])
    # regF[RegtoStore] = outputValue
    # print(insID, outputValue)
    
    # storing addr of instruction to delete later 
    delCoreID = -1
    delInsIndex = -1

    # replace existing pointers in reservation table to execute.    
    for coreID in resst:
        for indx, ins in enumerate(resst[coreID]):
            if(outputValue is not None and ins[1] == 1): # if output needs to be stored && instruction is not already completed
                Qj = ins[5]
                Qk = ins[6]
                if(Qj == "i"+str(insID)):
                    ins[5] = None
                    ins[3] = outputValue
                    if(broadcastTelemetry == 2): print("replaced i"+str(insID), "with", outputValue, "for operand 1 in insID =", insID, "for core=", coreID)

                if(Qk == "i"+str(insID)):
                    ins[6] = None
                    ins[4] = outputValue
                    if(broadcastTelemetry == 2): print("replaced i"+str(insID), "with", outputValue, "for operand 2 in insID =", insID, "for core=", coreID)
                
            # searching for insID in resst
            if(insID == ins[0]):
                if(broadcastTelemetry == 2): print("BROADCAST: Matched Instructions to delete.")
                delCoreID = coreID
                delInsIndex = indx


    
    # unblock the executing core
    coreFree[delCoreID] = 1


    # remove from reservation table
    # executedIns = resst[delCoreID].pop(delInsIndex)
    resst[delCoreID][delInsIndex][1] = 0
    if(broadcastTelemetry): print("Instruction Broadcasted =", resst[delCoreID][delInsIndex])

    #### Following code shifted to writeback()
    # # remove from RAT able
    # ## verify RAT table pointer was not over-written
    # if(RegtoStore in rat.keys()):
    #     if(rat[RegtoStore] == "i"+str(insID)):
    #         if(broadcastTelemetry): print("BROADCAST: deleting pointer in rat for insID =", insID, " for addr =", RegtoStore)
    #         del rat[RegtoStore]
    #     else:
    #         if(broadcastTelemetry): print("mismatched pointer in RAT, not deleted. addr =",RegtoStore, "  insID =",insID)
    # else:
    #     if(broadcastTelemetry): print("Not found in RAT insID =", insID)

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


def setRegF(regAddr, value):
    regF[regAddr] = value


def writeback(regAddr, value):
    if(value is not None):
        setRegF(regAddr, value)

    # remove from RAT able
    ## verify RAT table pointer was not over-written
    if(RegtoStore in rat.keys()):
        if(rat[RegtoStore] == "i"+str(insID)):
            if(broadcastTelemetry): print("WRITEBACK: deleting pointer in rat for insID =", insID, " for addr =", RegtoStore)
            del rat[RegtoStore]
        else:
            if(broadcastTelemetry): print("WRITEBACK: mismatched pointer in RAT, not deleted. addr =",RegtoStore, "  insID =",insID)
    else:
        if(broadcastTelemetry): print("Not found in RAT insID =", insID)

def dispatch(coreID, insNum):
    ins = resst[coreID][insNum]
    insId = ins[0]
    insOp = ins[2]
    
    Vj = ins[3]
    Vk = ins[4]

    Qj = ins[5]
    Qk = ins[6]
    m_immediateData = ins[7]

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
    outVal = exec(insOp, Val1, Val2, immediateData=m_immediateData)


    # block core from executing other instructions
    coreFree[coreID] = 0
    
    # find delay from the core properties
    delay = cores[coreID][2][(cores[coreID][0].index(insOp))]
    targetClock = clock + delay

    ## adding to broadcast queue
    if(targetClock in broadcastQueue.keys()):
        broadcastQueue[targetClock].append([insId, outVal])
    else:
        broadcastQueue[targetClock] = [[insId, outVal]]
    
    ## adding to writeback queue
    if((targetClock+writeback_delay) in writeBackQueue.keys()):  # checking if key already exists
        print("Multiple writebacks in", (targetClock + writeback_delay), "clock cycle.")
        writeBackQueue[targetClock+writeback_delay].append([insId, outVal])
    else:
        writeBackQueue[targetClock+writeback_delay] = [[insId, outVal]]

    # updating resst clock information for reference
    ## updating dispatch clk
    resst[coreID][insNum][9] = clock
    resst[coreID][insNum][10] = targetClock + writeback_delay


def dispatcher(coreID):
    # find easiest instruction to execute whose data is available (Qj == None & Qk == None)
    if(coreFree[coreID]):
        for indx, ins in enumerate(resst[coreID]):
            # check if is not issued in the same clock cycle
            if(ins[8] < clock):
                # check if (all data is available) and is not completed
                if((ins[5] is None and ins[6] is None) and ins[1] == 1):
                    if(dispatchTelemetry): print("DISPATCHING: core:",coreID," Ins:", ins)
                    dispatch(coreID, indx)
            else:
                if(dispatchTelemetry == 2): print("DISPATCH2: Instruction",ins[0],"ignored as issued in the same clock cycle (", clock ,").")
    else:
        if(dispatchTelemetry): print("core:", coreID, "is busy.")



def findBestCore(opCode, execution_Core_of_ins = -1):
    # finding fastest core capable of executing this instruction with least queue
    minDelay = -1
    minDelayCoreID = -1
    for coreID in resst:
        # check if core can exec the opcode && ( execution_Core_of_ins == coreID or execution_Core_of_ins = -1 )
        if((opCode in cores[coreID][0])):
            if((coreID in executionCoreCluster[execution_Core_of_ins]) or ( execution_Core_of_ins == -1 )):
                # counting number of entries in reservation table for that core.
                count = 0
                delay = 0
                for ins in resst[coreID]:   # summing delay for queues
                    if(ins[1]==1):
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
                Qj = "i" + (rat[ins[2]][1:])  # store the pointer to the insID whose result this is
            else: 
                # extract value from register at this clock
                if(ins[2] in regF.keys()):
                    Vj = getRegF(ins[2])
                else:
                    if(warningTelemetry == 1): print("WARNING: no link in rat found & addr uninitialized in regF. insID =",id,"  clock =",clock,"  addr =", ins[2])
                    Vj = 0
                    setRegF(ins[2], 0)

            # finding val2 in rat
            if(ins[3] in rat.keys() and rat[ins[3]][0] == "i"):
                # val1 = "i" + str(ins[3])
                Qk = "i" + (rat[ins[3]][1:])  # store the pointer to the insID whose result this is
            else: 
                # extract value from register at this clock
                if(ins[3] in regF.keys()):
                    Vk = getRegF(ins[3])
                else:
                    if(warningTelemetry == 1): print("WARNING: no link in rat found & addr uninitialized in regF. insID =",id,"  clock =",clock,"  addr =", ins[3])
                    Vk = 0
                    setRegF(ins[3], 0)

                   



            #                             [insID, Busy, OpCode, Vj, Vk, Qj, Qk, DispatchedStageClockCycle]
            bestCore = findBestCore(ins[0], instQueue[id][6])
            if(bestCore > -1):
                resst[bestCore].append([id, 1, ins[0], Vj, Vk, Qj, Qk, immediateData, clock, None, None])
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
    print("\n\n\n\n\nclock cycle =", clock)

    print("RAT =", rat)

    print("Reservation Table = ")
    for core in resst:
        for ins in resst[core]:
            print("core:", core, " > ",  ins)


    ## Issue Stage
    issue(clock)
    


    ## Broadcast Stage      (and remove instruction itself from reservation station)
    if(clock in broadcastQueue.keys()):
        pendingBrd = broadcastQueue[clock]

        if(broadcastTelemetry): print("Broadcasting: ", pendingBrd)
        for brd in pendingBrd:
            broadcast(insID=brd[0], outputValue=brd[1])


    ## Dispatch stage
    for coreID in resst:
        dispatcher(coreID=coreID)


    ## Writeback Queue      (Separated from broadcast just for simulation)
    ##### Write back refers to writing memory. Broadcast is used for forwarding result directly.
    if(clock in writeBackQueue.keys()):
        pendingWB = writeBackQueue[clock]

        if(broadcastTelemetry): print("pending writeback: ", pendingWB)
        for wb in pendingWB:
            RegtoStore = (instQueue[wb[0]][1])
            writeback(regAddr=RegtoStore, value=wb[1])

        del writeBackQueue[clock]


    # checking if all instructions are executed
    allInsIssued = 1
    for  insID in instQueue:
        if(instQueue[insID][5] == 0):
            allInsIssued = 0




    cycleViewer = input("Press enter to continue to next cycle.")

    # FIXME: Add exit condition

    if(len(broadcastQueue) == 0 and len(writeBackQueue) == 0 and allInsIssued == 1):
        break
    clock += 1
