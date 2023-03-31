class LinkedList:
    class Node:
        def __init__(self, data, next=None, prev=None):
            self.data = data
            self.next = next
            self.prev = prev

    def __init__(self):
        self.size = 0
        self.head = None
        self.tail = None

    def push(self, data):
        newnode = self.Node(data)
        self.size += 1
        if self.head is None:
            self.head = newnode
            self.tail = newnode
            return
        newnode.prev = None
        newnode.next = self.head
        self.head.prev = newnode
        self.head = newnode

    def delete(self, item: Node):
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
