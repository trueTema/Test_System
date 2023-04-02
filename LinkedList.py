class LinkedList:
    class Node:
        def __init__(self, data, next=None, prev=None):
            """
            Initialing constructor
            :param data: Data for current Node
            :param next: Pointer to next Node
            :param prev: Pointer to prev Node
            """
            self.data = data
            self.next = next
            self.prev = prev

    def __init__(self):
        """Initialing constructor"""
        self.size = 0
        self.head = None
        self.tail = None

    def push(self, data):
        """
        Pushes new Node to the end of List with data
        :param data: Data for new Node
        """
        new_node = self.Node(data)
        self.size += 1
        if self.head is None:
            self.head = new_node
            self.tail = new_node
            return
        new_node.prev = None
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node

    def delete(self, item: Node):
        """
        Deletes node from List
        :param item: Deleting node
        """
        self.size -= 1
        if item != self.head:
            item.prev.next = item.next
        else:
            self.head = item.next
        if item != self.tail:
            item.next.prev = item.prev
        else:
            self.tail = item.prev
        del item

    def pop(self):
        """Deletes node from the front of list"""
        if self.tail == self.head and self.tail is not None:
            cur = self.tail
            self.tail = self.head = None
            self.size -= 1
            del cur
            return
        if self.tail is not None:
            cur = self.tail
            self.size -= 1
            self.tail.prev.next = None
            self.tail = self.tail.prev
            del cur
