
import backtrader as bt
import datetime

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=15)

    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()

cerebro = bt.Cerebro()
cerebro.addstrategy(TestStrategy)

data = bt.feeds.YahooFinanceData(dataname='BTC-USD', fromdate=datetime.datetime(2022, 1, 1), todate=datetime.datetime(2022, 2, 1))
cerebro.adddata(data)
cerebro.run()
cerebro.plot()
