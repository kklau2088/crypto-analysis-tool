# app.py 顶部添加（安全获取环境变量）
import os
API_KEY = os.environ.get('bg_72c0d8b6b38cbca3688f58afc3e1afa7')
API_SECRET = os.environ.get('458ff44a55c501e72bfd98814bc39548658c0e0d2351ee6abb1f32e330036e33')
COINMARKETCAP_KEY = os.environ.get('ed162a65-bd02-4a30-bfe4-33eec239d61b')

# 删除所有明文API密钥

from flask import Flask, render_template, request, jsonify
import pandas as pd
from binance.client import Client
from ta import add_all_ta_features
import joblib
import plotly.express as px
import json
from models.onchain import OnchainAnalyzer  # 保持原样但要确保路径正确

app = Flask(__name__)

# 初始化API和模型
client = Client(api_key='your_binance_key', api_secret='your_binance_secret')
model = joblib.load('models/predictor.pkl')
onchain = OnchainAnalyzer(api_key='ed162a65-bd02-4a30-bfe4-33eec239d61b')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取用户输入
        symbol = request.form.get('symbol', 'BTCUSDT')
        period = int(request.form.get('period', 24))
        
        # 获取并处理数据
        df = fetch_data(symbol)
        df = create_features(df)
        df = prepare_target(df, period)
        
        # 链上数据整合
        df = onchain.merge_market_data(df)
        
        # 生成预测
        features = df[['close', 'volume', 'momentum_rsi', 'exchange_netflow']].iloc[-1].values.reshape(1, -1)
        proba = model.predict_proba(features)[0]
        
        # 生成图表
        fig = px.line(df, x='timestamp', y='close', title=f'{symbol} 价格走势')
        fig.add_scatter(x=df['timestamp'], y=df['upper_band'], name='阻力位')
        fig.add_scatter(x=df['timestamp'], y=df['lower_band'], name='支撑位')
        
        return jsonify({
            'probability': {
                'up': round(proba[1]*100, 1),
                'down': round(proba[0]*100, 1),
                'confidence': round(max(proba)*100, 1)
            },
            'chart': json.loads(fig.to_json()),
            'backtest': run_backtest(df)
        })
    
    return render_template('index.html')

def fetch_data(symbol='BTCUSDT'):
    """获取Binance数据（简化版）"""
    klines = client.get_klines(symbol=symbol, interval='1d', limit=365)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
    return df

def run_backtest(df):
    """简化版回测"""
    df['returns'] = df['close'].pct_change()
    return {
        'annual_return': round(df['returns'].mean() * 365 * 100, 1),
        'max_drawdown': round(df['returns'].min() * 100, 1)
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Render 默认使用8080端口
