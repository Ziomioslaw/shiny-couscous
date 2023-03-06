from phply.phpparse import make_parser
from phply import phplex, phpast


def raw_value_to_str(value):
    return str(value) if isinstance(value, int) else f"'{value}'"


def arrayOffset_to_str(offset):
    return f"{offset.node.node.name}[{raw_value_to_str(offset.node.expr)}]"


# Parse the PHP code using phply's lexer and parser
parser = make_parser()
lexer = phplex.lexer.clone()

input_file = open('./languages/Errors.polish.php', 'rt')
input_lines = input_file.read()
input_file.close()

# Traverse the AST to extract variable assignments and function calls
for line in parser.parse(input_lines, lexer=lexer):
    print(arrayOffset_to_str(line), '=', line.expr)
