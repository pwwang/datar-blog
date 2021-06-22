## `dplyr` vs `pandas`

Why people have made such efforts to port `dplyr` to python, include me?

Well, one of the biggest reasons is that `dplyr` has much cleaner APIs.

`pandas` has some comparisons between these two with some simple operations on
data frames. See its documentation [here]. Check out the left column of the tables, you may find the almost every statement in `R`/`dplyr` is shorter.

If things go complicated, say, filter a data frame with values from 2 columns:

```python
>>> iris[(iris['Species'] == 'setosa') & (iris['Petal_Length'] > 1.5)]
    Sepal_Length  Sepal_Width  Petal_Length  Petal_Width  Species
       <float64>    <float64>     <float64>    <float64> <object>
5            5.4          3.9           1.7          0.4   setosa
11           4.8          3.4           1.6          0.2   setosa
18           5.7          3.8           1.7          0.3   setosa
20           5.4          3.4           1.7          0.2   setosa
23           5.1          3.3           1.7          0.5   setosa
24           4.8          3.4           1.9          0.2   setosa
25           5.0          3.0           1.6          0.2   setosa
26           5.0          3.4           1.6          0.4   setosa
29           4.7          3.2           1.6          0.2   setosa
30           4.8          3.1           1.6          0.2   setosa
43           5.0          3.5           1.6          0.6   setosa
44           5.1          3.8           1.9          0.4   setosa
46           5.1          3.8           1.6          0.2   setosa
```

```r
r$> iris %>% filter(Species == 'setosa' & Petal.Length > 1.5)
   Sepal.Length Sepal.Width Petal.Length Petal.Width Species
1           5.4         3.9          1.7         0.4  setosa
2           4.8         3.4          1.6         0.2  setosa
3           5.7         3.8          1.7         0.3  setosa
4           5.4         3.4          1.7         0.2  setosa
5           5.1         3.3          1.7         0.5  setosa
6           4.8         3.4          1.9         0.2  setosa
7           5.0         3.0          1.6         0.2  setosa
8           5.0         3.4          1.6         0.4  setosa
9           4.7         3.2          1.6         0.2  setosa
10          4.8         3.1          1.6         0.2  setosa
11          5.0         3.5          1.6         0.6  setosa
12          5.1         3.8          1.9         0.4  setosa
13          5.1         3.8          1.6         0.2  setosa
```

What if you have even more columns and operations involved?

There are some other in-depth comparisons:

- [Python’s Pandas vs. R’s dplyr – Which Is The Best Data Analysis Library][2]
-

## Efforts been made

In order to turn this in R:

```R
iris %>% filter(Species == 'setosa')
```

to this in python:
```python
iris >> filter(Species == 'setosa')
```

efforts have been made to defer the execution of `filter(Species == 'setosa')`. Since it gets evaluated when python sees it right away, but we need the data (`iris`) to be piped in to evaluate it.

### `suiba`

`suiba` creates a `Pipeable` object for the verb, and attach `__rshift__` method to the `DataFrame` class or other types.

To defer the evaluation of the arguments in the verbs, `suiba` creates a `sui` expression that is initiated with a `Symbolic` object (named `_` by default).

`suiba` is powerful and potential to port more related functionalities from `R` packages, and has great support fro remote tables. It is also attracting attention in the community.

`suiba` has ported a couple verbs from `dplyr`, including:

- `select()` - keep certain columns of data.
- `filter()` - keep certain rows of data.
- `mutate()` - create or modify an existing column of data.
- `summarize()` - reduce one or more columns down to a single number.
- `arrange()` - reorder the rows of data.

that are most commonly used in data processing. But not all verbs and other helper functions are ported.

### `dfply`

[`dfply`][3] wraps verbs by a `pipe` decorator to turn them into a pipeable object (with `__rshift__()` and `__rrshift__()` defined). The arguments of the verbs are pre-compiled as `Intention` objects. Later on the data is piped in and the `Intention` objects get evaluated.

### `plydata`

[`plydata`][4] has very similar ideas as `dfply` does. It uses `metaclass` to make verbs pipeable. Instead of pre-compile the arguments into objects, `plydata` uses raw strings as the arguments. The magic for evaluation is to capture the environment from call stacks, by `EvalEnvironment.capture()`.

### `dplython`

[`dplython`][5] subclasses `pandas`' `DataFrame` class to `DplyFrame`, which enables piping (`__rshift__`) and some grouping functions by itself to easily implement `dplyr`'s `group_by` and related functions. The `Later` objects have carried the information for the function to be evaluated later. The wrapper around it `DelayedFunction` enables external functions to be registered as verbs.

## Insparitions/Considerations

- Keep `DataFrame` class clean

    In order to implement the piping, some of the packages have subclassed, or injected methods to `pandas`' `DataFrame` class, but it may not be necessary.
<!--
- Thread-safety

    None of the packages have seriously considered this issue, especially for those turn verbs into pipeable objects. Since piping in data and deferred evaluation of the verb calls are two different steps, it may cause unexpected results when run in multithreading environment.
-->
- Support of verb calling as regular function

    Some packages may be too focused on the piping implementation that regular verb calling is also supported in `dplyr`, as well as piping calling:

    ```R
    # legal
    df %>% select(a, b)
    # legal too
    select(df, a, b)
    ```

- Alignment with `dplyr` APIs

    Claiming port of `dplyr` in python, but not really following `dplyr`'s API design. Some packages even have their own verbs. This may scare users away as they may have to learn 3 sets of APIs: `dplyr`, `pandas` and the one created by the package.

[1]: https://pandas.pydata.org/pandas-docs/stable/getting_started/comparison/comparison_with_r.html#quick-reference
[2]: https://appsilon.com/pandas-vs-dplyr/
[3]: https://github.com/kieferk/dfply
[4]: https://github.com/has2k1/plydata
[5]: https://github.com/dodger487/dplython
