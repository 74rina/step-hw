#!/usr/bin/env python3

import sys
import math
from common import print_tour, read_input


# index: (座標) の辞書を作る
# O(N)
def create_cities_dict(cities):
    cities_dict = {}
    for i, location in enumerate(cities):
        cities_dict[i] = location
    return cities_dict


# 2点間の距離を計算する
# O(1)
def calc_distance(a, b):
    x1, y1 = a
    x2, y2 = b
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 外積を計算する
def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    

# 現在地に最も近い町（のインデックス）、その距離を求める
# O(N)
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
    
    
    # 点aと点bを結ぶ辺が、既存の辺と交差しているかを判定する
    # 交差している場合は、その辺の両端の町のインデックス(path上)も返す
    # O(N)
    def find_intersection(a, b, path):
        is_intersect = False
        
        # 交差している相手の辺の両端2点
        # m は a 側、n は b 側
        m = None
        n = None
        
        if len(path) <= 3:
            return (is_intersect, m, n)
        
        # path 上の隣り合う2点について、それらが作る辺が交差するか調べる
        for i in range(len(path) - 3):
            candidate_1 = path[i]
            candidate_2 = path[i + 1]
            can1_loc = cities[candidate_1]
            can2_loc = cities[candidate_2]

            # 2辺 (a-b), (can1-can2)
            if ccw(a, can1_loc, can2_loc) != ccw(b, can1_loc, can2_loc) and ccw(a, b, can1_loc) != ccw(a, b, can2_loc):
                is_intersect = True
                m = i
                n = i + 1
                break
 
        return (is_intersect, m, n)
    
    
    # 貪欲法 + 2-opt で起点から町を辿る
    while remain_cities:
        del remain_cities[cur_city]
        
        # 全ての町を経由した場合
        if not remain_cities:
            # 最後の町から基点に戻る
            path.append(BASE)
            total_dist += calc_distance(cur_location, cities[BASE])
            break
        
        # 現在地から最も近い町に進む
        nxt_city, dist = find_closest(cur_city, cur_location, remain_cities)
        nxt_location = remain_cities[nxt_city]
        path.append(nxt_city)
        
        # cur_city -> nxt_city の辺が、既存の辺と交差していないか
        is_intersect, swap_1, swap_2 = find_intersection(cur_location, nxt_location, path)
        
        if is_intersect:
            # 2辺 (swap1-swap2), (cur-nxt) を (swap1-cur), (swap2-nxt) に交換
            swap1_city = path[swap_1]
            swap2_city = path[swap_2]
            swap1_loc = cities[swap1_city]
            swap2_loc = cities[swap2_city]
            
            total_dist = (total_dist
                          - calc_distance(swap1_loc, swap2_loc)
                          + calc_distance(swap1_loc, cur_location)
                          + calc_distance(swap2_loc, nxt_location)
                          )
            
            cur_index = len(path) - 2
            path[swap_2:cur_index + 1] = reversed(path[swap_2:cur_index + 1])
            
        else:
            total_dist += dist
        
        # 現在地を更新
        cur_city = nxt_city
        cur_location = nxt_location
        
        
    # return list(range(len(cities)))
    return path, total_dist



if __name__ == '__main__':
    # assert len(sys.argv) > 1
    # input_file = input("入力ファイル名：")
    # tour = solve(read_input(input_file))
    tour = solve(read_input("input_output/input_0.csv"))
    print_tour(tour)
