from phply import phplex, phpast
from phply.phpparse import make_parser
import re


def transform_message(value: str) -> str:
    value = re.sub('[a-z]\w+', 'gimp', value)
    value = re.sub('[A-Z]\w+', 'Gimp', value)

    return value


def raw_value_to_str(value):
    return str(value) if isinstance(value, int) else f"'{value}'"


def arrayOffset_to_str(offset):
    return f"{offset.node.name}[{raw_value_to_str(offset.expr)}]"


def ternaryOp_to_str(node):
    return f"{node_to_str(node.expr)} ? {node_to_str(node.iftrue)} : {node_to_str(node.iffalse)}"


def binaryOp_to_str(node):
    return f"{node_to_str(node.left)} . {node_to_str(node.right)}"


def node_to_str(node):
    if isinstance(node, str):
        value = transform_message(str(node)).replace("'", "\\'")
        return f"'{value}'"
    if isinstance(node, int):
        return str(node)
    elif isinstance(node, phpast.Variable):
        return node.name
    elif isinstance(node, phpast.ArrayOffset):
        return arrayOffset_to_str(node)
    elif isinstance(node, phpast.BinaryOp):
        return binaryOp_to_str(node)
    elif isinstance(node, phpast.TernaryOp):
        return f"({ternaryOp_to_str(node)})"
    elif isinstance(node, phpast.Empty):
        return f"empty({node_to_str(node.expr)})"

    raise Exception(f"Unknown: {node}")


def translate_file(content):
    yield '<?php'
    yield ''

    yield from (
        ''.join((
                arrayOffset_to_str(line.node),
                ' = ',
                node_to_str(line.expr),
                ';'))
        for line in parser.parse(content, lexer=lexer)
    )


parser = make_parser()
lexer = phplex.lexer.clone()

input_file = open('./languages/Errors.polish.php', 'rt')
input = input_file.read()
input_file.close()

print('\n'.join(translate_file(input)))
