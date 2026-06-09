# メモ

cache = {url: webページ} 要素数X
新たなサイトを閲覧したとき、
bucketsを更新するが、
lru: queueにしてpopleftする
lfu: bucketsで登場回数が一番少ないものをreplaceする

目標：「もっとも直近にアクセスされた上位 X 個の <URL, Web ページ> の組が保存できるデータ構造」を作ればよい
与えられた <URL, Web ページ> があるかないかを検索
もしない場合、キャッシュ内で一番古い <URL, Web ページ> を捨てて、
代わりに与えられた <URL, Web ページ> を追加する

どの <URL, Web ページ> が一番古いかを O(1) で知るために、
ハッシュテーブルに工夫を加えて <URL, Web ページ> をアクセスされた順に並べておけばよい

↑ハッシュテーブルだけだと順序を管理できない（新たなサイトを閲覧したとき
どれを捨てるか判断できない）ので、他のデータ構造を組み合わせる
fifo: queue
lru: 連結リスト

# Cacheクラス

## 1. 初期化

- 訪問履歴の「新→古」順の双方向連結リスト Item()
  - key (urlの文字列)

  - value (web_page)

  - next, prev (Item)

- size（連結リストのノード数）

- capacity（連結リストの最大容量）

- urlとリストノードの対応表 hash_table = HashTable()

を用意する。

## 2. Webサイトを訪問した時の処理 visit(url, web_page)

url を hash_table から検索する。O(1)

- 見つかった場合
  1. そのノードを連結リストから削除する O(1)
  2. そのノードを連結リストの最初に挿入する O(1)
  3. ノードの value を web_page に更新する

- 見つからなかった場合
  1. 新たなノード（key=url, value=web_page）を作る
  2. そのノードを連結リストの最初に挿入する O(1)

連結リストの要素数 size が、最大容量 capacity を超えたら、

1. 連結リストの末尾のノードを削除する O(1)
2. その末尾ノード（とそのキー）を hash_table から削除する O(1)

## 3. 連結リストの最初にノードを挿入する insert_front(node)

head.next で最初のノード initial_node を取得し、

1. initial_node の prev を更新
2. 挿入するノード node の next を更新
3. head.next を挿入するノードにする

## 4. 連結リストのノードを削除する delete(node)

1. 削除するノードの prev, next を取得
2. prev_node.next および next_node.prev を更新
3. 削除するノードの prev, next を None にする

## 5. 連結リストの末尾のノードを削除する delete_last()

tail.prev で末尾のノードを取得し、それを delete(node) する。O(1)

# HashTableクラス

hw1 で実装。O(n) は O(item_count) のこと。

## 1. 追加 put(key, value)

- item_count がテーブルサイズの7割を占めたら rehash（ハッシュテーブルを拡大）する。

1. key のハッシュ値 hash を計算する。

2. 衝突しない場合は bucket に空リストを作成する。

3. bucket[hash] に同じ value が存在したら False。

4. bucket[hash] に [key, value] を append する。

5. item_count をインクリメントする。

bucket[hash] を全探索するので、基本はO(1)、最悪の場合O(n)。

最初に rehash を行う場合は O(n)。

## 2. 検索 get(key)

1. key のハッシュ値 hash を計算する。

2. bucket[hash] で全探索する。

随時 rahash して bucket[hash] の要素数を少なく保つため、基本は O(1)、最悪ケースは O(n)。

## 3. 削除 delete(key)

- item_count がテーブルサイズの7割を切ったら rehash（ハッシュテーブルを縮小）する。

1. key のハッシュ値 hash を計算する。

2. bucket[hash] を全探索して、keyが一致したらそれを pop する。

3. item_count をデクリメントする。

bucket[hash] を全探索するので、基本はO(1)、最悪の場合O(n)。

最初に rehash を行う場合は O(n)。

## 4. ハッシュ値の計算 calculate_hash()

base = 31, mod = 10^9, 各アルファベットはASCII変換して、

abc の場合：

hash = 97 _ 31^3 + 98 _ 31^2 + 99 \* 31^1

と計算する。key長が20以下であるため、O(1)。

## 5. ハッシュテーブルの拡大・縮小 rehash(new_bucket_size)

1.  現在のハッシュテーブルを old_buckets に退避させておく。

2.  サイズ new_bucket_size の新規リスト buckets を作成する。

3.  old_buckets の各bucketのkeyについて、mod を new_bucket_size として、ハッシュ値を計算し直す。

4.  buckets にマッピングする。

ハッシュテーブルの中身全てを再マッピングするので、O(n)。
