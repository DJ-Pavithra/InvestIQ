"""
Risk Manager Agent - Controls exposure & downside.
"""

import yfinance as yf
import pandas as pd
import numpy as np


class RiskManager:
    """Assesses risk and provides risk management recommendations."""
    
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
    
    def calculate_volatility(self, df, window=30):
        """Calculate volatility (standard deviation of returns)."""
        returns = df['Close'].pct_change().dropna()
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(252)  # 252 trading days
        
        # Recent volatility (last N days)
        recent_returns = returns.tail(window)
        recent_volatility = recent_returns.std() * np.sqrt(252)
        
        return {
            'annual_volatility': volatility * 100,  # As percentage
            'recent_volatility': recent_volatility * 100,
            'volatility_trend': 'increasing' if recent_volatility > volatility else 'decreasing'
        }
    
    def calculate_max_drawdown(self, df):
        """Calculate maximum drawdown."""
        cumulative = (1 + df['Close'].pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_drawdown = drawdown.min() * 100  # As percentage
        
        # Find the period of max drawdown
        max_dd_idx = drawdown.idxmin()
        peak_idx = cumulative[:max_dd_idx].idxmax()
        
        return {
            'max_drawdown': max_drawdown,
            'current_drawdown': drawdown.iloc[-1] * 100,
            'peak_date': peak_idx,
            'trough_date': max_dd_idx
        }
    
    def calculate_var(self, df, confidence=0.05):
        """Calculate Value at Risk (VaR)."""
        returns = df['Close'].pct_change().dropna()
        
        # Historical VaR
        var = np.percentile(returns, confidence * 100) * 100  # As percentage
        
        return var
    
    def calculate_sharpe_ratio(self, df, risk_free_rate=0.02):
        """Calculate Sharpe ratio (risk-adjusted return)."""
        returns = df['Close'].pct_change().dropna()
        
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
        
        return sharpe
    
    def calculate_risk_reward_ratio(self, df, lookback=252):
        """Calculate risk-to-reward ratio."""
        recent_data = df.tail(lookback)
        
        if len(recent_data) < 2:
            return 0
        
        returns = recent_data['Close'].pct_change().dropna()
        
        # Average gain vs average loss
        gains = returns[returns > 0]
        losses = returns[returns < 0]
        
        if len(losses) == 0:
            return float('inf')
        
        avg_gain = gains.mean() if len(gains) > 0 else 0
        avg_loss = abs(losses.mean())
        
        if avg_loss == 0:
            return float('inf')
        
        risk_reward = avg_gain / avg_loss
        
        return risk_reward
    
    def suggest_position_size(self, volatility, max_drawdown, account_size=10000, risk_per_trade=0.02):
        """Suggest position size based on risk metrics."""
        # Risk per trade as percentage of account
        risk_amount = account_size * risk_per_trade
        
        # Estimate stop loss based on volatility
        stop_loss_pct = volatility / 2  # Conservative stop loss
        
        if stop_loss_pct == 0:
            return 0
        
        # Position size = Risk amount / Stop loss percentage
        position_size = risk_amount / (stop_loss_pct / 100)
        
        # Cap position size at 25% of account
        max_position = account_size * 0.25
        
        return min(position_size, max_position)
    
    def suggest_stop_loss(self, df, volatility, method='atr'):
        """Suggest stop loss levels."""
        current_price = df['Close'].iloc[-1]
        
        if method == 'volatility':
            # Stop loss based on volatility
            stop_loss_pct = volatility / 100 * 2  # 2x volatility
            stop_loss = current_price * (1 - stop_loss_pct)
        else:
            # Simple percentage-based stop loss
            stop_loss_pct = 0.05  # 5% default
            stop_loss = current_price * (1 - stop_loss_pct)
        
        return {
            'stop_loss_price': stop_loss,
            'stop_loss_percentage': stop_loss_pct * 100,
            'distance_from_price': ((current_price - stop_loss) / current_price) * 100
        }
    
    def assess_risk_level(self, volatility, max_drawdown, sharpe_ratio):
        """Assess overall risk level."""
        risk_score = 0
        
        # Volatility contribution (40%)
        if volatility > 40:
            risk_score += 40
        elif volatility > 30:
            risk_score += 30
        elif volatility > 20:
            risk_score += 20
        else:
            risk_score += 10
        
        # Drawdown contribution (40%)
        if abs(max_drawdown) > 30:
            risk_score += 40
        elif abs(max_drawdown) > 20:
            risk_score += 30
        elif abs(max_drawdown) > 10:
            risk_score += 20
        else:
            risk_score += 10
        
        # Sharpe ratio contribution (20%) - lower Sharpe = higher risk
        if sharpe_ratio < 0:
            risk_score += 20
        elif sharpe_ratio < 0.5:
            risk_score += 15
        elif sharpe_ratio < 1:
            risk_score += 10
        else:
            risk_score += 5
        
        # Classify risk level
        if risk_score >= 70:
            return "Very High"
        elif risk_score >= 55:
            return "High"
        elif risk_score >= 40:
            return "Moderate"
        elif risk_score >= 25:
            return "Low"
        else:
            return "Very Low"
    
    def generate_recommendations(self, risk_level, volatility, max_drawdown):
        """Generate risk management recommendations."""
        recommendations = []
        
        if risk_level in ["High", "Very High"]:
            recommendations.append("Reduce exposure")
            recommendations.append("Consider tighter stop-loss")
            recommendations.append("Monitor closely for exit signals")
        
        if volatility > 30:
            recommendations.append("High volatility detected - consider smaller position size")
        
        if abs(max_drawdown) > 20:
            recommendations.append("Significant drawdown - review position")
        
        if not recommendations:
            recommendations.append("Risk levels acceptable")
        
        return recommendations
    
    def analyze(self, symbol):
        """Main analysis method."""
        df = self.fetch_price_data(symbol)
        
        if df is None or df.empty:
            return {
                'risk_level': 'Unknown',
                'volatility': 0,
                'max_drawdown': 0,
                'recommendations': ['Unable to fetch price data'],
                'metrics': {}
            }
        
        # Calculate risk metrics
        volatility_data = self.calculate_volatility(df)
        drawdown_data = self.calculate_max_drawdown(df)
        var = self.calculate_var(df)
        sharpe = self.calculate_sharpe_ratio(df)
        risk_reward = self.calculate_risk_reward_ratio(df)
        
        # Assess risk level
        risk_level = self.assess_risk_level(
            volatility_data['annual_volatility'],
            drawdown_data['max_drawdown'],
            sharpe
        )
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            risk_level,
            volatility_data['annual_volatility'],
            drawdown_data['max_drawdown']
        )
        
        # Position sizing suggestions
        position_size = self.suggest_position_size(
            volatility_data['annual_volatility'],
            drawdown_data['max_drawdown']
        )
        
        stop_loss = self.suggest_stop_loss(df, volatility_data['annual_volatility'])
        
        return {
            'risk_level': risk_level,
            'volatility': volatility_data['annual_volatility'],
            'max_drawdown': drawdown_data['max_drawdown'],
            'current_drawdown': drawdown_data['current_drawdown'],
            'var': var,
            'sharpe_ratio': sharpe,
            'risk_reward_ratio': risk_reward,
            'recommendations': recommendations,
            'position_size_suggestion': position_size,
            'stop_loss': stop_loss,
            'metrics': {
                'volatility_data': volatility_data,
                'drawdown_data': drawdown_data
            }
        }
    
    def format_output(self, analysis):
        """Format analysis output for display."""
        output = "Risk View:\n"
        
        if analysis['volatility'] > 0:
            output += f"- Volatility: {analysis['volatility']:.2f}%\n"
        
        if analysis['max_drawdown'] != 0:
            output += f"- Max drawdown: {analysis['max_drawdown']:.2f}%\n"
        
        output += f"=> Risk Level: {analysis['risk_level']}\n"
        
        if analysis['recommendations']:
            output += f"=> Recommendation: {analysis['recommendations'][0]}"
        
        return output

