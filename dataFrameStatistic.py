import numpy as np
import pandas as pd


class ColumnCompareError(Exception) :
    pass


class KeyColumnNotExistError(Exception) :
    pass
def logOutput():
    pass

def dfFill(originDf:pd.DataFrame,  # 需要修改的df
           inforDf:pd.DataFrame,  # 信息来源df
           keyColumn:str,  # 两df中相同的列，需要具有不可重复性，易识别。可增加数量提升判断准确度
           aimColumns: list,  # 需要修改的列
           supplyColumns: list = [],
           colExistWarn=True,  # 是否开启匹配存在警告
           overWrite = True,  # 是否开启数据覆盖
           ) -> pd.DataFrame:
    originMap = {}  # 建立修改df的index-keyColumn的映射
    inforMap = {}  # 建立信息df的index-keyColumn的映射
    inforCoulmns = list(inforDf.columns)  # 获取信息df的列
    keyColumns = [keyColumn] + supplyColumns
    for origin_index in list(originDf.index) :
        originMap[origin_index] = ''
        for keyColumn in keyColumns :
            if keyColumn in list(originDf.columns) :
                originMap[origin_index] += str(originDf.loc[origin_index, keyColumn])  # 建立映射
            else :
                keyColumnNotExistError = KeyColumnNotExistError(str(keyColumn) + '不在originDf.columns内')
                raise keyColumnNotExistError

    for infor_index in list(inforDf.index) :
        inforMap[infor_index] = ''
        for keyColumn in keyColumns :
            if keyColumn in list(inforDf.columns) :
                inforMap[infor_index] += str(inforDf.loc[infor_index, keyColumn])  # 建立映射
            else :
                keyColumnNotExistError = KeyColumnNotExistError(str(keyColumn) + '不在inforDf.columns内')
                raise keyColumnNotExistError

    for origin_index in originMap.keys() :
        if originMap[origin_index] in inforMap.values() :
            for infor_index in inforMap.keys() :
                # 当找到关键列中相同的元素，将信息DF的行索引逆向导出，方便修改
                if inforMap[infor_index] == originMap[origin_index] :  # 如果关键列中存在相同的元素
                    infor_key_index = infor_index  # 获取到信息DF的行索引
                    for column in aimColumns :  # 分别对需要修改df的目标列进行修改
                        if column in inforCoulmns :
                            if column not in originDf.columns:
                                originDf.insert(len(originDf.columns), column = column, value = np.nan)
                            if (not overWrite) and (not pd.isna(originDf.loc[origin_index, column])):
                                pass
                            else:
                                # 基于.loc[]方法，originDF中没有的列可以直接添加，开启数据覆盖后会将原有数据覆盖
                                originDf.loc[origin_index, column] = inforDf.loc[infor_key_index, column]
                                print(str(keyColumn) + ':' + str(originMap[origin_index]) + str(aimColumns) + '---填写完毕')
                        else :
                            exception = Exception('信息来源DataFrame中不存在该项column:' + str(column))
                            raise exception
                else :
                    pass

        elif pd.isna(originDf.loc[origin_index, keyColumn]):  # 空值处理
            continue
        else :
            # 如果匹配警告（colExistWarn）开启，当originDf中对应keyCoulmn元素在inforDf中不存在，则会报错并提醒
            if colExistWarn :
                columnCompareError = ColumnCompareError('keyColumn匹配异常, originDf的keyColumn不存在于inforDf' +
                                                        '--->匹配错误信息: ' +
                                                        str(origin_index) + '--' +
                                                        str(originMap[origin_index]))
                raise columnCompareError
            # 如果关闭，则不进行报错提醒
            else :
                continue


    print('''

    填写完毕
    ''')
    return originDf


'''
当二维表中keyColumns是重复的，而需要将其合并时可以使用该方法处理。
originDF：需要处理的二维表
keyColumns：元组数据类型，用于查找具有相同值的数据行，并合并
addColums：元组数据类型，合并时需要将元组内的列数据相加（数值类型）或连接（字符类型）便可设置该值

'''
def repeatedDataAdd(originDF:pd.DataFrame,
                    keyColumns: list,  # 筛选数据列标签，可以是多个
                    addColumns: list = []  # 需要进行相加或连接的列，可选参数
                    ) -> pd.DataFrame :
    repeatedIndexs = []  # 记录二次重复的行，
    for i in range(len(originDF.index)):  # 按照行遍历二维表
        aimIndex = originDF.index[i]  # 目标行定位
        if aimIndex not in repeatedIndexs :  # 当该目标行不是重复的行时才会开始寻找和目标行重复的行，用于节省时间
            aimIndexData = ''  # 目标行数据
            for keyColumn in keyColumns :  # 用于将目标行用于比对的数据组合后判断
                if keyColumn in list(originDF.columns) :
                    aimIndexData += str(originDF.loc[aimIndex, keyColumn])  # 将该行数据组合
                else :
                    ke = KeyColumnNotExistError(str(keyColumn) + '不在该DataFrame中')  # 如果某一筛选列标签不在二维表列内会报错
                    raise ke
            for j in range(i + 1, len(originDF.index)):  # 从目标行后开始遍历，因为目标行前重复的数据已经被记录，而不重复的数据已经被合并叠加，所以不用筛选
                iterIndex = originDF.index[j]  # 遍历行定位
                if iterIndex not in repeatedIndexs :  # 当该遍历行不是被记录重复行时才会被遍历，节省时间
                    iterIndexData = ''  # 遍历行数据
                    for keyColumn in keyColumns :  # 用于将遍历行用于比对的数据组合后判断
                        iterIndexData += str(originDF.loc[iterIndex, keyColumn])
                    if iterIndexData == aimIndexData :  # 如果该遍历行与目标行的筛选列值是相同的，便会开始合并叠加与记录
                        repeatedIndexs.append(iterIndex)  # 记录该遍历行为重复行
                        for addColumn in addColumns :  # 分别对需要叠加合并的列值进行处理
                            if addColumn in list(originDF.columns) :  # 判断叠加列是否在二维表列内，将该重复行进行叠加
                                if np.issubdtype(originDF.dtypes[addColumn], np.floating) or np.issubdtype(originDF.dtypes[addColumn], np.integer) :  # 判断是否为数值列
                                    originDF.loc[aimIndex, addColumn] = \
                                        float(originDF.loc[aimIndex, addColumn]) + \
                                        float(originDF.loc[iterIndex, addColumn])
                                else :  # 统一转化为字符列
                                    originDF.loc[aimIndex, addColumn] = \
                                        str(originDF.loc[aimIndex, addColumn]) + \
                                        str(originDF.loc[iterIndex, addColumn])
                            else :
                                ce = ColumnCompareError(str(addColumn) + '不在该DataFrame中')
                                raise ce
            print(str(aimIndex) + '填写完毕')
    # 将重复的行删除
    for repIndex in repeatedIndexs :
        originDF = originDF.drop(repIndex)

    print('''

    填写完毕

    ''')
    return originDF