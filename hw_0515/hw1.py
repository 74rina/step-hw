# receive an original dictionary
words = []
with open('./step2/anagram/words.txt') as f:
    for line in f:
        words.append(line.strip("\n"))

# 前処理
# create a new dictionary like: {"aet": ["eat", "tea"]}
# O(N * LlogL)
new_dict = {}
for i, word in enumerate(words):
    s_word = "".join(sorted(word))
    if s_word in new_dict:
        new_dict[s_word].append(word)
    else:
        new_dict[s_word] = [word]

# return valid anagrams from new_dict
# KlogK + N
def findAnagram(word):
    s_word = "".join(sorted(word))
    if s_word in new_dict:
        return " ".join(new_dict[s_word])
    else:
        return None

# N * LlogL + m * (KlogK + N)
# m
while True:
    query = input()
    print(findAnagram(query))