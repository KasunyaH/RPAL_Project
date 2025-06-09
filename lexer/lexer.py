import re
from enum import Enum

class TokenType(Enum):
    # Different types of tokens in RPAL
    KEYWORD = 1
    IDENTIFIER = 2
    INTEGER = 3
    STRING = 4
    END_OF_TOKENS = 5
    PUNCTUATION = 6
    OPERATOR = 7

class MyToken:
    # Token class to store token type and value
    def __init__(self, token_type, value):
        if not isinstance(token_type, TokenType):
            raise ValueError("token_type must be an instance of TokenType enum")
        self.type = token_type
        self.value = value

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

def tokenize(input_str):
    # Convert input string to tokens
    tokens = []
    
    # Patterns for different tokens
    patterns = {
        'COMMENT': r'//.*',  # Comments
        'KEYWORD': r'(let|in|fn|where|aug|or|not|gr|ge|ls|le|eq|ne|true|false|nil|dummy|within|and|rec)\b',  # Keywords
        'STRING': r'\'(?:\\\'|[^\'])*\'',  # Strings - will fail with nested quotes
        'IDENTIFIER': r'[a-zA-Z][a-zA-Z0-9_]*',  # Variable names
        'INTEGER': r'\d+',  # Numbers
        'OPERATOR': r'[+\-*<>&.@/:=~|$\#!%^_\[\]{}"\'?]+',  # Operators
        'SPACES': r'[ \t\n]+',  # Spaces
        'PUNCTUATION': r'[();,]'  # Special characters
    }
    
    # Process input
    while input_str:
        matched = False
        for key, pattern in patterns.items():
            match = re.match(pattern, input_str)
            if match:
                if key != 'SPACES':
                    if key == 'COMMENT':
                        comment = match.group(0)
                        input_str = input_str[match.end():]
                        matched = True
                        break
                    else:
                        token_type = getattr(TokenType, key)
                        if not isinstance(token_type, TokenType):
                            raise ValueError(f"Token type '{key}' is not a valid TokenType")
                        tokens.append(MyToken(token_type, match.group(0)))
                        input_str = input_str[match.end():]
                        matched = True
                        break
                input_str = input_str[match.end():]
                matched = True
                break
        if not matched:
            print("Error: Unable to tokenize input")
            break
    
    return tokens

# Example:
# input_file = open("input.txt", "r")
# input_str = input_file.read()
# input_file.close()
# tokens = tokenize(input_str)
# for token in tokens:
#     print(token.type, token.value)

