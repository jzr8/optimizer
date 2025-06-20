
class Stuff:
    def __init__(self, init_dict):
        self.weight = init_dict['重量']
        self.label = init_dict['生产炉次']
        self.part = init_dict['部位']
        self.granularity = init_dict['粒度']
        self.grade = init_dict['等级']
        self.brand = init_dict['牌号']
        self.Ti = init_dict['Ti']
        self.Fe = init_dict['Fe']
        self.Cl = init_dict['Cl']
        self.C = init_dict['C']
        self.N = init_dict['N']
        self.O = init_dict['O']
        self.Ni = init_dict['Ni']
        self.Cr = init_dict['Cr']
        self.hard = init_dict['hard']

        # 对部位的描述进行一定的处理
        self.process_part()

    def process_part(self):
        if '帽' in self.part:
            self.part = 'T'
        elif '中' in self.part:
            self.part = 'M'
        elif '底' in self.part:
            self.part = 'B'


class Day:
    # T_list 为该天部位为 帽 的物料（即Stuff的对象）   M_list 中    B_list  底
    # stand_list 为该天的标准含量 由字典构成
    # stove_num 为该天的总炉数
    def __init__(self, T_list, M_list, B_list, stand_list, stove_num):
        self.T_list = T_list
        self.M_list = M_list
        self.B_list = B_list
        self.stand = stand_list
        self.stove_num = stove_num
        self.lack = None  # None代表无缺省  'T'代表帽缺省  'M'代表中缺省  'B'代表底缺省
        self.judge_TMB()

    def judge_TMB(self):
        if not self.T_list:
            self.lack = 'T'
        elif not self.M_list:
            self.lack = 'M'
        elif not self.B_list:
            self.lack = 'B'

    # 手动设置标准指标
    def stand_set(self, name, value):
        self.stand['test'][name] = value
