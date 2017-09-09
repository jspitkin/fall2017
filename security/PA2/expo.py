""" jsp sept 8 2017 """

def exponentiate(m: int, d: int, n: int) -> int:
    """ Exponentiates big numbers modulo n

        Args:
            m - base
            d - exponent
            n - modulo
    """
    result = 1
    exponent_binary = "{0:b}".format(d)
    for bit in exponent_binary:
        result = result * result
        if bit == '1':
            result = result * m
        result = result % n
    return result