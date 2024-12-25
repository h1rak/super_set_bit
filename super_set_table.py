from super_set_list import SuperSetList
import itertools
import unittest
import random
import time
from itertools import combinations
import cProfile
import pstats
from collections import deque

class SuperSetTable:
    def __init__(self, root_list,srs_dic,Q_dic):
        # root_listの要素をすべてfrozensetに変換
        self.root_list = [frozenset(x) for x in root_list]
        self.list_table = {}
        self.keys_stack = deque()
        self.srs_dic = srs_dic
        self.srs_dic[frozenset()] = self.bit_score(frozenset())
        self.add_list(SuperSetList.new_root_list(self.root_list))
        self.Q_dic = Q_dic
        self.Q_dic_inverse = self.inverse_dic(Q_dic)


    # keyをseed_setとしてlist_tableに保存
    def add_list(self, set_list):
        seed_set = frozenset(set_list.seed_set())
        self.list_table[seed_set] = set_list
        self.keys_stack.append(seed_set)
        #self.sorted_keys.appendleft(frozenset(set_list.seed_set()))

    # list_tableに新しいリストを追加
    def add_new_list(self, mother_list, atom_list):
        start = time.time()
        #print("mother_list,atom_list:",vars(mother_list),atom_list)
        new_list = SuperSetList(mother_list=mother_list, atom_list=atom_list, srs_dic=self.srs_dic, Q_dic=self.Q_dic)
        #print("new_list:",vars(new_list))
        self.add_list(new_list)
        end = time.time()
        #print("add_new_list:",end-start)
        return new_list
    
    # seed_setに対応するスーパーセットが未探索かつフラグがTrueの場合、スーパーセットを取得
    def get_list(self, seed_set, auto_new_p=False):
        start = time.time()
        seed_set = frozenset(seed_set)
        _list = self.list_table.get(seed_set)
        #if _list is not None:
            #print("seed_set,_list:",seed_set,vars(_list))
        if _list is None and auto_new_p:
            sub_seed_set, diff_atom_list = self.find_largest_sub_seed_set(seed_set)
            #print("sub_seed_set,diff_atom_list:",sub_seed_set,diff_atom_list)
            _list = self.add_new_list(self.get_list(sub_seed_set, False), diff_atom_list)
            #print("__:",vars(_list))
        #print("_list:",vars(_list))
        end = time.time()
        #print("get_list:",end-start)
        return _list
    
    def __getitem__(self, seed_set):
        return self.get_list(seed_set, False)
    
    # seed_setの部分集合の内、list_tableに存在する最大の部分集合を検索
    def find_largest_sub_seed_set(self, seed_set):
        start = time.time()
        n = len(seed_set)
        count = 0
        #print("seed_set:",seed_set)
        #seed_set_score = self.bit_score(seed_set)
        #seed_set_score = self.srs_dic[seed_set]
        #seed_list = list(seed_set)
        #seed_list.pop()
        #seed_list_score = self.srs_dic[frozenset(seed_list)]
        #if seed_set_score & seed_list_score == seed_list_score:
        #    diff_atom_list = self.set_diff(seed_set,frozenset(seed_list))
        #    return frozenset(seed_list),diff_atom_list
        #for seed_set_key in reversed(list(self.list_table.keys())):
            #seed_set_key_score = self.bit_score(seed_set_key)
        #    count += 1
        #    seed_set_key_score = self.srs_dic[seed_set_key]
            #print(seed_set_key_score)
        #    if seed_set_score & seed_set_key_score == seed_set_key_score:
                #start = time.time()
        #        diff_atom_list = self.set_diff(seed_set,seed_set_key)
        #        end = time.time()
                #print("set_diff:",end-start)
        #        print("find_largest_sub_seed_set:",end-start)
        #        print(count)
                #print("seed_set_key:",seed_set_key)
                #print("diff_atom_list:",diff_atom_list)
                #print("len_seed_set_key:",len(seed_set_key))
                #print("len_seed_set:",len(seed_set))
                #print("sees_set_key:",seed_set_key)
                #break
        #        return frozenset(seed_set_key),diff_atom_list
        #end = time.time()
        #print("find_largest_sub_seed_set:",end-start)
        #print("count:",count)
        #return frozenset(),seed_set
        while n > 0:
            n -= 1
            for seed_sub_set in itertools.combinations(seed_set, n):
                count+=1
                if frozenset(seed_sub_set) in self.list_table:
                    diff_atom_list = self.set_diff(seed_set, frozenset(seed_sub_set))
                    end = time.time()
                    #print("diff_atom_list:",diff_atom_list)
                    return frozenset(seed_sub_set), diff_atom_list
        return frozenset(()), seed_set
    
    def set_diff(self, larger_set, smaller_set):
        """
        larger_set から smaller_set を引いた差分を返す。
        """
        return frozenset(atom for atom in larger_set if atom not in smaller_set)
        start = time.time()
        diff_atom_list = set()
        #larger_set_score = self.bit_score(larger_set)
        larger_set_score = self.srs_dic[larger_set]
        #smaller_set_score = self.bit_score(smaller_set)
        smaller_set_score = self.srs_dic[smaller_set]
        diff_score = larger_set_score & ~smaller_set_score
        #print(self.Q_dic)
        bit_len = diff_score.bit_length()
        for i in range(bit_len):
            if 2**i & diff_score == 2**i:
                diff_atom_list.add(self.Q_dic_inverse[i])
        end = time.time()
        #print("set_diff_time:",end-start)
        return frozenset(diff_atom_list)
        #return frozenset(atom for atom in larger_set if atom not in smaller_set)

    def bit_score(self, Z):
        set_score = 0
        for z in Z:
            set_score += 2**self.Q_dic[z]
        return set_score
    
    def inverse_dic(self,dictionary):
	    return {v:k for k,v in dictionary.items()}
    
