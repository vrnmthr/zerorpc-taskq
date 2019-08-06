import argparse

import zerorpc
import time

class MyService:
    def __init__(self):
        pass

    def call(self, function, args):
        func = getattr(self, function)
        return func(**args)

    def long(self, pid):
        print("worker on {} received long task".format(args["addr"]))
        time.sleep(20)
        return "finished!"

    def short(self, pid):
        print("worker on {} received short task".format(args["addr"]))
        return "finished!"


# def make_stop_method(server):
#     def stop():
#         # kill except the one executing the kill argument
#         greenlets = list(server._task_pool.greenlets)
#         for greenlet in greenlets:
#             func = greenlet.args[0].name
#             if func != "kill":
#                 print("killing func {}".format(func))
#                 server._task_pool.killone(greenlet)
#                 print("killed func {}".format(func))
#
#     return stop


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", help="address to start the given worker on")
    args = vars(parser.parse_args())
    # args["addr"] = "tcp://127.0.0.1:5000"

    s = zerorpc.Server(MyService())
    # print(s._methods)

    # # patch such this has "run" and "stop" methods too
    # s._methods['kill'] = make_stop_method(s)
    # s._methods['greenlets'] = lambda: s._task_pool.greenlets
    # for (k, functor) in iteritems(s._methods):
    #     if not isinstance(functor, DecoratorBase):
    #         s._methods[k] = rep(functor)
    # print(s._methods)

    s.bind(args["addr"])
    print("starting worker on {}".format(args["addr"]))
    s.run()
