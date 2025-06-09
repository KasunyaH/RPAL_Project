from .node import Node
from .ast import AST

#converting nodes from parser

class ASTFactory:
    @staticmethod
    def get_abstract_syntax_tree(data):
        if not data:
            return AST()
            
        root = Node(data[0], 0)
        prev_node = root
        current_depth = 0

        for s in data[1:]:
            # Count leading dots to determine depth
            depth = 0
            while s[depth] == '.':
                depth += 1
                
            # Create new node
            current_node = Node(s[depth:], depth)
            
            # Find parent node
            if depth > current_depth:
                prev_node.children.append(current_node)
                current_node.parent = prev_node
            else:
                while prev_node.depth != depth:
                    prev_node = prev_node.parent
                prev_node.parent.children.append(current_node)
                current_node.parent = prev_node.parent
                
            prev_node = current_node
            current_depth = depth
            
        return AST(root)  
