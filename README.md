#zerorpc-taskq

### A  `zerorpc` task queue + workers implementation:

Use this if you would like to:
- run a `zerorpc` server with multiple workers for CPU-based parallelism
- be able to throttle/prioritize/assign tasks with a queue
- cancel any tasks easily (even those that have already started)


This project is not yet fully threadsafe; work is ongoing in order to ensure this. 