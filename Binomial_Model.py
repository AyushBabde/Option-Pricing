import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from fredapi import Fred

#Taking inputs from user
ticker = input("Enter the stock ticker: ").strip().upper()
#print(get_stock_data(ticker))
K = float(input("Enter the strike price: "))
T = float(input("Enter time to maturity (in years): "))
N = int(input("Enter the number of steps in the binomial model: "))
option_type = input("Enter the option type ('call' or 'put'): ").strip().lower()


#Getting risk_free_rate using Fred_Api
fred = Fred(api_key = '1b3896dbdbd6878090ae00d80913a34b')
ten_year_treasury_rate = fred.get_series_latest_release('GS10')/100
r = ten_year_treasury_rate.iloc[-1] #riskfreerate

#Function to calculate Volatility using historical Data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    current_price = stock.history(period="1d")['Close'][0]
    returns = hist['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)  # Annualize the volatility

    return current_price, volatility

# Fetch stock data
S, sigma = get_stock_data(ticker) #here 'S' is Current stock price & sigma is volatility

def binomial_option_pricing(S, K, T, r, sigma, N, option_type='call'):
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))  # Up factor
    d = 1 / u  # Down factor
    p = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability

    # Initialize asset prices at maturity
    asset_prices = np.zeros(N + 1)
    for i in range(N + 1):
        asset_prices[i] = S * (u ** i) * (d ** (N - i))

    # Initialize option values at maturity
    option_values = np.maximum(0, asset_prices - K) if option_type == 'call' else np.maximum(0, K - asset_prices)
    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            option_values[j] = np.exp(-r * dt) * (p * option_values[j + 1] + (1 - p) * option_values[j])

    return option_values[0]



# Calculate option price
option_price = binomial_option_pricing(S, K, T, r, sigma, N, option_type)
print(f"{option_type.capitalize()} Option Price: {option_price:.2f}")
