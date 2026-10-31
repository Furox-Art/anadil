import asyncio
import math as m
from collections import Counter

LIMIT = 30
registry = {}


def fib(limit):
    a, b = 0, 1
    values = []
    while True:
        if a >= limit:
            break
        values.append(a)
        a, b = b, a + b
    return values


def evens(numbers):
    for number in numbers:
        if number % 2:
            continue
        yield number


def must_be_positive(value):
    if value <= 0:
        raise ValueError("not positive")
    return value


def safe_div(a, b):
    try:
        assert b != 0
        return a / b
    except AssertionError:
        return None
    finally:
        pass


class Accumulator:
    def __init__(self):
        self.total = 0

    def add(self, amount):
        self.total += amount

    def get(self):
        return self.total


class Section:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def register(name):
    global registry
    registry[name] = True


def outer():
    count = 0

    def inner():
        nonlocal count
        count += 1
        return count

    return inner


async def report(value):
    await asyncio.sleep(0)
    if value is None or not value:
        return "empty"
    elif value > 10 and value % 2 == 0:
        return "big even"
    else:
        return "other"


def main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    with Section():
        for value in evens(values):
            acc.add(value)
    double = lambda x: x * 2
    squares = [double(v) for v in values[:4]]
    register("fib")
    next_call = outer()
    next_call()
    print("fib", values)
    print("even sum", acc.get())
    print("squares", squares)
    print("zero count", counter[0])
    print("div", safe_div(9, 3))
    print("root", int(m.sqrt(81)))
    print("positive", must_be_positive(5))
    print("report", asyncio.run(report(4)))
    print("registry", registry["fib"])
    print("calls", next_call())
    del registry["fib"]
    print("clean", "fib" not in registry)


if True:
    main()
