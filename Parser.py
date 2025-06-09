from enum import Enum
from Lexer.lexical_analyzer import TokenType, MyToken

class NodeType(Enum):
    # Core nodes
    let = 1
    fcn_form = 2
    identifier = 3
    integer = 4
    string = 5
    # Control flow
    where = 6
    gamma = 7
    lambda_expr = 8
    tau = 9
    rec = 10
    # Operations
    aug = 11
    conditional = 12
    op_or = 13
    op_and = 14
    op_not = 15
    op_compare = 16
    op_plus = 17
    op_minus = 18
    op_neg = 19
    op_mul = 20
    op_div = 21
    op_pow = 22
    at = 23
    # Values
    true_value = 24
    false_value = 25
    nil = 26
    dummy = 27
    # Structure
    within = 28
    and_op = 29
    equal = 30
    comma = 31
    empty_params = 32

    def __str__(self):
        if self == NodeType.identifier:
            return "ID"
        elif self == NodeType.integer:
            return "INT"
        elif self == NodeType.string:
            return "STR"
        elif self == NodeType.true_value:
            return "TRUE_VALUE"
        elif self == NodeType.false_value:
            return "TRUE_VALUE"
        elif self == NodeType.nil:
            return "NIL"
        elif self == NodeType.dummy:
            return "dummy"
        else:
            return self.name.upper()

