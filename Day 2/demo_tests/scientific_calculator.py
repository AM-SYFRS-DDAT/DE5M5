from calculator import Calculator

#MyCalcv2 = Calculator(2,4)

#print(MyCalcv2.multiply())

class SciCalc(Calculator):
    def get_exp(self):
        return self.a**self.b
    
mySciCalc = SciCalc(a=2, b=3)
print(mySciCalc.get_exp())