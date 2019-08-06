import zerorpc
import argparse
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pid")
    parser.add_argument("--long", action="store_true")
    parser.add_argument("--cancel", action="store_true")

    args = vars(parser.parse_args())
    client = zerorpc.Client(timeout=1000000, heartbeat=1000000)
    client.connect("tcp://127.0.0.1:4444")
    print("connected")

    pid = int(args["pid"])
    if args['long']:
        print(client.launch("long", {"pid": pid}))
    elif args['cancel']:
        print(client.cancel(pid))
    else:
        print(client.launch("short", {"pid": pid}))

    client.close()