class Node:
    def __init__(self, node_type, value, children):
        self.type = node_type
        self.value = value
        self.no_of_children = children

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = []
        self.string_ast = []

    def parse(self):
        self.tokens.append(MyToken(TokenType.END_OF_TOKENS, ""))
        self.E()
        return self.ast if self.tokens[0].type == TokenType.END_OF_TOKENS else None

    def convert_ast_to_string_ast(self):
        dots, stack = "", []
        
        while self.ast:
            if not stack:
                node = self.ast.pop()
                if node.no_of_children == 0:
                    self.add_strings(dots, node)
                else:
                    stack.append(node)
            else:
                node = self.ast.pop()
                if node.no_of_children > 0:
                    stack.append(node)
                    dots += "."
                else:
                    stack.append(node)
                    dots += "."
                    while stack and stack[-1].no_of_children == 0:
                        self.add_strings(dots, stack.pop())
                        if stack:
                            dots = dots[:-1]
                            node = stack.pop()
                            node.no_of_children -= 1
                            stack.append(node)

        self.string_ast.reverse()
        return self.string_ast

    def add_strings(self, dots, node):
        if node.type in [NodeType.identifier, NodeType.integer, NodeType.string, 
                        NodeType.true_value, NodeType.false_value, NodeType.nil, NodeType.dummy]:
            self.string_ast.append(f"{dots}<{str(node.type)}:{node.value}>")
        elif node.type == NodeType.fcn_form:
            self.string_ast.append(f"{dots}function_form")
        else:
            self.string_ast.append(f"{dots}{node.value}")

    def consume_token(self, expected_value=None):
        if not self.tokens:
            raise SyntaxError("Unexpected end of input")
        token = self.tokens.pop(0)
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{token.value}'")
        return token

    def E(self):
        if not self.tokens:
            return

        token = self.tokens[0]
        if token.type == TokenType.KEYWORD:
            if token.value == "let":
                self.consume_token("let")
                self.D()
                self.consume_token("in")
                self.E()
                self.ast.append(Node(NodeType.let, "let", 2))
            elif token.value == "fn":
                self.consume_token("fn")
                n = 0
                while self.tokens and (self.tokens[0].type == TokenType.IDENTIFIER or self.tokens[0].value == "("):
                    self.Vb()
                    n += 1
                self.consume_token(".")
                self.E()
                self.ast.append(Node(NodeType.lambda_expr, "lambda", n + 1))
        else:
            self.Ew()

    def Ew(self):
        self.T()
        if self.tokens and self.tokens[0].value == "where":
            self.consume_token("where")
            self.Dr()
            self.ast.append(Node(NodeType.where, "where", 2))

    def T(self):
        self.Ta()
        n = 1
        while self.tokens and self.tokens[0].value == ",":
            self.consume_token(",")
            self.Ta()
            n += 1
        if n > 1:
            self.ast.append(Node(NodeType.tau, "tau", n))

    def Ta(self):
        self.Tc()
        while self.tokens and self.tokens[0].value == "aug":
            self.consume_token("aug")
            self.Tc()
            self.ast.append(Node(NodeType.aug, "aug", 2))

    def Tc(self):
        self.B()
        if self.tokens and self.tokens[0].value == "->":
            self.consume_token("->")
            self.Tc()
            self.consume_token("|")
            self.Tc()
            self.ast.append(Node(NodeType.conditional, "->", 3))

    def B(self):
        self.Bt()
        while self.tokens and self.tokens[0].value == "or":
            self.consume_token("or")
            self.Bt()
            self.ast.append(Node(NodeType.op_or, "or", 2))

    def Bt(self):
        self.Bs()
        while self.tokens and self.tokens[0].value == "&":
            self.consume_token("&")
            self.Bs()
            self.ast.append(Node(NodeType.op_and, "&", 2))

    def Bs(self):
        if self.tokens and self.tokens[0].value == "not":
            self.consume_token("not")
            self.Bp()
            self.ast.append(Node(NodeType.op_not, "not", 1))
        else:
            self.Bp()

    def Bp(self):
        self.A()
        token = self.tokens[0]
        if token.value in [">", ">=", "<", "<=", "gr", "ge", "ls", "le", "eq", "ne"]:
            self.consume_token(token.value)
            self.A()
            if token.value == ">":
                self.ast.append(Node(NodeType.op_compare, "gr", 2))
            elif token.value == ">=":
                self.ast.append(Node(NodeType.op_compare, "ge", 2))
            elif token.value == "<":
                self.ast.append(Node(NodeType.op_compare, "ls", 2))
            elif token.value == "<=":
                self.ast.append(Node(NodeType.op_compare, "le", 2))
            else:
                self.ast.append(Node(NodeType.op_compare, token.value, 2))

    def A(self):
        if self.tokens and self.tokens[0].value == "+":
            self.consume_token("+")
            self.At()
        elif self.tokens and self.tokens[0].value == "-":
            self.consume_token("-")
            self.At()
            self.ast.append(Node(NodeType.op_neg, "neg", 1))
        else:
            self.At()

        while self.tokens and self.tokens[0].value in {"+", "-"}:
            current_token = self.tokens[0]
            self.consume_token(current_token.value)
            self.At()
            if current_token.value == "+":
                self.ast.append(Node(NodeType.op_plus, "+", 2))
            else:
                self.ast.append(Node(NodeType.op_minus, "-", 2))

    def At(self):
        self.Af()
        while self.tokens and self.tokens[0].value in {"*", "/"}:
            current_token = self.tokens[0]
            self.consume_token(current_token.value)
            self.Af()
            if current_token.value == "*":
                self.ast.append(Node(NodeType.op_mul, "*", 2))
            else:
                self.ast.append(Node(NodeType.op_div, "/", 2))

    def Af(self):
        self.Ap()
        if self.tokens and self.tokens[0].value == "**":
            self.consume_token("**")
            self.Af()
            self.ast.append(Node(NodeType.op_pow, "**", 2))

    def Ap(self):
        self.R()
        while self.tokens and self.tokens[0].value == "@":
            
            if self.tokens[0].type != TokenType.IDENTIFIER:
                raise SyntaxError("Parsing error at Ap: IDENTIFIER EXPECTED")
            
            self.ast.append(Node(NodeType.identifier, self.tokens[0].value, 0))
            self.consume_token()
            
            self.R()
            self.ast.append(Node(NodeType.at, "@", 3))

    def R(self):
        self.Rn()
        while (self.tokens and self.tokens[0].type in [TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.STRING] or
            self.tokens[0].value in ["true", "false", "nil", "dummy"] or
            self.tokens[0].value == "("):
            
            self.Rn()
            self.ast.append(Node(NodeType.gamma, "gamma", 2))

    def Rn(self):
        token_type = self.tokens[0].type
        token_value = self.tokens[0].value

        if token_type == TokenType.IDENTIFIER:
            self.ast.append(Node(NodeType.identifier, token_value, 0))
            self.consume_token()
        elif token_type == TokenType.INTEGER:
            self.ast.append(Node(NodeType.integer, token_value, 0))
            self.consume_token()
        elif token_type == TokenType.STRING:
            self.ast.append(Node(NodeType.string, token_value, 0))
            self.consume_token()
        elif token_type == TokenType.KEYWORD:
            if token_value in ["true", "false", "nil", "dummy"]:
                node_type = {
                    "true": NodeType.true_value,
                    "false": NodeType.false_value,
                    "nil": NodeType.nil,
                    "dummy": NodeType.dummy
                }[token_value]
                self.ast.append(Node(node_type, token_value, 0))
                self.consume_token()
            else:
                raise SyntaxError("Parse Error at Rn: Unexpected KEYWORD")
        elif token_type == TokenType.PUNCTUATION:
            if token_value == "(":
                self.consume_token("(")
                self.E()
                self.consume_token(")")
            else:
                raise SyntaxError("Parsing error at Rn: Unexpected PUNCTUATION")
        else:
            raise SyntaxError(f"Unexpected token: {token_type}, {token_value}")

    def D(self):
        self.Da()
        if self.tokens and self.tokens[0].value == "within":
            self.consume_token("within")
            self.D()
            self.ast.append(Node(NodeType.within, "within", 2))

    def Da(self): 
        self.Dr()
        n = 1
        while self.tokens and self.tokens[0].value == "and":
            self.consume_token("and")
            self.Dr()
            n += 1
        if n > 1:
            self.ast.append(Node(NodeType.and_op, "and", n))

    def Dr(self):
        is_rec = False
        if self.tokens and self.tokens[0].value == "rec":
            self.consume_token("rec")
            is_rec = True
        self.Db()
        if is_rec:
            self.ast.append(Node(NodeType.rec, "rec", 1))

    def Db(self): 
        if self.tokens and self.tokens[0].type == TokenType.PUNCTUATION and self.tokens[0].value == "(":
            self.consume_token("(")
            self.D()
            if self.tokens[0].value != ")":
                raise SyntaxError("Parsing error at Db #1")
            self.consume_token()
        elif self.tokens and self.tokens[0].type == TokenType.IDENTIFIER:
            if self.tokens[1].value == "(" or self.tokens[1].type == TokenType.IDENTIFIER:
                self.ast.append(Node(NodeType.identifier, self.tokens[0].value, 0))
                self.consume_token()

                n = 1
                while self.tokens and (self.tokens[0].type == TokenType.IDENTIFIER or self.tokens[0].value == "("):
                    self.Vb()
                    n += 1
                if self.tokens[0].value != "=":
                    raise SyntaxError("Parsing error at Db #2")
                self.consume_token()
                self.E()

                self.ast.append(Node(NodeType.fcn_form, "fcn_form", n+1))
            elif self.tokens[1].value == "=":
                self.ast.append(Node(NodeType.identifier, self.tokens[0].value, 0))
                self.consume_token()
                self.consume_token()
                self.E()
                self.ast.append(Node(NodeType.equal, "=", 2))
            elif self.tokens[1].value == ",":
                self.Vl()
                if self.tokens[0].value != "=":
                    raise SyntaxError("Parsing error at Db")
                self.consume_token()
                self.E()

                self.ast.append(Node(NodeType.equal, "=", 2))

    def Vb(self):
        if self.tokens and self.tokens[0].type == TokenType.PUNCTUATION and self.tokens[0].value == "(":
            self.consume_token("(")
            isVl = False

            if self.tokens[0].type == TokenType.IDENTIFIER:
                self.Vl()
                isVl = True
            
            if self.tokens[0].value != ")":
                raise SyntaxError("Parse error unmatch )")
            self.consume_token()
            if not isVl:
                self.ast.append(Node(NodeType.empty_params, "()", 0))
        elif self.tokens and self.tokens[0].type == TokenType.IDENTIFIER:
            self.ast.append(Node(NodeType.identifier, self.tokens[0].value, 0))
            self.consume_token()

    def Vl(self):
        n = 0
        while True:
            if n > 0:
                self.consume_token()
            if not self.tokens or not self.tokens[0].type == TokenType.IDENTIFIER:
                raise SyntaxError("Parse error: an identifier was expected")
            self.ast.append(Node(NodeType.identifier, self.tokens[0].value, 0))
            
            self.consume_token()
            n += 1
            if not self.tokens[0].value == ",":
                break
        
        if n > 1:
            self.ast.append(Node(NodeType.comma, ",", n))

