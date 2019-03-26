# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 09:43:02 2018

@author: maxmaxwfl
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time,datetime
import urllib
import re
import os
import urllib2
import pandas as pd
from bs4 import BeautifulSoup,Comment
import datetime
import hashlib
import requests


#标题过滤，返回标题中所包含的标签
def head_filter(headline):
    #待搜索关键词列表
    keyword_list = [u"社区",u"坊会",u"坊众福利会",u"街坊会",u"街坊福利会",u"街坊福利事务促进会",u"街坊福利委员会",
                    u"社会企业",u"业主立案法团",u"互助委员会",u"业主委员会"]
    labels=[]
    for i in range(len(keyword_list)):
        if keyword_list[i] in headline:
            labels.append("\"%s\""%keyword_list[i])
    return labels
#时间过滤，筛选出2018,2017,2016年的新闻，其中日期以'/'分割,例如对于2018/07/05,split函数作用就是变为["2018","07","05"]的列表
def time_filter(times):
    year = times.split('/')[0]
    
    if(year==u'2018' or year==u'2017' or year==u'2016'):
        return True
    else:
        return False

#提取某一具体新闻网页中的各个信息
def get_link_content_text(url):
    html=urllib.urlopen(url)        
    #使用beautifulsoup解析网页内容
    sub_sp=BeautifulSoup(html,"html.parser",from_encoding="gb18030")
    #设置唯一文件名
    #获取今天的日期
    today = datetime.date.today().strftime('%Y%m%d')
    #加上CN前缀
    a_id = "CN"+today
    #使用全局变量
    global page_nums
    
    #需根据实际内容修改类型   
    #作者
    author = ""     
    #图片
    all_img=[]    
    #附件MD5
    attach_md5 = []
    #附件源文件
    attach_ori = []
    """
    正文部分:需根据标签修改find_all中的标签名
    html_context 保存的是带html原代码的原文
    all_context 是通过正则表达式将html_context中所有<>去掉得到内容
    """
    all_context = ""
    #找到网页中 所有td标签，class为'article-content'的内容
    context = sub_sp.find('td',attrs={'class':'article-content'})   
    #去除style标签
    [s.extract() for s in context('style')]
    
    
    if(context):
        """
        html_context =""
        #因为context结果是个数组，因此需用for循环读取context中所有元素
        for line in context:                            
            html_context +=str(line)
        #去除html中的所有<>内容
        html_label = re.compile('<.*?>')
        all_context = html_label.sub("",html_context)
        #去除空格
        all_context = all_context.strip()
        #得到摘要为正文的第一段
        abstract = all_context.split("。")[0]
        """
        html_context = context.prettify()    
        all_context = context.text.strip()
        abstract = all_context.encode("utf-8").split("。")[0]
    else:
        all_context=""
        abstract=""
        html_context=""
    
    #设置储存路径
    home_dir = "e:/"+today
    page_str = str(page_nums)
    a_id += page_str.zfill(6)
    #设置每个网页的路径
    dir_path = os.path.join(home_dir,a_id)
    #如果路径没有该文件夹，则创建新的
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
    #如果子文件夹路径不存在，则创建文件夹
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    #附件部分
    attach_link = sub_sp.find(href=re.compile("doc|xls|docx|pdf|txt|xlsx|csv|xml"))
    
    if(attach_link):
        file_path = attach_link["href"]
        if 'http' not in file_path:
            file_path = homepage+ '/' + file_path
            
        file_name = file_path.split('/')[-1]
        attach_ori.append("\"%s\""%file_name)
        file_before = file_name.split('.')[0]
        file_after = file_name.split('.')[1]
        m2 = hashlib.md5()
        m2.update(file_before)
        md5_file_before = m2.hexdigest()[8:-8]
        md5_filename = md5_file_before + '.'+ file_after
        attach_md5.append("\"%s\""%md5_filename)
        resource = requests.get(file_path)
        #得到附件存储路径
        file_save_path = dir_path + '/' +md5_filename
        #将路径编码为utf-8
        file_save_path = file_save_path.encode('utf-8')
        file_path = file_path.encode("utf-8")
        with open(file_save_path, mode="wb") as fh:
            fh.write(resource.content)
        
    #图片部分

    #用beautifulsoup解析html_context
    sub_c = BeautifulSoup(html_context,"html.parser",from_encoding="gb18030")
    #找出正文中所有的img标签
    imgs =  sub_c.select("p img")
    for i in range(len(imgs)):
        #读取img标签中的src标签，获取图片路径
        imgpath=imgs[i]['src']
        #获取src路径中'/'后的最后一截，如对于/edit/uploadfile/20180709161440651.jpg，提取的是20180709161440651.jpg
        imgname = imgpath.split('/')[-1]
        #去除imgname中的'?'
        imgname= re.sub(r'\?',"",imgname)
        #如果字符串长度大于4,且倒数第四位不是'.'，则需手动加.jpg
        if (len(imgname)>=4):
            if(imgname[-4] != '.'):
                imgname += '.jpg'
        else:
            imgname += '.jpg'
        #对图片进行MD5编码
        #将图片名按照'.'进行分割        
        imgname_before = imgname.split('.')[0]
        imgname_after  = imgname.split('.')[1]
        m2 = hashlib.md5()
        m2.update(imgname_before)
        md5_before = m2.hexdigest()[8:-8]
        md5_imgname = md5_before + '.'+ imgname_after
        all_img.append("\"%s\""%md5_imgname)
        
        #将html_context中的img标签替换为 image:(MD5加密后图片名)
        img_str = "image:(%s)"%md5_imgname
        #将img_str编码为utf-8                
        img_str = img_str.encode('utf-8')
        #使用正则表达式将html_context内的img标签替换为img_str字符串，re.sub中的count参数意思为一次for循环替换一个<img>标签
        html_context = re.sub("<img .*?>",img_str,html_context,count=1)
        
        #对于路径，如果没有http，则将原网站homepage+路径作为图片路径
        if 'http' not in imgpath:
            whole_img = homepage+ '/' + imgpath
        else:
            whole_img = imgpath

        #得到图片存储路径
        path = dir_path + '/' +md5_imgname
        #将路径编码为utf-8
        path = path.encode('utf-8')
        #将图片url路径编码为utf-8
        whole_img = whole_img.encode('utf-8')
        #保存图片
        try:
            urllib2.urlopen(whole_img,timeout=1)
            urllib.urlretrieve(whole_img,path)
        except IOError,UnicodeDecodeError:
            print whole_img      

    return a_id,abstract,author,html_context,all_context,attach_md5,attach_ori,all_img

