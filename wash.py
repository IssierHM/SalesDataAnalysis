import pandas as pd
import re

path = 'D:/pycode/Pratice/steam_game_visualization/2021 - Year Stats.csv'
df = pd.read_csv(path,index_col=0,encoding='gbk')
#处理价格数据
def price(x):
    try:
        pricenum=int(x['Price'].replace('$',''))
    except:
        pricenum=0
    return pricenum
df['Price'] = df.apply(lambda x:price(x),axis=1)
df['Price'] = pd.to_numeric(df['Price'])
#处理好评率
def review(x):
    try:
        reviewnum=int(x['Review'].replace('N/A (N/A/','').replace('%)',''))
    except:
        reviewnum=0
    return reviewnum
df['Review'] = df.apply(lambda x:review(x),axis=1)
df['Review'] = pd.to_numeric(df['Review'])
#玩家数
def owners(x):
    List = x['Owners'].replace(',', '')
    cut = List.index("?")  # 查找第一个 "?" 的索引位置
    n_str = List[:cut]  # 提取 "?" 之前的子字符串
    len1 = len(n_str)   
    y=List.replace("?..?",'')
    minnum = int(y[:len1])
    maxnum = int(y[len1:])
    average = (minnum + maxnum) / 2
    return average
df['Owners']=df.apply(lambda x:owners(x),axis=1)
df['Owners']=pd.to_numeric(df['Owners'])
df=df.drop('Unnamed: 8', axis=1)
df.to_csv(path)
print("Done")