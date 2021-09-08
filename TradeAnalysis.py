def AnalysisTradeData(df):
    stock_code = []
    stock_name = []
    buy_date = []
    sell_date = []
    buy_price = []
    sell_price = []
    for index, row in df.iterrows():
        name = row['证券名称']
        op = row['操作']
        if(op != '证券买入'):
            continue
        stock_name.append(name)
        code = str(row['证券代码'])
        while len(code) != 6:
            code = "0"+code
        stock_code.append(code)
        buy_date.append(str(row['成交日期']))
        buy_price.append(row['成交均价'])
        for index2, row2 in df.iterrows():
            if (index2 < index):
                continue
            if row2['证券名称'] == name and row2['操作'] == '证券卖出':
                sell_date.append(str(row2['成交日期']))
                sell_price.append(row2['成交均价'])
                break
            if index2 == len(df) - 1:
                sell_date.append("null")
                sell_price.append("null")

    return stock_code, stock_name, buy_date, sell_date, buy_price, sell_price
