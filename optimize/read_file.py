import pandas as pd
import numpy as np
from product_class import *


def read_date(path, date):
    df = pd.read_excel(path, sheet_name=date)
    # 读取第一列（第0列）
    first_column = df.iloc[:, 0].tolist()
    cleaned_lst = [x for x in first_column if x == x and x is not None]  # 得到当天序号列表
    stove_num = int(cleaned_lst[-1])  # 获得当天总炉数
    # if len(df)-5 != stove_num * 4:
    #     raise ValueError("当天不是所有炉配有帽、中、底三种搭配")

    # 等级标准指标
    stand = {
        '0A': {'牌号': None, 'Ti': None, 'Fe': None, 'Cl': None, 'C': None, 'N': None, 'O': None, 'Ni': None,
               'Cr': None,
               'hard': None, },
        '0': {'牌号': None, 'Ti': None, 'Fe': None, 'Cl': None, 'C': None, 'N': None, 'O': None, 'Ni': None, 'Cr': None,
              'hard': None, },
        '1': {'牌号': None, 'Ti': None, 'Fe': None, 'Cl': None, 'C': None, 'N': None, 'O': None, 'Ni': None, 'Cr': None,
              'hard': None, },
        'test': {'牌号': None, 'Ti': None, 'Fe': None, 'Cl': None, 'C': None, 'N': None, 'O': None, 'Ni': None,
                 'Cr': None, 'hard': None, },  # 这个test用来循环测试
    }

    # 获取当天各元素的标准含量
    for i, grade in enumerate(['0A', '0', '1']):
        # 从第三行（不算标题，默认第一行是标题，第一行数据为0）
        row = df.iloc[i + 2]  # 获取3 4 5 行数据
        row_list = row.tolist()  # 转为列表
        stand[grade]['牌号'] = row_list[7]
        stand[grade]['Ti'] = row_list[8]
        stand[grade]['Fe'] = row_list[9]
        stand[grade]['Cl'] = row_list[11]
        stand[grade]['C'] = row_list[12]
        stand[grade]['N'] = row_list[13]
        stand[grade]['O'] = row_list[14]
        stand[grade]['Ni'] = row_list[18]
        stand[grade]['Cr'] = row_list[19]
        stand[grade]['hard'] = row_list[20]

    # test 默认初始与 0级 一致
    for key in stand['test']:
        stand['test'][key] = stand['0'][key]

    T_ST_list = []  # 保存部位为 帽 的物料
    M_ST_list = []  # 中
    B_ST_list = []  # 底
    # 获取当天每个物料的参数
    for i in range(len(df) - 5):
        row = df.iloc[i + 5]
        row_list = row.tolist()
        # 不是预测行
        if pd.isna(row_list[1]):
            init_dic = {
                '重量': row_list[2], '生产炉次': row_list[3], '部位': row_list[4], '粒度': row_list[5],
                '等级': row_list[6],
                '牌号': row_list[7], 'Ti': row_list[8], 'Fe': row_list[9], 'Cl': row_list[11], 'C': row_list[12],
                'N': row_list[13], 'O': row_list[14], 'Ni': row_list[18], 'Cr': row_list[19], 'hard': row_list[20],
            }
            if row_list[4][0] == '帽':
                T_ST_list.append(Stuff(init_dic))
            elif row_list[4][0] == '中':
                M_ST_list.append(Stuff(init_dic))
            elif row_list[4][0] == '底':
                B_ST_list.append(Stuff(init_dic))

    if len(T_ST_list) == 0:
        if len(M_ST_list) != len(B_ST_list):
            raise ValueError("当天不是所有炉配有中、底两种搭配")
    elif len(M_ST_list) == 0:
        if len(T_ST_list) != len(B_ST_list):
            raise ValueError("当天不是所有炉配有帽、底两种搭配")
    elif len(B_ST_list) == 0:
        if len(T_ST_list) != len(M_ST_list):
            raise ValueError("当天不是所有炉配有帽、中两种搭配")

    day_st = Day(T_ST_list, M_ST_list, B_ST_list, stand, stove_num)

    return day_st
