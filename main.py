import requests
from bs4 import BeautifulSoup
import jieba
import jieba.analyse as anls
from selenium import webdriver
from lxml import etree
import  re
from time import sleep
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud
from selenium.webdriver.common.keys import Keys


def get_words():
    url="https://news.cnblogs.com/n/recommend"
    header={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
    }
    for i in range(100):
        parm = {
            "page": i+1
        }
        response=requests.request(method="post",url=url,params=parm,headers=header)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "lxml")
        h2= soup.find_all('h2', class_='news_entry')
        with open("data/words.txt","a",encoding="utf-8") as fp:
             for j in h2:
                fp.write(j.find("a").text+"\n")


def words_filter():
    jieba.load_userdict("data/THUOCL_IT.txt")
    jieba.analyse.set_stop_words("data/stopword.txt")
    text=str()
    with open("data/words.txt","r",encoding="utf-8") as fp:
        text=fp.read()
    words_list=jieba.lcut(text,False)
    words_filter_list = [word for word in words_list if word in jieba.dt.FREQ and len(word)>1  and not word.isnumeric()]
    with open("data/words_res.txt","a",encoding="utf-8") as fp:
        for word in words_filter_list:
            fp.write(word + "\n")
    res = str()
    with open("data/words_res.txt", "r", encoding="utf-8") as fp:
        res=fp.read()
    print("基于TF-IDF提取关键词结果：")
    with open("data/words_ans.txt","a",encoding="utf-8") as fp:
        for x, w in anls.extract_tags(res, topK=100, withWeight=True):
            fp.write('%s\t%s\n'%(x,w))
            print('%s\t%s' % (x, w))
def words_explain():
    word_list=[]
    with open("data/words_ans.txt","r",encoding="utf-8") as fp:
        line=fp.readline()
        while line:
            word_list.append(line.split("\t")[0])
            line=fp.readline()
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--disable-gpu')
    chro=webdriver.Chrome(executable_path="data/chromedriver.exe",options=option)
    with open("data/words_explain.txt", "a", encoding="utf-8") as fp:
        for i in word_list:
            chro.get("https://baike.sogou.com")
            sleep(2)
            query = chro.find_element_by_id("searchText")
            query.clear()
            query.send_keys(i, Keys.ENTER)
            sleep(2)
            page_text=chro.page_source
            tree=etree.HTML(page_text)
            divs=tree.xpath('//div[@class="abstract"]//text()')
            explain=''
            for j in divs:
                j=re.sub('\\s','',j)
                explain+=j
            print(i)
            fp.write(i+"\t"+explain+"\n")
    chro.quit()
def word_cloud():
    word_list=[]
    with open("data/words_ans.txt","r",encoding="utf-8") as fp:
        line=fp.readline()
        while line:
            word_line=line.strip().split("\t")
            word_list.append(word_line[0])
            line=fp.readline()
    text="/".join(word_list)
    maskph = np.array(Image.open('data/bg.jfif'))
    wordcloud:WordCloud = WordCloud(mask=maskph, background_color='white', font_path='data/SimHei.ttf',
                          margin=2).generate(text)

    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
    wordcloud.to_file("data/词云.jpg")




if __name__ == '__main__':
    if os.path.exists("data/words.txt"): os.remove("data/words.txt")
    if os.path.exists("data/words_res.txt"): os.remove("data/words_res.txt")
    if os.path.exists("data/words_ans.txt"): os.remove("data/words_ans.txt")
    if os.path.exists("data/words_explain.txt"): os.remove("data/words_explain.txt")
    get_words()
    words_filter()
    words_explain()
    word_cloud()