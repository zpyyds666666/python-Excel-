import os

path = r'C:\Users\ESIL\Desktop\帮扶文件夹暂存'

def deleteEmptyFile(inputPath):
    enterprises = os.listdir(inputPath)
    for enterprise in enterprises:
        enterprisePath = path+ '/' + str(enterprise)
        enterpriseDirs = os.listdir(enterprisePath)
        for dir in enterpriseDirs:
            if not os.listdir(enterprisePath + '/' + str(dir)) and os.path.isdir(enterprisePath + '/' + str(dir)):
                os.rmdir(enterprisePath + '/' + str(dir))

deleteEmptyFile(path)

