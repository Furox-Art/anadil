functie classify(n):
    indien n % 15 == 0:
        retourneer "FizzBuzz"
    anders_als n % 3 == 0:
        retourneer "Fizz"
    anders_als n % 5 == 0:
        retourneer "Buzz"
    anders:
        retourneer str(n)

voor n in range(1, 16):
    print(classify(n))
