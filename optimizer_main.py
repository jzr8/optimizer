from pyomo.environ import *


# day_st 一天的炉数据
# name 需要考虑的元素（列表）
# grand_stand  参考的标准指标  有'0A'、'0'、'1'、'test'
def opti_main(day_st, name, grand_stand):
    # 构建一个优化模型
    model = ConcreteModel()

    n = day_st.stove_num  # 变量维度，炉数

    element_num = len(name)  # 考虑的元素的个数

    # 参数（常量） 帽，中，底的质量
    theta = {}  # 标准偏差
    for ele_name in name:
        theta[ele_name] = day_st.stand[grand_stand][ele_name]

    if day_st.lack == 'T':
        alpha = [0]*n
        print("帽：缺省")
    else:
        alpha = [st.weight for st in day_st.T_list]  # 各个帽的质量
        print("帽(质量)：[" + ", ".join([f"x{i + 1}:{v}" for i, v in enumerate(alpha)]) + "]")
    # 中
    if day_st.lack == 'M':
        beta = [0]*n
        print("中：缺省")
    else:
        beta = [st.weight for st in day_st.M_list]
        print("中(质量)：[" + ", ".join([f"y{i + 1}:{v}" for i, v in enumerate(beta)]) + "]")
    # 底
    if day_st.lack == 'B':
        gamma = [0]*n
        print("底：缺省")
    else:
        gamma = [st.weight for st in day_st.B_list]
        print("底(质量)：[" + ", ".join([f"z{i + 1}:{v}" for i, v in enumerate(gamma)]) + "]")

    # 元素的含量，每一行分别表示帽，中，底的对应元素的含量
    element_T = {}  # 各个帽的元素含量
    element_M = {}  # 中
    element_B = {}  # 底
    for ele_name in name:
        if day_st.lack == 'T':
            element_T[ele_name] = [0]*n
        else:
            element_T[ele_name] = [getattr(st, ele_name) for st in day_st.T_list]
        if day_st.lack == 'M':
            element_M[ele_name] = [0]*n
        else:
            element_M[ele_name] = [getattr(st, ele_name) for st in day_st.M_list]
        if day_st.lack == 'B':
            element_B[ele_name] = [0]*n
        else:
            element_B[ele_name] = [getattr(st, ele_name) for st in day_st.B_list]

    # 布尔变量 0，1整数
    # 定义行列索引（比如 1 到 5）
    rows = range(0, n)
    cols = range(0, n)

    # 定义索引集合  就是两个取值范围
    model.I = Set(initialize=rows)  # 代表帽/中/底 的个数
    model.J = Set(initialize=cols)  # 代表炉的个数

    # 定义变量 x[i,j] 为0-1变量（即二进制）
    # 三个n*n布尔变量矩阵  分别代表各个 帽、中、底 放入哪个炉子
    model.x = Var(model.I, model.J, domain=Binary)
    model.y = Var(model.I, model.J, domain=Binary)
    model.z = Var(model.I, model.J, domain=Binary)

    model.ELE = Set(initialize=theta.keys())  # 元素名作为索引集
    model.theta = Param(model.ELE, initialize=theta)  # 模型中的变量，初始化为theta
    model.element_T = Param(model.ELE, model.I, initialize=lambda model, e, i: element_T[e][i])
    model.element_M = Param(model.ELE, model.I, initialize=lambda model, e, i: element_M[e][i])
    model.element_B = Param(model.ELE, model.I, initialize=lambda model, e, i: element_B[e][i])
    model.alpha = Param(model.I, initialize={i: alpha[i] for i in range(0, n)})
    model.beta = Param(model.I, initialize={i: beta[i] for i in range(0, n)})
    model.gamma = Param(model.I, initialize={i: gamma[i] for i in range(0, n)})


    #     # 定义常量
    #     model.theta[ele_name] = Param(initialize=theta[ele_name])  # 模型中的变量，初始化为theta
    #     # 模型中的类似于字典的形式  索引范围为model.I   初始化 键i 对应值FeT[i]
    #     model.element_T[ele_name] = Param(model.I, initialize={i: element_T[ele_name][i] for i in range(0, n)})
    #     model.element_M = Param(model.I, initialize={i: element_M[i] for i in range(0, n)})
    #     model.element_B = Param(model.I, initialize={i: element_B[i] for i in range(0, n)})
    #     model.alpha = Param(model.I, initialize={i: alpha[i] for i in range(0, n)})
    #     model.beta = Param(model.I, initialize={i: beta[i] for i in range(0, n)})
    #     model.gamma = Param(model.I, initialize={i: gamma[i] for i in range(0, n)})

    # 伪目标函数（常数0，不影响求解，仅用于触发求解器），用于求可行解
    model.obj = Objective(expr=0)

    '''--------------约束条件----------------'''

    # 每个帽 能且仅能 加入一个炉中
    # 每行的和为1：对每个 i，有 sum_j x[i, j] == 1
    def xrow_constraint_rule(model, i):
        return sum(model.x[i, j] for j in model.J) == 1

    if day_st.lack != 'T':
        # 添加一组恒等约束  这里I为[0,n]，即产生了n个约束
        model.xrow_constraint = Constraint(model.I, rule=xrow_constraint_rule)

    # 每个炉子 有且仅有 一个帽
    # 每列的和为1：对每个 j，有 sum_i x[i, j] == 1
    def xcol_constraint_rule(model, j):
        return sum(model.x[i, j] for i in model.I) == 1

    if day_st.lack != 'T':
        model.xcol_constraint = Constraint(model.J, rule=xcol_constraint_rule)

    # 每个中 能且仅能 加入一个炉中
    # 每行的和为1：对每个 i，有 sum_j x[i, j] == 1
    def yrow_constraint_rule(model, i):
        return sum(model.y[i, j] for j in model.J) == 1

    if day_st.lack != 'M':
        model.yrow_constraint = Constraint(model.I, rule=yrow_constraint_rule)

    # 每个炉子 有且仅有 一个中
    # 每列的和为1：对每个 j，有 sum_i x[i, j] == 1
    def ycol_constraint_rule(model, j):
        return sum(model.y[i, j] for i in model.I) == 1

    if day_st.lack != 'M':
        model.ycol_constraint = Constraint(model.J, rule=ycol_constraint_rule)

    # 每个底 能且仅能 加入一个炉中
    # 每行的和为1：对每个 i，有 sum_j x[i, j] == 1
    def zrow_constraint_rule(model, i):
        return sum(model.z[i, j] for j in model.J) == 1

    if day_st.lack != 'B':
        model.zrow_constraint = Constraint(model.I, rule=zrow_constraint_rule)

    # 每个炉子 有且仅有 一个底
    # 每列的和为1：对每个 j，有 sum_i x[i, j] == 1
    def zcol_constraint_rule(model, j):
        return sum(model.z[i, j] for i in model.I) == 1

    if day_st.lack != 'B':
        model.zcol_constraint = Constraint(model.J, rule=zcol_constraint_rule)

    # 每一个炉子的 元素的质量 小于等于  标准元素质量
    # 元素 的可行约束
    def Element_constraint_rule(model, ele_name, j):
        return sum(  # j炉中的元素的总质量
            model.alpha[i] * model.element_T[ele_name, i] * model.x[i, j]  # model.x[i, j]代表i这个帽 是否 放在 j这个炉中
            + model.beta[i] * model.element_M[ele_name, i] * model.y[i, j]  # 如果是，则model.x[i, j] = 1
            + model.gamma[i] * model.element_B[ele_name, i] * model.z[i, j]  # 否则，model.x[i, j] = 0
            for i in model.I
        ) <= model.theta[ele_name] * sum(  # 这个sum为j炉中的矿物总质量  乘上标准含量  为该j炉的标准质量
            model.alpha[i] * model.x[i, j]
            + model.beta[i] * model.y[i, j]
            + model.gamma[i] * model.z[i, j]
            for i in model.I
        )

    # 对每个炉子 进行约束
    model.element_constraints = Constraint(model.ELE, model.J, rule=Element_constraint_rule)

    '''--------------约束条件----------------'''

    # 求解并给出可行解
    solver = SolverFactory("cbc")  # 创建cbc求解器  或 glpk, scip
    results = solver.solve(model)  # 求解模型

    # 先判断模型是否成功求解
    if (results.solver.termination_condition == TerminationCondition.optimal  # 是否为最优解
            or results.solver.termination_condition == TerminationCondition.feasible):  # 是否为可行解

        # 每个炉子的配置：T（帽）、M（中）、B（底）
        stove_dic = {'T': None, 'M': None, 'B': None}
        # 得到n个炉子的列表 每个元素为炉子相应的字典
        stove_list = [stove_dic.copy() for _ in range(n)]

        model_list = [model.x, model.y, model.z]
        if day_st.lack == 'T':
            model_list = [model.y, model.z]
        elif day_st.lack == 'M':
            model_list = [model.x, model.z]
        elif day_st.lack == 'B':
            model_list = [model.x, model.y]

        # 遍历 帽、中、底
        for var in model_list:
            # 遍历每个帽/中/底
            for i in model.I:
                # 遍历每个炉
                for j in model.J:
                    val = value(var[i, j])
                    # var[i, j] = 1则代表对应 第i个 帽/中/底 被分配到 第j炉中了
                    if val == 1:
                        if var.name == 'x':
                            stove_list[j]['T'] = var.name + str(i + 1)
                        elif var.name == 'y':
                            stove_list[j]['M'] = var.name + str(i + 1)
                        elif var.name == 'z':
                            stove_list[j]['B'] = var.name + str(i + 1)

        for i, st in enumerate(stove_list):
            print(f'第{i + 1}炉：{st}')

        print('成功得到一个可行解')
        print('\n')
        return True

    else:
        print('无解')
        print('\n')
        return False
