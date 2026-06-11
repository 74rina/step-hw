import sys
import collections
from collections import deque
import heapq


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
        searched = set()
        edges = {} 
        
        while searching:
            # 探索中から id を1つ取り出す
            cur_node = searching.popleft()
            
            # 取り出した id が goal だった場合
            if cur_node == goal_id:
                path = [self.titles[cur_node]]
                
                # startまで辺をさかのぼる
                while cur_node in edges:
                    cur_node_origin = edges[cur_node]
                    path.append(self.titles[cur_node_origin])
                    cur_node = cur_node_origin
                print(f"The shortest path from {start} to {goal} is {path[::-1]}")
                return True
            
            # 取り出した id を探索済みにする
            searched.add(cur_node)

            # 取り出した id に隣接する id を探索中にする
            for nxt_node in self.links[cur_node]:
                if nxt_node not in searched:
                    searching.append(nxt_node)
                    edges[nxt_node] = cur_node
        
        print(f"No path from {start} to {goal}...") 
        return False

    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        
        # ページランクの収束判定
        def converge(old_pageranks, new_pageranks):
            diff = 0
            
            for page_id, rank in old_pageranks.items():
                old_rank = rank
                new_rank = new_pageranks[page_id]
                diff += (new_rank - old_rank) ** 2

            return diff < 0.01


        # ページランク上位k個の表示
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
        while True:
            # 更新後のページランクの辞書を初期化
            new_pageranks = dict.fromkeys(self.titles, 0)

            distribute_all = 0
            
            for cur_node, nxt_nodes in self.links.items():
                distribute_all += pageranks[cur_node] * 0.15 / len(self.titles)
                if nxt_nodes:
                    distribute_next = pageranks[cur_node] * 0.85 / len(nxt_nodes)
                
                # 隣接ノードに、ノードの85%を均等に分配
                if nxt_nodes:
                    for nxt_node in nxt_nodes:
                        new_pageranks[nxt_node] += distribute_next
                
            # 全ノードに、ノードの15%を分配
            for page_id in self.titles.keys():
                new_pageranks[page_id] += distribute_all
            
            # ページランクの収束判定
            if converge(pageranks, new_pageranks):
                return list_the_top_k(new_pageranks, 10)
            else:
                pageranks = new_pageranks
                print(pageranks)
                


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
        longest_path = []
        longest_path_length = 0
        
        # Beam Search の定数
        max_depth = 100000
        beam_width = 10
        dist_weight = 1.0
        edge_weight = 0.1
        
        
        # Beam Search のスコア算出
        
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
        beam = [([start_id], {start_id})]
        while beam:
            candidates = []
            
            for path, visited in beam:
                cur_node = path[-1]
                
                # 探索の深さ制限
                if len(path) > max_depth:
                    continue
                    
                # 隣接ノードを探索する
                for nxt_node in self.links[cur_node]:
                    # 枝刈り（ゴールに到達不能ノードを排除）
                    if nxt_node not in dist_to_goal:
                        continue
                    
                    # ゴールに達する場合
                    if cur_node == goal_id:
                        if len(path) > len(longest_path):
                            longest_path_length = len(path)
                            longest_path = path[:]
                            print("here")
                        continue
                    
                    # 隣接ノードの探索
                    if nxt_node not in visited:
                        new_path = path + [nxt_node]
                        new_visited = visited | {nxt_node}
                        
                        # 次の探索候補となる path のスコアを算出する
                        score = (
                            len(new_path)
                            + dist_weight * dist_to_goal[nxt_node]
                            + edge_weight * reachable_out_degree.get(nxt_node, 0)
                        )
                        
                        # 探索候補のリストに追加
                        candidates.append((score, new_path, new_visited))
            
            if not candidates:
                break
            
            # score 上位 beam_width 本だけ残す
            top_candidates = heapq.nlargest(
                beam_width,
                candidates,
                key=lambda x: x[0]
            )

            beam = [
                (path, visited)
                for score, path, visited in top_candidates
            ]
            
            print(beam)
            
        print(f"The length of longest path from {start} to {goal} is:")
        print(f"length: {longest_path_length}")
        return 
    

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
    # wikipedia.find_longest_titles()
    # Example
    # wikipedia.find_most_linked_pages()
    
    # Homework #1
    # wikipedia.find_shortest_path("A", "F")
    # wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # wikipedia.find_shortest_path("渋谷", "骨なし魚")
    
    # Homework #2
    # wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    # wikipedia.find_longest_path("A", "F")
    wikipedia.find_longest_path("渋谷", "池袋")