#找出要提取的新闻网页url
def get_content(bs,save_context):
    global page_nums
    #需要更改
    source= u"上海市浦东新区周家渡街道"
    country = u"中国"
    context_city="上海"
    city =  u"上海"
    constitute = u"上海市浦东新区周家渡街道"
    article_type ='html'
    small_img = ""
    
    #找出所有新闻链接和对应时间
    link_a_all = bs.find_all('td',attrs={'width':'561'})
    time_all = bs.find_all('td',attrs={'class':'sqdt2'})
    for i in range(len(link_a_all)):
        one_context =[]
        #找出新闻表格中的<a>标签
        link_a = link_a_all[i].a
        #用.string提取时间标签中的时间                   
        time_str = time_all[i].string[1:-1]
        time_format = datetime.datetime.strptime(time_str, '%Y/%m/%d')
        new_time = time_format.strftime('%Y-%m-%d %H:%M:%S')
        if(link_a.string and time_str):
            #得到新闻标题中的标签
            labels = head_filter(link_a.string)
            #判断时间是否为2018,2017,2016年
            time_flag = time_filter(time_str)
            
            #如果标签中有内容，而且时间符合条件
            if (len(labels)>0 and time_flag==True):
                
                #提取符合条件新闻的url，需要修改
                sub_url = link_a['href']                
                whole_url = homepage + '/' + sub_url
                #print whole_url
                a_id,abstract,author,html_context,all_context,attach_md5,attach_ori,all_img=get_link_content_text(whole_url)
                #print whole_url
                #唯一串行号	英文标题	中文标题	英文摘要	中文摘要	
                #作者	 发布单位	发布时间	标签	英文正文含标签	英文正文	中文正文含标签	中文正文	
                #附件名称（md5存储）	附件原名称	文章内容图片	文章内容城市	信息源网址	信息源国家	
                #信息源城市	信息源机构	文章类型	搜索关键词	缩略图
                one_context.append(a_id)
                one_context.append("")
                one_context.append(link_a.string)
                one_context.append("")
                one_context.append(abstract)
                one_context.append(author)
                one_context.append(source)                
                one_context.append(new_time)        
                one_context.append(labels)  
                one_context.append("")
                one_context.append("")
                one_context.append(html_context)
                one_context.append(all_context)
                one_context.append(attach_md5)
                one_context.append(attach_ori)
                one_context.append(all_img)
                one_context.append(context_city)
                one_context.append(whole_url)
                one_context.append(country)
                one_context.append(city)
                one_context.append(constitute)
                one_context.append(article_type)
                one_context.append(labels)
                one_context.append(small_img)
                
                save_context.append(one_context)
                page_nums +=1
            else:
                print 'not added'
    return save_context

