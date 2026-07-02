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

#define BIN_SIZE 32

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

// 空き領域リストに追加
void my_add_to_free_list(my_metadata_t *metadata) {
  assert(!metadata->next);
  metadata->next = my_heap.free_head;
  my_heap.free_head = metadata;
}

// 空き領域リストから除外
void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    my_heap.free_head = metadata->next;
  }
  metadata->next = NULL;
}

// 領域サイズ -> bin を計算
static int size_to_bin(size_t size) {
  size_t bin_idx = size / 1000;

  // 超過した場合
  if (bin_idx >= BIN_SIZE) {
    bin_idx = BIN_SIZE - 1;
  }

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
  // prev->next を変更
  if (m->prev) {
    m->prev->next = m->next;
  } else {
    bins[size_to_bin(m->size)] = m->next;
  }

  // next->prev を変更
  if (m->next) {
    m->next->prev = m->prev;
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

// my_malloc() is called every time an object is allocated.
// |size| is guaranteed to be a multiple of 8 bytes and meets 8 <= |size| <=
// 4000. You are not allowed to use any library functions other than
// mmap_from_system() / munmap_to_system().
void *my_malloc(size_t size) {
  // First-fit: Find the first free slot the object fits.
  // TODO: Update this logic to Best-fit!

  my_metadata_t *best = NULL;
  size_t best_size = INFINITY;
  int bin_idx = size_to_bin(size); // 該当 bin のインデックス

  // サイズが最小の空き領域を求める（該当 bin を探す）
  for (int i = bin_idx; i < BIN_SIZE; i++) {
    my_metadata_t *cur = bins[i]; // 連結リストの現在ノード
    my_metadata_t *candidate = NULL;
    size_t candidate_size = INFINITY;

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
      break;
    }
  }

  // now, metadata points to the first free slot
  // and prev is the previous entry.

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
    my_metadata_t *metadata = (my_metadata_t *)mmap_from_system(buffer_size);
    metadata->size = buffer_size - sizeof(my_metadata_t);
    metadata->next = NULL;
    metadata->prev = NULL;
    add_to_bin(metadata);
    // Now, try my_malloc() again. This should succeed.
    return my_malloc(size);
  }

  remove_from_bin(best);

  // |ptr| is the beginning of the allocated object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr

  // 確保する領域のサイズが足りない
  void *ptr = best + 1;
  size_t remaining_size = best->size - size;
  if (remaining_size > sizeof(my_metadata_t)) {
    // Shrink the metadata for the allocated object
    // to separate the rest of the region corresponding to remaining_size.
    // If the remaining_size is not large enough to make a new metadata,
    // this code path will not be taken and the region will be managed
    // as a part of the allocated object.
    best->size = size;
    // Create a new metadata for the remaining free slot.
    //
    // ... | metadata | object | metadata | free slot | ...
    //     ^          ^        ^
    //     metadata   ptr      new_metadata
    //                 <------><---------------------->
    //                   size       remaining size
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
    new_metadata->size = remaining_size - sizeof(my_metadata_t);
    new_metadata->next = NULL;
    new_metadata->prev = NULL;
    // Add the remaining free slot to the free list.
    add_to_bin(new_metadata);
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

  // 連結リストから外す
  metadata->next = NULL;
  metadata->prev = NULL;

  // 該当 bin に追加
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
