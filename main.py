from pyecharts.charts import Bar,Pie,Line,Liquid,Bar3D
from pyecharts.commons.utils import JsCode
from pyecharts import options as opts
import streamlit_echarts as ste
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import streamlit as st
import os
from streamlit_echarts import st_pyecharts
from PIL import Image
from wordcloud import WordCloud,ImageColorGenerator
import jieba
import time

#一些没用的侧边栏小组件,只是为了让页面布局更好看
with st.sidebar:
    st.metric(label="系统时间：", value=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    if st.button('雪花'):
        st.snow()
    if st.button('气球'):
        st.balloons()
#We will remove the ability to do this as it requires the use of Matplotlib's global figure object, which is not thread-safe.
st.set_option('deprecation.showPyplotGlobalUse', False)  #消除警报
#设置页面图片
image = Image.open(os.path.dirname(os.path.abspath(__file__))+'/steam.jpg')
#果运行报错，请首先在资源管理器中打开程序所在文件夹，或执行以下注释代码，请将路径改为该图片在自己计算机下的路径
#image = Image.open("/steam.jpg")
st.image(image, caption='2021Year')
st.title('2021年steam游戏发售数据可视化')
st.subheader("基于streamlit的可视化数据")
#获取路径
subpath=os.path.dirname(os.path.abspath(__file__))+"/2021 - Year Stats.csv"
#如果运行报错，请首先在资源管理器中打开程序所在文件夹，或执行以下注释代码，路径改为自己的
#subpath=""
df = pd.read_csv(subpath, index_col=0, encoding='gbk')
df['Price'] = pd.to_numeric(df['Price'])
df_re = df[df['Review'].values!=0].copy()  #拷贝一份好评不为零(存在评价)的
df_mon=df.groupby(['Month'])
#排名前50的游戏拥有数与价格随时间变化
def tDBar(df):
    #mon = st.slider('请选择时间', 1, 12, 1)
    get=df.groupby(['Month']).get_group(mon).head(50)
    game=get['Game']
    game_list=game.values.tolist()
    owners=get['Owners']
    owner_list=owners.values.tolist()
    price=get['Price']
    price_list=sorted(price.values.tolist())
    data=[]
    for index, row in get.iterrows():
        x = row['Price']
        y = row['Game']
        z = row['Owners']
        data.append([x, y, z])
    bar3d=Bar3D()
    bar3d.add(
        series_name="拥有人数",
        data=data,
        xaxis3d_opts=opts.Axis3DOpts(type_="category", data=price_list),
        yaxis3d_opts=opts.Axis3DOpts(type_="category", data=game_list),
        zaxis3d_opts=opts.Axis3DOpts(type_="value"),
    )
    bar3d.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=20,
            range_color=[
                "#313695",
                "#4575b4",
                "#74add1",
                "#abd9e9",
                "#e0f3f8",
                "#ffffbf",
                "#fee090",
                "#fdae61",
                "#f46d43",
                "#d73027",
                "#a50026",
            ],))
    st_pyecharts(bar3d)
st.markdown("## :mag_right:月排名前50游戏的拥有数与价格3D图")
mon = st.slider('请选择时间(月)', 1, 12, 1)
tDBar(df)
#评价信息
def Review_Timeline(df):
    re_liquid=df.groupby(['Month'])['Review'].mean()
    alist=re_liquid.values.tolist()
    new_list = [x/100 for x in alist]
    mid_np = np.array(new_list)
    mid_np_4f = np.round(mid_np,4) 
    n2_list = list(mid_np_4f)     #列表处理，列表转np数组再转列表
    #mon = st.slider('请选择时间', 1, 12, 1)
    want=n2_list[mon-1]
    liquid=Liquid()
    liquid.add("好评率", [want],
               label_opts=opts.LabelOpts(
            font_size=35,
            formatter=JsCode(
                """function (param) {
                    return (Math.floor(param.value * 10000) / 100) + '%';
                }"""            #设置精度
            )))
    liquid.set_global_opts(title_opts=opts.TitleOpts(title="{}月好评率-水球图".format(mon)))
    st_pyecharts(liquid)
    
st.markdown("## :+1:综合好评率")
Review_Timeline(df_re)
st.divider()
#月平均价格柱状图
def Price_Bar(df):
    color_function = """
        function (params) {
            if (params.value > 0 && params.value < 5.5) {
                return 'red';
            } else if (params.value > 5.5 && params.value < 6.5) {
                return 'green';
            }
            return 'gold';
        }
        """
    title_len = df.groupby(['Month'])['Price'].mean().round(2)  #设置小数点后两位
    #转化为列表
    agg_price=title_len.values.tolist()
    bar = Bar()
    bar.add_xaxis(['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'])
    bar.add_yaxis("售价$(单位:美元)",agg_price,itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title="月平均售价$(美元)"),
        toolbox_opts=opts.ToolboxOpts(),
    )
    return bar
#月平均价格折线图
def Price_Line(df):
    title_len = df.groupby(['Month'])['Price'].mean().round(2)  #设置小数点后两位
    #转化为列表
    agg_price=title_len.values.tolist()
    line = Line()
    line.add_xaxis(['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'])
    line.add_yaxis("售价$(单位:美元)",agg_price)
    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title="月平均售价$(美元)"),
        toolbox_opts=opts.ToolboxOpts(),
    )
    return line
#月价格散点图
def Price_sca(df):
    X=df['Date']
    Y=df['Price']
    plt.style.use('seaborn')
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    plt.figure(figsize=(15, 5))
    plt.scatter(X,Y, s=12000/(df.index+200), alpha=.7,cmap=plt.get_cmap('RdYlBu'))
    ax = plt.gca()
    tick_spacing = 30
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    plt.xlabel('时间轴(1~12月)',fontsize=20)
    plt.ylabel('价格',fontsize=20)
    st.pyplot()
