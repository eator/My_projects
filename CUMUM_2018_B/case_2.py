'''
代码名称： process_2_distribution_solution.py
所需编译器： python3.6
所需开源代码包： NumPy
说明： 打印出运行情况&完成工件数&加工序列
        通过枚举 [对cnc处理工序一还是工序二] 的排布问题，得到各个的排布下双工序所耗时间，选择最短时间对应的排布。
        最后输出结果就是最佳排布：
            如[1 2 1 2 1 2 1 2]对应解释即为：
            1#cnc做工序一， 2#cnc做工序二， 3#cnc做工序一， 4#cnc做工序二 ...
            结论：我们发现无论有无故障，最优排布都是[1 2 1 2 1 2 1 2]
        并且打印主程序的运行时间（枚举2^8-2次的总计算时间）
        参数调节（决定组数，决定有无故障情况——通过调节故障率是否为0）在主函数部分。
'''
import numpy as np
import time


class CNC:
    def __init__(self, reload_time, work_time, loc, d_, o_ind):
        self.loc = loc
        self.is_empty = True
        self.end_time = 0 # 当前state结束时间
        self.reload_time = reload_time
        self.work_time = work_time
        self.is_breakdown = False
        self.type = d_  # 做哪一道工序
        self.ind = o_ind
    def error_state_updating(self, time):
        if self.is_breakdown:
            if time > self.end_time:
                self.is_breakdown = False

class RGV:
    def __init__(self, move_time, cncs, wash_time, t_ind):
        self.loc = 1
        self.total_time = 0
        self.move_time = move_time
        self.cncs = cncs
        self.cncs_type_ind = t_ind # 加工第一道工序的cnc的索引 [0]->第1工序 [1]->第二工序
        self.wash_time = wash_time
        self.completed = 0
        self.has_semi_piece = False
    def move_to(self, id):
        # 移动到id对应的cnc处
        move_time = self.move_time[abs(self.loc-(int(id/2)+1))]
        self.total_time += move_time
        # print(f"移动到{id+1}#处：loc：[{self.loc}->{self.cncs[id].loc}], 移动时间 = {move_time}")
        self.loc = self.cncs[id].loc
    def remove_workpiece(self, id):
        # 拆除工件 cnc->empty
        # 消耗reload的时间
        # 仅仅针对二工序
        if self.cncs[id].type == 2:
            self.total_time += self.cncs[id].reload_time
            self.cncs[id].is_empty = True
            # 顺带清洗工件
            self.total_time += self.wash_time
            self.completed += 1
    def add_workpiece(self, id):
        # empty->加件
        # print(f"给{id+1}#加件")
        self.cncs[id].is_empty = False
        self.total_time += self.cncs[id].reload_time
        if 0.24 <= np.random.rand() < 0.24+err_rate:
            self.error_happen(id)
        else:
            self.cncs[id].end_time = self.total_time+self.cncs[id].work_time
        if self.cncs[id].type == 2:
            # 工件上交后就没有了
            self.has_semi_piece = False
    def change_workpiece(self, id):
        # waiting->换件+清洗（只针对工序2）
        # print(f"给{id+1}#换件+清洗")
        self.cncs[id].is_empty = False
        self.total_time += self.cncs[id].reload_time
        if 0 <= np.random.rand() < err_rate:
            self.error_happen(id)
        else:
            self.cncs[id].end_time = self.total_time+self.cncs[id].work_time
        if self.cncs[id].type == 2:
            self.has_semi_piece = False
            self.total_time += self.wash_time
            self.completed += 1
        else:
            # get到半成品
            self.has_semi_piece = True
        # print(f"{i+1}#已加工完成")
    def error_happen(self, error_ind):
        error_time_minute = 10+np.random.rand()*10
        print(f"{error_ind+1}# 发生了 {error_time_minute} 分钟的故障")
        self.cncs[error_ind].is_breakdown = True
        self.cncs[error_ind].is_empty = True # 拆下物件清空
        self.cncs[error_ind].end_time = self.total_time + self.cncs[error_ind].work_time*np.random.rand() + error_time_minute*60
    def find_best_obj(self):
        if self.has_semi_piece:
            # 有半成品马上去最近的2
            return self.find_best_obj_t(2)
        else:
            if not self.is_type2_empty():
                # 如果没件也不用去了，直接去1
                return self.find_best_obj_t(1)
            else:
                return self.find_best_obj_t(2)
    def is_type2_empty(self):
        is_type2_empty = False
        for id_2 in self.cncs_type_ind[1]:
            # 判断加工二工序的cnc是否都有件
            if self.cncs[id_2].is_empty:
                is_type2_empty = True
        return is_type2_empty
    def find_best_obj_t(self, f_t, require = 'none'):
        # 寻找最优(type = f_t)对象
        # 待找的cnc序列
        cncs2be_found = []
        for ind in self.cncs_type_ind[f_t - 1]:
            cncs2be_found.append(self.cncs[ind])
        # cncs2be_found就是f_t类的cnc们
        min_val = 1000
        min_ind = 0
        for i in range(len(cncs2be_found)):
            # i是待搜索列表中的序号
            go_time = 0
            # 非空
            if cncs2be_found[i].end_time > self.total_time:
                # 未加工完的
                go_time += max(self.move_time[abs(self.loc-(int(i/2)+1))], cncs2be_found[i].end_time-self.total_time)+cncs2be_found[i].reload_time
            else:
                # 已经加工完了
                go_time += self.move_time[abs(self.loc-(int(i/2)+1))]+cncs2be_found[i].reload_time
            extra = True
            if require == 'not_empty':
                # 如果要求有料，那么没料的cnc被排除
                if self.cncs[i].is_empty:
                    extra = False
            if go_time < min_val and extra:
                min_val = go_time
                min_ind = i
        # 这个min_ind应该是在所有的cnc中的ind
        return cncs2be_found[min_ind].ind

