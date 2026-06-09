import sys
from hash_table import HashTable # Use the hash table you implemented in Homework #2

# Implement a data structure that stores the most recently accessed N pages.
# See the test cases to see how it should work.
#
# Note: Please do not use a library like collections.OrderedDict). The goal is
#       to implement the data structure yourself!

class Node:
    def __init__(self, url, contents):
        # URL
        self.url = url
        # The contents of the URL
        self.contents = contents
        # Previous Node
        self.prev = None
        # Next Node
        self.next = None
        
        
class Cache:
    # Initialize the cache.
    # 'n': The size of the cache.
    def __init__(self, n):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        
        # キャッシュサイズ
        self.cache_capacity = n
        
        # 連結リストの初期化（ダミーノード）
        self.head = Node(None, None)
        self.tail = Node(None, None)       
        self.head.next = self.tail
        self.tail.prev = self.head
        
        # 「URL-Webページ」のハッシュマップ
        self.hash_table = HashTable()

    # Access a page and update the cache so that it stores the most recently
    # accessed N pages. This needs to be done with mostly O(1).
    # |url|: The accessed URL
    # |contents|: The contents of the URL
    def access_page(self, url, contents):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        
        node, found = self.hash_table.get(url)
        
        if found:
            assert type(node) == Node
            node.value = contents
            
            # 一つにまとめる
            self.delete(node)
            self.insert_front(node)
            
            
        else:
            new_node = Node(url, contents)
            
            self.insert_front(new_node)
            
            self.hash_table.put(new_node.url, new_node)
            
            if self.hash_table.size() > self.cache_capacity:
                last_node = self.delete_last()
                self.hash_table.delete(last_node.url)

    # Return the URLs stored in the cache. The URLs are ordered in the order
    # in which the URLs are mostly recently accessed.
    def get_pages(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pages = []
        cur_node = self.head.next
        
        while cur_node != self.tail:
            pages.append(cur_node.url)
            cur_node = cur_node.next
            
        return pages
    
    
    # 双方向連結リストの最初にノードを追加する
    def insert_front(self, node):
        initial_node = self.head.next # 現在の最初ノードを退避
        self.head.next = node
        node.prev = self.head
        node.next = initial_node
        initial_node.prev = node
    
    # 連結リストのノードを削除する
    def delete(self, node):
        
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
        
        node.prev = None
        node.next = None
    
    # 連結リストの末尾のノードを削除する
    def delete_last(self):
        last_node = self.tail.prev
        
        self.delete(last_node)
        
        return last_node


def cache_test():
    # Set the size of the cache to 4.
    cache = Cache(4)

    # Initially, no page is cached.
    assert cache.get_pages() == []

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # "a.com" is cached.
    assert cache.get_pages() == ["a.com"]

    # Access "b.com".
    cache.access_page("b.com", "BBB")
    # The cache is updated to:
    #   (new)<-- "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["b.com", "a.com"]

    # Access "c.com".
    cache.access_page("c.com", "CCC")
    # The cache is updated to:
    #   (new)<-- "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["c.com", "b.com", "a.com"]

    # Access "d.com".
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "d.com" again.
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "a.com" again.
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (new)<-- "a.com", "d.com", "c.com", "b.com" -->(old)
    assert cache.get_pages() == ["a.com", "d.com", "c.com", "b.com"]

    cache.access_page("c.com", "CCC")
    assert cache.get_pages() == ["c.com", "a.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is full, so we need to remove the least recently accessed page "b.com".
    # The cache is updated to:
    #   (new)<-- "e.com", "a.com", "c.com", "d.com" -->(old)
    assert cache.get_pages() == ["e.com", "a.com", "c.com", "d.com"]

    # Access "f.com".
    cache.access_page("f.com", "FFF")
    # The cache is full, so we need to remove the least recently accessed page "c.com".
    # The cache is updated to:
    #   (new)<-- "f.com", "e.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["f.com", "e.com", "a.com", "c.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is updated to:
    #   (new)<-- "e.com", "f.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["e.com", "f.com", "a.com", "c.com"]

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (new)<-- "a.com", "e.com", "f.com", "c.com" -->(old)
    assert cache.get_pages() == ["a.com", "e.com", "f.com", "c.com"]

    print("Tests passed!")


if __name__ == "__main__":
    cache_test()