st.markdown("## :moneybag:月售价图表")
option1 = st.selectbox('选择要显示的图表',('柱状图', '折线图','散点图'))
if option1=="柱状图":
    st_pyecharts(Price_Bar(df))
elif option1=="折线图":
    st_pyecharts(Price_Line(df))
elif option1=="散点图":
    Price_sca(df)
#分线
st.divider()
#月游戏发行数量
def Game_Bar(df):
    color_function = """
        function (params) {
            if (params.value > 0 && params.value < 800) {
                return 'red';
            } else if (params.value > 800 && params.value < 1000) {
                return 'green';
            }
            return 'gold';
        }
        """
    game_count=df.groupby(['Month'])['Game'].count()
    counts=game_count.values.tolist()
    bar = Bar()
    bar.add_xaxis(['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'])
    bar.add_yaxis("发行数",counts,itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title="月发行数-柱状图"),
        toolbox_opts=opts.ToolboxOpts(),
    )
    return bar
def Game_Line(df):
    game_count = df.groupby(['Month'])['Game'].count()
    counts=game_count.values.tolist()
    line = Line()
    line.add_xaxis(['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'])
    line.add_yaxis("发行数",counts)
    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title="月发行数-折线图"),
        toolbox_opts=opts.ToolboxOpts(),
    )
    return line
def Game_Pie(df):
    game_count=df.groupby(['Month'])['Game'].count()
    counts=game_count.values.tolist()
    mon=['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
    pie=Pie()
    pie.add("",[list(z) for z in zip(mon,counts)],center=["75%", "50%"],radius=["40%", "75%"])
    pie.set_global_opts(title_opts=opts.TitleOpts(title="月发行数-圆环图"),
                        legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"))
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    return pie
st.markdown("## :bulb:月发行数图表")
genre = st.radio('选择要显示的图表',('柱状图', '折线图','圆环图'))
if genre=="柱状图":
    st_pyecharts(Game_Bar(df))
elif genre=="折线图":
    st_pyecharts(Game_Line(df))
elif genre=="圆环图":
    st_pyecharts(Game_Pie(df))
st.divider()

def Game_sort(df):
    color_function = """
        function (params) {
            if (params.value > 0 && params.value < 86) {
                return 'red';
            } else if (params.value > 86 && params.value < 90) {
                return 'blue';
            }
            return 'green';
        }
        """
    game10=df.sort_values(by="Review",ascending=False)
    game10_h=game10.head(20)
    review_h=game10_h['Review'].values.tolist()
    game=game10_h['Game'].values.tolist()
    bar = Bar()
    bar.add_xaxis(game)
    bar.add_yaxis("前20",review_h,itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title="好评率前20游戏好评率排行"),
        toolbox_opts=opts.ToolboxOpts(),
    )
    return bar
st_pyecharts(Game_sort(df_re))
st.divider()
#发行商与开发商词云
def Dev_Wordcloud(df):
    text=''
    for line in df['Developer']:
        text += ' '.join(jieba.cut(str(line), cut_all=False))
        text +=' '
    wc = WordCloud(
        background_color='#003366',
        font_path='C:\Windows\Fonts\msyh.ttc',
        max_words=1000,
        max_font_size=150,
        min_font_size=10,
        width=960, 
        height=540,
        prefer_horizontal=1,
        random_state=50,
    )
    wc.generate_from_text(text)
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    st.markdown("开发商词云")
    st.pyplot()
def Pub_Wordcloud(df):
    text=''
    for line in df['Publisher']:
        text += ' '.join(jieba.cut(str(line), cut_all=False))
        text +=' '
    wc = WordCloud(
        background_color='#003366',
        font_path='C:\Windows\Fonts\msyh.ttc',
        max_words=1000,
        max_font_size=150,
        min_font_size=10,
        width=960, 
        height=540,
        prefer_horizontal=1,
        random_state=50,
    )
    wc.generate_from_text(text)
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    st.markdown("发行商词云")
    st.pyplot()
#游戏词云
def Game_Wordcloud(df):
    text=''
    for line in df['Game']:
        text += ' '.join(jieba.cut(str(line), cut_all=False))
        text +=' '
    wc = WordCloud(
        background_color='#003366',
        font_path='C:\Windows\Fonts\msyh.ttc',
        max_words=1000,
        max_font_size=150,
        min_font_size=10,
        width=960, 
        height=540,
        prefer_horizontal=1,
        random_state=50,
    )
    wc.generate_from_text(text)
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    st.markdown("游戏词云")
    st.pyplot()
st.markdown("## :scroll:词云")
option2 = st.multiselect(
    '请选择要展示的词云',
    ['开发商', '发行商', '游戏'],
    ['发行商'])
if option2==['开发商']:
    Dev_Wordcloud(df)
elif option2==['发行商']:
    Pub_Wordcloud(df)
elif option2==['游戏']:
    Game_Wordcloud(df)
elif option2==['开发商','发行商']:
    Dev_Wordcloud(df)
    Pub_Wordcloud(df)
elif option2==['发行商','开发商']:
    Pub_Wordcloud(df)
    Dev_Wordcloud(df)
elif option2==['发行商','游戏']:
    Pub_Wordcloud(df)
    Game_Wordcloud(df)
elif option2==['游戏','发行商']:
    Game_Wordcloud(df)
    Pub_Wordcloud(df)
elif option2==['开发商','游戏']:
    Dev_Wordcloud(df)
    Game_Wordcloud(df)
elif option2==['游戏','开发商']:
    Game_Wordcloud(df)
    Dev_Wordcloud(df)
else:
    Dev_Wordcloud(df)
    Pub_Wordcloud(df)
    Game_Wordcloud(df)