#需修改，根据不同网站来改homepage
homepage='http://www.zjd.gov.cn'
#需根据每个网站具体数目来设置下一个网站的page_nums,如网站1有10个，则对于网站2则需设page_nums=11,类似于offset的概念
page_nums = 0


test=[]
#设置selenium浏览器为chrome浏览器
driver = webdriver.Chrome()
#进入主页
driver.get("http://www.zjd.gov.cn/index.asp")
#根据搜索框id = 'searchinput'，找到搜索框位置
elem =driver.find_element_by_id("searchinput")
#清楚搜索框中内容
elem.clear()
#输入社区
elem.send_keys(u"社区")
#找到搜索按钮，并点击
driver.find_element_by_class_name("input_04").click()
#用beautifulsoup解析按钮点击后的网页
sub_sp=BeautifulSoup(driver.page_source,"html.parser",from_encoding="gb18030")
test = get_content(sub_sp,test)

#人工看发现只有关键词'社区'有搜索结果，其他几个关键词都没有搜索结果，而且搜“社区”后从第十四页开始都是2015年的新闻了，因此只用再点12次下一页
for i in range(13):
    #找到下一页的按钮，并点击
    driver.find_element_by_link_text(u"下一页").click()
    sub_sp=BeautifulSoup(driver.page_source,"html.parser",from_encoding="gb18030")
    #print sub_sp
    test = get_content(sub_sp,test)

today = datetime.date.today().strftime('%Y%m%d')
#设置csv文件保存路径，一个网站一个csv，以后网站的csv文件改名为pachong1.csv,pachong2.csv，。。。。以此类推
csv_path = 'e:/'+today + '/'+'pachong.csv'
#将数组转为pandas dataframe
df1 = pd.DataFrame(test,columns=["唯一串行号","英文标题","中文标题","英文摘要","中文摘要",
                                 "作者","发布单位","发布时间","标签","英文正文含标签","英文正文","中文正文含标签","中文正文",
                                 "附件名称（md5存储）","附件原名称","文章内容图片","文章内容城市","信息源网址","信息源国家",
                                 "信息源城市","信息源机构","文章类型","搜索关键词","缩略图"])
#去除重复的“中文标题”
df1 = df1.drop_duplicates("中文标题")
#将dataframe写入文件
df1.to_csv("a.csv",encoding="utf-8",index=False)
a = pd.read_csv("a.csv",encoding="utf-8")
a.to_excel("1.xlsx",sheet_name='data',index=False)
