from math import factorial
from decimal import Decimal, getcontext
from timeit import default_timer as timer
from argparse import ArgumentParser
from multiprocessing import Process, Manager
from os import path
from io import open


parser = ArgumentParser(description="Calculate Napier's constant up to a given precision on a given number of threads.")
parser.add_argument('-p', '--precision', metavar='P', type=int,
                    help='precision', required=True)

parser.add_argument('-t', '--tasks', metavar='T', type=int,
                    help='number of threads', required=True)

parser.add_argument('-o', metavar='File', type=str,
                    help='output file name')

parser.add_argument('-q', '--quiet', action='store_true',
                    help='quiet')

args = parser.parse_args()
precision = args.precision
tasks = args.tasks
quiet = args.quiet
output_file_name = args.o
getcontext().prec = precision + 1


def calculate(indexes, index, queue, quiet):
    if not quiet:
        print("Thread", index, "started.")
    getcontext().prec = precision + 1
    result = 0
    for i in indexes:
        result += Decimal(3-4*i*i)/Decimal(factorial(2*i + 1))
    queue.put(result)
    if not quiet:
        print("Thread", index, "finished.")

if __name__ == '__main__':
    calculation_params = []
    for _ in range(0, tasks):
        calculation_params.append([])
    for index in range(0, precision):
        calculation_params[index % tasks].append(index)

    queue = Manager().Queue(maxsize=tasks)
    start_time = timer()
    processes = []
    for thread_index in range(0, len(calculation_params)):
        p = Process(target=calculate, args=(calculation_params[thread_index],
                                            thread_index, queue, quiet))
        processes.append(p)
        p.start()

    result = 0
    for _ in range(0, tasks):
        result += queue.get()

    for p in processes:
        p.join()

    time = timer() - start_time
    message = 'Using %s tasks\nElapsed time: %s seconds' % (tasks,
                                                            time)
    if not quiet:
        print(message)
    if output_file_name:
        with open(output_file_name, 'a') as file:
            file.write('%s\n' % unicode(str(time), "utf-8"))
