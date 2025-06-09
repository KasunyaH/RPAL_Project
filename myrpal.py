import sys
from parser.Parser import Parser
from lexer.lexer import tokenize

def get_file_content(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except:
        print("Error reading file")
        return None

def main():
    # check input
    if len(sys.argv) < 2:
        print("Need input file")
        return

    # get file and flags
    input_file = sys.argv[1]
    show_ast = '-ast' in sys.argv

    # read file
    code = get_file_content(input_file)
    if not code:
        return

    # get tokens
    tokens = tokenize(code)

    try:
        # make AST
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        if not ast_nodes:
            return

        # get AST strings
        string_ast = parser.convert_ast_to_string_ast()

        # show AST if needed
        if show_ast:
            for line in string_ast:
                print(line)
            return

        # For now, just print the AST
        print("Abstract Syntax Tree:")
        for line in string_ast:
            print(line)

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()
