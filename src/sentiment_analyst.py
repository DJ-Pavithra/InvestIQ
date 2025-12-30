"""
Sentiment Analyst Agent - Captures market mood from news & social signals.
"""

import yfinance as yf
from textblob import TextBlob
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SentimentAnalyst:
    """Analyzes sentiment from news and generates sentiment score."""
    
    def __init__(self):
        self.sentiment_history = []
    
    def fetch_news(self, symbol, days=7):
        """Fetch recent news for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return []
            
            # Filter news by date (last N days)
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_news = []
            
            for article in news:
                pub_date = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                if pub_date >= cutoff_date:
                    filtered_news.append({
                        'title': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'date': pub_date,
                        'publisher': article.get('publisher', '')
                    })
            
            return filtered_news[:20]  # Limit to 20 most recent articles
            
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of a text using TextBlob."""
        if not text:
            return 0.0
        
        blob = TextBlob(text)
        # Polarity ranges from -1 (negative) to +1 (positive)
        return blob.sentiment.polarity
    
    def classify_sentiment(self, polarity):
        """Classify sentiment based on polarity score."""
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    def calculate_sentiment_metrics(self, news_items):
        """Calculate sentiment metrics from news items."""
        if not news_items:
            return {
                'average_sentiment': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_count': 0,
                'positive_percentage': 0.0,
                'sentiment_trend': []
            }
        
        sentiments = []
        sentiment_trend = []
        
        for item in news_items:
            # Combine title and summary for analysis
            text = f"{item['title']} {item.get('summary', '')}"
            polarity = self.analyze_sentiment(text)
            sentiments.append(polarity)
            sentiment_trend.append({
                'date': item['date'],
                'sentiment': polarity,
                'title': item['title'][:50]  # Truncate for display
            })
        
        sentiments = np.array(sentiments)
        average_sentiment = float(np.mean(sentiments))
        
        positive_count = np.sum(sentiments > 0.1)
        negative_count = np.sum(sentiments < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        total_count = len(sentiments)
        
        positive_percentage = (positive_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'average_sentiment': average_sentiment,
            'positive_count': int(positive_count),
            'negative_count': int(negative_count),
            'neutral_count': int(neutral_count),
            'total_count': total_count,
            'positive_percentage': round(positive_percentage, 2),
            'sentiment_trend': sentiment_trend
        }
    
    def detect_sentiment_spike(self, sentiment_trend):
        """Detect sudden sentiment spikes (news impact)."""
        if len(sentiment_trend) < 2:
            return None
        
        # Sort by date
        sorted_trend = sorted(sentiment_trend, key=lambda x: x['date'])
        recent_sentiments = [item['sentiment'] for item in sorted_trend[-5:]]
        
        if len(recent_sentiments) < 2:
            return None
        
        # Check for significant change in recent sentiment
        recent_avg = np.mean(recent_sentiments[-3:])
        previous_avg = np.mean(recent_sentiments[:-3]) if len(recent_sentiments) > 3 else recent_sentiments[0]
        
        change = recent_avg - previous_avg
        
        if abs(change) > 0.3:  # Significant change threshold
            return {
                'spike_detected': True,
                'direction': 'positive' if change > 0 else 'negative',
                'magnitude': abs(change),
                'recent_news': sorted_trend[-1]['title'] if sorted_trend else None
            }
        
        return {'spike_detected': False}
    
    def calculate_sentiment_score(self, average_sentiment):
        """Convert sentiment polarity to 0-100 score."""
        # Map from [-1, 1] to [0, 100]
        # Neutral (0) maps to 50, positive maps to 50-100, negative maps to 0-50
        score = 50 + (average_sentiment * 50)
        return max(0, min(100, round(score, 2)))
    
    def determine_bias(self, average_sentiment):
        """Determine market bias based on sentiment."""
        if average_sentiment > 0.3:
            return "Bullish"
        elif average_sentiment > 0.1:
            return "Slightly Bullish"
        elif average_sentiment > -0.1:
            return "Neutral"
        elif average_sentiment > -0.3:
            return "Slightly Bearish"
        else:
            return "Bearish"
    
    def analyze(self, symbol, days=7):
        """Main analysis method."""
        news_items = self.fetch_news(symbol, days)
        
        if not news_items:
            return {
                'score': 50.0,
                'bias': 'Neutral',
                'average_sentiment': 0.0,
                'positive_percentage': 0.0,
                'total_articles': 0,
                'spike': None,
                'insights': ['No recent news available']
            }
        
        metrics = self.calculate_sentiment_metrics(news_items)
        spike = self.detect_sentiment_spike(metrics['sentiment_trend'])
        score = self.calculate_sentiment_score(metrics['average_sentiment'])
        bias = self.determine_bias(metrics['average_sentiment'])
        
        insights = []
        insights.append(f"{metrics['positive_percentage']}% positive mentions")
        
        if spike and spike.get('spike_detected'):
            if spike['direction'] == 'positive':
                insights.append(f"Sudden positive spike after: {spike.get('recent_news', 'recent news')}")
            else:
                insights.append(f"Sudden negative spike after: {spike.get('recent_news', 'recent news')}")
        
        return {
            'score': score,
            'bias': bias,
            'average_sentiment': metrics['average_sentiment'],
            'positive_percentage': metrics['positive_percentage'],
            'total_articles': metrics['total_count'],
            'spike': spike,
            'insights': insights,
            'metrics': metrics
        }
    
    def format_output(self, analysis):
        """Format analysis output for display."""
        output = "Sentiment View:\n"
        
        for insight in analysis['insights']:
            output += f"- {insight}\n"
        
        output += f"=> Score: {analysis['average_sentiment']:+.2f}\n"
        output += f"=> Bias: {analysis['bias']}"
        
        return output

