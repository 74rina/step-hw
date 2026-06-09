from hash_table import HashTable
import random

cache_capacity = 10

class Item:
    # 'key': The key of the item. The key must be a string.
    # 'value': The value of the item.
    # 'next': The next item in the linked list. If this is the last item in the
    #         linked list, 'next' is None.
    # 'prev': 双方向リストに拡張
    def __init__(self, key, value, next, prev):
        self.key = key
        self.value = value
        self.next = next
        self.prev = prev
  
            
class Cache:
    def __init__(self, capacity):
        self.hash_table = HashTable()
        
        # 双方向連結リストの初期化
        self.head = Item(None, None, None, None)
        self.tail = Item(None, None, None, None)       
        self.head.next = self.tail
        self.tail.prev = self.head
        self.capacity = capacity
    
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
        
    # urlのwebページを閲覧したときの処理
    def visit(self, url, web_page):
        node, found = self.hash_table.get(url)
        
        if found:
            assert type(node) == Item
            node.value = web_page
            
            # 一つにまとめる
            self.delete(node)
            self.insert_front(node)
            
            
        else:
            new_node = Item(url, web_page, None, None)
            
            self.insert_front(new_node)
            
            self.hash_table.put(new_node.key, new_node)
            
            if self.hash_table.size() > self.capacity:
                last_node = self.delete_last()
                self.hash_table.delete(last_node.key)

def main():
    cache = Cache(cache_capacity)

    while True:
        accessed_url = input("URLを入力してください(str)")
        
        web_page = random.randint(1, 1000) # 簡単のため 1-1000 の整数で表す
        
        cache.visit(accessed_url, web_page)
        
        print(cache.hash_table.buckets) # キャッシュを表示

if __name__ == "__main__":
    main()