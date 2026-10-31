funkcja classify(n):
    jeśli n % 15 == 0:
        zwróć "FizzBuzz"
    inaczej_jeśli n % 3 == 0:
        zwróć "Fizz"
    inaczej_jeśli n % 5 == 0:
        zwróć "Buzz"
    inaczej:
        zwróć str(n)

dla n w range(1, 16):
    print(classify(n))
