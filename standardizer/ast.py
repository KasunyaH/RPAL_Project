from .node import Node

class AST:
    def __init__(self, root=None):
        self.root = root

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        if node is None:
            return

        # Print current node
        print('.' * level + str(node.data))

        # Print children
        for child in node.children:
            self.print_tree(child, level + 1)

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
