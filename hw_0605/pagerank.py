import sys
import collections
from collections import deque
import heapq
from dataclasses import dataclass


class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

        # self.title_to_id['渋谷'] = 1 のような辞書
        self.title_to_id = {title: page_id for page_id, title in self.titles.items()}


    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()


    # Homework #1: Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_shortest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        start_id = self.title_to_id[start]
        goal_id = self.title_to_id[goal]
        searching = deque([start_id])
        prev = {start_id: None}
        
        if start == goal:
            return False
        
        while searching:
            # 探索中から id を1つ取り出す
            cur_node = searching.popleft()

            # 取り出した id に隣接する id を探索中にする
            for nxt_node in self.links[cur_node]:
                if nxt_node not in prev:
                    prev[nxt_node] = cur_node
                    
                    # 隣接する id が goal だった場合
                    if nxt_node == goal_id:
                        path = []
                        cur = goal_id
                        while cur:
                            path.append(self.titles[cur])
                            cur = prev[cur]
                        print(f"The shortest path from {start} to {goal} is {path[::-1]}")
                        return True
                    
                    searching.append(nxt_node)
        
        print(f"No path from {start} to {goal}...") 
        return False

    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        
        limit = 10000 # ループの上限回数
        
        # ページランクの収束判定 O(N)
        def converge(old_pageranks, new_pageranks, step):
            diff = 0
            # ページランクの更新幅を計算 O(N)
            for page_id, rank in old_pageranks.items():
                old_rank = rank
                new_rank = new_pageranks[page_id]
                diff += (new_rank - old_rank) ** 2

            print(f"step{step}: {diff}") # デバッグ
            return diff < 0.01


        # ページランク上位k個の表示 O(NlogN)
        def list_the_top_k(pageranks, k):
            # ページランクの大きい順に並べる
            sorted_pageranks = sorted(pageranks.items(), key=lambda x: x[1], reverse=True)
            
            print("The most important pages are:")
            
            # ページランク上位k個 のページタイトルを出力する
            for i in range(k):
                if i == len(sorted_pageranks):
                    break
                
                page_id, rank = sorted_pageranks[i]
                print(f"{i+1}: {self.titles[page_id]}, {rank}")
                      
            return 
        
        
        # ページランクの辞書を初期化 {page_id: rank}
        pageranks = dict.fromkeys(self.titles, 1)
        
        # ページランクの更新
        step = 0
        while step < limit:
            # 更新後のページランクの辞書を初期化
            new_pageranks = dict.fromkeys(self.titles, 0)
            distribute_all = 0
            
            # 現在のノードのページランクを隣接/全ノードに分配
            for cur_node, nxt_nodes in self.links.items():        
                if nxt_nodes:
                    # 隣接ノードに 85%、全ノードに 15% を分配
                    distribute_next = pageranks[cur_node] * 0.85 / len(nxt_nodes)
                    distribute_all += pageranks[cur_node] * 0.15 / len(self.titles)
                    
                    for nxt_node in nxt_nodes:
                        new_pageranks[nxt_node] += distribute_next
                        
                else:
                    # 隣接ノードがない場合、100% を分配
                    distribute_all += pageranks[cur_node] / len(self.titles)
                
            # 全ノードに分配
            for page_id in self.titles.keys():
                new_pageranks[page_id] += distribute_all
            
            # ページランクの収束判定
            if converge(pageranks, new_pageranks, step):
                return list_the_top_k(new_pageranks, 10)
            else:
                pageranks = new_pageranks
                step += 1
                


    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#   
        start_id = self.title_to_id[start]
        goal_id = self.title_to_id[goal]
        
        visited = set()
        
        # 結果
        longest_path_length = 0
        best_state = None
        
        # Beam Search の定数
        max_depth = 200000
        beam_width = 10
        dist_weight = 0.05
        edge_weight = 0.01
        children_per_state = 30
        dist_cap = 1000
        
        # 長さの目標
        target_depth = 160000
        landing_weight = 0.1
        
        
        # path の状態クラス
        @dataclass
        class State:
            node: int
            parent: object
            depth: int
            score: float
        
        
        # 現在の状態の遷移元を辿る
        def reconstruct_path(state):
            path = []

            while state is not None:
                path.append(state.node)
                state = state.parent

            path.reverse()
            return path

        
        # 隣接ノードが訪問済みかの判定
        def contains_in_path(state, nxt):
            while state is not None:
                if state.node == nxt:
                    return True
                state = state.parent
            return False
            
        
        # 逆向きの links を作る
        reverse_links = {node: [] for node in self.links.keys()}
        for src in self.links.keys():
            for dst in self.links[src]:
                if dst in reverse_links:
                    reverse_links[dst].append(src)
        
        
        # ゴール→各ノードの最短経路を求める（逆向きBFS）
        dist_to_goal = {goal_id: 0}
        searching = deque([goal_id])

        while searching:
            cur_node = searching.popleft()
            for prev_node in reverse_links[cur_node]:
                if prev_node not in dist_to_goal:
                    dist_to_goal[prev_node] = dist_to_goal[cur_node] + 1
                    searching.append(prev_node)
            
        # start から goal に到達不可能の場合
        if start_id not in dist_to_goal:
            print("No path found...")
            return
              
                  
        # 各ノードからの、ゴールに到達可能な辺の数を求める
        reachable_out_degree = {}
        for node in self.links:
            count = 0
            for nxt in self.links[node]:
                if nxt in dist_to_goal:
                    count += 1
            reachable_out_degree[node] = count
        
        
        # Beam Search でスコアの高いものを選んで探索する
        start_state = State(
            node=start_id,
            parent=None,
            depth=1,
            score=0.0
        )
        
        beam = [start_state]
        step = 0
        
        while beam:
            step += 1
            candidates = []
            
            for state in beam:
                cur_node = state.node
                
                # 探索の深さ制限
                if state.depth > max_depth:
                    continue
                
                # 暫定候補
                local_candidates = []
                    
                    
                # 隣接ノードを探索する
                for nxt_node in self.links[cur_node]:
                    # ゴールに到達不能なら飛ばす
                    if nxt_node not in dist_to_goal:
                        continue
                    
                    # 訪問済みなら飛ばす
                    if contains_in_path(state, nxt_node):
                        continue

                    new_depth = state.depth + 1
                    
                    # ゴールに到達した場合
                    if nxt_node == goal_id:
                        if new_depth > longest_path_length:
                            goal_state = State(
                                node=nxt_node,
                                parent=state,
                                depth=new_depth,
                                score=state.score
                            )

                            # 最長 state を更新
                            best_state = goal_state
                            longest_path_length = new_depth

                            print(f"Updated best length: {longest_path_length}")

                        continue

                    # 序盤・中盤は「遠回りできそう」を評価
                    # target_depth を超えたら goal に近い候補も評価する
                    d = min(dist_to_goal[nxt_node], dist_cap)
                    out_deg = reachable_out_degree.get(nxt_node, 0)

                    # 探索用のスコアを算出
                    score = (
                        new_depth
                        + dist_weight * d
                        + edge_weight * out_deg
                    )

                    local_candidates.append((score, nxt_node, new_depth))


                # state の上位 children_per_state 個だけ残す
                if len(local_candidates) > children_per_state:
                    local_candidates = heapq.nlargest(
                        children_per_state,
                        local_candidates,
                        key=lambda x: x[0]
                    )

                for score, nxt_node, new_depth in local_candidates:
                    new_state = State(
                        node=nxt_node,
                        parent=state,
                        depth=new_depth,
                        score=score
                    )

                    candidates.append(new_state)
            
            
            # 探索候補リストが空の場合、ループを抜ける
            if not candidates:
                break

            
            # 探索候補リストから上位（beam幅）個を選ぶ
            far_keep = int(beam_width * 0.7)
            near_keep = beam_width - far_keep

            # 長く伸びそうな候補（far_keep 個）
            top_by_score = heapq.nlargest(
                far_keep,
                candidates,
                key=lambda s: s.score
            )

            # goal に近い候補（near_keep 個）
            top_by_near_goal = heapq.nsmallest(
                near_keep,
                candidates,
                key=lambda s: dist_to_goal[s.node]
            )


            new_beam = []
            seen_ids = set()

            for state in top_by_score + top_by_near_goal:
                state_id = id(state)

                if state_id not in seen_ids:
                    seen_ids.add(state_id)
                    new_beam.append(state)

            beam = new_beam

            # すでに max_depth 付近まで行ったら終了
            if step >= max_depth:
                break
            

            print(f"The length of the longest path is {longest_path_length}")
    

    # Helper function for Homework #3:
    # Please use this function to check if the found path is well formed.
    # 'path': An array of page IDs that stores the found path.
    #     path[0] is the start page. path[-1] is the goal page.
    #     path[0] -> path[1] -> ... -> path[-1] is the path from the start
    #     page to the goal page.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])
        visited = {}
        for node in path:
            assert(node not in visited)
            visited[node] = True


if __name__ == "__main__":
    '''
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)
    '''

    wikipedia = Wikipedia("./wikipedia_dataset/pages_medium.txt", "./wikipedia_dataset/links_medium.txt")
    # Example
    wikipedia.find_longest_titles()
    # Example
    wikipedia.find_most_linked_pages()
    
    # Homework #1
    # wikipedia.find_shortest_path("A", "F")
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    wikipedia.find_shortest_path("渋谷", "骨なし魚")
    wikipedia.find_shortest_path("骨なし魚", "バンビ")
    wikipedia.find_shortest_path("骨なし魚", "マカロン")
    
    # Homework #2
    wikipedia.find_most_popular_pages()
    
    # Homework #3 (optional)
    wikipedia.find_longest_path("A", "F")
    wikipedia.find_longest_path("渋谷", "池袋")