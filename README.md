# LoxPy

An implementation of **jlox** from part II of [Crafting Interpreters](https://www.craftinginterpreters.com/), written in python.

## Requiremnts

- Python3.10 or higher

## Usage

After cloning the repository and navigating to the working directory:

```bash
git clone https://github.com/HETHAT/LoxPy
cd LoxPy
```

You can run the interpreter in prompt mode with:

```bash
python3 ./src/lox.py
```

To run a specific file, use:

```bash
python3 ./src/lox.py example.lox
```

Replace "example.lox" with the path to your Lox file.

## Example

```bash
$ python3 ./src/lox
> name = "Med";
> print "Hello, " + name;
Hello, Med
```

More examples available [here](/examples).
