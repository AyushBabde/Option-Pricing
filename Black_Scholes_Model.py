import yfinance as yf
import numpy as np
from scipy.stats import norm
from fredapi import Fred

# User inputs
ticker = input("Enter the stock ticker: ").strip().upper()
K = float(input("Enter the strike price: "))
T = float(input("Enter time to maturity (in years): "))
#r = float(input("Enter the risk-free interest rate (annual): "))
option_type = input("Enter the option type ('call' or 'put'): ").strip().lower()


#Getting risk_free_rate using Fred_Api
fred = Fred(api_key = '1b3896dbdbd6878090ae00d80913a34b')
ten_year_treasury_rate = fred.get_series_latest_release('GS10')/100
r = ten_year_treasury_rate.iloc[-1] #riskfreerate

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    current_price = stock.history(period="1d")['Close'][0]
    returns = hist['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)  # Annualize the volatility

    return current_price, volatility

# Fetch stock data
S, sigma = get_stock_data(ticker)


def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

    return option_price

# Calculate option price
option_price = black_scholes(S, K, T, r, sigma, option_type)
print(f"{option_type.capitalize()} Option Price: {option_price:.2f}")
