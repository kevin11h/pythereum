# pythereum

Simple blockchain based cryptocurrency that can transact coins and store
python based code.

This is for a school project. Should not be used anywhere (unless you really want to)

### Requirements for creating a contract
- contract must include a `main` function
- all state variables should be declared outside of the contract
- main functions should return `state(),printed` at the bottom
Example:
```python3
def main():
	# Your code goes here

	return state(), printed
```
- Failing to return the correct arguments will result in the state not being updated

### Other contract notes:
- `import` statements are disallowed
- `exec` / `eval` functions are disallowed
- `range` function is limited to stop limit of 1000
- strings cannot be converted to lists or tuples `lst = list("hello")`

Please see the sample contracts to get a better idea
