import unittest
from main import Expression
import contextlib
from io import StringIO
from fractions import Fraction
from decimal import Decimal


class TestEvalMethods(unittest.TestCase):

    def test_simple_add(self):
        expr = Expression([1, '+', 2])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [3])
        with self.assertRaises(StopIteration) as context:
            expr.eval_once()

    def test_eq(self):
        expr1 = Expression([3])
        expr2 = Expression([3])
        self.assertEqual(expr1, expr2)

    def test_repr(self):
        expr = Expression([1, '+', -2, '*', Expression([-4, '+', 2]), '^', 3])
        self.assertEqual(expr.__repr__(), '1+(-2)*((-4)+2)^3')

    def test_add_and_multiply(self):
        expr = Expression([1, '+', -2, '*', 4])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [1, '+', -8])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [-7])
        with self.assertRaises(StopIteration) as context:
            expr.eval_once()

    def test_fractions(self):
        expr = Expression([2, '-', Fraction('11/4'), '/', Fraction('-7/3')])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [2, '-', Fraction('-33/28')])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [Fraction('89/28')])

    def test_decimal(self):
        expr = Expression([Decimal('0.8'), '^', 4, '/', Decimal('-3.1')])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [Decimal('0.4096'), '/', Decimal('-3.1')])
        expr.eval_once()
        self.assertAlmostEqual(expr.get_elements()[0], Decimal('-0.132129032258'))

    def test_to_fraction_expression(self):
        expr = Expression([Decimal('0.8'), '^', 4, '+', Decimal('-3.1')])
        expr.to_fraction_expression()
        self.assertEqual(expr.get_elements(), [Fraction('4/5'), '^', 4, '+', Fraction('-31/10')])

    def test_to_decimal_expression(self):
        expr = Expression([Fraction('4/5'), '^', 4, '+', Fraction('-31/10')])
        expr.to_decimal_expression()
        self.assertEqual(expr.get_elements(), [Decimal('0.8'), '^', 4, '+', Decimal('-3.1')])

    def test_mixed_four_operations(self):
        expr = Expression([2, '-', -2, '*', 4, '+', 3, '/', 6])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [2, '-', -8, '+', 3, '/', 6])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [2, '-', -8, '+', 0.5])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [10, '+', 0.5])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [10.5])

    def test_exponent(self):
        expr = Expression([2, '-', -2, '*', 4, '^', 3])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [2, '-', -2, '*', 64])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [2, '-', -128])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [130])

    def test_simple_brackets(self):
        expr = Expression([2, '*', Expression([1, '-', 7])])
        expr.eval_once()
        # assert result of bracket in -6
        self.assertEqual(expr.get_elements(), [2, '*', Expression([-6])])
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [-12])

    def test_more_brackets(self):
        expr = Expression([72, '/', Expression([2, '^', 3, '+', 1])])
        expr.eval_once()
        # assert result of bracket in -6
        self.assertEqual(expr.get_elements(), [72, '/', Expression([8, '+', 1])])
        expr.eval_once()
        expr.eval_once()
        self.assertEqual(expr.get_elements(), [8])

    def test_eval_full(self):
        expr = Expression([-63, '/', Expression([2, '^', 3, '+', 1]), '*', Expression([2, '-', 3, '/', 4])])
        self.assertEqual(expr.eval_full(), -8.75)

    def test_stdout(self):
        expr = Expression([-63, '/', Expression([2, '^', 3, '+', 1]), '*', Expression([2, '-', 3, '/', 4])])
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            expr.print_full_steps()
        output = temp_stdout.getvalue().strip()
        self.assertEqual(output.count('='), 6)
        self.assertEqual(output[-7:], '(35, 4)')


if __name__ == '__main__':
    unittest.main()