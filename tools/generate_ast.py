import sys


def main(args):
    if len(args) != 1:
        print("Usage: python generate_ast.py <output directory>")
        sys.exit(1)

    (output_dir,) = args

    define_ast(
        output_dir,
        "Expr",
        [
            "Assign | name: Token, value: Expr",
            "Binary | left: Expr, operator: Token, right: Expr",
            "Call | callee: Expr, paren: Token, args: list[Expr]",
            "Get | obj: Expr, name: Token",
            "Grouping | expression: Expr",
            "Literal | value",
            "Logical | left: Expr, operator: Token, right: Expr",
            "Set | obj: Expr, name: Token, value: Expr",
            "This | keyword: Token",
            "Unary | operator: Token, right: Expr",
            "Variable | name: Token",
        ],
        ["from token_ import Token"],
    )

    define_ast(
        output_dir,
        "Stmt",
        [
            "Block | statements: list[Stmt]",
            'Class | name: Token, methods: list["Function"]',
            "Expression | expression: Expr",
            "Function | name: Token, params: list[Token], body: list[Stmt]",
            "If | condition: Expr, then_branch: Stmt, else_branch: Stmt | None",
            "Print | expression: Expr",
            "Return | keyword: Token, val: Expr | None",
            "Var | name: Token, initializer: Expr | None",
            "While | condition: Expr, body: Stmt",
        ],
        ["from expr import Expr", "from token_ import Token"],
    )


def define_ast(output_dir, base_name, types, extra_imports=None):
    path = output_dir + "/" + base_name.lower() + ".py"
    output_file = open(path, "w", encoding="UTF-8")

    define_imports(output_file, extra_imports)
    define_visitor(output_file, base_name, types)
    define_base_class(output_file, base_name)

    # the AST classes
    for type in types:
        class_name = type.split("|", 1)[0].strip()
        fields = type.split("|", 1)[1].strip()
        define_type(output_file, base_name, class_name, fields)

    output_file.close()


def define_base_class(output_file, base_name):
    output_file.write(f"class {base_name}(ABC):\n")
    output_file.write("    @abstractmethod\n")
    output_file.write("    def accept(self, visitor: Visitor[V]) -> V:\n")
    output_file.write("        ...\n")


def define_imports(output_file, extra_imports):
    output_file.write("from abc import ABC, abstractmethod\n")
    output_file.write("from typing import Generic, TypeVar\n\n")
    for imprt in extra_imports:
        output_file.write(imprt + "\n")
    output_file.write("\n")


def define_visitor(output_file, base_name, types):
    output_file.write('V = TypeVar("V")\n\n\n')
    output_file.write("class Visitor(ABC, Generic[V]):\n")

    for type in types:
        type_name = type.split("|")[0].strip()
        output_file.write("    @abstractmethod\n")
        output_file.write(
            f"    def visit_{type_name.lower()}_{base_name.lower()}"
            f'(self, {base_name.lower()}: "{type_name}") -> V:\n'
        )
        output_file.write("        ...\n\n")

    output_file.write("\n")


def define_type(output_file, base_name, class_name, field_list):
    output_file.write("\n\n")
    output_file.write(f"class {class_name}({base_name}):\n")
    output_file.write(f"    def __init__(self, {field_list}):\n")

    # Store parameters in fields
    fields = field_list.split(", ")
    for field in fields:
        name = field.strip()
        output_file.write(f"        self.{name} = {name.split(':')[0]}\n")
    output_file.write("\n")

    # Visitor Pattern
    output_file.write("    def accept(self, visitor: Visitor):\n")
    output_file.write(
        f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n"
    )


if __name__ == "__main__":
    main(sys.argv[1:])
