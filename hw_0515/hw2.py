# receive an original dictionary
words = []
with open('./words.txt') as f:
    for line in f:
        words.append(line.strip("\n"))

# return word counter like: {a:1, c:1, h:1}
# O(len(word))
def word_counter(word):
    counter = {}
    for c in word:
        counter[c] = counter.get(c, 0) + 1
    return counter

# create a new dictionary like: {"cha": {a:1, c:1, h:1}, "chair": {a:1, c:1, h:1, i:1, r:1}, ...}
# O(sum_len_words)
dict_counters = {}
for i, word in enumerate(words):
    dict_counters[word] = word_counter(word)

# scores
p4 = set(["j", "k", "q", "x", "z"])
p3 = set(["b", "f", "g", "p", "v", "w", "y"])
p2 = set(["c", "d", "l", "m", "u"])
p1 = set(["a", "e", "h", "i", "n", "o", "r", "s", "t" ])

# receive queries
queries = []
with open('./large.txt') as f:
    for line in f:
        queries.append(line.strip('\n'))

# O(sum_len_queries + Q * sum_len_words)
for i, q in enumerate(queries):
    candidates = []
    # search all words' counter from dict_counters
    query_counter = word_counter(q)
    
    for word, counter in dict_counters.items():
        for key, value in counter.items():
            if key not in query_counter:
                break
            else:
                if query_counter[key] < counter[key]:
                    break
        else:
            candidates.append(word)

    score = 0
    ans = ""
    for c in candidates:
        cur_score = 0
        for j in range(len(c)):
            if c[j] in p4:
                cur_score += 4
            elif c[j] in p3:
                cur_score += 3
            elif c[j] in p2:
                cur_score += 2
            elif c[j] in p1:
                cur_score += 1
        if cur_score > score:
            ans = c
            score = cur_score

    print(ans)
