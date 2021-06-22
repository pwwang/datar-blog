
## Function calls as verb arguments

What if we want to do:

```python
iris >> mutate(mean_sepal_length=mean(f.Sepal_Length))
```

`f.Sepal_Length` and `f.Petal_Length` refer to two columns in `iris`. We need to defer the evaluation of the arguments, too, as we did for the verbs.

To retrieve the series in the data, we need to let `f.Sepal_Length` to be evaluated when a data frame is available:

```python
class Symbolic:
    def __getattr__(self, name):
        self.name = name
        return self

    def _eval(self, data):
        return data[self.name]

```

Similarly, when python sees `mean(f.Sepal_Length)`, it gets evaluated. But python hasn't seen the data yet. So the expression needs to be evaluated later, inside `Verb.__rrshift__()`. This needs us to turn the function `mean` into `Verb`-like, but not exactly a `Verb`, because a verb takes data as the first argument but the function may or may not.

Ask the verb to evaluate the arguments with the data:
```python

class Verb:
    # ...

    # Evaluate args and kwargs in verb
    def __rrshift__(self, data):
        args = eval_args(args, data)
        kwargs = eval_kwargs(kwargs, data)
        return self.func(data, *args, **kwargs)

eval_args = lambda args, data: (
    arg._eval(data) if isinstance(arg, (Symbolic, Func)) else arg
    for arg in args
)

eval_kwargs = lambda kwargs, data: {
    key: (val._eval(data) if isinstance(val, (Symbolic, Func)) else arg)
    for key, val in kwargs.items()
}
```

Define the function:
```
class Func(Verb):

    def _eval(self, data):
        # evaluate my args/kwargs too
        args = eval_args(args, data)
        kwargs = eval_kwargs(kwargs, data)
        return self.func(*args, **kwargs)

@Func
def mean(series):
    return series.mean()
```

## Operators as verb arguments

Operators in python are actually functions, too. For example:

```python
import operator

a = b = 1
a + b # 2

operator.add(a, b) # 2
```

Then we are able to turn the operators into function in:
```python
class Symbolic:

    def __add__(self, other):
        return Func(operator.add)(self, other)
```
