εισαγωγή asyncio
εισαγωγή math ως m
από collections εισαγωγή Counter

LIMIT = 30
registry = {}


συνάρτηση fib(limit):
    a, b = 0, 1
    values = []
    όσο Αληθές:
        αν a >= limit:
            διακοπή
        values.append(a)
        a, b = b, a + b
    επιστροφή values


συνάρτηση evens(numbers):
    για number σε numbers:
        αν number % 2:
            συνέχεια
        παράγω number


συνάρτηση must_be_positive(value):
    αν value <= 0:
        εγείρω ValueError("not positive")
    επιστροφή value


συνάρτηση safe_div(a, b):
    δοκιμή:
        βεβαίωση b != 0
        επιστροφή a / b
    εξαίρεση AssertionError:
        επιστροφή Κανένα
    τελικά:
        παράλειψη


κλάση Accumulator:
    συνάρτηση __init__(self):
        self.total = 0

    συνάρτηση add(self, amount):
        self.total += amount

    συνάρτηση get(self):
        επιστροφή self.total


κλάση Section:
    συνάρτηση __enter__(self):
        επιστροφή self

    συνάρτηση __exit__(self, exc_type, exc, traceback):
        επιστροφή Ψευδές


συνάρτηση register(name):
    καθολικό registry
    registry[name] = Αληθές


συνάρτηση outer():
    count = 0

    συνάρτηση inner():
        μη_τοπικό count
        count += 1
        επιστροφή count

    επιστροφή inner


ασύγχρονο συνάρτηση report(value):
    αναμονή asyncio.sleep(0)
    αν value είναι Κανένα ή όχι value:
        επιστροφή "empty"
    αλλιώς_αν value > 10 και value % 2 == 0:
        επιστροφή "big even"
    αλλιώς:
        επιστροφή "other"


συνάρτηση main():
    values = fib(LIMIT)
    counter = Counter(values)
    acc = Accumulator()
    με Section():
        για value σε evens(values):
            acc.add(value)
    double = λάμβδα x: x * 2
    squares = [double(v) για v σε values[:4]]
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
    διαγραφή registry["fib"]
    print("clean", "fib" όχι σε registry)


αν Αληθές:
    main()
