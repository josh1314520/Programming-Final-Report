from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    ticker = data.get('ticker', '').upper()
    try:
        monthly_investment = float(data.get('monthly_investment', 0))
        years = int(data.get('years', 0))
    except ValueError:
        return jsonify({'error': '無效的投資金額或年限'}), 400

    if not ticker or monthly_investment <= 0 or years <= 0:
        return jsonify({'error': '請提供完整的投資條件'}), 400

    # Calculate start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    # Fetch data
    try:
        stock_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval='1mo')
    except Exception as e:
        return jsonify({'error': f'無法獲取股票資料：{str(e)}'}), 500

    if stock_data.empty:
        return jsonify({'error': '找不到該股票的歷史資料，請確認代碼是否正確'}), 404

    # The returned columns from yf.download may be multi-index if downloading multiple tickers, 
    # but for single ticker it's single index in older versions, and multi-index in newer versions of yf.
    # To be safe, we check if columns are multi-level.
    if isinstance(stock_data.columns, pd.MultiIndex):
        close_prices = stock_data['Close'][ticker]
    else:
        close_prices = stock_data['Close']
        
    close_prices = close_prices.dropna()
    if close_prices.empty:
        return jsonify({'error': '該股票歷史資料不完整'}), 404

    # Simulation variables
    total_shares = 0.0
    total_invested = 0.0
    
    labels = []
    investment_history = []
    value_history = []
    
    for date, price in close_prices.items():
        price = float(price)
        # Buy shares at this month's close price
        shares_bought = monthly_investment / price
        total_shares += shares_bought
        total_invested += monthly_investment
        
        current_value = total_shares * price
        
        labels.append(date.strftime('%Y-%m'))
        investment_history.append(round(total_invested, 2))
        value_history.append(round(current_value, 2))

    if not value_history:
        return jsonify({'error': '無法計算資產價值'}), 500

    final_value = value_history[-1]
    total_return_pct = ((final_value - total_invested) / total_invested * 100) if total_invested > 0 else 0

    return jsonify({
        'labels': labels,
        'investment': investment_history,
        'value': value_history,
        'summary': {
            'total_invested': round(total_invested, 2),
            'final_value': round(final_value, 2),
            'total_return_pct': round(total_return_pct, 2)
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
