import baostock as bs
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, EffectScatter
from datetime import datetime, timedelta
import talib as tl
import logging

def InitEnv():
    lg = bs.login()
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename="./log/" + datetime.now().strftime("%Y-%m-%d") + '.log', level=logging.INFO, format=LOG_FORMAT)

def GenGraph(code, stock_name, buy_date, sell_date, buy_price, sell_price):
    if code[:2] == "60":
        code = "sh." + code
    else:
        code = "sz." + code

    #生成数据获取时间，向前多获取1年，向后多获取2个月数据
    #手动convert str to datetime
    b_year = buy_date[:4]
    b_month = buy_date[4:6]
    b_day = buy_date[6:]
    dt_buy_date = datetime(int(b_year), int(b_month), int(b_day))

    s_year = sell_date[:4]
    s_month = sell_date[4:6]
    s_day = sell_date[6:]
    dt_sell_date = datetime(int(s_year), int(s_month), int(s_day))

    #making datetime delay
    year = timedelta(days=365)
    two_month = timedelta(days=60)

    #gen datetime extend
    buy_date_extend = dt_buy_date - year
    sell_date_extend = dt_sell_date + two_month

    #gen datetime to str format
    buy_date_extend_str = buy_date_extend.strftime('%Y-%m-%d')
    sell_date_extend_str = sell_date_extend.strftime('%Y-%m-%d')

    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=buy_date_extend_str, end_date=sell_date_extend_str,
                                      frequency="d", adjustflag="2")
    df_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        df_list.append(rs.get_row_data())
    df_data = pd.DataFrame(df_list, columns=rs.fields)
    if len(df_data) == 0:
        logging.error("该笔交易数据下载失败:from %s to %s, name: %s code: %s"%(buy_date, sell_date, stock_name, code))
        return

    #获取用于显示的数据
    data_list = df_data[['open', 'close', 'high', 'low', 'pctChg']].values.tolist()
    date_list = df_data[['date']].values
    trade_gain = (sell_price - buy_price) / buy_price

    #由于有周六日，因此获取买入卖出在数组中的下标
    buy_date_str = dt_buy_date.strftime("%Y-%m-%d")
    sell_date_str = dt_sell_date.strftime("%Y-%m-%d")
    temp_date_list = list(date_list.flatten())
    buy_idx = temp_date_list.index(buy_date_str)
    sell_idx = temp_date_list.index(sell_date_str)

    kline = Kline()
    kline.add_xaxis(date_list.tolist())
    for i in range(len(data_list)):
        for j in range(len(data_list[i])):
            data_list[i][j] = float(data_list[i][j])
    kline.add_yaxis("kline", data_list)
    kline.set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True, is_show=False),
            yaxis_opts=opts.AxisOpts(is_scale=True),  # y轴起始坐标可自动调整
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),

            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=True,
                    type_="inside",
                    xaxis_index=[0, 1],  # 设置第0轴和第1轴同时缩放
                    range_start=0,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1],
                    type_="slider",
                    pos_top="90%",
                    range_start=0,
                    range_end=100,
                ),
            ],
            title_opts=opts.TitleOpts(title="持股%s天，收益%.3f\n" % (
                                      str(sell_idx - buy_idx),
                                      trade_gain * 100),)
    )

    # 移动平均线
    line = (
        Line()
            .add_xaxis(xaxis_data=date_list.flatten())
            .add_yaxis(
            series_name="MA5",
            y_axis=tl.SMA(df_data['close'], 5).values.tolist(),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="MA10",
            y_axis=tl.SMA(df_data['close'], 10).values.tolist(),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="MA20",
            y_axis=tl.SMA(df_data['close'], 20).values.tolist(),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="MA60",
            y_axis=tl.SMA(df_data['close'], 60).values.tolist(),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )
    # 将K线图和移动平均线显示在一个图内
    kline.overlap(line)


    #买点卖点
    high_spot = [data_list[buy_idx][2]]
    buy_pt = (
        EffectScatter()
            .add_xaxis(date_list.tolist()[buy_idx])
            .add_yaxis("Buy", high_spot)
            .set_colors(["Red"])
    )
    kline.overlap(buy_pt)

    high_spot = [data_list[sell_idx][2]]
    sell_pt = (
        EffectScatter()
            .add_xaxis(date_list.tolist()[sell_idx])
            .add_yaxis("Sell", high_spot)
            .set_colors(["Green"])
    )
    kline.overlap(buy_pt)
    kline.overlap(sell_pt)


    # 成交量柱形图
    x = df_data[["date"]].values[:, 0].tolist()
    y = df_data[["volume"]].values[:, 0].tolist()

    bar = (
        Bar()
            .add_xaxis(x)
            .add_yaxis("成交量", y, label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(color="#008080"))
            .set_global_opts(title_opts=opts.TitleOpts(title="成交量", pos_top="70%"),
                             legend_opts=opts.LegendOpts(is_show=False),
                             datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")]
                             )
    )

    # 使用网格将多张图标组合到一起显示
    grid_chart = Grid()

    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", height="55%"),
    )

    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top="70%", height="20%"),
    )
    grid_chart.render("./result/%s_%s_%.3f.html" % (buy_date, stock_name, trade_gain * 100))
    logging.info("Done generate trade record from %s to %s, code: %s, name %s"% (buy_date, sell_date, code, stock_name))