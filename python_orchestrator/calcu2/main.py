import math

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

def integrate(f, a, b):
    h = (b - a) / 1000
    integral = 0
    for i in range(1000):
        integral += f(a + i * h)
    return integral * h

def derivative(f, x, h=0.0001):
    return (f(x + h) - f(x)) / h

# Test functions
print("Addition:", add(5, 3))
print("Subtraction:", subtract(5, 3))
print("Multiplication:", multiply(5, 3))
print("Division:", divide(5, 3))
print("Integration of x^2 from 0 to 1:", integrate(lambda x: x**2, 0, 1))
print("Derivative of sin(x) at x=pi/4:", derivative(math.sin, math.pi / 4))