# Tomasulo Simulator
is a python script that can simulate operations taking place at CPU level. 

#### What steps included?
In brief, these are the steps:
### Issue Stage
At this stage, instructions are distributed to appropriate compute unit (reservation tables of the core that supports that operation).

### Dispatch Stage
This occurs at each compute unit, and has to control when to execute the instruction and when to wait for required data to be calculated.

### Broadcast Stage
This is the "final" step when calculated values are stored at appropriate register and passed to needed executions waiting.