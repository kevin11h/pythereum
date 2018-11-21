# pythereum

Simple blockchain based cryptocurrency that can transact coins and store
python based code.

This is for a school project. Should not be used anywhere (unless you really want to)

### Few notes on contracts:
The following safe builtins are available:
- None
- False
- True
- abs
- bool
- callable
- chr
- complex
- divmod
- float
- hash
- hex
- id
- int
- isinstance
- issubclass
- len
- oct
- ord
- pow
- range
- repr
- round
- slice
- str
- tuple
- zip

The following custom builtins are available:
- sqrt      (alias for math.sqrt)
- ceil      (math.ceil)
- floor     (math.floor)
- factorial (math.factorial)
- gcd       (math.gcd)
- log       (math.log)
- pow       (math.pow)
- sin       (math.sin)
- asin      (math.asin)
- cos       (math.cos)
- acos      (math.acos)
- tan       (math.tan)
- atan      (math.atan)
- pi        (math.pi)
- random    (random.random)
- randint   (random.randint)
- randrange (random.randrange)
- choice    (random.choice)
- choices   (random.choices)
- shuffle   (random.shuffle)
- sample    (random.sample)

Other notes:
- `import` statements are disallowed
- `exec` / `eval` functions are disallowed
- `range` function is limited to stop limit of 1000
- strings cannot be converted to lists or tuples (limited)
```python3
# The following code will fail
lst = list("hello")
```

- any builtins function not listed above is disallowed

Please see the sample contracts to get a better idea
