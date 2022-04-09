import pandas as pd
import numpy as np
import openpyxl as opxl
import os
import shutil as st
import time
import re

'''
把originDf的keyColumn的文件名从源文件夹提取出至目标文件夹
'''
def df_aimFile_output (originDf,
                       keyColumn,
                       inputDirPath,
                       outputDirPath,
                       fileExistWarn = False,
                       keyWord = False):
    aimFiles = []
    if keyColumn not in list (originDf.columns):
        keyColumnNotExistError = KeyColumnNotExistError (str (keyColumn) + '不在originDf.columns内')
        raise keyColumnNotExistError

    # 获取keyColumn中的元素
    for index in originDf.index:
        aimFiles.append (originDf.loc[index, keyColumn])
    for aimFile in aimFiles:
        # 判断空值
        if aimFile is not np.nan:
            aimFilePath = dir_research (aimFile, inputDirPath, keyWord)  # 获取到df中对应企业的路径
            if aimFilePath:
                try:
                    dirCopy (aimFilePath, outputDirPath)
                    print (str (keyColumn) + ':' + str (aimFile) + '---文件夹复制成功')
                except:
                    pass  # 可同时统计文件夹是否存在，但是已经统计过就不统计了
            else:
                if fileExistWarn:
                    fileExistsError = FileExistsError ('inputPath: ' + str (inputDirPath))
                    raise fileExistsError
                else:
                    continue

    print ('''

    提取成功

    ''')
    return 0


'''
路径检索
根据文件名字，从源文件夹内找出文件名字所属的文件路径
'''
def dir_research (dirName, filePath, keyWord = False):
    i = 0
    for root, dirs, files in os.walk (filePath):
        if keyWord:
            if dirName in os.path.basename (root):
                i = 1
                return os.path.normpath (root)
        else:
            if dirName == os.path.basename (root):
                i = 1
                return os.path.normpath (root)
    if not i:
        return None
'''
文件夹及文件复制
'''
def dirCopy (inputPath, outputPath):
    if not os.path.exists (outputPath):
        os.mkdir (outputPath)
    if os.path.exists (inputPath):
        if os.path.isdir (inputPath):
            os.mkdir (outputPath + '\\' + os.path.basename (inputPath))
            dirs = os.listdir (inputPath)
            if dirs:
                for dir in dirs:
                    dirCopy (inputPath + '\\' + str (dir), outputPath + '\\' + os.path.basename (inputPath))
            else:
                return 0
        else:
            st.copy (inputPath, outputPath)
    else:
        fileExistsError = FileExistsError ('inputPath: ' + str (inputPath))
        raise fileExistsError

'''
用于判定资料收集情况
可引申到其他资料判定
documentStatistic(originDf, keyColumn,documentPath):
    originDf: 表格DataFrame数据
    keyColumn: 统计时文件夹所属列, 需要有不可重复性，可识别性
    documentPath: 统计的目标文件夹
'''


def documentStatistic (originDf, keyColumn, documentPath, keyWord = False):
    correct_folder = ['1.《挥发性有机物排放重点企业调查表》',
                      '2.“近三年生产情况调查表”',
                      '3.涉VOCs物料的检测报告或安全说明书',
                      '4.有机废气治理设施设计方案',
                      '5.最近1年各废气治理设施监测报告',
                      '6.环境影响评价报告'
                      ]
    originMap = { }
    if keyColumn not in list (originDf.columns):
        keyColumnNotExistError = KeyColumnNotExistError (str (keyColumn) + '不在originDf.columns内')
        raise keyColumnNotExistError
    # 获取originDf的index与keyColumn的映射
    for origin_index in list (originDf.index):
        originMap[origin_index] = originDf.loc[origin_index, keyColumn]

    # 使用index遍历keyColumn
    for index in originMap.keys ( ):
        if originMap[index] is not np.nan:
            i = 0  # 文件夹计数器

            # 检索keyColumn中元素所在的文件夹
            valuePath = dir_research (originMap[index], documentPath, keyWord)
            if valuePath:
                for folder in correct_folder:
                    if folder in os.listdir (valuePath):
                        i = i + 1  # 遍历keyColumn文件夹中的子文件夹，与标准文件夹匹配，更新文件夹计数器

                # 进行文件夹计数判断
                if i > 4:
                    originDf.loc[index, '资料收集情况'] = '齐'

                elif 4 >= i and i > 2:
                    originDf.loc[index, '资料收集情况'] = '缺'

                elif 2 >= i and i > 0:
                    originDf.loc[index, '资料收集情况'] = '很缺'

                else:
                    originDf.loc[index, '资料收集情况'] = '无'
            else:
                originDf.loc[index, '资料收集情况'] = '无'
            print (str (keyColumn) + ':' + str (originMap[index]) + '---资料收集情况正在统计')

    print ('''

    资料收集统计完毕

    ''')
    return originDf



'''
标记表格的入户时间
'''

def dateMark(originDf: pd.DataFrame,
             keyColumn,
             dateColumn ):
    dateMap = {}
    fillColumn = '入户情况'
    if keyColumn not in list(originDf.columns):
        keyColumnNotExistError = KeyColumnNotExistError(str(keyColumn) + '不在originDf.columns内')
        raise keyColumnNotExistError
    # 建立index与keyColumn的映射表
    for index in originDf.index:
        dateMap[index] = originDf.loc[index, dateColumn]
    today = time.strftime('%d', time.localtime())
    thisMonth = time.strftime('%m', time.localtime())
    mark = ''  # 预设时间标记
    for index in dateMap.keys():
        if originDf.loc[index, dateColumn] is not np.nan:
            mark = originDf.loc[index, dateColumn]  # 当为时间类型时，时间标记为当前时间
        if originDf.loc[index, keyColumn] is not np.nan and mark:
            date = re.findall(r'\d+', mark) # 正则表达式匹配日期中的数字
            month = str(date[0])
            day = str(date[1])

            if int(month) > int(thisMonth):
                originDf.loc[index, fillColumn] = '准备' + str(month) + '/' + str(day) + '入户调查'
            elif int(month) == int(thisMonth):
                if int(day) <= int(today):
                    originDf.loc[index, fillColumn] = str(month) + '/' + str(day) + '已入户调查'
                else:
                    originDf.loc[index, fillColumn] = '准备' + str(month) + '/' + str(day) + '入户调查'
            else:
                originDf.loc[index, fillColumn] = str(month) + '/' + str(day) + '已入户调查'
    return originDf


'''
将一个Excel表格内的多个工作表拆分并导出
'''
def sheetSeparate(excelPaths:list,
                  outputPath: str):
    for excelPath in excelPaths:
        wb = opxl.load_workbook(excelPath)
        sheets = wb.sheetnames

        for sheet in sheets:
            writer = pd.ExcelWriter(outputPath + '\\' + sheet + '-' + os.path.basename (excelPath))
            originDf = pd.read_excel(excelPath, sheet_name = sheet)
            originDf.to_excel(writer)
            writer.save()
            print(os.path.basename (excelPath) + sheet + '输出成功')


class ColumnCompareError(Exception):
    pass

class KeyColumnNotExistError(Exception):
    pass