class TestSuperSetTable(unittest.TestCase):
    def gen_comb_list(self, atom_list, nof_drop=0):
        comb_list = []
        for k in range(len(atom_list) + 1):
            comb_list.extend(itertools.combinations(atom_list, k))
        comb_list = [list(c) for c in comb_list]
        for _ in range(nof_drop):
            if comb_list:
                comb_list.pop(random.randint(0, len(comb_list) - 1))
        return comb_list
    
    def gen_comb_list_frozen(self, atom_list, n):
        """
        atom_listから全ての組み合わせを生成し、frozensetのリストを返す
        :param atom_list: 元の要素リスト
        :param n: 特定の組み合わせのサイズ (n=0 の場合、全てのサイズの組み合わせを生成)
        :return: frozensetのリスト
        """
        comb_list = []
        if n == 0:
            for i in range(1, len(atom_list) + 1):
                comb_list.extend(frozenset(tuple(comb)) for comb in combinations(atom_list, i))
        else:
            comb_list.extend(frozenset(tuple(comb)) for comb in combinations(atom_list, n))
        return comb_list

    def gen_comb_list2(self, atom_list, drop_prob=0.0):
        comb_list = []
        for k in range(len(atom_list) + 1):
            comb_list.extend(itertools.combinations(atom_list, k))
        comb_list = [list(c) for c in comb_list]
        nof_drop = int(len(comb_list) * drop_prob)
        for _ in range(nof_drop):
            if comb_list:
                comb_list.pop(random.randint(0, len(comb_list) - 1))
        return comb_list

    def test_a(self):
        """
        スーパーセットテーブルのテスト
        """
        #atom_list = ["a", 'b', 'c']
        n = 0
        #root_list = self.gen_comb_list(atom_list, n)
        #print("Root List:", root_list)
        #root_set_list = self.gen_comb_list_frozen(atom_list, n)  # 修正点
        root_set_list = [frozenset({('a_2',), ('a_1', 'a_3')}), frozenset({('a_3',), ('a_1', 'a_2')}), frozenset({('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_1',), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_2', 'a_3')}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_1', 'a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_1',), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1',), ('a_2', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_2', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_3',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_1', 'a_2', 'a_3')}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_1',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_3',)}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_3',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1',), ('a_3',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_1', 'a_3'), ('a_3',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_1',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1',), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1', 'a_2')}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_3',), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_3'), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3')}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_1', 'a_3'), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_3',)}), frozenset({('a_2',), ('a_1',), ('a_1', 'a_2', 'a_3'), ('a_1', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1', 'a_2'), ('a_2', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2')}), frozenset({('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1',), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',)}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_3',), ('a_2', 'a_3'), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1',), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1', 'a_2')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3'), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')}), frozenset({('a_2',), ('a_1', 'a_2', 'a_3'), ('a_3',), ('a_2', 'a_3'), ('a_1',), ('a_1', 'a_2'), ('a_1', 'a_3')})]
        print("Root Set List:", root_set_list)
        ss_table = SuperSetTable(root_set_list)
        print("ss_table:", vars(ss_table))
        count = 0
        max_count = len(root_set_list)

        for a_set in root_set_list:
            #super_set_list = ss_table.get_list(a_set, True)
            
            for Q in a_set:
                Z = a_set - {Q}
                count += 1
                #print("a_set:",a_set)
                #print("Q,Z:",Q,Z)
                super_set_list = ss_table.get_list(Z, True)  # 修正点
                #print("super_set_list:",vars(super_set_list))
                #print("known_list:",super_set_list.known_list)
                def process_set(_set):
                    print([count, a_set, _set])
                super_set_list.each(process_set)
                print(super_set_list.atom_list)
                #print("super_set_list:",vars(super_set_list))
                #print("konwn_list:",super_set_list.known_list)
            #print(vars(super_set_list))
            if count >= max_count:
                    break
    def test_a1(self):
        """
        スーパーセットテーブルのテスト
        """
        atom_list = ['a', 'b', 'c', 'd', 'e', 'f']
        phis_dic = {phi: i for i, phi in enumerate(atom_list)}
        Q_dic = {q: sum(2 ** phis_dic[qq] for qq in q) for q in Q}
        n = 0
        root_list = self.gen_comb_list(atom_list, n)
        print("Root List:", root_list)

        ss_table = SuperSetTable(root_list,Q_dic)
        print("ss_table:",vars(ss_table))
        count = 0
        max_count = len(root_list)

        def run_test():
            count = 0
            for a_set in root_list:
                count += 1
                super_set_list = ss_table.get_list(a_set, True)

                if super_set_list is None:
                    print(f"Warning: No SuperSetList for {a_set}")
                    continue
                #print("super_set_list:",vars(super_set_list))
                def process_set(_set):
                    print([count, a_set, _set])
                super_set_list.each(process_set)
                #print("super_set_list:",vars(super_set_list))
                if count >= max_count:
                    break

            # プロファイルを実行
        profiler = cProfile.Profile()
        profiler.enable()
        run_test()
        profiler.disable()

        # 結果の表示
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()

    def test_b(self):
        root_list = [['a'], ['a', 'b'], ['a', 'c'], ['a', 'b', 'c', 'd']]
        ss_table = SuperSetTable(root_list)
        seed_set = ['a', 'b', 'c']
        result = ss_table.get_list(seed_set, auto_new_p=True)
        print("Resulting List:", vars(result))
        count = 0
        for a_set in root_list:
            count+=1
            result = ss_table.get_list(a_set, auto_new_p=True)
            print("result:",vars(result.mother_list))
            def process_set(_set):
                print([count, a_set, _set])
            result.each(process_set)

    def test_c(self):
        atom_list = ['a', 'b', 'c', 'd', 'e', 'f']
        #atom_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
        n = 10
        root_list = self.gen_comb_list(atom_list, n)
        ss_table = SuperSetTable(root_list)
        count = 0
        for z_set in root_list:
            if len(z_set) == 0:
                continue
            for q in z_set:
                z_subset = z_set.copy()
                z_subset.remove(q)
                
                for subset in ss_table.get_list(z_subset, True):
                    count += 1
                    if subset is None:
                        break
                    #print(z_subset,subset)
                    

        size = len(root_list)
        result = ['result', 'count', count, size, count / (size * size)]
        print(result)
        print(vars(ss_table))
        print(len(ss_table.root_list),len(ss_table.list_table))
        print(ss_table.root_list)
        print(ss_table.list_table)

    def test_d(self):
        # atom_list の定義
        # atom_list = ['a', 'b', 'c', 'd', 'e', 'f']
        # atom_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
        atom_list = list("abcdefghijklmnopq")

        prob = 0.5
        root_list = self.gen_comb_list2(atom_list, prob)

        ss_table = SuperSetTable(root_list)

        check_count = 0
        z_set_count = 0
        start_time = time.time()
        pre_time = time.time()

        for z_set in root_list:
            z_set_count += 1
            if len(z_set) == 0:
                continue
            list_size = 0
            for q in z_set:
                z_subset = z_set.copy()
                z_subset.remove(q)
                for subset in ss_table.get_list(z_subset, True):
                    check_count += 1
                    list_size += 1
                    if subset is None:
                        break

            cycle_time = time.time()
            print([
                "cycle_zSet", z_set_count, len(ss_table.list_table),
                list_size, check_count,
                cycle_time - start_time, cycle_time - pre_time
            ])
            pre_time = cycle_time

        size = len(root_list)
        print(["result", "count", check_count, size, check_count / (size * size)])

    # プロファイル対象の関数
    def run_test(self):
            # root_list と Q_dic のサンプルデータ
            root_list = [["a"], ["a", "b"], ["b", "c"], ["c", "d"], ["e"]]
            Q_dic = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
            # SuperSetTableのインスタンスを作成
            table = SuperSetTable(root_list, Q_dic)
            # テスト対象のseed_set
            test_seed_set = frozenset(["a", "b", "c"])
            # get_list関数を実行
            super_list = table.get_list(test_seed_set, True)
            def process_set(_set):
                return None
            super_list.each(process_set)

if __name__ == '__main__':
    test = TestSuperSetTable()

        # プロファイルの開始
    profiler = cProfile.Profile()
    profiler.enable()
    test.run_test()
    # プロファイルの停止
    profiler.disable()

    # プロファイル結果の表示
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()