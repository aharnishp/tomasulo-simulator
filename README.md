# Tomasulo Simulator
is a python script that simulates instruction level parallelism in the CPU, while maintaining correctness. 

Project as a part of course on High Speed Computer Architecture.

#### What steps included?
In brief, these are the steps:
### Issue Stage
At this stage, instructions are distributed to appropriate compute unit (reservation tables of the core that supports that operation).

### Dispatch Stage
This occurs at each compute unit, and has to control when to execute the instruction and when to wait for required data to be calculated.

### Broadcast Stage
This is the "final" step when calculated values are stored at appropriate register and passed to needed executions waiting.

#### What does not work?
Currently, there is no support for conditional instructions, and hence there is no branch prediction as of yet. 
