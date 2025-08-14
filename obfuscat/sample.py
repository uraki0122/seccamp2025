# 難読化対象となるPythonコード
def greet(name):
    if len(name) > 5:
        print("^^")
    else:
        print("Hello World")

def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def encode_message(message):
    encoded = ""
    for c in message:
        encoded += chr(ord(c) + 3)
    return encoded

def main():
    user = "Alice"
    greet(user)

    number = 5
    fact = factorial(number)
    print(f"The factorial of {number} is {fact}")

    secret = "TopSecret"
    encoded = encode_message(secret)
    print(f"Encoded message: {encoded}")

if __name__ == "__main__":
    main()
