//
// >>>> malloc challenge! <<<<
//
// Your task is to improve utilization and speed of the following malloc
// implementation.
// Initial implementation is the same as the one implemented in simple_malloc.c.
// For the detailed explanation, please refer to simple_malloc.c.

#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BIN_SIZE 10

//
// Interfaces to get memory pages from OS
//

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

//
// Struct definitions
//

// メモリのメタデータ用 双方向連結リスト
typedef struct my_metadata_t {
  size_t size;
  bool allocated;
  struct my_metadata_t *next;
  struct my_metadata_t *prev;
} my_metadata_t;

// ヒープ領域
typedef struct my_heap_t {
  my_metadata_t *free_head;
  my_metadata_t dummy;
} my_heap_t;

// Free List Bin（サイズ別の空き領域リスト）
my_metadata_t *bins[BIN_SIZE];

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;

//
// Helper functions (feel free to add/remove/edit!)
//

// 領域のサイズを求める
static size_t payload_size(my_metadata_t *m) { return m->size; }

// 前（左）の領域の先頭を求める
static my_metadata_t *get_prev_block(my_metadata_t *m) {
  size_t prev_size = *((size_t *)m - 1);

  // 既に先頭の場合
  if (prev_size == 0) {
    return NULL;
  }

  return (my_metadata_t *)((char *)m - sizeof(size_t) - sizeof(my_metadata_t) -
                           prev_size);
}

// 次（右）の領域の先頭を求める
static my_metadata_t *get_next_block(my_metadata_t *m) {
  my_metadata_t *next = (my_metadata_t *)((char *)m + sizeof(my_metadata_t) +
                                          m->size + sizeof(size_t));

  // 既に末端の場合
  if (next->size == 0) {
    return NULL;
  }

  return next;
}

// footer（各ブロックの末尾に置く、領域のサイズ情報）を書く
static void write_footer(my_metadata_t *m) {
  size_t *footer = (size_t *)((char *)m + sizeof(my_metadata_t) + m->size);
  *footer = m->size;
}

// 空き領域判定
static bool is_free(my_metadata_t *m) { return !m->allocated; }

// 確保済み領域にする
static void mark_allocated(my_metadata_t *m) { m->allocated = true; }

// 空き領域にする
static void mark_free(my_metadata_t *m) { m->allocated = false; }

//
// 空き領域 bin
//

// 領域サイズ -> bin を計算する
static int size_to_bin(size_t size) {
  size_t bin_idx = size / 1000;
  return (int)bin_idx;
}

// 空き領域 bin に追加する
void add_to_bin(my_metadata_t *m) {
  int bin_idx = size_to_bin(m->size);

  // 該当 bin の先頭に追加
  m->next = bins[bin_idx];
  if (m->next) {
    m->next->prev = m;
  }
  m->prev = NULL;

  // 該当 bin の先頭を更新
  bins[bin_idx] = m;
}

// 空き領域 bin から削除する
void remove_from_bin(my_metadata_t *m) {
  // 安全対策: NULL チェック
  if (!m)
    return;

  int bin_idx = size_to_bin(m->size);
  my_metadata_t *head = bins[bin_idx];

  // 先頭が削除対象か
  my_metadata_t *pred = NULL;
  if (head == m) {
    bins[bin_idx] = m->next;
    pred = NULL;
  } else {
    // predecessor をリストから探す（m->prev が壊れている可能性を避ける）
    my_metadata_t *cur = head;
    while (cur && cur->next != m) {
      cur = cur->next;
    }
    pred = cur; // 見つからなければ NULL のまま
    if (cur) {
      cur->next = m->next;
    }
  }

  // next の prev を更新
  if (m->next) {
    m->next->prev = pred;
  }

  // 自分の next, prev を無効化
  m->next = NULL;
  m->prev = NULL;
}

//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// This is called at the beginning of each challenge.
void my_initialize() {
  // 空き領域 bin を初期化
  for (int i = 0; i < BIN_SIZE; i++) {
    bins[i] = NULL;
  }
}

// 確保するページの先頭・末尾を、サイズ 0 で初期化する
void init_region(void *region, size_t region_size) {
  // 領域先頭に front sentinel
  size_t *front_sentinel = (size_t *)region;
  *front_sentinel = 0;

  // 最初の実ブロックは sentinel の直後に置く
  my_metadata_t *first = (my_metadata_t *)((char *)region + sizeof(size_t));
  first->size = region_size - sizeof(size_t) - sizeof(my_metadata_t) -
                sizeof(size_t) - sizeof(my_metadata_t);
  first->allocated = false;
  first->next = first->prev = NULL;
  write_footer(first);

  // 末尾 sentinel ヘッダ
  my_metadata_t *term =
      (my_metadata_t *)((char *)first + sizeof(my_metadata_t) + first->size +
                        sizeof(size_t));
  term->size = 0;
  term->allocated = true; // free list に入れない
  term->next = term->prev = NULL;
}

