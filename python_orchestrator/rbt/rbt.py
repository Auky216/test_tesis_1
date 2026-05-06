class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.color = 'red'

class RBT:
    def __init__(self):
        self.nil = Node(0)
        self.root = self.nil

    def insert(self, z):
        y = self.nil
        x = self.root
        while x != self.nil:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y == self.nil:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        z.left = self.nil
        z.right = self.nil
        z.color = 'red'
        self._fix_insert(z)

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.nil:
            x.right.parent = y
        x.parent = y.parent
        if y.parent == self.nil:
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        x.right = y
        y.parent = x

    def _fix_insert(self, z):
        while z.parent.color == 'red':
            if z.parent == z.parent.parent.left:
                uncle = z.parent.parent.right
                if uncle.color == 'red':
                    z.parent.color = 'black'
                    uncle.color = 'black'
                    z.parent.parent.color = 'red'
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self._rotate_left(z)
                    z.parent.color = 'black'
                    z.parent.parent.color = 'red'
                    self._rotate_right(z.parent.parent)
            else:
                uncle = z.parent.parent.left
                if uncle.color == 'red':
                    z.parent.color = 'black'
                    uncle.color = 'black'
                    z.parent.parent.color = 'red'
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._rotate_right(z)
                    z.parent.color = 'black'
                    z.parent.parent.color = 'red'
                    self._rotate_left(z.parent.parent)
        self.root.color = 'black'

    def delete(self, z):
        y = z
        original_color = y.color
        if z.left == self.nil:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.nil:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self.minimum(z.right)
            original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if original_color == 'black':
            self._fix_delete(x)

    def _transplant(self, u, v):
        if u.parent == self.nil:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def minimum(self, x):
        while x.left != self.nil:
            x = x.left
        return x
def inorder_traversal(self, node):
    if node is not None:
        self.inorder_traversal(node.left)
        print(node.key)
        self.inorder_traversal(node.right)

if __name__ == "__main__":
    # Crear un árbol RB
    rbt = RBT()

    # Insertar algunos elementos
    rbt.insert(10)
    rbt.insert(20)
    rbt.insert(30)
    rbt.insert(40)
    rbt.insert(50)

    # Realizar una recorrido in-order
    print("Inorder traversal:")
    rbt.inorder_traversal(rbt.root)