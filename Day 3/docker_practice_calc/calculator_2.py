import math

class Calculator:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def add(self):
        return self.a + self.b
    
    def subtract(self):
        return self.a - self.b

    def divide(self):
        return self.a / self.b
    
    def multiply(self):
        return self.a * self.b
    
    def sqrt(self):
        return math.sqrt(self.c)

if __name__ == "__main__":
    myCalc = Calculator(a=3, b=5, c=435)
    print(myCalc.add())
    print(myCalc.subtract())
    print(myCalc.divide())
    print(myCalc.multiply())
    print(myCalc.sqrt())