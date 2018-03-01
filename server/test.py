import json
import thread
import time
import threading

def test_fun():
    for i in range(8):
        print(i)
        time.sleep(1)


def e():
    while True:
        d = raw_input()
        print(d)
        if d == "e":

            thread.interrupt_main()
            return


if __name__ == "__main__":
    f = lambda : thread.interrupt_main()
    t = threading.Thread(target=e, args=[])

    try:
        t.start()
        test_fun()
        print("sleep over")
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt")
        exit(0)
    exit(1)