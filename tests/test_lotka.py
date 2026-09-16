import hgscomp

"""
Known solution structure of Lotka-Volterra model gives us test cases to check correctness against:

Equillibrium points of lotak volterra equations:
x*,y* = (0, 0)
x*,y* = (gamma/delta, alpha/beta)

For (x0=0, y0>0): y = y0 exp(-gamma t)
For (x0>0, y0=0): x = x0 exp(alpha t)
so if one species is 0, the other follows an exponential with the birth rate alpha or death rate gamma, respectively.

For all initials (x0 > 0, y0 > 0) we have stable oscillations around x*,y* = (gamma/delta, alpha/beta).

So if the model is initialized to the fixpoint, they should stay there forever,
and if not, they should oscilater forever.
"""
