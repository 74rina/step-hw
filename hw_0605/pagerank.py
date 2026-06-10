import sys
import collections
from collections import deque


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
        print(self.links)

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
                print(path[::-1])
                return 
            
            # 取り出した id を探索済みにする
            searched.add(cur_node)

            # 取り出した id に隣接する id を探索中にする
            for nxt_node in self.links[cur_node]:
                if nxt_node not in searched:
                    searching.append(nxt_node)
                    edges[nxt_node] = cur_node
                    
        return False

    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pass


    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pass


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
    wikipedia.find_shortest_path("A", "F")
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    wikipedia.find_shortest_path("渋谷", "骨なし魚")
    
    # Homework #2
    wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")