"""
Creating an interpreter in Python

Author:
Aviv Filber - 206360257
"""


import ast
import math
from functools import reduce

class Interpreter:
  """
  This interpreter can handle basic arithmetic operations, comparisons,
  variable assignments, conditionals, and some built-in functions.
  """
  def __init__(self):
    """_summary_
    Initialization with empty variables dictionary and a dispatch dictionary for the operations
    """
    # Variables dict
    self.variables = {}
    # Binary Ops dict
    self.dispatch = {
      #Basic aritmathematcs ops
      ast.Add: lambda x, y: x + y,
      ast.Sub: lambda x, y: x - y,
      ast.Mult: lambda x, y: x * y,
      ast.Div: lambda x, y: x / y,
      #Comparisons
      ast.Gt: lambda x, y: x > y,
      ast.Lt: lambda x, y: x < y,
      ast.Eq: lambda x, y: x == y,
      ast.GtE: lambda x, y: x >= y,
      ast.LtE: lambda x, y: x <= y,
      ast.NotEq: lambda x, y: x != y,
      #Logical ops
      ast.And: lambda x, y: x and y,
      ast.Or: lambda x, y: x or y,
      #Advanced aritmathematcs ops
      'sqrt': math.sqrt,
      ast.Mod: lambda x, y: x % y,
      ast.Pow: lambda x, y: x ** y,
      ast.FloorDiv: lambda x, y: x // y,  
    }

  def eval(self, node):
    """
    Evaluate an AST node and return the result.
    Args:
      node ast.AST: The AST node to evaluate.
    Returns:
      The result of evaluating the node.
    Raises:
      TypeError: If the node type is not supported.
    """
    # Constants
    if isinstance(node, ast.Constant):
      return node.value
    
    # Variables Name
    elif isinstance(node, ast.Name):
      # Get the variable value from the variables dictionary
      return self.variables.get(node.id)
    
    # Unary Ops
    elif isinstance(node, ast.UnaryOp):
      op = node.op
      if isinstance(op, ast.USub):
        return -self.eval(node.operand)
      elif isinstance(op, ast.UAdd):
        return +self.eval(node.operand)
      elif isinstance(op, ast.Not):
        return not self.eval(node.operand)
      
    # Binary Operations
    elif isinstance(node, ast.BinOp):
      # Get the right operation from the dispatch dict and apply him on the operands
      return self.dispatch[type(node.op)](
          self.eval(node.left),
          self.eval(node.right))
      
    # Boolean Operations (and, or)
    elif isinstance(node, ast.BoolOp):
      #  Make a list of the values in the node 
      # and then use reducer function with the right function from dispatch dict on the values  
      values = [self.eval(value) for value in node.values]
      return reduce(self.dispatch[type(node.op)], values)

    # Comparison
    elif isinstance(node, ast.Compare):
      # Compare between the left and right expressions  using the right dispatch function from the dict
      left = self.eval(node.left)
      for op, right in zip(node.ops, node.comparators):
        if not self.dispatch[type(op)](left, self.eval(right)):
          return False
        left = self.eval(right)
      return True
    
    # Assignment
    elif isinstance(node, ast.Assign):
      value = self.eval(node.value)
      for target in node.targets:
        self.assign(target, value)
      return value
    
    # If-statements
    elif isinstance(node, ast.If):
      if self.eval(node.test):
        return self.eval_body(node.body)
      elif node.orelse:
        return self.eval_body(node.orelse)
    
    # For loops
    elif isinstance(node, ast.For):
      iterable = self.eval(node.iter)
      for item in iterable:
        self.variables[node.target.id] = item
        self.eval_body(node.body)
      return None
    
    # While loop
    elif isinstance(node, ast.While):
      while self.eval(node.test):
          self.eval_body(node.body)
          
    # Attribute
    elif isinstance(node, ast.Attribute):
      value = self.eval(node.value)
      return getattr(value, node.attr)
    
    # Callables
    elif isinstance(node, ast.Call):
      func = self.eval(node.func)
      args = [self.eval(arg) for arg in node.args]
      return func(*args)
    
    # Lists
    elif isinstance(node, ast.List):
      return [self.eval(elt) for elt in node.elts]
    
    # Tuples
    elif isinstance(node, ast.Tuple):
      return tuple(self.eval(elt) for elt in node.elts)
    
    # Dictionaries
    elif isinstance(node, ast.Dict):
      return {self.eval(key): self.eval(value) for key, value in zip(node.keys, node.values)}
    
    # Subscript
    elif isinstance(node, ast.Subscript):
      value = self.eval(node.value)
      
      if isinstance(node.slice, ast.Index):   
        index = self.eval(node.slice.value)
        
      elif isinstance(node.slice, ast.Slice):
        lower = self.eval(node.slice.lower) if node.slice.lower else None
        upper = self.eval(node.slice.upper) if node.slice.upper else None
        step = self.eval(node.slice.step) if node.slice.step else None
        index = slice(lower, upper, step)
      else:
        index = self.eval(node.slice)
      return value[index]
      
    # Slices 
    elif isinstance(node, ast.Slice):
      lower = self.eval(node.lower) if node.lower else None
      upper = self.eval(node.upper) if node.upper else None
      step = self.eval(node.step) if node.step else None
      return slice(lower, upper, step)
    
    # AugAssign (+=, -=, *=, /=)
    elif isinstance(node, ast.AugAssign):
      target = node.target
      op = type(node.op)
      value = self.eval(node.value)
      
      if isinstance(target, ast.Name):
        current_value = self.variables.get(target.id, 0)
        new_value = self.dispatch[op](current_value, value)
        self.variables[target.id] = new_value
        return new_value
      
      elif isinstance(target, ast.Subscript):
        obj = self.eval(target.value)
        if isinstance(target.slice, ast.Index):
          index = self.eval(target.slice.value)
        else:
          index = self.eval(target.slice)
        current_value = obj[index]
        new_value = self.dispatch[op](current_value, value)
        obj[index] = new_value
        return new_value
      else:
        raise TypeError(f"Unsupported augmented assignment target: {type(target)}")
    
    # Expressions
    elif isinstance(node, ast.Expr):
      # evaluate values of expressions
      return self.eval(node.value)
    
    else:
      raise TypeError(f"Unsupported node type: {type(node)}")
 
  def assign(self, target, value):
    """
    Assign a value to a target (variable or subscript).
    Args:
      target ast.AST: The target of the assignment.
      value: The value to assign.

    Raises:
      TypeError: If the assignment target is not supported.
    """
    # Name variable
    if isinstance(target, ast.Name):
      self.variables[target.id] = value
    # Subscript
    elif isinstance(target, ast.Subscript):
      obj = self.eval(target.value)
      if isinstance(target.slice, ast.Index):
          index = self.eval(target.slice.value)
      elif isinstance(target.slice, ast.Slice):
        lower = self.eval(target.slice.lower) if target.slice.lower else None
        upper = self.eval(target.slice.upper) if target.slice.upper else None
        step = self.eval(target.slice.step) if target.slice.step else None
        index = slice(lower, upper, step)
      else:
        index = self.eval(target.slice)
      obj[index] = value
    else:
      raise TypeError(f"Unsupported assignment target: {type(target)}")
 
  def eval_body(self, body):
    """
    Evaluate a body of statements and return the result of the last one.
    Args:
      body (list): A list of AST nodes representing statements.
    Returns:
      The result of the last statement in the body.
    """
    result = None
    for node in body:
      result = self.eval(node)
    return result

  def parse_and_eval(self, code):
    """
    Parse a string of code and evaluate it.
    Args:
      code (str): A string of Python code.
    Returns:
      The result of evaluating the code.
    """
    tree = ast.parse(code)
    return self.eval_body(tree.body)

  def repl(self):
    """
    Start a Read-Eval-Print Loop for interactive use of the interpreter.
    """
    while True:
      try:
        user_input = input('> ')
        if user_input.lower() == 'exit':
          break
        result = self.parse_and_eval(user_input)
        if result is not None:
          print(result)
      except Exception as e:
        print(f"Error: {e}")

