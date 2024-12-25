from super_set_list_bit import SuperSetListBit
import itertools
import unittest
import random
import time
from itertools import combinations
import cProfile
import pstats
from collections import deque

class SuperSetTableBit:
    def __init__(self, root_list):
        # root_listの要素をすべてfrozensetに変換
        self.root_list = root_list
        self.list_table = {}
        self.list_table_key = deque()
        #self.srs_dic = srs_dic
        #self.srs_dic[frozenset()] = self.bit_score(frozenset())
        self.add_list(SuperSetListBit.new_root_list(self.root_list))
        #self.Q_dic = Q_dic
        #self.Q_dic_inverse = self.inverse_dic(Q_dic)


    # keyをseed_setとしてlist_tableに保存
    def add_list(self, set_list):
        seed_set = set_list.seed_set()
        self.list_table[seed_set] = set_list
        self.list_table_key.append(seed_set)

    # list_tableに新しいリストを追加
    def add_new_list(self, mother_list, atom_list):
        #print("mother_list,atom_list:",vars(mother_list),atom_list)
        new_list = SuperSetListBit(mother_list=mother_list, atom_list_bit=atom_list)
        #print("new_list:",vars(new_list))
        self.add_list(new_list)
    
        return new_list
    
    # seed_setに対応するスーパーセットが未探索かつフラグがTrueの場合、スーパーセットを取得
    def get_list(self, seed_set_bit, auto_new_p=False):
        _list = self.list_table.get(seed_set_bit)
        if _list is None and auto_new_p:
            sub_seed_set, diff_atom_list = self.find_largest_sub_seed_set(seed_set_bit)
            _list = self.add_new_list(self.get_list(sub_seed_set, False), diff_atom_list)
        return _list
    
    def __getitem__(self, seed_set):
        return self.get_list(seed_set, False)
    
    # seed_setの部分集合の内、list_tableに存在する最大の部分集合を検索
    def find_largest_sub_seed_set(self, seed_set_bit):
        count = 0
        #for seed_set_key_bit in reversed(list(self.list_table.keys())):
        for seed_set_key_bit in reversed(self.list_table_key):
            count += 1
            if seed_set_bit & seed_set_key_bit == seed_set_key_bit:
                diff_atom_list = self.set_diff(seed_set_bit,seed_set_key_bit)
                return seed_set_key_bit,diff_atom_list
        return 0,seed_set_bit
    
    def set_diff(self, larger_set_bit, smaller_set_bit):
        """
        larger_set から smaller_set を引いた差分を返す。
        """
        diff_bit = larger_set_bit & ~smaller_set_bit
        return diff_bit

    def bit_score(self, Z):
        set_score = 0
        for z in Z:
            set_score += 2**self.Q_dic[z]
        return set_score
    
    def inverse_dic(self,dictionary):
	    return {v:k for k,v in dictionary.items()}
    

class TestSuperSetList(unittest.TestCase):
    def setUp(self):
        """
        Set up method to display the test name.
        """
        name = f"{self._testMethodName}({self.__class__.__name__})"
        print(f"***** Running: {name} *****")
        super().setUp()

    def test_a(self):
        count = 0
        srs_set_list = [128, 96, 40, 192, 144, 72, 24, 130, 160, 36, 66, 136, 132, 152, 74, 100, 112, 28, 56, 104, 168, 140, 208, 98, 88, 224, 196, 164, 146, 70, 44, 138, 194, 52, 82, 134, 176, 76, 148, 162, 200, 184, 156, 92, 106, 240, 210, 180, 150, 60, 172, 102, 204, 216, 142, 78, 120, 212, 166, 170, 198, 228, 178, 86, 202, 108, 90, 154, 226, 116, 114, 232, 206, 186, 218, 220, 244, 124, 248, 242, 174, 234, 182, 230, 94, 158, 122, 236, 118, 214, 110, 188, 190, 222, 252, 238, 250, 126, 246, 254]
        ss_table = SuperSetTableBit(srs_set_list)
        print(vars(ss_table.list_table[0]))
        for Z_bit in srs_set_list:
            essential_flag = True
            Q_list = self.extract_set_bits(Z_bit)
            for Q_bit in Q_list:
                Z_pp_bit = Z_bit & ~Q_bit
                super_set_list = ss_table.get_list(Z_pp_bit, True)
                def process_set(_set):
                    return None
                super_set_list.each(process_set)
                #print("known_list:",super_set_list.known_list)
                print("len_known_list:",len(super_set_list.known_list))
                if super_set_list.known_list:
                    for Z_p_bit in super_set_list.known_list:
                        count+=1
                        print("left:",(Z_bit - (Z_bit & Z_p_bit)))
                        print("right:",2**Q_bit)
                        if (Z_bit - (Z_bit & Z_p_bit)) == 2**Q_bit:
                            print("aaaa")
            print("len_count:",count)

    def extract_set_bits(self,num):
        result = []
        bit_position = 0
        while num > 0:
            if num & 1 == 1:
                result.append(bit_position)
            
            num >>= 1
            bit_position += 1
        return result
    
if __name__ == "__main__":
    unittest.main()
