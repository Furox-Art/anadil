συνάρτηση classify(n):
    αν n % 15 == 0:
        επιστροφή "FizzBuzz"
    αλλιώς_αν n % 3 == 0:
        επιστροφή "Fizz"
    αλλιώς_αν n % 5 == 0:
        επιστροφή "Buzz"
    αλλιώς:
        επιστροφή str(n)

για n σε range(1, 16):
    print(classify(n))
