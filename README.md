# extended-abm
## Project 2: Duo-Core Processor Extension

### Purpose
The primary goal of this project is to extend the stack-based microprocessor simulator by implementing a duo-core processor. This extension involves creating an additional core with similar properties to the original processor developed in Project 1.

### Details
- **Simulator Enhancement:** The project focuses on creating a duo-core version of the ABM abstract machine, extending the original simulator.
- **Instruction Set Extension:** This version of the simulator will include all the instructions in the existing ABM instruction set. Additionally, it will introduce new instructions:
  - `.data`: Marks the start of the data segment, allowing the declaration of global variables accessible by all cores.
  - `.text`: Indicates that the subsequent instructions are stored in the user text segment.
  - `.int d1, …, dn`: Stores 'n' integers in successive data memory locations.
  - `:&`: Replaces the stack top with the lvalue below it and pops both. Both operands are memory addresses, assigning one memory address to another.
  - `+, -`: Overloads addition and subtraction operators to manipulate memory addresses respectively.
- **Shared Memory Bus:** The enhanced simulator provides access to shared memory using a shared memory bus. All processor communications with memory are controlled by the memory bus component to ensure data integrity.

### Code Summary
The code employs threading to execute and simulate the two cores concurrently. It initializes the ABM class for the original processor and its duo-core extension and reads instructions from provided files. Methods in the code simulate stack manipulation, control, calculations, output, and subprogram functionalities as per the ABM instructions. It showcases shared memory features by displaying data segments of both cores.

---

## Project 3: Private Cache Addition

### Purpose
Building upon Project 2, the primary objective of this phase is to enhance the duo-core version of the ABM simulator by introducing private cache support to each core. This includes implementing the MSI cache coherence write-back protocol.

### Details
- **Cache Support Extension:** The project extends the duo-core version of the ABM simulator to incorporate private cache support for each core.
- **Instruction Set:** It includes all the instructions of Project 2 while incorporating the MSI cache coherence write-back protocol.
- **Memory and Processor Interaction:** The memory bus component continues to control all interactions between processors and memory.
- **Private Cache Features:** Each core includes a private cache supporting the MSI protocol to manage the cache coherence between cores.
- **Code Development:** The implementation involves adapting the existing codebase from Project 2, enhancing it to manage private caches while ensuring data coherence between the cores.

### Code Summary
The code initializes and extends the ABM class for private cache support, introducing cache blocks and maintaining cache coherence via the MSI protocol. It incorporates cache mechanisms to manage data access, retrieval, and modification within the private caches of both cores. The threading setup allows concurrent execution and simulation of the duo-core processors. It exemplifies shared memory functionality and cache utilization by demonstrating data segments for both cores and cache manipulations.

---
*Documented by ChatGPT*
