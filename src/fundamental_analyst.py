"""
Fundamental Analyst Agent - Analyzes financial health of a company.
"""

import yfinance as yf
import pandas as pd
import numpy as np


class FundamentalAnalyst:
    """Analyzes company fundamentals and generates a fundamental score."""
    
    def __init__(self):
        self.weights = {
            'revenue_growth': 0.25,
            'profit_margin': 0.25,
            'pe_ratio': 0.20,
            'debt_to_equity': 0.15,
            'roe': 0.15  # Return on Equity
        }
    
    def fetch_financial_metrics(self, symbol):
        """Fetch company financial metrics from yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            metrics = {}
            
            # Revenue Growth
            if not financials.empty and 'Total Revenue' in financials.index:
                revenue = financials.loc['Total Revenue']
                if len(revenue) >= 2:
                    current_rev = revenue.iloc[0]
                    prev_rev = revenue.iloc[1]
                    if prev_rev != 0:
                        metrics['revenue_growth'] = ((current_rev - prev_rev) / abs(prev_rev)) * 100
                    else:
                        metrics['revenue_growth'] = 0
                else:
                    metrics['revenue_growth'] = 0
            else:
                metrics['revenue_growth'] = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
            
            # Profit Margin
            if not financials.empty and 'Net Income' in financials.index and 'Total Revenue' in financials.index:
                net_income = financials.loc['Net Income'].iloc[0]
                revenue = financials.loc['Total Revenue'].iloc[0]
                if revenue != 0:
                    metrics['profit_margin'] = (net_income / revenue) * 100
                else:
                    metrics['profit_margin'] = 0
            else:
                profit_margin = info.get('profitMargins', 0)
                metrics['profit_margin'] = profit_margin * 100 if profit_margin else 0
            
            # P/E Ratio
            metrics['pe_ratio'] = info.get('trailingPE', 0) or info.get('forwardPE', 0) or 0
            
            # Debt-to-Equity
            if not balance_sheet.empty:
                if 'Total Debt' in balance_sheet.index and 'Stockholders Equity' in balance_sheet.index:
                    debt = balance_sheet.loc['Total Debt'].iloc[0]
                    equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
                    if equity != 0:
                        metrics['debt_to_equity'] = debt / equity
                    else:
                        metrics['debt_to_equity'] = 0
                else:
                    metrics['debt_to_equity'] = info.get('debtToEquity', 0) or 0
            else:
                metrics['debt_to_equity'] = info.get('debtToEquity', 0) or 0
            
            # Return on Equity (ROE)
            if not financials.empty and not balance_sheet.empty:
                if 'Net Income' in financials.index and 'Stockholders Equity' in balance_sheet.index:
                    net_income = financials.loc['Net Income'].iloc[0]
                    equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
                    if equity != 0:
                        metrics['roe'] = (net_income / equity) * 100
                    else:
                        metrics['roe'] = 0
                else:
                    metrics['roe'] = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
            else:
                metrics['roe'] = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
            
            return metrics, info
            
        except Exception as e:
            print(f"Error fetching metrics for {symbol}: {e}")
            return None, None
    
    def normalize_score(self, value, metric_type, industry_avg=None):
        """Normalize metric values to 0-100 scale."""
        if metric_type == 'revenue_growth':
            # Good: >10%, Excellent: >20%, Poor: <0%
            if value > 20:
                return 100
            elif value > 10:
                return 70 + (value - 10) * 3
            elif value > 0:
                return 50 + value * 2
            else:
                return max(0, 50 + value * 2)
        
        elif metric_type == 'profit_margin':
            # Good: >10%, Excellent: >20%, Poor: <5%
            if value > 20:
                return 100
            elif value > 10:
                return 70 + (value - 10) * 3
            elif value > 5:
                return 50 + (value - 5) * 4
            else:
                return max(0, value * 10)
        
        elif metric_type == 'pe_ratio':
            # Lower is better (but not too low), optimal: 15-25
            if 15 <= value <= 25:
                return 100
            elif 10 <= value < 15 or 25 < value <= 30:
                return 80
            elif 5 <= value < 10 or 30 < value <= 40:
                return 60
            elif value < 5 or 40 < value <= 60:
                return 40
            else:
                return 20
        
        elif metric_type == 'debt_to_equity':
            # Lower is better, optimal: <0.5, concerning: >1.0
            if value < 0.3:
                return 100
            elif value < 0.5:
                return 85
            elif value < 1.0:
                return 70
            elif value < 2.0:
                return 50
            else:
                return max(0, 100 - value * 20)
        
        elif metric_type == 'roe':
            # Good: >15%, Excellent: >20%, Poor: <10%
            if value > 20:
                return 100
            elif value > 15:
                return 80 + (value - 15) * 4
            elif value > 10:
                return 60 + (value - 10) * 4
            else:
                return max(0, value * 6)
        
        return 50  # Default neutral score
    
    def calculate_fundamental_score(self, metrics):
        """Calculate weighted fundamental score (0-100)."""
        if not metrics:
            return 0, {}
        
        scores = {}
        weighted_sum = 0
        
        for metric, value in metrics.items():
            if metric in self.weights:
                normalized = self.normalize_score(value, metric)
                scores[metric] = normalized
                weighted_sum += normalized * self.weights[metric]
        
        total_score = round(weighted_sum, 2)
        return total_score, scores
    
    def determine_bias(self, score):
        """Determine market bias based on score."""
        if score >= 75:
            return "Bullish"
        elif score >= 60:
            return "Slightly Bullish"
        elif score >= 45:
            return "Neutral"
        elif score >= 30:
            return "Slightly Bearish"
        else:
            return "Bearish"
    
    def generate_insights(self, metrics, info):
        """Generate textual insights from metrics."""
        insights = []
        
        if metrics:
            revenue_growth = metrics.get('revenue_growth', 0)
            if revenue_growth > 15:
                insights.append("Strong revenue growth")
            elif revenue_growth > 5:
                insights.append("Moderate revenue growth")
            elif revenue_growth < 0:
                insights.append("Declining revenue")
            
            debt_to_equity = metrics.get('debt_to_equity', 0)
            if debt_to_equity < 0.5:
                insights.append("Low debt")
            elif debt_to_equity < 1.0:
                insights.append("Moderate debt")
            else:
                insights.append("High debt")
            
            pe_ratio = metrics.get('pe_ratio', 0)
            if pe_ratio > 30:
                insights.append("Overvalued P/E")
            elif pe_ratio < 15:
                insights.append("Undervalued P/E")
            else:
                insights.append("Fair P/E valuation")
        
        return insights
    
    def analyze(self, symbol):
        """Main analysis method."""
        metrics, info = self.fetch_financial_metrics(symbol)
        
        if not metrics:
            return {
                'score': 0,
                'bias': 'Unknown',
                'insights': ['Unable to fetch financial data'],
                'metrics': {}
            }
        
        score, normalized_scores = self.calculate_fundamental_score(metrics)
        bias = self.determine_bias(score)
        insights = self.generate_insights(metrics, info)
        
        return {
            'score': score,
            'bias': bias,
            'insights': insights,
            'metrics': metrics,
            'normalized_scores': normalized_scores
        }
    
    def format_output(self, analysis):
        """Format analysis output for display."""
        output = "Fundamental View:\n"
        
        for insight in analysis['insights']:
            output += f"- {insight}\n"
        
        output += f"=> Score: {analysis['score']}/100\n"
        output += f"=> Bias: {analysis['bias']}"
        
        return output

