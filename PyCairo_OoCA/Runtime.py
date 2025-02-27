#!/usr/bin/env python
import sympy as sp

# Define symbols for L and S
L, S = sp.symbols('L S')

# Define the expressions as given:
#n = 5 * L * S * (10*L*(0.5*L + S) * [10*L*(L+S)*(2*S*(L+S) + 1) + 1] + 1)
#m = L * S
#n = (L * S) + S*(S-1) + S First layer
#m = 5*L*(L+S) Second layer
ab = 5*L*(L + S)*(2*L*S + 2*S*(S - 1) + 2*S + 1) # First output
bc = 5*L*(0.5*L + S)*(10*L*(L + S) + 1)
cd = 5*L*S*(10*L*(0.5*L + S) + 1)
de = L*S*(10*L*S + 1)
# Compute the expression m*(2*n+1)
#m= 5*L*S
#m= L*S
#expr = m * (2 * n + 1)
expr = ab + bc + cd + de
# # Fully expand the expression
expanded_expr = sp.simplify(expr)

# Print out the original and the fully expanded expressions
#print("m(2n+1) =")
#sp.pprint(expr)
#print("\nFully expanded m(2n+1) =")
#sp.pprint(expanded_expr)

L = 25
S = 4
total = L * (25*L**3 + 110*(L**2)*S + 130*L*(S**2) + 7.5*L + 10*S**3 + 16*S)
#
print(total)
