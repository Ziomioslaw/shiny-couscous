from phply import phplex, phpast
from phply.phpparse import make_parser
import re
import os


def transform_message(value: str) -> str:
    lower_case_word_pattern = re.compile(r'[a-ząćęłńóśźż]\w+',re.UNICODE)
    upper_case_word_pattern = re.compile(r'[A-ZĄĆĘŁŃÓŚŹŻ]\w+',re.UNICODE)

    value = re.sub(lower_case_word_pattern, 'gimp', value)
    value = re.sub(upper_case_word_pattern, 'Gimp', value)

    return value


def raw_value_to_str(value):
    return str(value) if isinstance(value, int) else f"'{value}'"


def arrayOffset_to_str(offset):
    return f"{node_to_str(offset.node)}[{raw_value_to_str(offset.expr)}]"


def ternaryOp_to_str(node):
    return f"{node_to_str(node.expr)} ? {node_to_str(node.iftrue)} : {node_to_str(node.iffalse)}"


def binaryOp_to_str(node):
    return f"{node_to_str(node.left)} . {node_to_str(node.right)}"


def node_to_str(node):
    if isinstance(node, str):
        value = transform_message(str(node)).replace("'", "\\'")
        return f"'{value}'"
    elif isinstance(node, int):
        return str(node)
    elif isinstance(node, phpast.Constant):
        return node.name
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
    elif isinstance(node, phpast.IsSet):
        value = ', '.join(node_to_str(n) for n in node.nodes)
        return f"isset({value})"
    elif isinstance(node, phpast.FunctionCall):
        value = ', '.join(node_to_str(p.node) for p in node.params)
        return f"{node.name}({value})"
    elif isinstance(node, phpast.Array):
        return ', '.join(
                n.value if n.key == None else f'{n.key} => {node_to_str(n.value)}'
                for n in node.nodes
            )

    raise Exception(f"Unknown: {node}")


def translate_line(line):
    if isinstance(line, phpast.Assignment):
        return ''.join((
            arrayOffset_to_str(line.node) if isinstance(line.node, phpast.ArrayOffset) else line.node.name,
            ' = ',
            node_to_str(line.expr),
            ';'))
    elif isinstance(line, phpast.Global):
        return 'global ' + ', '.join(n.name for n in line.nodes) + ';'
    else:
        raise Exception(f"Unknown: {line}")


def translate_file(content, parser, lexer):
    yield '<?php'
    yield ''

    yield from (
        translate_line(line)
        for line in parser.parse(content, lexer=lexer)
        if not isinstance(line, phpast.InlineHTML)
    )


def remove_dictionary(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            os.remove(filepath)

        for dirname in dirnames:
            subdirectory = os.path.join(dirpath, dirname)
            remove_dictionary(subdirectory)

    os.rmdir(directory)


def list_files(in_directory, out_directory):
    for root, dirs, _ in os.walk(in_directory):
        for dir in dirs:
            source_dir = os.path.join(in_directory, dir)
            dest_dir = source_dir.replace(in_directory, out_directory)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)


    for root, _, files in os.walk(in_directory):
        for file in files:
            if not file.endswith('polish.php'):
                continue

            file_path = os.path.join(root, file)
            encoding = 'iso-8859-2' if 'backend' in root else 'utf-8'

            input_file = open(file_path, 'rt', encoding=encoding)
            input = input_file.read()
            input_file.close()

            parser = make_parser()
            lexer = phplex.lexer.clone()
            output = '\n'.join(translate_file(input, parser, lexer))

            output_file = open(os.path.join(root.replace(in_directory, out_directory), file), 'wt', encoding=encoding)
            output_file.write(output)
            output_file.close()


remove_dictionary('output')
list_files('languages', 'output')
