importeer asyncio
importeer math als m
van collections importeer Counter

LIMIT = 30
registry = {}


functie fib(limit):
    a, b = 0, 1
    values = []
    zolang Waar:
        indien a >= limit:
            breek
        values.append(a)
        a, b = b, a + b
    retourneer values


functie evens(numbers):
    voor number in numbers:
        indien number % 2:
            doorgaan
        genereer number


functie must_be_positive(value):
    indien value <= 0:
        werp ValueError("not positive")
    retourneer value


functie safe_div(a, b):
    probeer:
        beweer b != 0
        retourneer a / b
    behalve AssertionError:
        retourneer Niets
    tenslotte:
        pas


klasse Accumulator:
    functie __init__(self):
        self.total = 0

    functie add(self, amount):
        self.total += amount

    functie get(self):
        retourneer self.total


klasse Section:
    functie __enter__(self):
        retourneer self

    functie __exit__(self, exc_type, exc, traceback):
        retourneer Onwaar


functie register(name):
    globaal registry
    registry[name] = Waar


functie outer():
    count = 0

    functie inner():
        niet_lokaal count
        count += 1
        retourneer count

    retourneer inner


asynchroon functie report(value):
    wacht asyncio.sleep(0)
    indien value is Niets of niet value:
        retourneer "empty"
    anders_als value > 10 en value % 2 == 0:
        retourneer "big even"
    anders:
        retourneer "other"


functie main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    met Section():
        voor value in evens(values):
            acc.add(value)
    double = lambda x: x * 2
    squares = [double(v) voor v in values[:4]]
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
    verwijder registry["fib"]
    print("clean", "fib" niet in registry)


indien Waar:
    main()
