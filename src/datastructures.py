from collections import OrderedDict
import random


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            return None

    def put(self, key, value):
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value

    def __len__(self):
        return len(self.cache)


class RandomStack:
    def __init__(self) -> None:
        self.internal_list = []

    def __len__(self):
        return len(self.internal_list)

    def put(self, item):
        self.internal_list.append(item)

    def get(self):
        self._shuffle()
        return self.internal_list.pop()

    def _shuffle(self):
        random.shuffle(self.internal_list)
