
from datetime import date, datetime

from pyalgotrade import strategy, plotter
from pyalgotrade.constants.Constants import Y_M_D_H_M_S
from pyalgotrade.plotter import  GuppyLongMarker, GuppyShortMarker
from pyalgotrade.technical import ma, cross
from pyalgotrade.tools import NseDT


class GuppyCrossover(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, short_ema_periods, long_ema_periods):
        super(GuppyCrossover, self).__init__(feed)
        self.__instrument = instrument

        # Create a dictionary of short and long EMAs based on the provided periods.
        self.__short_emas = {}
        self.__long_emas = {}

        for period in short_ema_periods:
            self.__short_emas[period] = ma.SMA(feed[instrument].getPriceDataSeries(), period)

        for period in long_ema_periods:
            self.__long_emas[period] = ma.SMA(feed[instrument].getPriceDataSeries(), period)

        self.__position = None
        self.__chart=[]

    def getShortEMABars(self,period):
        return self.__short_emas[period]
    def getLongEMABars(self,period):
        return self.__long_emas[period]

    def onBars(self, bars):
        for period in self.__short_emas:
            index= len(self.__short_emas[period])
            break
        short_ema_values = [self.__short_emas[period][-1] for period in self.__short_emas]
        long_ema_values = [self.__long_emas[period][-1]  for period in self.__long_emas]


        print(bars[self.__instrument].getDateTime())
        print(short_ema_values)
        print(long_ema_values)

        cross_above=True
        cross_below=True
        # for short_period in self.__short_emas:
        #     for long_period in self.__long_emas:
        #         self.__chart.append( {"Cross Above":{short_period: {long_period: cross.cross_above(self.__short_emas[short_period], self.__long_emas[long_period])}}})
        #         self.__chart.append( {"Cross Below":{short_period: {long_period: cross.cross_below(self.__short_emas[short_period], self.__long_emas[long_period])}}})

        # print(self.__chart)
        # Check for trends based on the relationship between short and long EMAs.
        if all(short_ema is not None and long_ema is not None and  short_ema > long_ema for short_ema, long_ema in zip(short_ema_values, long_ema_values)) and self.__position is None:
            self.__position = self.enterLong(self.__instrument, 10)  # Enter a long position

        elif any(short_ema is not None and long_ema is not None and short_ema < long_ema for short_ema, long_ema in zip(short_ema_values, long_ema_values)) and self.__position is not None:
            self.__position.exitMarket()  # Exit the long position
            self.__position = None

def main():

    # Load historical price data
    symbol = "TCS"
    instruments = [symbol]
    startdate = date(year=2022, month=1, day=1)
    enddate = date(year=2024, month=1, day=1)
    feed = NseDT.build_feed(instruments, startdate=startdate, enddate=enddate)

    # Set short and long EMA periods
    short_ema_periods = [3, 5, 8,10,12,15]
    long_ema_periods = [30, 35, 40,45,50,60]

    # Create and run the strategy
    strategy = GuppyCrossover(feed, symbol, short_ema_periods, long_ema_periods)

    # Attach a plotter to visualize the strategy's performance
    plt = plotter.StrategyPlotter(strategy)

    for period in short_ema_periods:
        plt.getInstrumentSubplot(symbol).addDataSeries(f"EMA {period}", strategy.getShortEMABars(period), defaultClass=GuppyShortMarker)

    for period in long_ema_periods:
        plt.getInstrumentSubplot(symbol).addDataSeries(f"EMA {period}", strategy.getLongEMABars(period), defaultClass=GuppyLongMarker)

    strategy.info("Initial portfolio value: $%.2f" % strategy.getResult())

    strategy.run()
    strategy.info("Final portfolio value: $%.2f" % strategy.getResult())

    # Plot the strategy's performance
    plt.plot()

if __name__ == "__main__":
    main()
