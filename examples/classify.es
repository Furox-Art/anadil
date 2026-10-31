función classify(n):
    si n % 15 == 0:
        devolver "FizzBuzz"
    sino_si n % 3 == 0:
        devolver "Fizz"
    sino_si n % 5 == 0:
        devolver "Buzz"
    sino:
        devolver str(n)

para n en range(1, 16):
    print(classify(n))
