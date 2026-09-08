# Operating Systems: Deadlocks & Process Synchronization

## 1. What is a Deadlock?
A deadlock in an operating system is a situation where a set of processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process. None of the processes can run, release resources, or be awakened.

## 2. The Four Necessary Coffman Conditions for Deadlock
A deadlock occurs if and only if all four of the following conditions hold simultaneously:
1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode. Only one process can use the resource at any given time.
2. **Hold and Wait**: A process must currently be holding at least one resource and requesting additional resources that are being held by other processes.
3. **No Preemption**: Resources cannot be preempted; that is, a resource can be released only voluntarily by the process holding it, after that process has completed its task.
4. **Circular Wait**: A closed chain of processes exists such that each process holds at least one resource needed by the next process in the chain (e.g., P0 waits for P1, P1 waits for P2, and Pn waits for P0).

## 3. Deadlock Handling Strategies
Operating systems manage deadlocks through four primary approaches:
- **Deadlock Ignorance (Ostrich Algorithm)**: Stick your head in the sand and pretend the problem never occurs. Common in general-purpose OS like Linux and Windows when deadlock frequency is low.
- **Deadlock Prevention**: Design protocols that guarantee at least one of the four necessary conditions cannot hold (e.g., resource ordering to eliminate circular wait).
- **Deadlock Avoidance**: The OS dynamically examines resource allocation state to ensure a safe state always exists.
- **Deadlock Detection and Recovery**: Allow deadlocks to occur, periodically detect them using wait-for graphs, and recover via process termination or resource preemption.

## 4. Banker's Algorithm for Deadlock Avoidance
Developed by Edsger Dijkstra, the Banker's Algorithm tests for safety by simulating the allocation for predetermined maximum possible amounts of all resources, before deciding whether allocation should be allowed to continue.
Key Data Structures:
- **Available Vector**: Array of length $m$ indicating available instances of each resource type.
- **Max Matrix**: $n \times m$ matrix defining the maximum demand of each process.
- **Allocation Matrix**: $n \times m$ matrix defining the number of resources of each type currently allocated to each process.
- **Need Matrix**: Calculated as $\text{Need}[i][j] = \text{Max}[i][j] - \text{Allocation}[i][j]$.

A state is **safe** if there exists a safe sequence $\langle P_1, P_2, \dots, P_n \rangle$ such that for each $P_i$, the resources that $P_i$ can still request can be satisfied by currently available resources plus resources held by all prior $P_j$ ($j < i$).
