import jieba
import jieba.posseg as psg
import json
import xlrd
import re
import string
import pandas
import os
import math
import json

others = ("👍","🙏","💪","❤","❌","😂","🎉","🐊","😷","👌","😭","👏","🙃","🌹","✊")

def  readJson(fPath,target,type):
    #原始数据父目录，目标文件
    files = os.listdir(fPath)
    for i in files:
        f= open(fPath+i,encoding="utf-8").read()
        result = json.loads(f)
        data = list()
        for i in range(0,len(result)):
            filePath = open((target), mode='a', encoding='utf-8')
            for j in result[i][type]:
                data.append(j)
                filePath.writelines(j + "\n")

def readJsonForIDF():
    def readJson(fPath, target, type):
        # 原始数据父目录，目标文件夹路径
        files = os.listdir(fPath)
        for i in files:
            f = open(fPath + i, encoding="utf-8").read()
            result = json.loads(f)
            data = list()
            for i in range(0, len(result)):
                if not os.path.exists(target+result[i][date]):
                    os.makedirs(target+result[i][date])
                filepath = target+result[i][date]
                for j in result[i][type]:
                    result.append(j)
                    open(target+result[i][date],mode="a",encoding="utf-8").writelines(j)


def calSumTf(fPath,target):
    #输入readjson所得数据以及结果路径，以文件形式输出研究对象
        target = open(fPath,mode="w",encoding="utf-8")
        dicts = getTFDicsts(path)
        copys = dicts.copy()
        for k in copys.keys():
            if k in others or not re.match('[^0-9A-Za-z\u4e00-\u9fa5]+',k):
               target.writelines(k+":"+str(dicts[k])+"\n")


def getTFDicsts(filepath):
    strs = open(filepath,encoding="utf-8").read()
    dicts2 = stopWordCal(dict(pandas.Series(jieba.lcut(strs,use_paddle=True)).value_counts()))
    return dicts2


def stopWordCal(dicts):
    stopWordList = [line.strip() for line in open("D:\文档\大二上\评论\评论停用词.txt", encoding="utf_8").readlines()]
    copy = dicts.copy()
    for i in copy.keys():
        if i  in stopWordList:
            del dicts[i]
    return dicts


def tf_idf(fPath, target):
    # fPath:研究对象保存文件路径；target:tfidf数据保存路径
    sumPaper = open(fPath, encoding='utf-8')
    sumFre = sumPaper.readlines()
    for i in range(0, len(sumFre)):
        sumFre[i] = sumFre[i].replace("\n", "")
        sumFre[i] = sumFre[i].split(":")
        sumFre[i][1] = int(sumFre[i][1])
    wordSum = sum(i[1] for i in sumFre)
    tf = list(range(len(sumFre)))
    for i in range(0, len(sumFre)):
        tf[i] = sumFre[i][1] / wordSum
    idf = idfCalculate(sumFre, filesPath, k)
    for i in range(0, len(sumFre)):
        sumFre[i][1] = 1000 * tf[i] * idf[i]
    sumFre.sort(key=takeSecond, reverse=True)
    tfidf = open(target, mode="w", encoding="utf-8")
    for i in range(0, len(sumFre)):
        tfidf.write(sumFre[i][0] + ":" + str(sumFre[i][1]) + "\n")

def idfCalculate(dicts,filesPath,k):
    #filesPath为指定的文件化研究对象的父路径，文件化研究对象的文件生成使用readJson的改编方法，本份研究中不赘述;k为idf值的对数基底
    #文件化研究对象采二级存储结构，也即“父文件夹——子文件夹（命名为日期数据，以对应以天为单位研究心态极性指数）——文件名”
    j = 0
    fileList = os.listdir(filesPath)
    for i in range(0,len(dicts)):
        dicts[i][1] = 0
    for i in fileList:
        tempPath = path + i
        strs = open(tempPath,encoding="utf-8").read()
        dicts2 = dict(pandas.Series(jieba.lcut(strs,use_paddle=True)).value_counts())
        for i in range(0,len(dicts2)):
            if dicts[i][0] in dicts2.keys():
                dicts[i][1]+=1
        j+=1
    idf = list(range(len(dicts)))
    for i in range(0,len(dicts)):
        idf[i] = float(math.log((j)/(dicts[i][1]+1),k))
    return idf


def takeSecond(elem):
    return elem[1]

def getExpre(posPath,negPath,dirPath,targetPath):
    #正向心态词典路径，负向心态词典路径，每日研究对象文件父路径，输出文件路径
        expDict = makeExDict(posPath,negPath)
        result = list()
        dirpath = "D:\文档\大二上\分条评论\\"
        paperList = os.listdir(dirpath)
        tempSum =0
        for j in range(0,len(paperList)):
            dirList = os.listdir(dirpath+paperList[j])
            result.append(
                paperList[j] + ":" )
            tempSum = 0
            for k in range(0,len(dirList)):
                tempSum+=float(calExpre(dirpath+
                                        paperList[j]+"\\"+dirList[k],expDict))
            result.append(str(tempSum) + "\n")
        open(target,mode = "w").writelines(result)

def makeExDict(posPath,negPath):
    expDict = dict()
    pos = open(posPath,encoding="utf-8").readlines()
    neg = open(negPath,encoding="utf-8").readlines()
    for i in range(0,len(pos)):
        pos[i] = pos[i].replace("\n","").split(" ")
        expDict[pos[i][0]] = float(pos[i][1])
    for i in range(0,len(neg)):
        neg[i] = neg[i].replace("\n","").split(" ")
        expDict[neg[i][0]] = - float(neg[i][1])
    return expDict

def calExpre(filepath,expreDict):
    strs = open(filepath,encoding="utf-8").read()
    dicts2 = stopWordCal(dict(pandas.Series(jieba.lcut(strs,use_paddle=True)).value_counts()))
    result = float()
    sum = 0
    for i in dicts2.keys():
        sum += dicts2[i]
        if i in expreDict.keys():
            result += dicts2[i] * expreDict[i]
        return 1000*result/sum

getExpre("D:\文档\大二上\评论\pos-评论.txt",
         "D:\文档\大二上\评论\\neg-评论.txt",
         "D:\文档\大二上\数据初步整理\阶段1",
         "D:\文档\大二上\数据初步整理\情感极性.txt")
