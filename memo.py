N, M = map(int, input().split())
graph = [[] for _ in range(N+1)]
for _ in range(M):
    a, b, x, y = map(int, input().split())
    graph[a].append((b, x, y))
    graph[b].append((a, -x, -y))

positions = [None] * (N+1)
positions[1] = (0, 0)

def dfs(idx):
    cur_x, cur_y = positions[idx]
    for nxt, dx, dy in graph[idx]:
        if positions[nxt] is None:
            positions[nxt] = (cur_x + dx, cur_y + dy)
            dfs(nxt)
    
dfs(1)

for i in range(1, N+1):
    if positions[i] is None:
        print("undecidable")
    else:
        x, y = positions[i]
        print(x, y)