from TradeAnalysis import *
from Output import *
import pandas as pd

if __name__ == "__main__":
    df = pd.read_excel('F://pingan1.xlsx',engine="openpyxl")
    code, name, buy_date, sell_date, buy_price, sell_price = AnalysisTradeData(df)
    InitEnv()
    for i in range(len(sell_date)):
        if sell_date[i] == "null" or sell_price[i] == "null":
            continue
        GenGraph(code[i], name[i], buy_date[i], sell_date[i], buy_price[i], sell_price[i])