// my_malloc() is called every time an object is allocated.
// |size| is guaranteed to be a multiple of 8 bytes and meets 8 <= |size| <=
// 4000. You are not allowed to use any library functions other than
// mmap_from_system() / munmap_to_system().
void *my_malloc(size_t size) {
  // First-fit: Find the first free slot the object fits.
  // TODO: Update this logic to Best-fit!

  my_metadata_t *best = NULL;
  int bin_idx = size_to_bin(size); // 該当 bin のインデックス

  // サイズが最小の空き領域を求める（該当 bin を探す）
  for (int i = bin_idx; i < BIN_SIZE; i++) {
    my_metadata_t *cur = bins[i]; // 連結リストの現在ノード
    my_metadata_t *candidate = NULL;
    size_t candidate_size = SIZE_MAX;

    // 現在 bin の連結リストから空き領域を探す
    while (cur) {
      if (cur->size >= size && cur->size < candidate_size) {
        candidate = cur;
        candidate_size = cur->size;

        // bin サイズがヒット
        if (candidate_size == size) {
          break;
        }
      }
      cur = cur->next;
    }

    // 該当 bin が見つかった
    if (candidate) {
      best = candidate;
      mark_allocated(best);
      write_footer(best);
      break;
    }
  }

  // now, metadata points to the first free slot
  // and prev is the previous entry.

  // 該当 bin がない場合
  if (!best) {
    // There was no free slot available. We need to request a new memory region
    // from the system by calling mmap_from_system().
    //
    //     | metadata | free slot |
    //     ^
    //     metadata
    //     <---------------------->
    //            buffer_size
    size_t buffer_size = 4096;
    void *region = mmap_from_system(buffer_size);
    init_region(region, buffer_size);
    my_metadata_t *first = (my_metadata_t *)((char *)region + sizeof(size_t));
    add_to_bin(first);
    return my_malloc(size); // 再度 malloc する
  }

  // 空き領域 bin から削除する
  remove_from_bin(best);

  // |ptr| is the beginning of the allocated object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr

  // |ptr| is the beginning of the allocated object.
  void *ptr = best + 1;
  size_t remaining_size = best->size - size;
  // 分割するためには新しいメタデータ、フッタ、最小ペイロードが必要
  const size_t min_payload = 8;
  if (remaining_size >= sizeof(my_metadata_t) + sizeof(size_t) + min_payload) {
    // Shrink the metadata for the allocated object
    // to separate the rest of the region corresponding to remaining_size.
    // If the remaining_size is not large enough to make a new metadata,
    // this code path will not be taken and the region will be managed
    // as a part of the allocated object.
    best->size = size;
    mark_allocated(best);
    write_footer(best);
    // Create a new metadata for the remaining free slot.
    //
    // ... | metadata | object | metadata | free slot | ...
    //     ^          ^        ^
    //     metadata   ptr      new_metadata
    //                 <------><---------------------->
    //                   size       remaining size
    my_metadata_t *new_metadata =
        (my_metadata_t *)((char *)ptr + size + sizeof(size_t));
    // new_payload = remaining_size - header - footer
    new_metadata->size =
        remaining_size - sizeof(my_metadata_t) - sizeof(size_t);

    // 空き領域に設定してフッタを書き、bin に追加
    new_metadata->next = NULL;
    new_metadata->prev = NULL;
    mark_free(new_metadata);
    write_footer(new_metadata);
    add_to_bin(new_metadata);
  } else {
    mark_allocated(best);
    write_footer(best);
  }

  return ptr;
}

// This is called every time an object is freed.  You are not allowed to
// use any library functions other than mmap_from_system / munmap_to_system.
void my_free(void *ptr) {
  // Look up the metadata. The metadata is placed just prior to the object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
  mark_free(metadata);
  write_footer(metadata);

  // 左右の領域
  my_metadata_t *prev = get_prev_block(metadata);
  my_metadata_t *next = get_next_block(metadata);

  // 左も空き領域の場合
  if (prev && is_free(prev)) {
    remove_from_bin(prev);
    // 左領域のサイズを右に拡張する
    prev->size = payload_size(prev) + sizeof(my_metadata_t) + sizeof(size_t) +
                 payload_size(metadata);
    write_footer(prev);
    metadata = prev;
  }

  // 右も空き領域の場合
  if (next && is_free(next)) {
    remove_from_bin(next);
    // 領域本体のサイズを右に拡張する
    metadata->size = payload_size(metadata) + sizeof(my_metadata_t) +
                     sizeof(size_t) + payload_size(next);
    write_footer(metadata);
  }

  add_to_bin(metadata);
}

// This is called at the end of each challenge.
void my_finalize() {
  // Nothing is here for now.
  // feel free to add something if you want!
}

void test() {
  // Implement here!
  assert(1 == 1); /* 1 is 1. That's always true! (You can remove this.) */
}
