class Trade:
    def __init__(self, tradeSide,priceEntry, entryTime, isComplete):
        self.tradeSide = tradeSide
        self.priceEntry = priceEntry
        self.priceExit = None
        self.entryTime = entryTime
        self.exitTime = None
        self.profit = None
        self.isComplete = isComplete

    def setProfit(self):
        if self.tradeSide == "BUY":
            self.profit =  self.priceExit - self.priceEntry
        elif self.tradeSide == "SELL":
            self.profit = self.priceEntry - self.priceExit

    def setPriceExit(self, priceExit):
        self.priceExit = priceExit

    def setExitTime(self, exitTime):
        self.exitTime = exitTime