определить classify(n):
    если n % 15 == 0:
        вернуть "FizzBuzz"
    иначе_если n % 3 == 0:
        вернуть "Fizz"
    иначе_если n % 5 == 0:
        вернуть "Buzz"
    иначе:
        вернуть str(n)

для n в range(1, 16):
    print(classify(n))
