funktion classify(n):
    om n % 15 == 0:
        returnera "FizzBuzz"
    annars_om n % 3 == 0:
        returnera "Fizz"
    annars_om n % 5 == 0:
        returnera "Buzz"
    annars:
        returnera str(n)

för n i range(1, 16):
    print(classify(n))
