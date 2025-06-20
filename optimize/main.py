from read_file import *
from optimizer_main import *


def get_limit(ele_list, ele, ele_stand_init, min_unit):
    if ele not in ele_list:
        raise KeyError('指定的元素并不在约束元素列表中')
    ele_stand = ele_stand_init
    day_st.stand_set(ele, ele_stand)
    while opti_main(day_st, ele_list, 'test'):
        ele_stand = ele_stand - min_unit
        day_st.stand_set(ele, ele_stand)

    if ele_stand != ele_stand_init:
        print(f'当前的指标为:{ele_stand}, 最近的具有可行解的指标为:{ele_stand + min_unit}')
    else:
        print(f'给定的初始指标即无解')


if __name__ == '__main__':
    input = 'F:/西门子项目/海绵钛程序 527/海绵钛程序/5月份数据/before/2#线掺配预测表5.29.xlsx'
    day_st = read_date(input, '5.2')  # 提取指定日期的数据
    element_list = ['Fe', 'Cl', 'O']  # 考虑的元素  约束元素列表

    '''-------------------------获取一个可行解----------------------------'''
    # opti_main(day_st, element_list, '0')  # 给出一个可行解

    '''----------------------------------------------------------------'''

    '''----------------循环获取 可以得到可行解 的 标准下限--------------------'''
    element = 'Cl'  # 指定 对某个元素 进行循环
    # ele_stand_init 为指定元素的 初始标准指标
    # min_unit为每次降低指标的单位量
    get_limit(element_list, element, ele_stand_init=0.060, min_unit=0.001)

    '''-----------------------------------------------------------------'''
