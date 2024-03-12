import unittest

from src.datastructures import LRUCache, RandomStack

class ClientTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_lru_cache(self):

        cache = LRUCache(5)
        cache.put("k_1", "v_1")
        
        assert cache.get("k_1") == "v_1"
        assert not cache.get("k_2")

        cache.put("k_2", "v_2")
        cache.put("k_3", "v_3")
        cache.put("k_4", "v_4")
        cache.put("k_5", "v_5")
        cache.put("k_1", "v_1")
        cache.put("k_6", "v_6")

        assert cache.get("k_1") == "v_1"