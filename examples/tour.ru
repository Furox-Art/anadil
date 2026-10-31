импорт asyncio
импорт math как m
из collections импорт Counter

LIMIT = 30
registry = {}


определить fib(limit):
    a, b = 0, 1
    values = []
    пока Истина:
        если a >= limit:
            прервать
        values.append(a)
        a, b = b, a + b
    вернуть values


определить evens(numbers):
    для number в numbers:
        если number % 2:
            продолжить
        генерировать number


определить must_be_positive(value):
    если value <= 0:
        поднять ValueError("not positive")
    вернуть value


определить safe_div(a, b):
    попробовать:
        утверждать b != 0
        вернуть a / b
    исключение AssertionError:
        вернуть Ничто
    наконец:
        пропустить


класс Accumulator:
    определить __init__(self):
        self.total = 0

    определить add(self, amount):
        self.total += amount

    определить get(self):
        вернуть self.total


класс Section:
    определить __enter__(self):
        вернуть self

    определить __exit__(self, exc_type, exc, traceback):
        вернуть Ложь


определить register(name):
    глобальный registry
    registry[name] = Истина


определить outer():
    count = 0

    определить inner():
        нелокальный count
        count += 1
        вернуть count

    вернуть inner


асинхронный определить report(value):
    ожидать asyncio.sleep(0)
    если value это Ничто или не value:
        вернуть "empty"
    иначе_если value > 10 и value % 2 == 0:
        вернуть "big even"
    иначе:
        вернуть "other"


определить main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    с Section():
        для value в evens(values):
            acc.add(value)
    double = лямбда x: x * 2
    squares = [double(v) для v в values[:4]]
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
    удалить registry["fib"]
    print("clean", "fib" не в registry)


если Истина:
    main()
