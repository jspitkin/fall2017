""" 
    Jake Pitkin - u0891770
    CS - 6490 Fall 2017
    Programming Assignment #2
"""

def exponentiate(m, d, n):
    """ 
        Exponentiates big numbers modulo n

        Args:
            m - base
            d - exponent
            n - modulo
    """
    result = 1
    exponent_binary = "{0:b}".format(d)
    # Traverse from high-bit to low-bit
    for bit in exponent_binary:
        result = result * result
        if bit == '1':
            result = result * m
        result = result % n
    return result