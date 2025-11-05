"""
data_manager.py
---------------
Fetches crypto price data from Binance with caching.
"""

from datetime import datetime, timedelta
import pandas as pd
from binance.client import Client

class DataManager:

    def __init__(self):
        
        # Public (no auth needed)
        self.client = Client()

        # Simple in-memory cache: {symbol: (timestamp, dataframe)}
        self._cache = {}
        self.cache_expiry = 10  # minutes
        
        # Historical data path
        self.historical_data_path = "resources/data/historical"

        # Map from Fynix-style interval to Binance format
        self._interval_map = {
            "1m": Client.KLINE_INTERVAL_1MINUTE,
            "5m": Client.KLINE_INTERVAL_5MINUTE,
            "15m": Client.KLINE_INTERVAL_15MINUTE,
            "30m": Client.KLINE_INTERVAL_30MINUTE,
            "1h": Client.KLINE_INTERVAL_1HOUR,
            "4h": Client.KLINE_INTERVAL_4HOUR,
            "1d": Client.KLINE_INTERVAL_1DAY,
            "1w": Client.KLINE_INTERVAL_1WEEK,
            "1M": Client.KLINE_INTERVAL_1MONTH,
        }

    def get_crypto_data(self, symbol: str, period="1mo", interval="1h") -> pd.DataFrame:
        """
        Parameters
        ----------
        symbol : str
            Trading pair, e.g. 'BTCUSDT', 'ETHUSDT'
        period : str | None
            Time range (e.g. '1d', '1w', '1mo', '3mo', '1y'). If None, returns all available data.
        interval : str
            Candle interval (1m, 5m, 1h, 1d, etc.)

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: [open, high, low, close, volume]
        """
        symbol = symbol.upper()

        if self._is_cached(symbol):
            print(f"[CACHE] Using cached data for {symbol}")
            return self._cache[symbol][1]

        print(f"[FETCH] Getting data for {symbol} ({period}, {interval})")

        interval_binance = self._interval_map.get(interval, Client.KLINE_INTERVAL_1HOUR)

        # Compute approximate lookback
        lookback_dt = datetime.strptime(self._parse_period(period), "%Y-%m-%d %H:%M:%S")
        
        # Try to get data from local storage first
        local_data = self._get_local_data(symbol, interval, lookback_dt)
        if local_data is not None:
            print(f"[LOCAL] Using local historical data for {symbol}")
            self._cache[symbol] = (datetime.now(), local_data)
            return local_data
            
        print(f"[API] Downloading data from Binance for {symbol}")
        try:
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval_binance,
                start_str=self._parse_period(period),
            )
        except Exception as e:
            print(f"[ERROR] Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()

        if not klines:
            print(f"[WARN] No data returned for {symbol}")
            return pd.DataFrame()

        # Format to DataFrame
        df = pd.DataFrame(
            klines,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ],
        )

        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        df = df.astype(
            {
                "open": "float",
                "high": "float",
                "low": "float",
                "close": "float",
                "volume": "float",
            }
        )

        # Cache it
        self._cache[symbol] = (datetime.now(), df)

        return df[["open", "high", "low", "close", "volume"]]

    def clear_cache(self):
        self._cache.clear()
        print("[INFO] Cache cleared.")

    def update_historical_data(self, symbol: str, interval="1h"):
        """
        Downloads all available historical data for a symbol and stores it locally.
        
        Parameters
        ----------
        symbol : str
            Trading pair, e.g. 'BTCUSDT', 'ETHUSDT'
        interval : str
            Candle interval (1m, 5m, 1h, 1d, etc.)
        """
        import os
        from pathlib import Path
        
        symbol = symbol.upper()
        interval_binance = self._interval_map.get(interval, Client.KLINE_INTERVAL_1HOUR)
        
        print(f"[HISTORY] Downloading complete history for {symbol} @ {interval}")
        
        try:
            # Get all historical data
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval_binance,
                start_str="1 Jan 2010"
            )
            
            if not klines:
                print(f"[WARN] No historical data available for {symbol}")
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(
                klines,
                columns=[
                    "open_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_asset_volume",
                    "number_of_trades",
                    "taker_buy_base",
                    "taker_buy_quote",
                    "ignore",
                ]
            )
            
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df.set_index("open_time", inplace=True)
            df = df.astype({
                "open": "float",
                "high": "float",
                "low": "float",
                "close": "float",
                "volume": "float"
            })
            
            # Create directory if it doesn't exist
            Path(self.historical_data_path).mkdir(parents=True, exist_ok=True)
            
            # Save to parquet file
            filename = f"{symbol}_{interval}.parquet"
            filepath = os.path.join(self.historical_data_path, filename)
            df.to_parquet(filepath)
            
            print(f"[HISTORY] Successfully saved historical data for {symbol} to {filepath}")
            
        except Exception as e:
            print(f"[ERROR] Failed to download historical data for {symbol}: {e}")

    def _get_local_data(self, symbol: str, interval: str, start_time: datetime) -> pd.DataFrame:
        """
        Retrieve data from local historical storage.
        """
        import os
        
        filename = f"{symbol}_{interval}.parquet"
        filepath = os.path.join(self.historical_data_path, filename)
        
        if not os.path.exists(filepath):
            return None
            
        try:
            df = pd.read_parquet(filepath)
            df = df[df.index >= start_time]
            return df[["open", "high", "low", "close", "volume"]]
        except Exception as e:
            print(f"[ERROR] Failed to read local data for {symbol}: {e}")
            return None

    def _is_cached(self, symbol: str) -> bool:
        """Check if cached data is still valid."""
        if symbol not in self._cache:
            return False

        ts, _ = self._cache[symbol]
        if datetime.now() - ts > timedelta(minutes=self.cache_expiry):
            del self._cache[symbol]
            print(f"[CACHE] Expired for {symbol}")
            return False
        return True

    def _parse_period(self, period: str | None) -> str:
        """Convert human-readable period into Binance start_str."""
        if period is None:
            return "2010-01-01 00:00:00"
            
        now = datetime.utcnow()
        mapping = {
            "1d": now - timedelta(days=1),
            "5d": now - timedelta(days=5),
            "1w": now - timedelta(weeks=1),
            "1mo": now - timedelta(days=30),
            "3mo": now - timedelta(days=90),
            "6mo": now - timedelta(days=180),
            "1y": now - timedelta(days=365),
        }
        start_time = mapping.get(period, now - timedelta(days=30))
        return start_time.strftime("%Y-%m-%d %H:%M:%S")