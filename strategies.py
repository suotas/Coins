
import ccxt
import pandas as pd
import numpy as np
import os

class SimpleStrategy:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_API_SECRET"),
            'enableRateLimit': True
        })

    def get_signal(self):
        symbol = 'BTC/USDT'
        timeframe = '1m'
        candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=20)
        closes = [c[4] for c in candles]
        current_price = closes[-1]
        ma = sum(closes) / len(closes)

        if current_price > ma:
            return "BUY", current_price
        elif current_price < ma:
            return "SELL", current_price
        else:
            return "HOLD", current_price

class MomentumStrategy:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_API_SECRET"),
            'enableRateLimit': True
        })

    def get_signal(self):
        symbol = 'BTC/USDT'
        timeframe = '1m'
        candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=15)
        closes = [c[4] for c in candles]

        momentum = closes[-1] - closes[-5]
        current_price = closes[-1]

        if momentum > 0:
            return "BUY", current_price
        elif momentum < 0:
            return "SELL", current_price
        else:
            return "HOLD", current_price

class EMARSIComboStrategy:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_API_SECRET"),
            'enableRateLimit': True
        })

    def get_signal(self):
        symbol = 'BTC/USDT'
        timeframe = '1m'
        candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["ema_short"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema_long"] = df["close"].ewm(span=21, adjust=False).mean()
        df["rsi"] = self._calculate_rsi(df["close"], period=14)
        df["volume_ma"] = df["volume"].rolling(window=20).mean()

        trend = None
        if df["ema_short"].iloc[-1] > df["ema_long"].iloc[-1]:
            trend = "up"
        elif df["ema_short"].iloc[-1] < df["ema_long"].iloc[-1]:
            trend = "down"

        rsi = df["rsi"].iloc[-1]
        current_price = df["close"].iloc[-1]
        current_volume = df["volume"].iloc[-1]
        avg_volume = df["volume_ma"].iloc[-1]

        if trend == "up" and rsi < 30 and current_volume > avg_volume:
            return "BUY", current_price
        elif trend == "down" and rsi > 70 and current_volume > avg_volume:
            return "SELL", current_price
        else:
            return "HOLD", current_price

    def _calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / (avg_loss + 1e-6)
        return 100 - (100 / (1 + rs))

def get_strategy(name):
    strategies = {
        "simple": SimpleStrategy,
        "momentum": MomentumStrategy,
        "emaricombo": EMARSIComboStrategy
    }
    return strategies.get(name, SimpleStrategy)
