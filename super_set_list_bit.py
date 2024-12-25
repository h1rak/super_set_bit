import unittest
from itertools import combinations
from pprint import pprint
import logging
import pdb
import time
from itertools import product,chain,combinations,combinations_with_replacement

class SuperSetListBit:
    def __init__(self, mother_list=None, atom_list_bit=None, init_index=0):
        """
        Initialize the SuperSetList instance.
        
        :param mother_list: The parent SuperSetList instance (or None).
        :param atom_list: List of atoms to be added (or None).
        :param init_index: Initial index for the parent list.
        """
        self.known_list = []  # 現在までに見つかった要素のリスト
        self.mother_list = mother_list  # スーパーセットリスト
        self.atom_list_bit = atom_list_bit if atom_list_bit else 0  # フィルター条件のリスト
        self.mother_index = init_index  # 探索済みの位置
        self.is_complete = mother_list is None  # 探索フラグ
        self.seed_set_value = None  # 現在のスーパーセットリストで可能な最大積集合の記録
        self.seed_set()  # 最大積集合の初期化

        if self.mother_list and not atom_list_bit:
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

    def should_include(self, candidate_bit):
        # atom_listの要素が全てcandidateに含まれているか
        if candidate_bit & self.atom_list_bit == self.atom_list_bit:
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
            if not self.atom_list_bit:
                self.seed_set_value = 0
            else:
                self.seed_set_value = (self.mother_list.seed_set() if self.mother_list else 0 ) + self.atom_list_bit #if self.mother_list.seed_set() else 0
        return self.seed_set_value

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
        atom_list = [1, 2, 3]
        
        ss_list0 = SuperSetListBit.new_root_list([0,2,4,8,6,10,12,14])
        print(vars(ss_list0))
        ss_list0.each(lambda x: pprint(x))
        ss_list1 = SuperSetListBit(ss_list0, 2)
        ss_list2 = SuperSetListBit(ss_list1, 4)
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
        phis = ["a", "b", "c", "d", "e", "f"]
        Q = self.powerset(phis)
        phis_dic = {phi: i for i, phi in enumerate(phis)}
        Q_dic = {q: sum(2 ** phis_dic[qq] for qq in q) for q in Q}
        print(Q_dic)
        ss_list0 = SuperSetListBit.new_root_list(list(Q_dic.values()))
        k = 0
        ss_list0.each(lambda x: print([x]))
        
        ss_list1 = SuperSetListBit(ss_list0, 1)
        ss_list2 = SuperSetListBit(ss_list1, 2)
        ss_list3 = SuperSetListBit(ss_list2, 4)
        ss_list4 = SuperSetListBit(ss_list3, 8)
        print(vars(ss_list3))
        pprint([":init", ss_list4, ":seed", ss_list4.seed_set()])

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

    def powerset(self,iterable):
            powerset=[]
            s = list(iterable)
            return chain.from_iterable(combinations(s,r) for r in range(len(s)+1))

if __name__ == "__main__":
    unittest.main()