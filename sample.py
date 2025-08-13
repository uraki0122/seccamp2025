class MyClass:
    def __init__(self, value):
        self.value = value

    def normal_method(self):
        print(f"Value is {self.value}")

    def __str__(self):
        return f"MyClass with value {self.value}"

def hello():
    print("Hello, world!")
#^^
def hoge():
    obj = MyClass(42)
    obj.normal_method()
    print(obj)
    hello()

if __name__ == "__main__":
    hoge()

