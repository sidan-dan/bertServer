import os
from imp import reload

import pymysql
import jieba
import xlrd
from flask import Flask
from gensim.corpora import Dictionary
from gensim.models import LdaModel,TfidfModel
import pyLDAvis.gensim
import re
import math
import matplotlib.pyplot as plt
from gensim import corpora
import jieba.posseg as psg


app = Flask(__name__)

THEME_FOLDER = 'theme'
app.config['THEME_FOLDER'] = THEME_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))

class Clustering():
    def load_data(self):
        # db = pymysql.connect(host="localhost", user="root", password="hsk123456", port=3306, db="dianping",
        #                      charset="utf8")  # 使用cursor()方法获取操作游标
        db = pymysql.connect(host="localhost", user="root", password=".Rebootcat2020.", port=3306, db="my_db",charset="utf8")

        cursor = db.cursor()
        # 3编写sql
        # sql = "select id_review,shop_comment from shop_comment where id_review<50"
        sql = "select id_review,shop_comment from shop_comment where taste=5 and environment=5 and service=5 and id_review<300000"
        # 4.执行sql
        cursor.execute(sql)
        # 5.查看结果
        sentence_dict = {}  # 用于存储id和句子的字典 sentence_dict[id] = sentence
        sentences = []  # 用于存储一句话分词后的列表
        results = cursor.fetchall()  # 用于返回多条数据
        for i in results:
            id_review = i[0]
            review = i[1]
            if review:
                review = review.replace("\n",'')
                review = review.replace("收起评价",'')
                review = review.replace(r"\n",'')
                sentence = review.replace('\u202a', '')
                sentence = sentence.replace('\u202b', '')
                sentence = sentence.replace('\u202c', '')
                sentence = sentence.replace('\u202d', '')
                sentence = sentence.replace('\u202e', '')
                sentence = sentence.replace('\u202f', '')
                sentence = sentence.replace(' ', '')
                sentence_dict[id_review]=sentence
                word_info = self.cut_count_score(sentence)
                sentences.append(word_info)
                # print(review)

        cursor.close()
        # 关闭数据库
        db.close()
        return sentences,sentence_dict

    def load_execldata(self,excel_path):
        theme_dir = os.path.join(basedir, app.config['THEME_FOLDER'])
        if not os.path.exists(theme_dir):
            os.makedirs(theme_dir)

        # excel_path = "C:/Users/司丹/Desktop/test.xls"
        print('Excel文件的路径：' + excel_path)
        excel_file = xlrd.open_workbook(excel_path)  # 打开Excel文件
        table = excel_file.sheets()[0]  # 通过索引打开
        print('已经打开的工作簿的名字：' + table.name)
        print('**********开始读取Excel单元格的内容**********')
        all_content = []
        for i in range(table.nrows):
            cell_value = table.cell(i, 0).value  # 获取单元格内容
            all_content.append(cell_value)
            # Logger().info('[' + ', '.join("'" + str(element) + "'" for element in row_content) + ']')
        print(all_content)
        print('**********Excel单元格的内容读取完毕**********')
        # sentence_dict = {}  # 用于存储id和句子的字典 sentence_dict[id] = sentence
        sentences = []  # 用于存储一句话分词后的列表
        for i in all_content:
            review = i
            if review:
                review = review.replace("\n", '')
                review = review.replace("收起评价", '')
                review = review.replace(r"\n", '')
                sentence = review.replace('\u202a', '')
                sentence = sentence.replace('\u202b', '')
                sentence = sentence.replace('\u202c', '')
                sentence = sentence.replace('\u202d', '')
                sentence = sentence.replace('\u202e', '')
                sentence = sentence.replace('\u202f', '')
                sentence = sentence.replace(' ', '')
                # sentence_dict[id_review] = sentence
                word_info = self.cut_count_score(sentence)
                sentences.append(word_info)
                print(review)
        # return sentences, sentence_dict
        return sentences
    def stopwordslist(self):
        """
        this file aim to load stopwords
        :return:
        """
        theme_dir = os.path.join(basedir, app.config['THEME_FOLDER'])
        stopwords = [line.strip() for line in
                     open(os.path.join(theme_dir,'/stopword.txt'), encoding='UTF-8').readlines()]
                     # open('/Users/sikehu/PycharmProjects/pythonProject/caculate_review_emotion_score/stopword.txt', encoding='UTF-8').readlines()]
        return stopwords
    def load_self_words(self):
        """
        this file aim to load self defination word
        :return:
        """
        # 加载自定义词汇
        jieba.add_word('宽巷子', freq=20000)
        jieba.add_word('兰韩', freq=20000)
        jieba.add_word('韩餐', freq=20000)
        jieba.add_word('装修', freq=20000)
        jieba.add_word('子非', freq=20000)
        jieba.add_word('川大', freq=20000)
        jieba.add_word('麻辣', freq=20000)
        jieba.add_word('私房菜', freq=20000)
        jieba.add_word('毛笔酥', freq=20000)
        jieba.add_word('定制款', freq=20000)
        jieba.add_word('行酒令', freq=20000)
        jieba.add_word('摇色子', freq=20000)
        jieba.add_word('米翘', freq=20000)
        jieba.add_word('宽窄巷子', freq=20000)
        jieba.add_word('播音腔', freq=20000)
        jieba.add_word('不同', freq=20000)
        jieba.add_word('刚刚熟', freq=20000)
        jieba.add_word('外酥里嫩', freq=20000)
        jieba.add_word('一级棒', freq=20000)
        jieba.add_word('店面设计', freq=20000)
        jieba.add_word('动筷子', freq=20000)
        jieba.add_word('川渝', freq=20000)
        jieba.add_word('工匠精神', freq=20000)
        jieba.add_word('毫不夸张', freq=20000)
        jieba.add_word('仪式感', freq=20000)
        jieba.add_word('商务宴请', freq=20000)
        jieba.add_word('夫妻肺片', freq=20000)
        jieba.add_word('没得挑', freq=20000)
        jieba.add_word('大众点评', freq=20000)
        jieba.add_word('一脸懵逼', freq=20000)
        jieba.add_word('没什么特别', freq=20000)
        jieba.add_word('创意菜', freq=20000)
        jieba.add_word('米二', freq=20000)
        jieba.add_word('意境菜', freq=20000)
        jieba.add_word('早有耳闻', freq=20000)
        jieba.add_word('老宅子', freq=20000)
        jieba.add_word('一步一景', freq=20000)
        jieba.add_word('嚼不动', freq=20000)
        jieba.add_word('加分项目', freq=20000)
        jieba.add_word('黑珍珠餐厅', freq=20000)
        jieba.add_word('么么哒', freq=20000)
        jieba.add_word('电话预约', freq=20000)
        jieba.add_word('商务接待', freq=20000)
        jieba.add_word('私房菜馆', freq=20000)
        jieba.add_word('文艺范', freq=20000)
        jieba.add_word('富贵花开', freq=20000)
        jieba.add_word('金熊猫餐厅', freq=20000)
        jieba.add_word('Q弹', freq=20000)
        jieba.add_word('大v', freq=20000)
        jieba.add_word('兰亭序', freq=20000)
        jieba.add_word('超级贵', freq=20000)
        jieba.add_word('很辣', freq=20000)
        jieba.add_word('源远文化', freq=20000)
        jieba.add_word('莲蓉千层酥', freq=20000)
        jieba.add_word('宰游客', freq=20000)
        jieba.add_word('年代感', freq=20000)
        jieba.add_word('打飞的', freq=20000)
        jieba.add_word('鸡蛋里挑骨头', freq=20000)
        jieba.add_word('金熊猫', freq=20000)
        jieba.add_word('出挑', freq=20000)
        jieba.add_word('清洁阿姨', freq=20000)
        jieba.add_word('烘烘', freq=20000)
        jieba.add_word('良心商家', freq=20000)
        jieba.add_word('寬窄巷子', freq=20000)
        jieba.add_word('花钱买教训', freq=20000)
        jieba.add_word('夫妻肺片', freq=20000)
        jieba.add_word('别有一番滋味', freq=20000)
        jieba.add_word('宫保鸡丁', freq=20000)
        jieba.add_word('菌菇汤', freq=20000)
        jieba.add_word('彭子渝', freq=20000)
        jieba.add_word('体验感', freq=20000)
        jieba.add_word('慢生活', freq=20000)
        jieba.add_word('地铁口', freq=20000)
        jieba.add_word('个人喜好', freq=20000)
        jieba.add_word('萌萌哒', freq=20000)
        jieba.add_word('兰亭叙', freq=20000)
        jieba.add_word('太古里', freq=20000)
        jieba.add_word('中规中矩', freq=20000)
        jieba.add_word('中矩中规', freq=20000)
        jieba.add_word('刷锅水', freq=20000)
        jieba.add_word('热门菜套路', freq=20000)
        jieba.add_word('老天不作美', freq=20000)
        jieba.add_word('不得不说', freq=20000)
        jieba.add_word('宝宝椅', freq=20000)
        jieba.add_word('兜兜转转', freq=20000)
        jieba.add_word('蜀江春', freq=20000)
        jieba.add_word('有颜有味', freq=20000)
        jieba.add_word('中医大附院', freq=20000)
        jieba.add_word('现杀现做', freq=20000)
        jieba.add_word('玉米汁', freq=20000)
        jieba.add_word('清江东路店', freq=20000)
        jieba.add_word('科华路店', freq=20000)
        jieba.add_word('自贡菜', freq=20000)
        jieba.add_word('川菜馆子', freq=20000)
        jieba.add_word('仔姜鸭', freq=20000)
        jieba.add_word('省医院', freq=20000)
        jieba.add_word('热毛巾', freq=20000)
        jieba.add_word('双人餐', freq=20000)
        jieba.add_word('棒棒哒', freq=20000)
        jieba.add_word('双人套餐', freq=20000)
        jieba.add_word('温哥华广场', freq=20000)
        jieba.add_word('青羊小区', freq=20000)
        jieba.add_word('点赞', freq=20000)
        jieba.add_word('倍加', freq=20000)
        jieba.add_word('必定', freq=20000)
        jieba.add_word('必须', freq=20000)
        jieba.add_word('并非不', freq=20000)
        jieba.add_word('不得不', freq=20000)
        jieba.add_word('不妨', freq=20000)
        jieba.add_word('常常', freq=20000)
        jieba.add_word('超', freq=20000)
        jieba.add_word('超级', freq=20000)
        jieba.add_word('处处', freq=20000)
        jieba.add_word('从来', freq=20000)
        jieba.add_word('大', freq=20000)
        jieba.add_word('大概', freq=20000)
        jieba.add_word('大约', freq=20000)
        jieba.add_word('单', freq=20000)
        jieba.add_word('单单', freq=20000)
        jieba.add_word('的确', freq=20000)
        jieba.add_word('都', freq=20000)
        jieba.add_word('顿时', freq=20000)
        jieba.add_word('多', freq=20000)
        jieba.add_word('非常', freq=20000)
        jieba.add_word('分外', freq=20000)
        jieba.add_word('赶紧', freq=20000)
        jieba.add_word('感觉', freq=20000)
        jieba.add_word('格外', freq=20000)
        jieba.add_word('更', freq=20000)
        jieba.add_word('更加', freq=20000)
        jieba.add_word('更其', freq=20000)
        jieba.add_word('更为', freq=20000)
        jieba.add_word('共', freq=20000)
        jieba.add_word('过于', freq=20000)
        jieba.add_word('还', freq=20000)
        jieba.add_word('还是', freq=20000)
        jieba.add_word('何等', freq=20000)
        jieba.add_word('很', freq=20000)
        jieba.add_word('极', freq=20000)
        jieba.add_word('极度', freq=20000)
        jieba.add_word('极端', freq=20000)
        jieba.add_word('极力', freq=20000)
        jieba.add_word('极其', freq=20000)
        jieba.add_word('极为', freq=20000)
        jieba.add_word('几乎', freq=20000)
        jieba.add_word('简直', freq=20000)
        jieba.add_word('渐渐', freq=20000)
        jieba.add_word('将要', freq=20000)
        jieba.add_word('较', freq=20000)
        jieba.add_word('较比', freq=20000)
        jieba.add_word('较为', freq=20000)
        jieba.add_word('仅仅', freq=20000)
        jieba.add_word('尽', freq=20000)
        jieba.add_word('进一步', freq=20000)
        jieba.add_word('净', freq=20000)
        jieba.add_word('居然', freq=20000)
        jieba.add_word('决非不', freq=20000)
        jieba.add_word('绝顶', freq=20000)
        jieba.add_word('绝对', freq=20000)
        jieba.add_word('立刻', freq=20000)
        jieba.add_word('连忙', freq=20000)
        jieba.add_word('略微', freq=20000)
        jieba.add_word('蛮', freq=20000)
        jieba.add_word('偶尔', freq=20000)
        jieba.add_word('偏偏', freq=20000)
        jieba.add_word('颇', freq=20000)
        jieba.add_word('恰恰', freq=20000)
        jieba.add_word('强', freq=20000)
        jieba.add_word('全', freq=20000)
        jieba.add_word('稍', freq=20000)
        jieba.add_word('稍微', freq=20000)
        jieba.add_word('甚为', freq=20000)
        jieba.add_word('十分', freq=20000)
        jieba.add_word('十足', freq=20000)
        jieba.add_word('时常', freq=20000)
        jieba.add_word('始终', freq=20000)
        jieba.add_word('太', freq=20000)
        jieba.add_word('忒', freq=20000)
        jieba.add_word('特', freq=20000)
        jieba.add_word('特别', freq=20000)
        jieba.add_word('挺', freq=20000)
        jieba.add_word('统统', freq=20000)
        jieba.add_word('完全', freq=20000)
        jieba.add_word('往往', freq=20000)
        jieba.add_word('未', freq=20000)
        jieba.add_word('未免', freq=20000)
        jieba.add_word('无比', freq=20000)
        jieba.add_word('无不', freq=20000)
        jieba.add_word('相当', freq=20000)
        jieba.add_word('幸而', freq=20000)
        jieba.add_word('幸亏', freq=20000)
        jieba.add_word('也许', freq=20000)
        jieba.add_word('一点都', freq=20000)
        jieba.add_word('一点也', freq=20000)
        jieba.add_word('一概', freq=20000)
        jieba.add_word('一律', freq=20000)
        jieba.add_word('一齐', freq=20000)
        jieba.add_word('一向', freq=20000)
        jieba.add_word('尤其', freq=20000)
        jieba.add_word('尤为', freq=20000)
        jieba.add_word('有点儿', freq=20000)
        jieba.add_word('愈', freq=20000)
        jieba.add_word('愈加', freq=20000)
        jieba.add_word('愈来愈', freq=20000)
        jieba.add_word('愈益', freq=20000)
        jieba.add_word('远远', freq=20000)
        jieba.add_word('越', freq=20000)
        jieba.add_word('越发', freq=20000)
        jieba.add_word('越加', freq=20000)
        jieba.add_word('越来越', freq=20000)
        jieba.add_word('越是', freq=20000)
        jieba.add_word('再', freq=20000)
        jieba.add_word('再三', freq=20000)
        jieba.add_word('早已', freq=20000)
        jieba.add_word('这般', freq=20000)
        jieba.add_word('这样', freq=20000)
        jieba.add_word('只', freq=20000)
        jieba.add_word('只好', freq=20000)
        jieba.add_word('终于', freq=20000)
        jieba.add_word('准', freq=20000)
        jieba.add_word('总', freq=20000)
        jieba.add_word('总共', freq=20000)
        jieba.add_word('总是', freq=20000)
        jieba.add_word('足', freq=20000)
        jieba.add_word('足足', freq=20000)
        jieba.add_word('最', freq=20000)
        jieba.add_word('最为', freq=20000)
        jieba.add_word('至极', freq=20000)
        jieba.add_word('之至', freq=20000)
        jieba.add_word('之极', freq=20000)
        jieba.add_word('贼', freq=20000)
        jieba.add_word('异常', freq=20000)
        jieba.add_word('万万', freq=20000)
        jieba.add_word('万般', freq=20000)
        jieba.add_word('滔天', freq=20000)
        jieba.add_word('十二分', freq=20000)
        jieba.add_word('莫大', freq=20000)
        jieba.add_word('奇', freq=20000)
        jieba.add_word('满心', freq=20000)
        jieba.add_word('刻骨', freq=20000)
        jieba.add_word('不堪', freq=20000)
        jieba.add_word('百分之百', freq=20000)
        jieba.add_word('备至', freq=20000)
        jieba.add_word('不得了', freq=20000)
        jieba.add_word('不可开交', freq=20000)
        jieba.add_word('不亦乐乎', freq=20000)
        jieba.add_word('不折不扣', freq=20000)
        jieba.add_word('彻头彻尾', freq=20000)
        jieba.add_word('充分', freq=20000)
        jieba.add_word('到头', freq=20000)
        jieba.add_word('地地道道', freq=20000)
        jieba.add_word('截然', freq=20000)
        jieba.add_word('惊人地', freq=20000)
        jieba.add_word('绝对化', freq=20000)
        jieba.add_word('酷', freq=20000)
        jieba.add_word('满贯', freq=20000)
        jieba.add_word('入骨', freq=20000)
        jieba.add_word('死', freq=20000)
        jieba.add_word('痛', freq=20000)
        jieba.add_word('透', freq=20000)
        jieba.add_word('完完全全', freq=20000)
        jieba.add_word('万', freq=20000)
        jieba.add_word('万分', freq=20000)
        jieba.add_word('无度', freq=20000)
        jieba.add_word('无可估量', freq=20000)
        jieba.add_word('无以复加', freq=20000)
        jieba.add_word('无以伦比', freq=20000)
        jieba.add_word('要命', freq=20000)
        jieba.add_word('要死', freq=20000)
        jieba.add_word('已极', freq=20000)
        jieba.add_word('已甚', freq=20000)
        jieba.add_word('逾常', freq=20000)
        jieba.add_word('卓绝', freq=20000)
        jieba.add_word('佼佼', freq=20000)
        jieba.add_word('不少', freq=20000)
        jieba.add_word('不胜', freq=20000)
        jieba.add_word('惨', freq=20000)
        jieba.add_word('沉', freq=20000)
        jieba.add_word('沉沉', freq=20000)
        jieba.add_word('出奇', freq=20000)
        jieba.add_word('大为', freq=20000)
        jieba.add_word('多多', freq=20000)
        jieba.add_word('多加', freq=20000)
        jieba.add_word('多么', freq=20000)
        jieba.add_word('够瞧的', freq=20000)
        jieba.add_word('够呛', freq=20000)
        jieba.add_word('好', freq=20000)
        jieba.add_word('好不', freq=20000)
        jieba.add_word('很是', freq=20000)
        jieba.add_word('坏', freq=20000)
        jieba.add_word('可', freq=20000)
        jieba.add_word('老', freq=20000)
        jieba.add_word('老大', freq=20000)
        jieba.add_word('良', freq=20000)
        jieba.add_word('颇为', freq=20000)
        jieba.add_word('甚', freq=20000)
        jieba.add_word('实在', freq=20000)
        jieba.add_word('太甚', freq=20000)
        jieba.add_word('远', freq=20000)
        jieba.add_word('着实', freq=20000)
        jieba.add_word('大不了', freq=20000)
        jieba.add_word('更进一步', freq=20000)
        jieba.add_word('还要', freq=20000)
        jieba.add_word('那般', freq=20000)
        jieba.add_word('那么', freq=20000)
        jieba.add_word('那样', freq=20000)
        jieba.add_word('如斯', freq=20000)
        jieba.add_word('尤甚', freq=20000)
        jieba.add_word('怪', freq=20000)
        jieba.add_word('好生', freq=20000)
        jieba.add_word('或多或少', freq=20000)
        jieba.add_word('略', freq=20000)
        jieba.add_word('略加', freq=20000)
        jieba.add_word('略略', freq=20000)
        jieba.add_word('略为', freq=20000)
        jieba.add_word('稍稍', freq=20000)
        jieba.add_word('稍为', freq=20000)
        jieba.add_word('稍许', freq=20000)
        jieba.add_word('些微', freq=20000)
        jieba.add_word('一点', freq=20000)
        jieba.add_word('一点儿', freq=20000)
        jieba.add_word('一些', freq=20000)
        jieba.add_word('不大', freq=20000)
        jieba.add_word('半点', freq=20000)
        jieba.add_word('不定点儿', freq=20000)
        jieba.add_word('不甚', freq=20000)
        jieba.add_word('不怎么', freq=20000)
        jieba.add_word('没怎么', freq=20000)
        jieba.add_word('轻度', freq=20000)
        jieba.add_word('弱', freq=20000)
        jieba.add_word('丝毫', freq=20000)
        jieba.add_word('相对', freq=20000)
        jieba.add_word('不为过', freq=20000)
        jieba.add_word('超额', freq=20000)
        jieba.add_word('过度', freq=20000)
        jieba.add_word('过分', freq=20000)
        jieba.add_word('过火', freq=20000)
        jieba.add_word('过劲', freq=20000)
        jieba.add_word('过猛', freq=20000)
        jieba.add_word('过热', freq=20000)
        jieba.add_word('过甚', freq=20000)
        jieba.add_word('过头', freq=20000)
        jieba.add_word('何止', freq=20000)
        jieba.add_word('偏', freq=20000)
        jieba.add_word('何况', freq=20000)
        jieba.add_word('况且', freq=20000)
        jieba.add_word('不但', freq=20000)
        jieba.add_word('不仅', freq=20000)
        jieba.add_word('连', freq=20000)
        jieba.add_word('不但不', freq=20000)
        jieba.add_word('甚至', freq=20000)
        jieba.add_word('原来', freq=20000)
        jieba.add_word('由于', freq=20000)
        jieba.add_word('以便', freq=20000)
        jieba.add_word('所以', freq=20000)
        jieba.add_word('以致', freq=20000)
        jieba.add_word('因此', freq=20000)
        jieba.add_word('既然', freq=20000)
        jieba.add_word('可见', freq=20000)
        jieba.add_word('就', freq=20000)
        jieba.add_word('则', freq=20000)
        jieba.add_word('但', freq=20000)
        jieba.add_word('却', freq=20000)
        jieba.add_word('然而', freq=20000)
        jieba.add_word('但是', freq=20000)
        jieba.add_word('只不过', freq=20000)
        jieba.add_word('可是', freq=20000)
        jieba.add_word('尽管', freq=20000)
        jieba.add_word('不过', freq=20000)
        jieba.add_word('即使', freq=20000)
        jieba.add_word('若', freq=20000)
        jieba.add_word('假如', freq=20000)
        jieba.add_word('如果', freq=20000)
        jieba.add_word('假使', freq=20000)
        jieba.add_word('纵是', freq=20000)
        jieba.add_word('纵然', freq=20000)

    def cut_count_score(self,review):
        """
        this file aim to get the emotion score of the review
        :param review:
        :return:
        """
        chinese_words = re.compile(u"[\u4e00-\u9fa5]+")
        noun_list = ['n', 'nr', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng','ad','ag','an','a']  # 名词词性\adj
        # korean_words = re.compile(u"[\uac00-\ud7ff]+")
        # 创建一个停用词列表
        stopwords = self.stopwordslist()
        #加载自定义词汇
        self.load_self_words()
        sentence = str(review)
        word_list = []
        if sentence:
            m1 = re.findall(chinese_words, sentence)
            # m2 = re.findall(korean_words, sentence)
            for i in m1:
                # 词性标注
                seg = psg.cut(i)
                # 将词性标注结果打印出来
                for ele in seg:
                    # print(ele)
                    ele = list(ele)
                    print(ele)
                    word = ele[0]
                    part_of_speech = ele[1]
                    if part_of_speech in noun_list and word not in stopwords:
                        word_list.append(word)

        print("打印word_list")
        print(word_list)
        return word_list

    def train_model(self,a,excel_path):
        '''
        lda: 计算好的话题模型
        corpus: 文档词频矩阵
        dictionary: 词语空间
        '''
        # import  sys
        # reload(sys)
        # sys.setdefaultencoding("utf-8")
        theme_dir = os.path.join(basedir, app.config['THEME_FOLDER'])
        docs  = self.load_execldata(excel_path)
        print("打印docs")
        print(docs)
        dictionary = Dictionary(docs)  # Create a dictionary representation of the documents
        # print(dictionary)
        corpus = [dictionary.doc2bow(doc) for doc in docs]  # Bag-of-words representation of the docs
        corpora.MmCorpus.serialize('corpus.mm', corpus)
        tfidf = TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        temp = dictionary[0]  # This is only to "load" the dictionary
        print("打印corpus_tfidf")
        print(corpus_tfidf)
        print('Number of unique words in initital documents:', len(dictionary))
        print('Number of unique tokens: %d' % len(dictionary))
        print('Number of documents: %d' % len(corpus))
        print("打印dictionary")
        print(dictionary)
        print("打印corpus")
        print(corpus)
        perps1 = []
        perps2 = []
        cohers1=[]
        cohers2=[]

        corpus_test = corpora.MmCorpus('corpus.mm')
        testset = []
        for c in range(int(corpus_test.num_docs / 3)):  # 如何抽取训练集
            testset.append(corpus_test[c * 3])
        # for c in range(int(corpus_test.num_docs / 10)):  # 如何抽取训练集
        #     testset.append(corpus_test[c * 10])
        for num_topics in a:
            #训练LDA模型
            chunksize = 8688  # Size of the doc looked at every pass
            chunksize = 10  # Size of the doc looked at every pass
            passes = 35  # Number of passes through the corpus
            iterations = 400  # Maximum number of iterations through the corpus when inferring the topic distribution of a corpus
            eval_every = None  # Don't evaluate model perplexity, takes too much time.
            id2word = dictionary.id2token

            model1 = LdaModel(corpus=corpus, id2word=id2word, chunksize=chunksize,
                             alpha='auto', eta='auto',
                             iterations=iterations, num_topics=num_topics,
                             passes=passes, eval_every=eval_every, random_state=2)
            model2 = LdaModel(corpus=corpus_tfidf, id2word=id2word, chunksize=chunksize,
                              alpha='auto', eta='auto',
                              iterations=iterations, num_topics=num_topics,
                              passes=passes, eval_every=eval_every, random_state=2)
            top_topics1 = model1.top_topics(corpus)
            top_topics2 = model2.top_topics(corpus)
            print("主题打印1")
            print(top_topics1)
            print("主题打印2")
            print(top_topics2)
            # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
            avg_topic_coherence1 = sum([t[1] for t in top_topics1]) / num_topics
            avg_topic_coherence2 = sum([t[1] for t in top_topics2]) / num_topics
            prep1 = self.perplexity(model1, testset, dictionary, len(dictionary.keys()), num_topics)
            prep2 = self.perplexity(model2, testset, dictionary, len(dictionary.keys()), num_topics)
            perps1.append(prep1)
            perps2.append(prep2)
            cohers1.append(avg_topic_coherence1)
            cohers2.append(avg_topic_coherence2)
            print('Average topic coherence1: %.4f.' % avg_topic_coherence1)
            print('Average topic coherence2: %.4f.' % avg_topic_coherence2)
            # print(top_topics)

            txt1 = "bad1theme{}.txt".format(num_topics)
            txt2 = "badd2theme{}.txt".format(num_topics)
            # modelname1 = 'bad1LDA{}'.format(num_topics)
            # modelname2 = 'bad2LDA{}'.format(num_topics)
            html1 = "bad1_{}.html".format(num_topics)
            html2 = "bad2_{}.html".format(num_topics)
            with open(os.path.join(theme_dir,txt1), "w", encoding='utf-8') as f:
                for i in top_topics2:
                    f.write(str(i))
                    f.write('\n')
            with open(os.path.join(theme_dir,txt2), "w", encoding='utf-8') as f:
                for i in top_topics1:
                    f.write(str(i))
                    f.write('\n')
            # Save model to disk.
            # model2.save(modelname1)
            # model1.save(modelname2)
            # try:

            # d1 = pyLDAvis.gensim.prepare(model1, corpus, dictionary)    #当模型的主题为1时不行
            # d2 = pyLDAvis.gensim.prepare(model2, corpus, dictionary)
            #
            # pyLDAvis.save_html(os.path.join(theme_dir,d2), html1)  # 将结果保存为该html文件
            # pyLDAvis.save_html(os.path.join(theme_dir,d1), html2)  # 将结果保存为该html文件
            # except:
            #     pass
        # print(top_topics)
        return perps1,perps2,cohers1,cohers2

    def perplexity(self,ldamodel, testset, dictionary, size_dictionary, num_topics):
        print('num of topics: %s' % num_topics)
        prep = 0.0
        prob_doc_sum = 0.0
        topic_word_list = []
        for topic_id in range(num_topics):
            topic_word = ldamodel.show_topic(topic_id, size_dictionary)
            dic = {}
            for word, probability in topic_word:
                dic[word] = probability
            topic_word_list.append(dic)
        doc_topics_ist = []
        for doc in testset:
            doc_topics_ist.append(ldamodel.get_document_topics(doc, minimum_probability=0))
        testset_word_num = 0
        for i in range(len(testset)):
            prob_doc = 0.0  # the probablity of the doc
            doc = testset[i]
            doc_word_num = 0
            for word_id, num in dict(doc).items():
                prob_word = 0.0
                doc_word_num += num
                word = dictionary[word_id]
                for topic_id in range(num_topics):
                    # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                    prob_topic = doc_topics_ist[i][topic_id][1]
                    prob_topic_word = topic_word_list[topic_id][word]
                    prob_word += prob_topic * prob_topic_word
                prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
            prob_doc_sum += prob_doc
            testset_word_num += doc_word_num
        prep = math.exp(-prob_doc_sum / testset_word_num)  # perplexity = exp(-sum(p(d)/sum(Nd))
        print("模型困惑度的值为 : %s" % prep)
        return prep

    def graph_draw(self,topic,prep1, prep2, cohers1, cohers2):  # 做主题数与困惑度的折线图
        theme_dir = os.path.join(basedir, app.config['THEME_FOLDER'])
        score_list = []
        score_list.append(prep1)
        score_list.append(prep2)
        score_list.append(cohers1)
        score_list.append(cohers2)
        with open("score_info.txt","w",encoding='utf-8') as f:
            f.write(str(score_list))
        plt.clf()  # 清空图像
        plt.plot(topic, prep1, 'skyblue', label='lda_perp')
        plt.plot(topic, prep2, 'gray', label='tfidf_lda_perp')
        plt.plot(topic, cohers1, 'darkorange', label='lda_coher')
        plt.plot(topic, cohers2, 'darkseagreen', label='tfidf_lda_coher')
        plt.title('Perplexity and Coherence Score')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        # plt.savefig('/root/hsk/lda/bad/totalbad.png')  # 保存图片
        plt.savefig(os.path.join(theme_dir,'totalbad.png'))  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(topic, prep1, 'skyblue', label='lda_perp')
        plt.plot(topic, prep2, 'darkorange', label='tfidf_lda_perp')
        plt.title('Perplexity Score')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        # plt.savefig('/root/hsk/lda/bad/perlbad.png')  # 保存图片
        plt.savefig(os.path.join(theme_dir,'perlbad.png'))  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(topic, cohers1, 'skyblue', label='lda_coher')
        plt.plot(topic, cohers2, 'darkorange', label='tfidf_lda_coher')
        plt.title(' Coherence Score')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        # plt.savefig('/root/hsk/lda/bad/coherbad.png')  # 保存图片
        plt.savefig(os.path.join(theme_dir,'coherbad.png'))  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(topic, prep1, 'skyblue', label='lda_perp')
        plt.plot(topic, cohers1, 'darkorange', label='lda_coher')
        plt.title('Perplexity and Coherence Score of LDA model ')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        plt.savefig(os.path.join(theme_dir,'total1bad.png'))  # 保存图片
        # plt.savefig('/root/hsk/lda/bad/total1bad.png')  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(topic, prep2, 'skyblue', label='tfidf_lda_perp')
        plt.plot(topic, cohers2, 'darkorange', label='tfidf_lda_coher')
        plt.title('Perplexity and Coherence Score of Tfidf_LDA model')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        # plt.savefig('/root/hsk/lda/bad/total2bad.png')  # 保存图片
        plt.savefig(os.path.join(theme_dir,'total2bad.png'))  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(topic, prep1, 'skyblue', label='perplexity')
        plt.title('Perplexity Score')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        # plt.savefig('/root/hsk/lda/bad/totalbad.png')  # 保存图片
        plt.savefig(os.path.join(theme_dir,'lda_prep.png'))  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(topic, prep2, 'skyblue', label='perplexity')
        plt.title('Perplexity Score')
        plt.legend(loc='upper right')
        plt.xlabel("Number of topic")
        plt.ylabel("Score")
        # plt.savefig('/root/hsk/lda/bad/totalbad.png')  # 保存图片
        plt.savefig(os.path.join(theme_dir,'tfidf_prep.png'))  # 保存图片



if __name__=='__main__':
    # obj = Clustering()
    # # a = range(2, 10, 1)  # 主题个数
    # a = range(2, 21, 1)  # 主题个数
    # prep1, prep2, cohers1, cohers2=obj.train_model(a,"E:/test.xls")
    # obj.graph_draw(a, prep1, prep2, cohers1, cohers2)
    THEME = []
    with open("theme/bad1theme2.txt", mode="rt", encoding="utf-8") as f:
        res = f.read()
        print(res)
        # data = re.sub("[A-Za-z0-9\!\%\[\]\,\。\ \.\']", "", res)
        # print(data)
        a = res.split("\'")[1]
        THEME.append(a)
        a = res.split("\'")[3]
        THEME.append(a)
        a = res.split("\'")[5]
        THEME.append(a)
        a = res.split("\'")[7]
        THEME.append(a)
        a = res.split("\'")[9]
        THEME.append(a)
    print(THEME)
    # obj = Clustering()
    # sentences = obj.load_execldata("E:/test.xls")
    # print("-"*100)
    # print(sentences)


