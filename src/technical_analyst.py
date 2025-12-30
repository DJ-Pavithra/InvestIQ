"""
Technical Analyst Agent - Interprets price charts & indicators.
"""

import yfinance as yf
import pandas as pd
import numpy as np


class TechnicalAnalyst:
    """Analyzes technical indicators and generates technical score."""
    
    def __init__(self, period='1y'):
        self.period = period
    
    def fetch_price_data(self, symbol):
        """Fetch historical price data."""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=self.period)
            
            if df.empty:
                return None
            
            return df
            
        except Exception as e:
            print(f"Error fetching price data for {symbol}: {e}")
            return None
    
    def calculate_moving_averages(self, df, windows=[20, 50]):
        """Calculate moving averages."""
        ma_data = {}
        
        for window in windows:
            ma_data[f'MA{window}'] = df['Close'].rolling(window=window).mean()
        
        return ma_data
    
    def calculate_rsi(self, df, period=14):
        """Calculate Relative Strength Index (RSI)."""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)."""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def identify_support_resistance(self, df, window=20):
        """Identify support and resistance levels."""
        high = df['High'].rolling(window=window).max()
        low = df['Low'].rolling(window=window).min()
        
        current_price = df['Close'].iloc[-1]
        resistance = high.iloc[-1]
        support = low.iloc[-1]
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': current_price,
            'distance_to_support': ((current_price - support) / support) * 100,
            'distance_to_resistance': ((resistance - current_price) / current_price) * 100
        }
    
    def determine_trend(self, df, ma_data):
        """Determine trend direction."""
        current_price = df['Close'].iloc[-1]
        
        if 'MA20' in ma_data and 'MA50' in ma_data:
            ma20 = ma_data['MA20'].iloc[-1]
            ma50 = ma_data['MA50'].iloc[-1]
            
            if current_price > ma20 > ma50:
                return "Strong Uptrend"
            elif current_price > ma20 and ma20 < ma50:
                return "Weak Uptrend"
            elif current_price < ma20 < ma50:
                return "Strong Downtrend"
            elif current_price < ma20 and ma20 > ma50:
                return "Weak Downtrend"
            else:
                return "Sideways"
        
        return "Unknown"
    
    def detect_breakout(self, df, support_resistance):
        """Detect potential breakouts."""
        current_price = support_resistance['current_price']
        resistance = support_resistance['resistance']
        support = support_resistance['support']
        
        # Check if price is near resistance (potential breakout)
        if current_price >= resistance * 0.98:  # Within 2% of resistance
            return {
                'breakout_detected': True,
                'type': 'resistance_breakout',
                'direction': 'upward'
            }
        
        # Check if price is near support (potential breakdown)
        if current_price <= support * 1.02:  # Within 2% of support
            return {
                'breakout_detected': True,
                'type': 'support_breakdown',
                'direction': 'downward'
            }
        
        return {'breakout_detected': False}
    
    def assess_overbought_oversold(self, rsi):
        """Assess if asset is overbought or oversold."""
        current_rsi = rsi.iloc[-1]
        
        if current_rsi > 70:
            return "Overbought"
        elif current_rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    def calculate_technical_score(self, indicators):
        """Calculate weighted technical score (0-100)."""
        score = 50  # Start neutral
        
        # RSI contribution (30%)
        rsi = indicators.get('rsi', 50)
        if 30 <= rsi <= 70:
            score += (rsi - 50) * 0.3
        elif rsi > 70:
            score -= (rsi - 70) * 0.5  # Penalize overbought
        else:
            score += (30 - rsi) * 0.5  # Penalize oversold
        
        # Trend contribution (40%)
        trend = indicators.get('trend', 'Unknown')
        if trend == "Strong Uptrend":
            score += 20
        elif trend == "Weak Uptrend":
            score += 10
        elif trend == "Strong Downtrend":
            score -= 20
        elif trend == "Weak Downtrend":
            score -= 10
        
        # MACD contribution (20%)
        macd_hist = indicators.get('macd_histogram', 0)
        if macd_hist > 0:
            score += min(10, macd_hist * 100)  # Positive momentum
        else:
            score += max(-10, macd_hist * 100)  # Negative momentum
        
        # Support/Resistance contribution (10%)
        price_position = indicators.get('price_position', 0.5)
        score += (price_position - 0.5) * 20
        
        return max(0, min(100, round(score, 2)))
    
    def determine_bias(self, score, trend, rsi):
        """Determine market bias based on technical indicators."""
        if score >= 70:
            return "Bullish"
        elif score >= 55:
            if rsi > 65:
                return "Bullish but cautious"
            return "Slightly Bullish"
        elif score >= 45:
            return "Neutral"
        elif score >= 30:
            return "Slightly Bearish"
        else:
            return "Bearish"
    
    def analyze(self, symbol):
        """Main analysis method."""
        df = self.fetch_price_data(symbol)
        
        if df is None or df.empty:
            return {
                'score': 50,
                'bias': 'Unknown',
                'insights': ['Unable to fetch price data'],
                'indicators': {}
            }
        
        # Calculate indicators
        ma_data = self.calculate_moving_averages(df)
        rsi = self.calculate_rsi(df)
        macd_data = self.calculate_macd(df)
        support_resistance = self.identify_support_resistance(df)
        trend = self.determine_trend(df, ma_data)
        breakout = self.detect_breakout(df, support_resistance)
        overbought_oversold = self.assess_overbought_oversold(rsi)
        
        # Prepare indicators for scoring
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        current_macd_hist = macd_data['histogram'].iloc[-1] if not macd_data['histogram'].empty else 0
        
        # Calculate price position between support and resistance
        price_range = support_resistance['resistance'] - support_resistance['support']
        if price_range > 0:
            price_position = (support_resistance['current_price'] - support_resistance['support']) / price_range
        else:
            price_position = 0.5
        
        indicators = {
            'rsi': current_rsi,
            'trend': trend,
            'macd_histogram': current_macd_hist,
            'price_position': price_position
        }
        
        score = self.calculate_technical_score(indicators)
        bias = self.determine_bias(score, trend, current_rsi)
        
        # Generate insights
        insights = []
        
        if 'MA20' in ma_data and 'MA50' in ma_data:
            current_price = df['Close'].iloc[-1]
            ma20 = ma_data['MA20'].iloc[-1]
            ma50 = ma_data['MA50'].iloc[-1]
            
            if current_price > ma50:
                insights.append("Price above 50-day MA")
            else:
                insights.append("Price below 50-day MA")
        
        insights.append(f"RSI = {current_rsi:.1f} ({overbought_oversold})")
        
        if breakout.get('breakout_detected'):
            insights.append(f"Potential {breakout['type']} detected")
        
        return {
            'score': score,
            'bias': bias,
            'insights': insights,
            'indicators': {
                'rsi': current_rsi,
                'trend': trend,
                'macd': macd_data,
                'support_resistance': support_resistance,
                'breakout': breakout,
                'overbought_oversold': overbought_oversold,
                'moving_averages': {k: v.iloc[-1] for k, v in ma_data.items()}
            }
        }
    
    def format_output(self, analysis):
        """Format analysis output for display."""
        output = "Technical View:\n"
        
        for insight in analysis['insights']:
            output += f"- {insight}\n"
        
        output += f"=> Score: {analysis['score']}/100\n"
        output += f"=> Bias: {analysis['bias']}"
        
        return output

