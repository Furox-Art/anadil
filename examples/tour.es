importar asyncio
importar math como m
desde collections importar Counter

LIMIT = 30
registry = {}


función fib(limit):
    a, b = 0, 1
    values = []
    mientras Verdadero:
        si a >= limit:
            romper
        values.append(a)
        a, b = b, a + b
    devolver values


función evens(numbers):
    para number en numbers:
        si number % 2:
            continuar
        generar number


función must_be_positive(value):
    si value <= 0:
        lanzar ValueError("not positive")
    devolver value


función safe_div(a, b):
    intentar:
        afirmar b != 0
        devolver a / b
    excepto AssertionError:
        devolver Ninguno
    finalmente:
        pasar


clase Accumulator:
    función __init__(self):
        self.total = 0

    función add(self, amount):
        self.total += amount

    función get(self):
        devolver self.total


clase Section:
    función __enter__(self):
        devolver self

    función __exit__(self, exc_type, exc, traceback):
        devolver Falso


función register(name):
    global registry
    registry[name] = Verdadero


función outer():
    count = 0

    función inner():
        no_local count
        count += 1
        devolver count

    devolver inner


asíncrono función report(value):
    esperar asyncio.sleep(0)
    si value es Ninguno o no value:
        devolver "empty"
    sino_si value > 10 y value % 2 == 0:
        devolver "big even"
    sino:
        devolver "other"


función main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    con Section():
        para value en evens(values):
            acc.add(value)
    double = lambda x: x * 2
    squares = [double(v) para v en values[:4]]
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
    eliminar registry["fib"]
    print("clean", "fib" no en registry)


si Verdadero:
    main()
