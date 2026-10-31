importera asyncio
importera math som m
från collections importera Counter

LIMIT = 30
registry = {}


funktion fib(limit):
    a, b = 0, 1
    values = []
    medan Sant:
        om a >= limit:
            bryt
        values.append(a)
        a, b = b, a + b
    returnera values


funktion evens(numbers):
    för number i numbers:
        om number % 2:
            fortsätt
        generera number


funktion must_be_positive(value):
    om value <= 0:
        res ValueError("not positive")
    returnera value


funktion safe_div(a, b):
    försök:
        hävda b != 0
        returnera a / b
    undantag AssertionError:
        returnera Inget
    slutligen:
        passera


klass Accumulator:
    funktion __init__(self):
        self.total = 0

    funktion add(self, amount):
        self.total += amount

    funktion get(self):
        returnera self.total


klass Section:
    funktion __enter__(self):
        returnera self

    funktion __exit__(self, exc_type, exc, traceback):
        returnera Falskt


funktion register(name):
    global registry
    registry[name] = Sant


funktion outer():
    count = 0

    funktion inner():
        icke_lokal count
        count += 1
        returnera count

    returnera inner


asynkron funktion report(value):
    vänta asyncio.sleep(0)
    om value är Inget eller inte value:
        returnera "empty"
    annars_om value > 10 och value % 2 == 0:
        returnera "big even"
    annars:
        returnera "other"


funktion main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    med Section():
        för value i evens(values):
            acc.add(value)
    double = lambda x: x * 2
    squares = [double(v) för v i values[:4]]
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
    radera registry["fib"]
    print("clean", "fib" inte i registry)


om Sant:
    main()
