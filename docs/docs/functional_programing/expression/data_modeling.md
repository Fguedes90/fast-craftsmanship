# Data Modelling

Learn how to effectively model data types using Expression in Python with data-classes and tagged-unions.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from expression import case, tag, tagged_union

# Simple data types using dataclasses
@dataclass
class Rectangle:
    width: float
    length: float

@dataclass
class Circle:
    radius: float

# Tagged union for type safety
@tagged_union
class Shape:
    tag: Literal["rectangle", "circle"] = tag()

    rectangle: Rectangle = case()
    circle: Circle = case()

    @staticmethod
    def Rectangle(width: float, length: float) -> Shape:
        return Shape(rectangle=Rectangle(width, length))

    @staticmethod
    def Circle(radius: float) -> Shape:
        return Shape(circle=Circle(radius))

# Using pattern matching with tagged unions
def calculate_area(shape: Shape) -> float:
    match shape:
        case Shape(tag="rectangle", rectangle=rect):
            return rect.width * rect.length
        case Shape(tag="circle", circle=circ):
            return 3.14 * circ.radius ** 2
        case _:
            raise ValueError("Unknown shape")

# Example usage
rect = Shape.Rectangle(width=10, length=5)
circle = Shape.Circle(radius=3)

print(f"Rectangle area: {calculate_area(rect)}")
print(f"Circle area: {calculate_area(circle)}")
```

This example demonstrates:
1. Creating simple data types with `@dataclass`
2. Defining tagged unions with `@tagged_union`
3. Using pattern matching for type-safe operations
4. Static factory methods for constructing union cases

Tagged unions provide better type safety than regular unions and support nested structures. Each case in a tagged union produces the same type, making them ideal for modeling domain-specific data structures.
