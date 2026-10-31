importuj asyncio
importuj math jako m
z collections importuj Counter

LIMIT = 30
registry = {}


funkcja fib(limit):
    a, b = 0, 1
    values = []
    dopóki Prawda:
        jeśli a >= limit:
            przerwij
        values.append(a)
        a, b = b, a + b
    zwróć values


funkcja evens(numbers):
    dla number w numbers:
        jeśli number % 2:
            kontynuuj
        generuj number


funkcja must_be_positive(value):
    jeśli value <= 0:
        zgłoś ValueError("not positive")
    zwróć value


funkcja safe_div(a, b):
    spróbuj:
        upewnij b != 0
        zwróć a / b
    wyjątek AssertionError:
        zwróć Nic
    wreszcie:
        pomiń


klasa Accumulator:
    funkcja __init__(self):
        self.total = 0

    funkcja add(self, amount):
        self.total += amount

    funkcja get(self):
        zwróć self.total


klasa Section:
    funkcja __enter__(self):
        zwróć self

    funkcja __exit__(self, exc_type, exc, traceback):
        zwróć Fałsz


funkcja register(name):
    globalny registry
    registry[name] = Prawda


funkcja outer():
    count = 0

    funkcja inner():
        nielokalny count
        count += 1
        zwróć count

    zwróć inner


asynchroniczny funkcja report(value):
    czekaj asyncio.sleep(0)
    jeśli value jest Nic lub nie value:
        zwróć "empty"
    inaczej_jeśli value > 10 i value % 2 == 0:
        zwróć "big even"
    inaczej:
        zwróć "other"


funkcja main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    w_kontekście Section():
        dla value w evens(values):
            acc.add(value)
    double = lambda x: x * 2
    squares = [double(v) dla v w values[:4]]
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
    usuń registry["fib"]
    print("clean", "fib" nie w registry)


jeśli Prawda:
    main()
