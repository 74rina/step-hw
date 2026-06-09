import random, sys, time

'''
key->value 検索・追加・削除を絶対にO(1)で行うハッシュマップ

key も value も 20文字以下（定数時間で処理可能）
key に重複はない（同一の名前のユーザは受け付けない）

アルファベット26文字or空白 を20文字分なので、26^20個のテーブルを用意すれば絶対にO(1)

26^20個のうち、使わないものを削りたい

Trie木にする
'''


class TrieNode:
    def __init__(self):
        self.value = None
        self.children = [None] * 26
        self.is_end = False

class HashTable:
    def __init__(self):
        self.root = TrieNode()

    # 追加
    def put(self, key, value):
        node = self.root
        # 木をrootから辿っていく
        for c in key:
            idx = ord(c) - ord("a")
            if node.children[idx] is None:
                node.children[idx] = TrieNode()
            node = node.children[idx]
        
        if node.is_end:
            is_new = False # update
        else:
            is_new = True
        
        node.value = value
        node.is_end = True
        return is_new

    # 検索
    def get(self, key):
        node = self.root
        for c in key:
            idx = ord(c) - ord("a")
            if node.children[idx] is None:
                return (None, False)
            node = node.children[idx]
        if node.is_end:
            return (node.value, True)
        else:
            return (None, False)
        

    # 削除
    def delete(self, key):
        node = self.root
        for c in key:
            idx = ord(c) - ord("a")
            if node.children[idx] is None:
                return False
            node = node.children[idx]
        if not node.is_end:
            return False
        else:
            node.value = None
            node.is_end = False
            return True



# Test the functional behavior of the hash table.
def functional_test():
    hash_table = HashTable()

    assert hash_table.put("aaa", 1) == True

    assert hash_table.get("aaa") == (1, True) 
    # assert hash_table.size() == 1

    assert hash_table.put("bbb", 2) == True
    assert hash_table.put("ccc", 3) == True
    assert hash_table.put("ddd", 4) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.get("bbb") == (2, True)
    assert hash_table.get("ccc") == (3, True)
    assert hash_table.get("ddd") == (4, True) 
    print(hash_table.get("a"))
    assert hash_table.get("a") == (None, False)
    assert hash_table.get("aa") == (None, False)
    assert hash_table.get("aaaa") == (None, False)
    # assert hash_table.size() == 4

    assert hash_table.put("aaa", 11) == False
    assert hash_table.get("aaa") == (11, True)
    # assert hash_table.size() == 4

    assert hash_table.delete("aaa") == True
    assert hash_table.get("aaa") == (None, False)
    # assert hash_table.size() == 3

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
    # assert hash_table.size() == 0

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
    # assert hash_table.size() == 6

    assert hash_table.delete("abc") == True
    assert hash_table.delete("cba") == True
    assert hash_table.delete("bac") == True
    assert hash_table.delete("bca") == True
    assert hash_table.delete("acb") == True
    assert hash_table.delete("cab") == True
    # assert hash_table.size() == 0

    # Test the rehashing.
    keys = []
    for i in range(100):
        key = random_lower_string(20)
        keys.append(key)
        assert hash_table.put(key, key) == True

    for key in keys:
        assert hash_table.get(key) == (key, True)

    for key in keys:
        assert hash_table.delete(key) == True
        
    hash_table.put("abc", 1)
    hash_table.put("acb", 2)
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    print("Functional tests passed!")


def random_lower_string(length=20):
    return ''.join(chr(ord('a') + random.randint(0, 25)) for _ in range(length))

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

        keys = []
        for i in range(10000):
            key = random_lower_string(20)
            keys.append(key)
            hash_table.put(key, key)

        for key in keys:
            hash_table.get(key)

        end = time.time()
        print("%d %.6f" % (iteration, end - begin))

    for iteration in range(100):
        random.seed(iteration)

        keys = []
        for i in range(10000):
            key = random_lower_string(20)
            keys.append(key)

        for key in keys:
            hash_table.delete(key)

    # assert hash_table.size() == 0
    print("Performance tests passed!")


if __name__ == "__main__":
    functional_test()
    performance_test()