import random
import bisect
from web_cache2 import Cache

def build_zipf_cumulative_weights(page_count, alpha):
    cumulative = []
    total = 0.0

    for rank in range(1, page_count + 1):
        weight = 1.0 / (rank ** alpha)
        total += weight
        cumulative.append(total)

    return cumulative, total


def sample_zipf_page_id(cumulative, total):
    r = random.random() * total
    index = bisect.bisect_left(cumulative, r)
    return index + 1


def zipf_cache_test():
    page_count = 10000
    cache_size = 500
    access_count = 1000000
    alpha = 1.35

    random.seed(42)

    cache = Cache(cache_size)

    cumulative, total = build_zipf_cumulative_weights(page_count, alpha)

    hit_count = 0

    for _ in range(access_count):
        page_id = sample_zipf_page_id(cumulative, total)

        url = "https://example.com/page/" + str(page_id)
        contents = "contents_" + str(page_id)

        _, found = cache.hash_table.get(url)

        if found:
            hit_count += 1

        cache.access_page(url, contents)

    hit_rate = hit_count / access_count

    print("Zipf cache test:")
    print("  access_count =", access_count)
    print("  hit_count =", hit_count)
    print("  hit_rate =", hit_rate)
    print("  hit_rate_percent =", hit_rate * 100, "%")

    assert 0.90 <= hit_rate <= 0.92

    print("Zipf test passed!")


if __name__ == "__main__":
    zipf_cache_test()