def list_all():
    return np.unique(np.random.randint(1,3,size=(10000, 8)), axis=0)

def workpieces_in_time(work_time, ds):
    # CNC对象初始化
    cncs = []
    type_ind_all = [[], []]
    for c, d in enumerate(ds):
        new_cnc = CNC(cnc_reload_time[c%2], work_time_val[d-1], int(c/2)+1, d, c)
        cncs.append(new_cnc)
        type_ind_all[d-1].append(c)

    rgv = RGV(move_time, cncs, wash_time, type_ind_all)

    # rgv逻辑表
    while rgv.total_time < work_time:
        aim_id = rgv.find_best_obj()
        rgv.move_to(aim_id)
        for cnc in rgv.cncs:
            cnc.error_state_updating(rgv.total_time)
            # cnc 状态更新
        if rgv.cncs[aim_id].is_empty:
            rgv.add_workpiece(aim_id)
        else:
            if rgv.cncs[aim_id].type == 1:
                # 如果是一号直接换料
                if rgv.total_time < rgv.cncs[aim_id].end_time:
                    rgv.total_time = rgv.cncs[aim_id].end_time
                rgv.change_workpiece(aim_id)
            else:
                if rgv.has_semi_piece:
                    # 如果rgv带着半成品来找工序2的cnc了->换
                    if rgv.total_time < rgv.cncs[aim_id].end_time:
                        rgv.total_time = rgv.cncs[aim_id].end_time
                    rgv.change_workpiece(aim_id)
                else:
                    # 空手而来—>拆件
                    if rgv.total_time < rgv.cncs[aim_id].end_time:
                        rgv.total_time = rgv.cncs[aim_id].end_time
                    rgv.remove_workpiece(aim_id)
    return rgv.completed


if __name__ == '__main__':
    # 位置分布:
    distribution = [1, 2, 1, 2, 1, 2, 1, 2]
    # for 1#，3#，5#，7#
    cnc_reload_time_1 = 30
    # for 2#，4#，6#，8#
    cnc_reload_time_2 = 35
    cnc_reload_time = [cnc_reload_time_1, cnc_reload_time_2]
    work_time_val = [400, 378]
    move_time = [0, 23, 41, 59]
    wash_time = 30
    err_rate = 0.01
    # 【参数列表】-- end
    print('共完成', workpieces_in_time(8*60*60, distribution))