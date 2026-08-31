import random
from typing import Any

def merge_sort(arr: list[Any]) -> list[Any]:
    if len(arr) <= 1:
        return arr[:]

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list[Any], right: list[Any]) -> list[Any]:
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort(arr: list[Any]) -> list[Any]:
    items = arr[:]
    _quick_sort_in_place(items, 0, len(items) - 1)
    return items


def _quick_sort_in_place(arr: list[Any], low: int, high: int) -> None:
    if low >= high:
        return
    pivot_index = _partition(arr, low, high)
    _quick_sort_in_place(arr, low, pivot_index - 1)
    _quick_sort_in_place(arr, pivot_index + 1, high)


def _partition(arr: list[Any], low: int, high: int) -> int:
    random_index = random.randint(low, high)
    arr[random_index], arr[high] = arr[high], arr[random_index]

    pivot = arr[high]
    i = low - 1  
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1