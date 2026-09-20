import pandas as pd
df=pd.read_csv(r"C:\Users\白玉琦\PycharmProjects\PythonProject\.venv\TB.csv")
##print(df.shape)
##print(df.info())
##print(df.duplicated().sum())
##print(df.isnull().sum())
##print(df.head(15))
##用户行为分析
print(f"表头{df.columns})")
print(df.info())
number_ID=df["用户ID"].nunique()
print("用户分析:")
print(f"用户数量{number_ID}")
buy_df=df[df["行为类型"]=="buy"]
##print(len(buy_df))
average_buy=len(buy_df)/number_ID
print(f"人均订单(已完成）数量:{average_buy}")
total_action=len(df)
number_buy=len(df[df["行为类型"]=="buy"])
number_addbuy=len(df[df["行为类型"]=="addbuy"])
rate_buy=number_buy/total_action
print(f"购买转化比:{rate_buy}")
##复购分析
buy_df=df[df["行为类型"]=="buy"]
user_buy_count=buy_df.groupby("用户ID").size()
re_buy_user_df=user_buy_count[user_buy_count>1]
re_buy_user_number=len(re_buy_user_df)
print(f"复购人数:{re_buy_user_number}")
buy_user_number=len(buy_df.groupby("用户ID"))
re_buy_user_rate=re_buy_user_number/buy_user_number
print(f"复购率:{re_buy_user_rate}")
##用户价值分层
buy_df["消费"]=buy_df["售价"]*buy_df["销量"]
##print(buy_df.head())
user_m=buy_df.groupby("用户ID")["消费"].sum().reset_index()
user_m.columns=["用户ID","总消费金额"]
##print(user_m)
user_m.columns=["用户ID","总消费金额"]
user_m["价值等级"]=pd.qcut(
    user_m["总消费金额"],
    q=3,
    labels=["低","中","高"]
)
##print(user_m.head())
user_m.to_csv("user_m.csv",index=False,encoding="utf-8")
##商品分析
buy_df=df[df["行为类型"]=="buy"]
buy_df["金额"]=buy_df["售价"]*buy_df["销量"]
##print(buy_df.head())
band_sale=buy_df.groupby("品牌")["金额"].sum()
##print("品牌金额:")
print(band_sale)
band_sale=band_sale.reset_index()
##print(band_sale)
classification_sale=buy_df.groupby("商品类目ID")["金额"].sum().reset_index(name="总金额")
##print(classification_sale)
category_map = {
    1:"智能手机",
    2:"笔记本电脑",
    3:"平板电脑",
    4:"耳机",
    5:"智能手表",
    6:"相机",
    7:"电视"
}
##print(classification_sale.info())
classification_sale["商品大类"]=classification_sale["商品类目ID"].map(category_map)
print(classification_sale)
classification_buy_rate=((df.groupby('商品类别')['行为类型']
 .apply(lambda x: (x=='buy').sum() / (x=='addbuy').sum()))
 .reset_index(name="加购率"))
print("各商品大类加购率")
print(classification_buy_rate)
##时间维度分析

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
import matplotlib.dates as mdates

df["时间戳"]=pd.to_datetime(df["时间戳"])
df["日期"]=df["时间戳"].dt.date
##print(df["日期"].describe())
##print(df["日期"])
##print(df.info())
buy_df=df[df["行为类型"]=="buy"].copy()
buy_df["金额"]=buy_df["售价"]*buy_df["销量"]
daily_sale=buy_df.groupby("日期").agg(
    总金额=("金额" ,"sum"),
    订单数=("用户ID","count")
)
##print(daily_sale.head())
fig, ax1 = plt.subplots(figsize=(16,9))
ax1.plot(daily_sale.index, daily_sale["总金额"]/10000, color="#2E86AB", linewidth=2, label="总销售额")
ax1.set_xlabel("日期")
ax1.set_ylabel("总销售额(万元)", color="#2E86AB")
ax1.tick_params(axis='y', labelcolor="#2E86AB")
ax2 = ax1.twinx()
ax2.plot(daily_sale.index, daily_sale["订单数"], color="#A23B72", linewidth=2, label="订单数量")
ax2.set_ylabel("订单数量", color="#A23B72")
ax2.tick_params(axis='y', labelcolor="#A23B72")
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.title("每日销售额与订单量趋势")
ax1.grid(True, axis='both', alpha=0.8, linestyle='--')
ax2.grid(False)
plt.tight_layout()
plt.savefig("每日销售趋势.png")
##plt.show()
##print(buy_df["日期"])
buy_df['小时'] = buy_df['时间戳'].dt.hour
##print(buy_df.head(15))
category_hour=buy_df.groupby(["商品类别","小时"]).size().unstack()
##print(category_hour.head())
import seaborn as sns
plt.figure(figsize=(24,7))
sns.heatmap(category_hour,annot=True,cmap="RdYlGn_r")
plt.title("各商品时段销量分布")
##plt.savefig("各商品购买时段热力图.png",dpi=300,bbox_inches="tight")
##plt.show()
##交叉分析
user_layer=user_m[["用户ID","价值等级"]]
buy_df=df[df["行为类型"]=="buy"].copy()
buy_df=buy_df.merge(user_layer,on="用户ID",how="left")
##print(buy_df.columns)
crosstable_class_purchase=pd.crosstab(
    buy_df["价值等级"],
    buy_df["商品类别"],
    values=buy_df["售价"]*buy_df["销量"],
    aggfunc=sum
)
##print(crosstable_class_purchase)
cross_pct =crosstable_class_purchase.div(crosstable_class_purchase.sum(axis=1), axis=0)*100
print(cross_pct.round(2))
import matplotlib.ticker as mtick
ax=cross_pct.plot(
    kind="bar",
    stacked=True,
    figsize=(16,9),
    colormap="Set3"
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.title("不同价值用户品类消费比例占比")
plt.legend(title='商品类别', bbox_to_anchor=(1.05,1),reverse=True)
plt.tight_layout()
plt.savefig('用户分层_品类偏好.png', dpi=300, bbox_inches='tight')
plt.show()















































