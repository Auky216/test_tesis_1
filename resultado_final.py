class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.parent = None
        self.color = 'RED'

def insert(root, key):
    if not root:
        return Node(key)
    
    node = root
    parent = None
    
    while node:
        parent = node
        if key < node.key:
            node = node.left
        else:
            node = node.right
    
    new_node = Node(key)
    new_node.parent = parent
    if key < parent.key:
        parent.left = new_node
    else:
        parent.right = new_node
    
    new_node.color = 'RED'
    
    while new_node != root and new_node.parent.color == 'RED':
        uncle = None
        if new_node.parent == new_node.parent.parent.left:
            uncle = new_node.parent.parent.right
        else:
            uncle = new_node.parent.parent.left
        
        if uncle and uncle.color == 'RED':
            # Case 1: Uncle is RED
            parent.color = 'BLACK'
            uncle.color = 'BLACK'
            grandparent = new_node.parent.parent
            grandparent.color = 'RED'
            new_node = grandparent
        else:
            if new_node == parent.right and new_node.parent == grandparent.left:
                # Case 2: Uncle is BLACK, New node is right child of its parent, Parent is left child of Grandparent
                new_node = parent
                rotate_left(new_node)
            elif new_node == parent.left and new_node.parent == grandparent.right:
                # Case 3: Uncle is BLACK, New node is left child of its parent, Parent is right child of Grandparent
                new_node = parent
                rotate_right(new_node)
            
            # Case 4: Uncle is BLACK, New node is left child of its parent, Parent is left child of Grandparent
            if new_node == parent.left:
                grandparent.color = 'RED'
                parent.color = 'BLACK'
                rotate_right(parent)
            else:
                # Case 4: Uncle is BLACK, New node is right child of its parent, Parent is right child of Grandparent
                grandparent.color = 'RED'
                parent.color = 'BLACK'
                rotate_left(parent)

def rotate_left(node):
    right_child = node.right
    node.right = right_child.left
    if right_child.left:
        right_child.left.parent = node
    
    right_child.parent = node.parent
    if not node.parent:
        root = right_child
    elif node == node.parent.left:
        node.parent.left = right_child
    else:
        node.parent.right = right_child
    
    right_child.left = node
    node.parent = right_child

def rotate_right(node):
    left_child = node.left
    node.left = left_child.right
    if left_child.right:
        left_child.right.parent = node
    
    left_child.parent = node.parent
    if not node.parent:
        root = left_child
    elif node == node.parent.left:
        node.parent.left = left_child
    else:
        node.parent.right = left_child
    
    left_child.right = node
    node.parent = left_child
