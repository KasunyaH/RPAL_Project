class Node:
    def __init__(self, data=None, depth=0, parent=None, children=None, is_standardized=False):
        self.data = data
        self.depth = depth
        self.parent = parent
        self.children = children or []
        self.is_standardized = is_standardized

    def standardize(self):
        if self.is_standardized:
            return

        for child in self.children:
            child.standardize()

        if self.data == "let":
            # LET -> GAMMA with LAMBDA
            temp1 = self.children[0].children[1]
            temp2 = self.children[1]
            temp1.parent = self
            temp1.depth = self.depth + 1
            temp2.parent = self.children[0]
            temp2.depth = self.depth + 2
            self.children[1] = temp1
            self.children[0].data = "lambda"
            self.children[0].children[1] = temp2
            self.data = "gamma"
        elif self.data == "where":
            # WHERE -> LET
            self.children[0], self.children[1] = self.children[1], self.children[0]
            self.data = "let"
            self.standardize()
        elif self.data == "function_form":
            # FCN_FORM -> EQUAL with LAMBDA chain
            Ex = self.children[-1]
            current_lambda = Node("lambda", self.depth + 1, self, [], True)
            self.children.insert(1, current_lambda)

            i = 2
            while self.children[i] != Ex:
                V = self.children[i]
                self.children.pop(i)
                V.depth = current_lambda.depth + 1
                V.parent = current_lambda
                current_lambda.children.append(V)

                if len(self.children) > 3:
                    current_lambda = Node("lambda", current_lambda.depth + 1, current_lambda, [], True)
                    current_lambda.parent.children.append(current_lambda)

            current_lambda.children.append(Ex)
            self.children.pop(2)
            self.data = "="
        elif self.data == "lambda" and len(self.children) > 2:
            # LAMBDA with multiple variables -> LAMBDA chain
            Ey = self.children[-1]
            current_lambda = Node("lambda", self.depth + 1, self, [], True)
            self.children.insert(1, current_lambda)

            i = 2
            while self.children[i] != Ey:
                V = self.children[i]
                self.children.pop(i)
                V.depth = current_lambda.depth + 1
                V.parent = current_lambda
                current_lambda.children.append(V)

                if len(self.children) > 3:
                    current_lambda = Node("lambda", current_lambda.depth + 1, current_lambda, [], True)
                    current_lambda.parent.children.append(current_lambda)

            current_lambda.children.append(Ey)
            self.children.pop(2)
        elif self.data == "within":
            # WITHIN -> EQUAL with GAMMA and LAMBDA
            X1, E1 = self.children[0].children
            X2, E2 = self.children[1].children
            gamma = Node("gamma", self.depth + 1, self, [], True)
            lambda_ = Node("lambda", self.depth + 2, gamma, [], True)
            
            X1.depth = X1.depth + 1
            X1.parent = lambda_
            X2.depth = X1.depth - 1
            X2.parent = self
            E1.parent = gamma
            E2.depth = E2.depth + 1
            E2.parent = lambda_
            
            lambda_.children.extend([X1, E2])
            gamma.children.extend([lambda_, E1])
            self.children = [X2, gamma]
            self.data = "="
        elif self.data == "@":
            # AT -> GAMMA chain
            gamma1 = Node("gamma", self.depth + 1, self, [], True)
            e1, n = self.children[:2]
            e1.depth += 1
            e1.parent = gamma1
            n.depth += 1
            n.parent = gamma1
            gamma1.children.extend([n, e1])
            self.children[0:2] = [gamma1]
            self.data = "gamma"
        elif self.data == "and":
            # SIMULTDEF -> EQUAL with COMMA and TAU
            comma = Node(",", self.depth + 1, self, [], True)
            tau = Node("tau", self.depth + 1, self, [], True)

            for equal in self.children:
                equal.children[0].parent = comma
                equal.children[1].parent = tau
                comma.children.append(equal.children[0])
                tau.children.append(equal.children[1])

            self.children = [comma, tau]
            self.data = "="
        elif self.data == "rec":
            # REC -> EQUAL with GAMMA and LAMBDA
            X, E = self.children[0].children
            F = Node(X.data, self.depth + 1, self, X.children, True)
            G = Node("gamma", self.depth + 1, self, [], True)
            Y = Node("<Y*>", self.depth + 2, G, [], True)
            L = Node("lambda", self.depth + 2, G, [], True)

            X.depth = L.depth + 1
            X.parent = L
            E.depth = L.depth + 1
            E.parent = L
            L.children.extend([X, E])
            G.children.extend([Y, L])
            self.children = [F, G]
            self.data = "="

        self.is_standardized = True

class NodeFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_node(data, depth):
        node = Node()
        node.set_data(data)
        node.set_depth(depth)
        node.children = []
        return node

    @staticmethod
    def get_node_with_parent(data, depth, parent, children, is_standardized):
        node = Node()
        node.set_data(data)
        node.set_depth(depth)
        node.set_parent(parent)
        node.children = children
        node.is_standardized = is_standardized
        return node