# Add built-in functions
interpreter = Interpreter()
interpreter.variables.update({
  'math': math,
  'print': print,
  'len': len,
  'str': str,
  'int': int,
  'float': float,
  'list': list,
  'tuple': tuple,
  'dict': dict,
  'bool': bool,
  'range': range,
  'sum': sum,
  'min': min,
  'max': max,
})

if __name__ == "__main__":
  example_code = """
# Basic arithmetic and variable assignment
x = 10
y = 5
z = x + y * 2

# Unary operations :
print("Not true is :", not True)

# Comparison and conditional statements:
if z > 20:
  print("z is greater than 20")
else:
  print("z is not greater than 20")

# Lists , list operations and for-loops:
numbers = [1, 2, 3, 4, 5]
squares = []
for num in numbers:
    squares.append(num ** 2)
print("Squares:", squares)

# While-loops:
current = 0
while current < 5 :
  print(current)
  current += 1 

# Dictionary:
person = {"name": "Alice", "age": 30}
print("Person:", person)

# Tuple:
coordinates = (10, 20)
print("Coordinates:", coordinates)

# String operations:
greeting = "Hello, " + person["name"] + "!"
print(greeting)

# Built-in functions:")
print("Length of squares:", len(squares))
print("Sum of squares:", sum(squares))

# Slicing:
print("First three squares:", squares[:3])

# Boolean operations:
is_adult = person["age"] >= 18 and person["name"] != ""
print("Is adult:", is_adult)

  """

  print("\nRunning example code:")
  interpreter.parse_and_eval(example_code)
  
  
  print("Entering REPL mode:")
  interpreter.repl()