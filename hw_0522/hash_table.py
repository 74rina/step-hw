import random, sys, time

###########################################################################
#                                                                         #
# Implement a hash table from scratch!                                    #
#                                                                         #
# Please do not use Python's dictionary or Python's collections library.  #
# The goal is to implement the data structure yourself.                   #
#                                                                         #
###########################################################################

# Hash function.
#
# 'key': string
# Return value: a hash value

# O(key長) → O(1)
def calculate_hash(key):
    assert type(key) == str
    # Note: This is not a good hash function. Make it better!
    hash = 0
    base = 31
    mod = 10 ** 9 + 7 # 素数にする
    for c in key:
        hash = (hash * base + ord(c)) % mod
    return hash


# An item object that represents one key - value pair in the hash table.
class Item:
    # 'key': The key of the item. The key must be a string.
    # 'value': The value of the item.
    # 'next': The next item in the linked list. If this is the last item in the
    #         linked list, 'next' is None.
    def __init__(self, key, value, next):
        assert type(key) == str
        self.key = key
        self.value = value
        self.next = next


# The main data structure of the hash table that stores key - value pairs.
# The key must be a string. The value can be any type.
#
# 'self.bucket_size': The bucket size.
# 'self.buckets': An array of the buckets. self.buckets[hash % self.bucket_size]
#                 stores a linked list of items whose hash value is 'hash'.
# 'self.item_count': The total number of items in the hash table.
class HashTable:

    # Initialize the hash table.
    def __init__(self):
        # Set the initial bucket size to 97. A prime number is chosen to reduce
        # hash conflicts.
        
        self.bucket_size = 97 # ハッシュテーブルのサイズ
        self.buckets = [None] * self.bucket_size
        self.item_count = 0
        
        
    # O(item_size)
    def rehash(self, new_bucket_size):
        
        old_buckets = self.buckets
        
        self.bucket_size = new_bucket_size
        self.buckets = [None] * self.bucket_size
        self.item_count = 0
        
        for bucket in old_buckets:
            cur_node = bucket
            while cur_node:
                self.put_for_rehash(cur_node.key, cur_node.value)
                cur_node = cur_node.next
    
    
    # rehash 用の put
    def put_for_rehash(self, key, value):
        key_hash = calculate_hash(key) % self.bucket_size
        
        new_node = Item(key, value, self.buckets[key_hash])
        self.buckets[key_hash] = new_node
        self.item_count += 1


    # Put an item to the hash table. If the key already exists, the
    # corresponding value is updated to a new value.
    #
    # 'key': The key of the item.
    # 'value': The value of the item.
    # Return value: True if a new item is added. False if the key already exists
    #               and the value is updated.
    def put(self, key, value):
        assert type(key) == str
        check_size(self.size(), self.bucket_size)  # Don't remove this code.
        #------------------------#
        # Write your code here!  #
        #------------------------#    
         
        key_hash = calculate_hash(key) % self.bucket_size
            
        # update
        cur_node = self.buckets[key_hash]
        while cur_node:
            if cur_node.key == key:
                cur_node.value = value
                return False
            cur_node = cur_node.next
        
        # リストの最初に挿入
        new_node = Item(key, value, self.buckets[key_hash])
        self.buckets[key_hash] = new_node
    
        self.item_count += 1
        
        # rehash when: item_size / all > 0.7
        # O(item_size)
        if self.item_count > self.bucket_size * 0.7:
            self.rehash(self.bucket_size * 2 + 1)
        
        return True
    
    # vectorを使うと、内部でrevectorが起こるので最悪O(n)、平均はO(1)
    # 連結リストを使った方が良い
        
        
    # Get an item from the hash table.
    #
    # 'key': The key.
    # Return value: If the item is found, return (the value of the item, True).
    #               Otherwise, return (None, False).
    def get(self, key):
        assert type(key) == str
        check_size(self.size(), self.bucket_size)  # Don't remove this code.
        #------------------------#
        # Write your code here!  #
        #------------------------#
        
        key_hash = calculate_hash(key) % self.bucket_size
        
        cur_node = self.buckets[key_hash] 
        
        while cur_node:
            if cur_node.key == key:
                return (cur_node.value, True)
            cur_node = cur_node.next
        
        return (None, False)


    # Delete an item from the hash table.
    #
    # 'key': The key.
    # Return value: True if the item is found and deleted successfully. False
    #               otherwise.
    def delete(self, key):
        assert type(key) == str
        #------------------------#
        # Write your code here!  #
        #------------------------#
        
        key_hash = calculate_hash(key) % self.bucket_size
            
        cur_node = self.buckets[key_hash]
        prev_node = None
        
        while cur_node:
            if cur_node.key == key:
                if prev_node is None:
                    self.buckets[key_hash] = cur_node.next # 削除対象が先頭の場合
                else:
                    prev_node.next = cur_node.next
                    
                self.item_count -= 1
                
                # rehash when: item_size / all < 0.3
                # O(item_size)
                if self.bucket_size >= 100 and self.item_count < self.bucket_size * 0.3:
                    self.rehash(max(97, self.bucket_size // 2 + 1))
                
                return True

            prev_node = cur_node
            cur_node = cur_node.next
        
        return False

    # Return the total number of items in the hash table.
    def size(self):
        return self.item_count


# Check that the hash table has a "reasonable" bucket size.
# The bucket size is judged "reasonable" if it is smaller than 100 or
# the buckets are 30% or more used.
#
# Note: Don't change this function.
def check_size(item_count, bucket_size):
    assert (bucket_size < 100 or item_count >= bucket_size * 0.3)


# Test the functional behavior of the hash table.
def functional_test():
    hash_table = HashTable()

    assert hash_table.put("aaa", 1) == True

    assert hash_table.get("aaa") == (1, True) 
    assert hash_table.size() == 1

    assert hash_table.put("bbb", 2) == True
    assert hash_table.put("ccc", 3) == True
    assert hash_table.put("ddd", 4) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.get("bbb") == (2, True)
    assert hash_table.get("ccc") == (3, True)
    assert hash_table.get("ddd") == (4, True) 
    assert hash_table.get("a") == (None, False)
    assert hash_table.get("aa") == (None, False)
    assert hash_table.get("aaaa") == (None, False)
    assert hash_table.size() == 4

    assert hash_table.put("aaa", 11) == False
    assert hash_table.get("aaa") == (11, True)
    assert hash_table.size() == 4

    assert hash_table.delete("aaa") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.size() == 3

    assert hash_table.delete("a") == False
    assert hash_table.delete("aa") == False
    assert hash_table.delete("aaa") == False
    assert hash_table.delete("aaaa") == False

    assert hash_table.delete("ddd") == True
    assert hash_table.delete("ccc") == True
    assert hash_table.delete("bbb") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.get("bbb") == (None, False)
    assert hash_table.get("ccc") == (None, False)
    assert hash_table.get("ddd") == (None, False)
    assert hash_table.size() == 0

    assert hash_table.put("abc", 1) == True
    assert hash_table.put("acb", 2) == True
    assert hash_table.put("bac", 3) == True
    assert hash_table.put("bca", 4) == True
    assert hash_table.put("cab", 5) == True
    assert hash_table.put("cba", 6) == True
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    assert hash_table.get("bac") == (3, True)
    assert hash_table.get("bca") == (4, True)
    assert hash_table.get("cab") == (5, True)
    assert hash_table.get("cba") == (6, True)
    assert hash_table.size() == 6

    assert hash_table.delete("abc") == True
    assert hash_table.delete("cba") == True
    assert hash_table.delete("bac") == True
    assert hash_table.delete("bca") == True
    assert hash_table.delete("acb") == True
    assert hash_table.delete("cab") == True
    assert hash_table.size() == 0

    # Test the rehashing.
    for i in range(100):
        hash_table.put(str(i), str(i))
    for i in range(100):
        assert hash_table.get(str(i)) == (str(i), True)
    for i in range(100):
        assert hash_table.delete(str(i)) == True
    hash_table.put("abc", 1)
    hash_table.put("acb", 2)
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    print("Functional tests passed!")


# Test the performance of the hash table.
#
# Your goal is to make the hash table work with mostly O(1).
# If the hash table works with mostly O(1), the execution time of each iteration
# should not depend on the number of items in the hash table. To achieve the
# goal, you will need to 1) implement rehashing (Hint: expand / shrink the hash
# table when the number of items in the hash table hits some threshold) and
# 2) tweak the hash function (Hint: think about ways to reduce hash conflicts).
def performance_test():
    hash_table = HashTable()

    for iteration in range(100):
        begin = time.time()
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.put(str(rand), str(rand))
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.get(str(rand))
        end = time.time()
        print("%d %.6f" % (iteration, end - begin))

    for iteration in range(100):
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.delete(str(rand))

    assert hash_table.size() == 0
    print("Performance tests passed!")


if __name__ == "__main__":
    functional_test()
    performance_test()