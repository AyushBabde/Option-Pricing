import numpy as np
import yfinance as yf
from fredapi import Fred

# Function to calculate Volatility using historical Data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    current_price = stock.history(period="1d")['Close'][0]
    returns = hist['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)  # Annualize the volatility

    return current_price, volatility


# Taking inputs from the user
ticker = input("Enter the stock ticker: ").strip().upper()
print(get_stock_data(ticker))
K = float(input("Enter the strike price: "))
T = float(input("Enter time to maturity (in years): "))
M = int(input("Enter the number of simulations: "))
option_type = input("Enter the option type ('call' or 'put'): ").strip().lower()

# Getting risk_free_rate using Fred_Api
fred = Fred(api_key='1b3896dbdbd6878090ae00d80913a34b')
ten_year_treasury_rate = fred.get_series_latest_release('GS10') / 100
r = ten_year_treasury_rate.iloc[-1]  # risk-free rate


# Fetch stock data
S, sigma = get_stock_data(ticker)  # 'S' is Current stock price & sigma is volatility

def monte_carlo_option_pricing(S, K, T, r, sigma, M, option_type='call'):
    # Simulate end-of-period prices using Geometric Brownian Motion (GBM)
    Z = np.random.standard_normal(M)
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)

    # Calculate option payoff
    if option_type == 'call':
        payoff = np.maximum(0, ST - K)
    else:
        payoff = np.maximum(0, K - ST)

    # Discount the expected payoff back to present value
    option_price = np.exp(-r * T) * np.mean(payoff)
    return option_price

# Calculate option price using Monte Carlo simulation
option_price_mc = monte_carlo_option_pricing(S, K, T, r, sigma, M, option_type)
print(f"{option_type.capitalize()} Option Price (Monte Carlo): {option_price_mc:.2f}")
