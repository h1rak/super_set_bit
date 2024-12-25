import unittest
from itertools import combinations
from pprint import pprint
import logging
import pdb
import time

class SuperSetList:
    def __init__(self, mother_list=None, atom_list=None, init_index=0, srs_dic={}, Q_dic={}):
        """
        Initialize the SuperSetList instance.
        
        :param mother_list: The parent SuperSetList instance (or None).
        :param atom_list: List of atoms to be added (or None).
        :param init_index: Initial index for the parent list.
        """
        self.known_list = []  # 現在までに見つかった要素のリスト
        self.mother_list = mother_list  # スーパーセットリスト
        self.atom_list = frozenset(atom_list) if atom_list else frozenset()  # フィルター条件のリスト
        self.mother_index = init_index  # 探索済みの位置
        self.is_complete = mother_list is None  # 探索フラグ
        self.seed_set_value = None  # 現在のスーパーセットリストで可能な最大積集合の記録
        self.seed_set()  # 最大積集合の初期化
        self.srs_dic = srs_dic
        self.Q_dic = Q_dic
        
        if self.mother_list and not atom_list:
            raise ValueError("atom_list is required to create a SuperSetList instance.")

    def set_known_list(self, known_list):
        """
        Set the known list.
        
        :param known_list: A list to set as the known list.
        """
        self.known_list = known_list

    @classmethod
    def new_root_list(cls, root_list):
        """
        Create a new root SuperSetList instance.
        
        :param root_list: Initial list to set as the root known list.
        :return: A new SuperSetList instance.
        """
        ss_list = cls()
        ss_list.set_known_list(root_list)
        return ss_list

    def nth(self, n):
        if n >= len(self.known_list) and self.is_complete:
            return None
        while n >= len(self.known_list):
            candidate = self.mother_list.nth(self.mother_index) if self.mother_list else None
            self.mother_index += 1
            if candidate is None:
                self.is_complete = True
                return None
            start = time.time()
            if self.should_include(candidate):
                self.known_list.append(candidate)
            end = time.time()
            #print("should_include:",end-start)
        return self.known_list[n]

    def should_include(self, candidate):
        # atom_listの要素が全てcandidateに含まれているか
        return self.atom_list.issubset(candidate)
        #atom_score = self.bit_score(self.atom_list)
        #candidate_score = self.bit_score(candidate)
        if self.atom_list not in self.srs_dic:
            atom_score = self.bit_score(self.atom_list)
            self.srs_dic[self.atom_list]= atom_score
        else:
            atom_score = self.srs_dic[self.atom_list]
        if candidate not in self.srs_dic:
            candidate_score = self.bit_score(candidate)
            self.srs_dic[candidate] = candidate_score
        else:
            candidate_score = self.srs_dic[candidate]
        if candidate_score & atom_score == atom_score:
            return True
        else:
            return False

    def __getitem__(self, n):
        """
        Allow access to nth element using square brackets.
        
        :param n: Index of the element to retrieve.
        :return: The nth element.
        """
        return self.nth(n)

    def each(self, callback):
        n = 0
        start = time.time()
        while True:
            _set = self[n]  # 実際はself.__getitem__(n)
            if _set is None:
                break
            callback(_set)
            n += 1
        end = time.time()
        #print("each:",end-start)
        #print("count:",self.count)

    def seed_set(self):
        # seed_setを階層的に作成
        if self.seed_set_value is None:
            if not self.atom_list:
                self.seed_set_value = frozenset()
            else:
                self.seed_set_value = frozenset(
                    (self.mother_list.seed_set() if self.mother_list else frozenset()) | self.atom_list
                )
        #print("seed_set_value:", self.seed_set_value)
        return self.seed_set_value
    
    def bit_score(self, Z):
        set_score = 0
        for z in Z:
            set_score += 2**self.Q_dic[z]
        return set_score


class TestSuperSetList(unittest.TestCase):
    def setUp(self):
        """
        Set up method to display the test name.
        """
        name = f"{self._testMethodName}({self.__class__.__name__})"
        print(f"***** Running: {name} *****")
        super().setUp()

    def test_a(self):
        """
        Simple list test
        """
        #ss_list0 = SuperSetList.new_root_list([["a"], ["b"], ["c"]])
        atom_list = ["a", "b", "c"]
        comb_list = self.gen_comb_list(atom_list)
        print(comb_list)
        ss_list0 = SuperSetList.new_root_list(comb_list)
        print(vars(ss_list0))
        ss_list0.each(lambda x: pprint(x))
        ss_list1 = SuperSetList(ss_list0, ["a"])
        ss_list2 = SuperSetList(ss_list1, ["b"])
        k = 0
        def print_each(set):
            nonlocal k
            print([k, set])
            k += 1
        print(vars(ss_list2))
        ss_list2.each(print_each)
        
    def test_b(self):
        """
        Test the whole combination.
        """
        atom_list = ["a", "b", "c", "d", "e", "f"]
        comb_list = self.gen_comb_list(atom_list)
        print(comb_list)
        ss_list0 = SuperSetList.new_root_list(comb_list)
        k = 0
        ss_list0.each(lambda x: print([x]))
        
        ss_list1 = SuperSetList(ss_list0, ["a"])
        ss_list2 = SuperSetList(ss_list1, ["b"])
        ss_list3 = SuperSetList(ss_list2, ["c"])
        ss_list4 = SuperSetList(ss_list3, ["d"])
        #print(vars(ss_list3))
        #pprint([":init", ss_list4, ":seed", ss_list4.seed_set()])

        k = 0
        def print_each(set):
            nonlocal k
            print([k, set])
            k += 1
        ss_list1.each(print_each)
        k = 0
        #ss_list2.each(print_each)
        k = 0
        #ss_list3.each(print_each)
        k = 0
        ss_list4.each(print_each)

    def gen_comb_list(self, atom_list):
        """
        Generate all combinations of the given atom list.
        
        :param atom_list: List of atoms.
        :return: List of all combinations.
        """
        comb_list = []
        for k in range(len(atom_list) + 1):
            comb_list.extend(list(combinations(atom_list, k)))
        return [list(c) for c in comb_list]


if __name__ == "__main__":
    unittest.main()