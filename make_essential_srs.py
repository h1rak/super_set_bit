from super_set_table import SuperSetTable
from super_set_table_bit import SuperSetTableBit
import numpy as np
import matplotlib.pyplot as plt
import random
from itertools import product,chain,combinations,combinations_with_replacement
from copy import copy
import json
import time
from functools import reduce
from linear import CSPSolver
#def find_all_x(num_elements):
    # 0.0から1.0までの値を0.1刻みで生成
#    values = [x / 10 for x in range(11)]

    # 合計が1になるパターンのみを抽出
#    patterns = []
#    for combo in product(values, repeat=num_elements):
#        if sum(combo) == 1.0:
#            patterns.append(combo)

#    return patterns
class SatisfiabilityChecker:
    def __init__(self, elements, probabilities, combinations):
        self.elements = elements
        self.probabilities = probabilities
        self.combinations = combinations

    def find_all_x(self,num_elements):
        values = [x / 10 for x in range(11)]  # 0.0から1.0まで0.1刻みの値
        target_sum = 10  # 合計が1.0に相当する整数値

        # 合計がtarget_sumになる組み合わせを見つける
        all_combos = combinations_with_replacement(range(11), num_elements)
        valid_combos = [
            combo for combo in all_combos
            if sum(combo) == target_sum
        ]
        # 有効な組み合わせを元の値に変換
        patterns = [
            tuple(value / 10 for value in combo) for combo in valid_combos
        ]
        return patterns

    def unique_permutations(self, arr):
        from collections import Counter

        def backtrack(path, counter):
            if len(path) == len(arr):
                result.append(tuple(path))
                return
            for num in counter:
                if counter[num] > 0:
                    path.append(num)
                    counter[num] -= 1
                    backtrack(path, counter)
                    path.pop()
                    counter[num] += 1
    
        result = []
        counter = Counter(arr)  # 各要素の出現回数をカウント
        backtrack([], counter)
        return result

    def make_srs(self,x,phis,p,Q,sign):
        x_sum=sum(x)
        x_flag=True
        x_sum_flag=True
        srs=[]
        for x_j in x:
            if x_j<0:
                x_flag=False
        for i in range(len(p)):
            x_sum_phi_in_q=0
            phis_ls=[]
            for k in range(len(Q)):
                if phis[i] in Q[k]:
                    phis_ls.append(Q[k])
                    x_sum_phi_in_q+=x[k]
            if sign[i]=="ope_gt":
                if x_sum_phi_in_q<p[i]:
                    x_sum_flag=False
            if sign[i]=="ope_et":
                if x_sum_phi_in_q<=p[i]:
                    x_sum_flag=False

        if x_sum==1 and x_flag and x_sum_flag:
            for j in range(len(x)):
                if x[j]!=0:
                    srs.append(tuple(Q[j]))
            return srs
        else:
            return False
    
    def make_srs_set(self,num_elements,phis,p,Q,sign):
        patterns = self.find_all_x(num_elements)
        srs_set=set()
        for arr in patterns:
            unique_patterns = self.unique_permutations(arr)
            print(len(unique_patterns))
            #for pattern in unique_patterns:
            #    pattern = list(pattern)
            #    pattern.insert(0,0)

            for pattern in unique_patterns:
                pattern = list(pattern)
                pattern.insert(0,0)
                srs = self.make_srs(pattern,phis,p,Q,sign)
                if srs:
                    #srs_list = [list(tup) for tup in srs]
                    with open('./srs.txt', 'a', encoding="utf-8") as f:
                        json_data = {"x": pattern, "srs": srs}
                        f.write(str(json_data))
                        f.write('\n')
                    srs_set.add(frozenset(srs))
        return srs_set

    def powerset(self,iterable):
        powerset=[]
        s = list(iterable)
        return chain.from_iterable(combinations(s,r) for r in range(len(s)+1))


    def is_essential(self,Z,Z_p,essential_srs):
        essential_flag=True
        #print(Z_p)
        for Q in Z:
            Q_powerset = set()
            powerset = self.powerset(Q)
            for i in powerset:
                Q_powerset.add(i)
            Q_powerset.remove(())
            Z_pp_powerset = self.powerset(Q_powerset)
            for Z_pp in Z_pp_powerset:
                #print("Z_pp:",Z_pp)
                Z_ = copy(Z)
                for j in Z_pp:
                    Z_.add(j)
                #print("Z_:",Z_)
                Z_.remove(Q)
                #print("Q:",Q)
                #print("Z_:",Z_)
                if Z_ in Z_p:
                    essential_flag=False
                    break
        #print("Z_ppp",Z_p)
        #print("Z",Z)
        #print(essential_flag)
        if essential_flag:
            essential_srs.append(Z)

        return essential_srs
    
    def is_essential_reverse(self,Z,srs_set,essential_srs):
        essential_flag=True
        #print("srs_set:",srs_set)
        for Q in Z:
            #print("Q:",Q)
            for Z_p in srs_set:
                if Q in Z_p:
                    continue
                else:
                    #print("Z_p:",Z_p)
                    Z_ = copy(Z)
                    Z_.remove(Q)
                    #print("Z_:",Z_)
                    if Z_.issubset(Z_p):
                        Z_p = set(Z_p)
                        Z_p.difference_update(Z_)
                        #print("new Z_p:",Z_p)
                        q = set()
                        for z in Z_p:
                            for i in z:
                                q.add(i)
                        #print("q:",q)
                        if q.issubset(set(Q)):
                            essential_flag = False
                        else:
                            continue
                    else:
                        continue

        if essential_flag:
            essential_srs.append(Z)

        return essential_srs
    
    def is_essential_reverse2(self,Z,srs_set,essential_srs):
        essential_flag=True
        #print("Z:",Z)
        for Q in Z:
            #print("Q:",Q)
            for Z_p in srs_set:
                if Q in Z_p:
                    continue
                else:
                    #Z_ = copy(Z)
                    Z_= Z - {Q}
                    if Z_.issubset(Z_p):
                        Z_p = set(Z_p)
                        remaining = Z_p - Z_
                        q = set().union(*[set(item) for item in remaining])
                        #print("Reverse2: remaining", remaining, "q", q)
                        #Z_p.difference_update(Z_)
                        #q = set()
                        #for z in Z_p:
                        #    for i in z:
                        #        q.add(i)
                        if q.issubset(set(Q)):
                            essential_flag = False
                            break
            if not essential_flag :
                break

        if essential_flag:
            essential_srs.append(Z)

        return essential_srs
    
    def is_essential_reverse3(self, Z, srs_set, essential_srs):
        essential_flag = True
        Z_p_flag = True
        Q_set = set()
        print(f"Zの本質性を確認中: {Z}")

        for Z_p in srs_set:
            R = set()
            # ZをZ_pから除いた残りの部分をチェック
            R_p = Z_p - Z
            for element_set in R_p:
                for element in element_set:
                    R.add(element)
            if Z == {('a_1', 'a_3'), ('a_2', 'a_3')}:
                print(f"Z: {Z}, Z_p: {Z_p}, R: {R}")
            for Q in Z:
                # 残りの部分がQの部分集合であるかをチェック
                if R.issubset(set(Q)):
                    essential_flag = False
                    Q_set.add(Q)
        print("Q:",Q_set,"essential_flag:",essential_flag)

        if not essential_flag:
            # Q_set内の各Qに対して、ZがZ_pに対して本質的かどうかをチェック
            for Q in Q_set:
                for Z_p in srs_set:
                    Z_pp_set = self.powerset(Z_p - Z)
                    for Z_pp in Z_pp_set:
                        # ZとZ_ppを組み合わせ、Qを除いた「right」集合を作成
                        right = Z | set(Z_pp)
                        right = right - {Q}
                        if Z_p == right:
                            print("Z_p:",Z_p,"Z_pp:",Z_pp)
                            Z_p_flag = False
                            break
                    if not Z_p_flag:
                        break
                if Z_p_flag:
                    print(f"Zは本質的です: {Z}")
                    essential_srs.append(list(Z))
        else:
            print(f"Zは本質的です: {Z}")
            essential_srs.append(list(Z))
        
        return essential_srs
    
    #とりあえず動く(なぜか遅い)
    def is_essential_bit_1(self, Q_dic, srs_set, srs_set_sorted_dic, essential_srs):
        search_space = {}
        count=0
        for Z in srs_set:
            count+=1
            essential_flag = True
            srs_sub_set = srs_set - {Z}
            #print(Z)
            for Q in Z:
                Z_p_set = set()
                Z_pp = Z - {Q}
                Z_score = self.bit_score(Q_dic,Z_pp)
                for Z_p in srs_sub_set:
                    if Z-Z_p == frozenset({Q}):
                        if Z_score & srs_set_sorted_dic[Z_p] == Z_score:
                            Z_p_set.add(Z_p)
                for Z_p in Z_p_set:
                    R_p = Z_p -Z
                    q = set().union(*[set(set(item)) for item in R_p])
                    q_ = tuple(sorted(q))
                    if Q_dic[q_] & Q_dic[Q] == Q_dic[q_]:
                        essential_flag = False
                        break
            if essential_flag:
                #with self.lock:
                essential_srs.append(Z)
            print(str(count)+"/"+str(len(srs_set)))
        return essential_srs
    
    #改良していく
    def is_essential_bit_2(self, Q_dic, srs_set, srs_set_sorted_dic, essential_srs):
        count=0
        for Z in srs_set:
            count+=1
            essential_flag = True
            srs_sub_set = srs_set - {Z}
            for Q in Z:
                Z_p_set = set()
                Z_pp = Z - {Q}
                if Z_pp in srs_set_sorted_dic:
                    Z_score = srs_set_sorted_dic[Z_pp]
                else:
                    Z_score = self.bit_score(Q_dic,Z_pp)
                    srs_set_sorted_dic[Z_pp] = Z_score
                for Z_p in srs_sub_set:
                    if Z-Z_p == frozenset({Q}):
                        if Z_score & srs_set_sorted_dic[Z_p] == Z_score:
                            Z_p_set.add(Z_p)
                            R_p = Z_p -Z
                            #print("R_p:",R_p)
                            q = set().union(*[set(set(item)) for item in R_p])
                            q_ = tuple(sorted(q))
                            #if q_==():
                            #    essential_flag = False
                            #    break
                            if Q_dic[q_] & Q_dic[Q] == Q_dic[q_]:
                                essential_flag = False
                                break
                    if not essential_flag:
                        break
            if essential_flag:
                essential_srs.append(Z)
            print(str(count)+"/"+str(len(srs_set)))
        return essential_srs
    
    def is_essential_bit(self, Q_dic, srs_set, srs_set_sorted, srs_set_sorted_dic, essential_srs):
        count=0
        len_count=0
        for Z in srs_set_sorted:
            start = time.time()
            count+=1
            essential_flag = True
            srs_sub_set = srs_set - {Z}
            #print(Z)
            for Q in Z:
                Z_p_set = set()
                Z_pp = Z - {Q}
                if Z_pp in srs_set_sorted_dic:
                    Z_pp_score = srs_set_sorted_dic[Z_pp]
                else:
                    Z_pp_score = self.bit_score(Q_dic,Z_pp)
                    srs_set_sorted_dic[Z_pp] = Z_pp_score
                for Z_p in srs_sub_set:
                    len_count+=1
                    #if Z-Z_p == frozenset({Q}):
                    Z_score = srs_set_sorted_dic[Z]
                    Z_p_score = srs_set_sorted_dic[Z_p]
                    if (Z_score - (Z_score & Z_p_score)) == 2**Q_dic[Q]:
                        if Z_pp_score & srs_set_sorted_dic[Z_p] == Z_pp_score:
                            Z_p_set.add(Z_p)
                            R_p = Z_p -Z
                            q = set().union(*[set(set(item)) for item in R_p])
                            q_ = tuple(sorted(q))
                            #if q_==():
                            #    if len(Z)==len(Z_p)+1:
                            #        essential_flag = False
                            #        break
                            #    else:
                            #        continue
                            if Q_dic[q_] & Q_dic[Q] == Q_dic[q_]:
                                essential_flag = False
                                break
                    if not essential_flag:
                        break
            if essential_flag:
                #with self.lock:
                essential_srs.append(Z)
            end= time.time()
            print("time:",end-start)
            print(str(count)+"/"+str(len(srs_set)))
            print("len_count:",len_count)
        return essential_srs
    
    def is_essential_bit_pruning(self, Q_dic, srs_set, srs_set_sorted, srs_set_sorted_dic, essential_srs):
        count=0
        ss_table = SuperSetTable(srs_set)
        print("ss_table:",vars(ss_table))
        for Z in srs_set_sorted:
            count+=1
            essential_flag = True
            #print(Z)
            for Q in Z:
                Z_p_set = set()
                Z_pp = Z - {Q}
                if Z_pp in srs_set_sorted_dic:
                    Z_pp_score = srs_set_sorted_dic[Z_pp]
                else:
                    Z_pp_score = self.bit_score(Q_dic,Z_pp)
                    srs_set_sorted_dic[Z_pp] = Z_pp_score
                super_set_list = ss_table.get_list(Z_pp,True)
                #print("known_list:",vars(super_set_list))
                for Z_p in super_set_list.known_list:
                    print("Z_p:",Z_p)
                #for Z_p in srs_sub_set:
                    #if Z-Z_p == frozenset({Q}):
                    Z_score = srs_set_sorted_dic[Z]
                    Z_p_score = srs_set_sorted_dic[Z_p]
                    if (Z_score - (Z_score & Z_p_score)) == 2**Q_dic[Q]:
                        #if Z_pp_score & srs_set_sorted_dic[Z_p] == Z_pp_score:
                            Z_p_set.add(Z_p)
                            R_p = Z_p -Z
                            q = set().union(*[set(set(item)) for item in R_p])
                            q_ = tuple(sorted(q))
                            #if q_==():
                            #    if len(Z)==len(Z_p)+1:
                            #        essential_flag = False
                            #        break
                            #    else:
                            #        continue
                            if Q_dic[q_] & Q_dic[Q] == Q_dic[q_]:
                                essential_flag = False
                                break
                    if not essential_flag:
                        break
            if essential_flag:
                #with self.lock:
                essential_srs.append(Z)
            print(str(count)+"/"+str(len(srs_set)))
        return essential_srs

    def is_essential_bit_pruning2(self, Q_dic, srs_set, srs_set_sorted, srs_set_sorted_dic, essential_srs):
        count = 0
        len_count = 0
        Z_count = 0
        Q_count = 0
        get_list_count = 0
        each_count = 0
        known_list_count = 0
        time_data = {"Z":0,"Q":0,"get_list":0,"each":0,"known_list_loop":0}
        #srs_set_list = list(srs_set_sorted_dic.values())
        ss_table = SuperSetTable(srs_set_sorted,srs_set_sorted_dic,Q_dic)
        #ss_table = SuperSetTable(srs_set_list)
        #print("ss_table:",vars(ss_table))
        for Z in srs_set_sorted:
            start_Z = time.time()
            Z_count += 1
            count += 1
            essential_flag = True
            #super_set_list = ss_table.get_list(Z, True)
            #def process_set(_set):
            #    return None
            #super_set_list.each(process_set)
            for Q in Z:
                start_Q = time.time()
                Q_count += 1
                #print("Z:",Z)
                #print("Q:",Q)
                Z_p_set = set()
                Z_pp = Z - {Q}
                if Z_pp in srs_set_sorted_dic:
                    Z_pp_score = srs_set_sorted_dic[Z_pp]
                else:
                    Z_pp_score = self.bit_score(Q_dic, Z_pp)
                    srs_set_sorted_dic[Z_pp] = Z_pp_score
                start_get_list = time.time()
                get_list_count += 1
                super_set_list = ss_table.get_list(Z_pp, True)
                time_data["get_list"] += time.time()-start_get_list
                #super_set_list = ss_table.get_list(Z_pp_score, True)
                start_each = time.time()
                each_count += 1
                def process_set(_set):
                    return None
                super_set_list.each(process_set)
                time_data["each"] += time.time()-start_each
                #print("atom_list:",super_set_list.atom_list)
                if super_set_list is None:
                    continue
                if super_set_list.known_list:
                    for Z_p in super_set_list.known_list:
                        start_known_list = time.time()
                        known_list_count += 1
                        len_count+=1
                        Z_score = srs_set_sorted_dic[Z]
                        Z_p_score = srs_set_sorted_dic[Z_p]
                        #Z_p_score = Z_p
                        #print("Z_bit:",Z_score)
                        #print("Z_p:",Z_p_score)
                        #print("Q:",Q_dic[Q])
                        if (Z_score - (Z_score & Z_p_score)) == 2**Q_dic[Q]:
                            Z_p_set.add(Z_p)
                            R_p = Z_p - Z
                            q = set().union(*[set(set(item)) for item in R_p])
                            q_ = tuple(sorted(q))
                            if Q_dic[q_] & Q_dic[Q] == Q_dic[q_]:
                                essential_flag = False
                                break
                        time_data["known_list_loop"] += time.time()-start_known_list
                        if not essential_flag:
                            break
                time_data["Q"] += time.time()-start_Q
            if essential_flag:
                essential_srs.append(Z)
            time_data["Z"] += time.time()-start_Z
            #print(str(count) + "/" + str(len(srs_set)))
            #print("len_count:",len_count)
        time_data["Z"] = time_data["Z"]/Z_count
        time_data["Q"] = time_data["Q"]/Q_count
        time_data["get_list"] = time_data["get_list"]/get_list_count
        time_data["each"] = time_data["each"]/each_count
        time_data["known_list_loop"] = time_data["known_list_loop"]/known_list_count
        #print("Timing Data (is_essential_bit_pruning2):", time_data)
        return essential_srs
    
    def is_essential_bit_pruning_integer(self, Q_dic, srs_set, srs_set_sorted, srs_set_sorted_dic, essential_srs):
        count = 0
        len_count = 0
        Z_count = 0
        Q_count = 0
        get_list_count = 0
        each_count = 0
        known_list_count = 0
        time_data = {"Z":0,"Q":0,"get_list":0,"each":0,"known_list_loop":0}
        srs_set_list = list(srs_set_sorted_dic.values())
        ss_table = SuperSetTableBit(srs_set_list)
        for Z in srs_set_sorted:
            start_Z = time.time()
            Z_count += 1
            Z_bit = srs_set_sorted_dic[Z]
            count += 1
            essential_flag = True
            #Qのビットリストを作成
            Q_list = self.extract_set_bits(Z_bit)
            for Q_bit in Q_list:
                start_Q = time.time()
                Q_count += 1
                Z_pp_bit = Z_bit & ~2**Q_bit
                start_get_list = time.time()
                get_list_count += 1
                super_set_list = ss_table.get_list(Z_pp_bit, True)
                time_data["get_list"] += time.time()-start_get_list
                start_each = time.time()
                each_count += 1
                def process_set(_set):
                    return None
                super_set_list.each(process_set)
                time_data["each"] += time.time()-start_each
                #print("time_list_table_bit:",end-start)
                if super_set_list is None:
                    continue
                if super_set_list.known_list:
                    for Z_p_bit in super_set_list.known_list:
                        start_known_list = time.time()
                        known_list_count += 1
                        len_count+=1
                        if (Z_bit - (Z_bit & Z_p_bit)) == 2**Q_bit:
                            #R_p = Z_p - Z
                            R_p_bit = Z_p_bit & ~Z_bit
                            if R_p_bit !=0:
                                R_p_bit_list = self.extract_set_bits(R_p_bit)
                                q_bit = self.list_or(R_p_bit_list)
                            else:
                                q_bit = 0
                            if q_bit & Q_bit == q_bit:
                                essential_flag = False
                                break
                        time_data["known_list_loop"] += time.time()-start_known_list
                        if not essential_flag:
                            break
                time_data["Q"] += time.time()-start_Q
            if essential_flag:
                essential_srs.append(Z)
            time_data["Z"] += time.time()-start_Z
            print(str(count) + "/" + str(len(srs_set)))
            #print("len_count:",len_count)
        time_data["Z"] = time_data["Z"]/Z_count
        time_data["Q"] = time_data["Q"]/Q_count
        time_data["get_list"] = time_data["get_list"]/get_list_count
        time_data["each"] = time_data["each"]/each_count
        time_data["known_list_loop"] = time_data["known_list_loop"]/known_list_count
        print("Timing Data (is_essential_bit_pruning_integer):", time_data)
        return essential_srs

    def extract_set_bits(self,num):
        result = []
        bit_position = 0
        while num > 0:
            if num & 1 == 1:
                result.append(bit_position)
            
            num >>= 1
            bit_position += 1
        return result
    
    def list_or(self,elements):
        """
        リスト内の全ての要素に対して OR 演算を行う。
        
        Args:
            elements (list): OR 演算を適用する整数のリスト。
        
        Returns:
            int: 全ての要素で OR を取った結果。
        """
        return reduce(lambda x, y: x | y, elements)

    def bit_score(self,Q_dic, Z):
        set_score = 0
        for z in Z:
            set_score += 2**Q_dic[z]
        return set_score
    

    def make_essential_srs(self,phis,p,sign):
        #srs_set=self.make_srs_set(len(Q)-1,phis,p,Q,sign)
        #start = time.time()
        count=0
        essential_srs = []
        srs_set_sorted_dic = {}
        solver = CSPSolver(phis,p,sign)
        srs_set = solver.make_srs_set()
        srs_set_sorted = sorted(srs_set, key=len)
        srs_set_sorted_dic = solver.make_srs_set_sorted_dic(srs_set_sorted)
        #srs_set_sorted = sorted(srs_set,key=len)
        #num_cores = multiprocessing.cpu_count()
        # phis_dicを一度に作成
        #phis_dic = {phi: i for i, phi in enumerate(phis)}
        # Q_dicを一度に作成
        #Q_dic = {q: sum(2 ** phis_dic[qq] for qq in q) for q in Q}
        # srs_set_sorted_dicを一度に作成
        #srs_set_sorted_dic = {Z: sum(2 ** Q_dic[z] for z in Z) for Z in srs_set_sorted}
        #print("phis_dic:",phis_dic)
        #print("Q_dic:",Q_dic)
        #print(len(srs_set))
        #print("srs_set_sorted_dic:",srs_set_sorted_dic)
        #print(len(srs_set))
        #print(srs_set_sorted)
        #start = time.time()
        essential_srs = solver.is_essential_bit_pruning2(srs_set, srs_set_sorted, srs_set_sorted_dic, essential_srs)
        #essential_srs = self.is_essential_bit_pruning2(Q_dic,srs_set,srs_set_sorted,srs_set_sorted_dic,essential_srs)
        #end = time.time()
        #print("pruning:",end-start)
        #start = time.time()
        #essential_srs = self.is_essential_bit_pruning_integer(Q_dic,srs_set,srs_set_sorted,srs_set_sorted_dic,essential_srs)
        #end = time.time()
        #print("pruning_bit:",end-start)
        #essential_srs = self.is_essential_bit(Q_dic,srs_set,srs_set_sorted,srs_set_sorted_dic,essential_srs)
        
        #for Z in srs_set:
        #    srs_set_sub = copy(srs_set)
        #    srs_set_sub.remove(Z)
        #    essential_srs = self.is_essential(set(Z),srs_set_sub,essential_srs)
        #    count+=1
        #    print(str(count)+"/"+str(len(srs_set)))
        #end=time.time()
        #print("phis_dic:",phis_dic)
        #print("Q_dic:",Q_dic)
        #print("Q:",Q)
        #print("srs_set_sorted_dic:",srs_set_sorted_dic)
        #print(f"処理時間: {end - start} 秒")
        return essential_srs


if __name__=="__main__":
    phis = ["a_1", "a_2", "a_3", "a_4"]
    p = [0.1, 0.7, 0.2, 0.9]
    sign = ["ope_gt", "ope_gt", "ope_gt", "ope_gt"]
    # Q = [[],["a_1"],["a_2"],["a_3"],["a_4"],["a_1","a_2"],["a_1","a_3"],["a_1","a_4"],["a_2","a_3"],["a_2","a_4"],["a_3","a_4"],["a_1","a_2","a_3"],["a_1","a_2","a_4"],["a_1","a_3","a_4"],["a_2","a_3","a_4"],["a_1","a_2","a_3","a_4"]]
    Q=[]
    checker = SatisfiabilityChecker(phis,p,Q)   
    powerset_Q = checker.powerset(phis)
    for i in powerset_Q:
        print(i)
        Q.append(i)
    #print(Q)
    essential_srs = checker.make_essential_srs(phis,p,sign)
    print(essential_srs)
    print("srs:",len(essential_srs))
    for srs in essential_srs:
        print(srs)