import unittest
from calculator import Calculator

class TestOperations(unittest.TestCase):
    def test_sum(self):
        calc = Calculator(8,2)
        self.assertEqual(calc.add(), 10, "The answer was not 10")
    
    def test_subtract(self):
        calc = Calculator(8,2)
        self.assertEqual(calc.subtract(), 6, "The answer was not 6")

    def test_divide(self):
        calc = Calculator(8,2)
        self.assertEqual(calc.divide(), 4, "The answer was not 4")

    def test_multiply(self):
        calc = Calculator(8,2)
        self.assertEqual(calc.multiply(), 16, "The answer was not 16")

if __name__ == "__main__":
    unittest.main()