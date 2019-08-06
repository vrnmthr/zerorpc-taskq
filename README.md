# zerorpc-taskq

### A  `zerorpc` task queue + workers implementation:

Use this if you would like to:
- run a `zerorpc` server with multiple workers for CPU-based parallelism
- easily change the number of workers used
- be able to throttle/prioritize/assign tasks with a queue
- cancel any tasks easily (even those that have already started)

## Quickstart
```shell script
pip3 install -r requirements.txt
python3 server.py

# start a long process with pid 1
python3 client.py 1 --long
# start a short process with pid 2
python3 client.py 2
# cancel the long process
python3 client.py 1 --cancel
```

The server automatically starts and maintains its workers. 
See `client.py` for details on how to use the client.


This project is not yet fully threadsafe; work is ongoing in order to ensure this. 
