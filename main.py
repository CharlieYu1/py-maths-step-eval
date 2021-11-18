import numbers
from fractions import Fraction
from decimal import Decimal


def fraction_new_str_method(f):
    if f < 0:
        return '-' + repr(-f)
    else:
        return repr(f)


Fraction.__str__ = fraction_new_str_method


class Expression:
    PRIORITY = (('^',), ('*', '/'), ('+', '-'))
    MAX_EVALUATIONS = 50000

    def __init__(self, *args):
        if type(args[0]) == list:
            self._elements = args[0]
        else:
            self._elements = list(args)

    def __eq__(self, other):
        if type(other) is not Expression:
            return False
        self_elem = self.get_elements()
        other_elem = self.get_elements()
        if len(self_elem) != len(other_elem):
            return False
        n = len(self_elem)
        return all(self_elem[i] == other_elem[i] for i in range(n))

    def is_done(self):
        # check whether expression has finished evaluation
        return len(self._elements) == 1

    def eval_once(self):
        if self.is_done():
            raise StopIteration # finished_evaluation, now just a number

        # find any brackets expressions
        for i, element in enumerate(self._elements):
            if type(element) is Expression:
                try:
                    element.eval_once()
                    return
                except StopIteration:
                    self._elements[i] = element.get_elements()[0]

        i = self.find_top_priority_operator_pos()
        to_eval = self._elements[i-1:i+2]
        self._elements = self._elements[:i-1] + [self._eval(self._elements[i-1:i+2])] + self._elements[i+2:]

    def eval_full(self):
        for _ in range(self.MAX_EVALUATIONS): # stop the iteration in case of infinite loop
            if self.is_done():
                return self._elements[0]
            else:
                self.eval_once()
        raise RuntimeError('maximum number of evaluations reached')

    def print_full_steps(self):
        print(self.__repr__())
        for _ in range(self.MAX_EVALUATIONS): # stop the iteration in case of infinite loop
            if self.is_done():
                return
            else:
                self.eval_once()
                print('=' + self.__repr__())
        raise RuntimeError('maximum number of evaluations reached')

    def to_fraction_expression(self):
        for i, element in enumerate(self._elements):
            if type(element) is Expression:
                element.to_fraction_expression()
            if type(element) is Decimal:
                self._elements[i] = Fraction(element)

    def to_decimal_expression(self):
        for i, element in enumerate(self._elements):
            if type(element) is Expression:
                element.to_decimal_expression()
            if type(element) is Fraction:
                self._elements[i] = Decimal(element.numerator) / Decimal(element.denominator)

    def __repr__(self):
        if self.is_done():
            return str(self._elements[0])
        output_str = ''
        for e in self._elements:
            if type(e) is not Expression:
                try:
                    if float(e) < 0:
                        output_str += '(' + str(e) + ')'
                    else:
                        output_str += str(e)
                except:
                    output_str += str(e)
            elif e.is_done():
                if e.get_elements()[0] >= 0:
                    output_str += repr(e)
                else:
                    output_str += '(' + repr(e) + ')'
            else:
                output_str += '(' + repr(e) + ')'
        return output_str

    def get_elements(self):
        return self._elements

    def find_top_priority_operator_pos(self):
        for ops in self.PRIORITY:
            if any(op in self._elements for op in ops):
                return min(self._elements.index(op) for op in ops if op in self._elements)

    @staticmethod
    def _eval(expr):
        a, op, b = expr
        if op == '+':
            return a + b
        if op == '-':
            return a - b
        if op == '*':
            return a * b
        if op == '/':
            if type(a) is int and type(b) is int:
                if a / b == a // b:
                    return a // b
                return Fraction(a) / Fraction(b)
            else:
                return a / b
        if op == '^':
            return a ** b



