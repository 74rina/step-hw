#!/usr/bin/env python3

import sys
import math
from common import print_tour, read_input


# index: (座標) の辞書を作る
def create_cities_dict(cities):
    cities_dict = {}
    for i, location in enumerate(cities):
        cities_dict[i] = location
    return cities_dict


# 2点間の距離を計算する
def calc_distance(a, b):
    x1, y1 = a
    x2, y2 = b
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    

# 現在地に最も近い町・その距離を求める
def find_closest(cur_city, cur_location, cities):
    closest_city = cur_city
    min_dist = float('inf')
    
    for nxt_city, nxt_location in cities.items():
        dist = calc_distance(cur_location, nxt_location)
        if dist < min_dist:
            closest_city = nxt_city
            min_dist = dist

    return (closest_city, min_dist)


def solve(cities):
    # Build a trivial solution.
    # Visit the cities in the order they appear in the input.
    BASE = 0
    
    remain_cities = create_cities_dict(cities)
    cur_city = BASE
    cur_location = cities[BASE]
    
    path = [BASE]
    total_dist = 0
    
    while remain_cities:
        del remain_cities[cur_city]
        
        # 全ての町を経由した
        if not remain_cities:
            path.append(BASE)
            total_dist += calc_distance(cur_location, cities[BASE])
            break
        
        nxt_city, dist = find_closest(cur_city, cur_location, remain_cities)
        
        path.append(nxt_city)
        total_dist += dist

        cur_city = nxt_city
        cur_location = remain_cities[cur_city]
        
        
    # return list(range(len(cities)))
    return path, total_dist



if __name__ == '__main__':
    # assert len(sys.argv) > 1
    input_file = input("入力ファイル名：")
    tour = solve(read_input(input_file))
    print_tour(tour)
