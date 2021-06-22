## Piping

Based on the [survey] we had previously, to port `dplyr` to python, given

```python
df >> select(...)
```
we need to turn this `select(...)` into `select(df, ...)`. But `select(...)` gets executed before python knows the data `df` on the left side of the piping sign (`>>`).

Instead of letting python evaluate the real call of the verb (with the data), we could let `select(...)` returns an object that holds the arguments and other related information that are needed for the real call to be executed. The execution should happen right after the data is piped in.

This could be implemented by method `__rrshift__(self, data)`, where we could put the data as the first argument of the verb and then evaluate it.

The following example implements the idea:

```python
class Verb:
    """Works as a decorator to turn verb functions as Verb objects"""
    def __init__(self, func):
        self.func = func
        self.args = self.kwargs = None

    def __call__(self, *args, **kwargs):
        """When python sees `select(...)` in `df >> select(...)`"""
        self.args = args
        self.kwargs = kwargs
        return self

    def __rrshift__(self, data):
        """When python sees `df >>`"""
        # put data as the first argument of func
        return self.func(data, *self.args, **self.kwargs)

@Verb
def select(df, *columns):
    """Select columns from df"""
    return df[list(columns)]
```

```python
from datar.datasets import iris
iris >> select('Species')

#        Species
#       <object>
# 0       setosa
# 1       setosa
# 2       setosa
# 3       setosa
# ..         ...
# 4       setosa
# 145  virginica
# 146  virginica
# 147  virginica
# 148  virginica
# 149  virginica

# [150 rows x 1 columns]
```

## Normal calling

But can do we normal calling as `dplyr` does:

```python
select(iris, 'Species')
# <__main__.Verb at 0x7f6f5676d5d0>
# but expect the Species series
```

The problem is that this only triggers `__call__()` but not `__rrshift__()`. A solution is to trigger `__rrshift__()` inside `__call__()` in this situation. But we definitely don't want it to be triggered twice in `df >> select(...)`. Then how do we know if there is `df >>` before the call inside `select(...)`?

There is a way. As when python executes `select(...)`, the source code has already been written. So we can look up the AST tree to see if there is a `>>` (`BinOp/RShift`) node:

```python
import ast
import sys
from executing import Source

def is_piping():
    # need to skip this function
    frame = sys._getframe(2)
    # executing is a package to accurately detect nodes
    node = Source.executing(frame).node
    parent = getattr(node, 'parent', None)
    return (
        parent and
        isinstance(parent, ast.BinOp) and
        isinstance(parent.op, ast.RShift)
    )
```

The use it in `Verb.__call__()`:
```python
def __call__(self, *args, **kwargs):
    if is_piping(): # do the piping
        self.args = args
        self.kwargs = kwargs
        return self
    # do the normal call
    return args[0] >> self(*args[1:], **kwargs)
```

Now both `iris >> select('Species')` and `select(iris, 'Species')` work.


[1]: https://pwwang.github.io/datar-blog/efforts.html
