class Calculator:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self):
        return self.a + self.b
    
    def subtract(self):
        return self.a - self.b

    def divide(self):
        return self.a / self.b
    
    def multiply(self):
        return self.a * self.b

if __name__ == "__main__":
    myCalc = Calculator(a=3, b=5)
    print(myCalc.add())
    print(myCalc.subtract())
    print(myCalc.divide())
    print(myCalc.multiply())