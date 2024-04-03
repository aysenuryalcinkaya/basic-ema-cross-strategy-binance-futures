import ccxt, config
import pandas as pd
import json
import numpy as np

def calculate_rsi(close_prices, window=14):
    diff = np.diff(close_prices)
    gain = np.where(diff > 0, diff, 0)
    loss = -np.where(diff < 0, diff, 0)

    avg_gain = np.mean(gain[:window])
    avg_loss = np.mean(loss[:window])

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))

    return np.array([rsi])

def get_rsi(symbol, timeframe='5m', limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Calculate RSI
    close_prices = df['close'].to_numpy()
    rsi = calculate_rsi(close_prices)

    return df, rsi

def get_account_balance():
    account_info = exchange.fetch_balance(params={'type': 'future'})
    return account_info['total']

def get_ema(close_prices, window=200):
    return pd.Series(close_prices).ewm(span=window, adjust=False).mean().iloc[-1]

def check_positions_and_alert(coin_list):
    for symbol in coin_list:
        df, rsi = get_rsi(symbol)
        close_prices = df['close'].to_numpy()
        ema_200 = get_ema(close_prices)

        last_rsi = rsi[-1]
        last_close = close_prices[-1]

        # Check if RSI is above 80 and EMA(200) is below close price for long position
        if last_rsi > 80 and ema_200 < last_close:
            print(f"LONG ALERT: {symbol} - RSI: {last_rsi}, EMA(200): {ema_200}")

            # Open long position with specified parameters
             # Adjust the quantity as needed
            total_balance = get_account_balance()
            quantity = total_balance  # Adjust the quantity as needed

            # Check if there are sufficient funds for trading
            if 'quantity' in quantity and quantity['quantity'] > 0:
                # Place the order using the ccxt library
                order_params = {
                    'symbol': symbol,
                    'side': 'buy',
                    'type': 'market',
                    'quantity':  quantity['quantity'],
                }

                order = exchange.create_order(**order_params)
                print(f"Long position opened: {order}")

        # Check if RSI is below 20 for short position
        elif last_rsi < 20 and ema_200 > last_close:
            print(f"SHORT ALERT: {symbol} - RSI: {last_rsi}, EMA(200): {ema_200}")

            # Open short position with specified parameters
            total_balance = get_account_balance()
            quantity = total_balance  # Adjust the quantity as needed

            # Check if there are sufficient funds for trading
            if 'quantity' in quantity and quantity['quantity'] > 0:
                # Place the order using the ccxt library
                order_params = {
                    'symbol': symbol,
                    'side': 'sell',
                    'type': 'market',
                    'quantity':  quantity['quantity'],
                }

                order = exchange.create_order(**order_params)
                print(f"Short position opened: {order}")
                
            

# API CONNECT
exchange = ccxt.binance({
    "apiKey": config.apiKey,
    "secret": config.secretKey,
    'options': {
        'defaultType': 'future'
    },
    'enableRateLimit': True
})
# Read coin list from JSON file
with open('coinlist.json') as json_file:
    coin_list = json.load(json_file)

# Run the check_positions_and_alert function
check_positions_and_alert(coin_list)
