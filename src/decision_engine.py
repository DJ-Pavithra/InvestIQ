"""
Decision Engine - Combines agent outputs and generates final recommendation.
"""

from fundamental_analyst import FundamentalAnalyst
from sentiment_analyst import SentimentAnalyst
from technical_analyst import TechnicalAnalyst
from risk_manager import RiskManager


class DecisionEngine:
    """Combines all analyst agents and generates final investment decision."""
    
    def __init__(self):
        self.weights = {
            'fundamental': 0.30,
            'sentiment': 0.20,
            'technical': 0.30,
            'risk': 0.20
        }
        
        self.fundamental_analyst = FundamentalAnalyst()
        self.sentiment_analyst = SentimentAnalyst()
        self.technical_analyst = TechnicalAnalyst()
        self.risk_manager = RiskManager()
    
    def normalize_risk_score(self, risk_level):
        """Convert risk level to a score that can be used in weighted calculation."""
        # Lower risk = higher score contribution
        risk_mapping = {
            'Very Low': 100,
            'Low': 80,
            'Moderate': 60,
            'High': 40,
            'Very High': 20,
            'Unknown': 50
        }
        return risk_mapping.get(risk_level, 50)
    
    def combine_scores(self, fundamental_score, sentiment_score, technical_score, risk_score):
        """Combine scores with weighted average."""
        weighted_sum = (
            fundamental_score * self.weights['fundamental'] +
            sentiment_score * self.weights['sentiment'] +
            technical_score * self.weights['technical'] +
            risk_score * self.weights['risk']
        )
        
        return round(weighted_sum, 2)
    
    def resolve_conflicts(self, biases, risk_level):
        """Resolve conflicts between different agent recommendations."""
        bullish_count = sum(1 for b in biases if 'Bullish' in b)
        bearish_count = sum(1 for b in biases if 'Bearish' in b)
        neutral_count = sum(1 for b in biases if 'Neutral' in b)
        
        # If high risk, be more conservative
        if risk_level in ['High', 'Very High']:
            if bullish_count >= 2:
                return "Hold", "Strong fundamentals and sentiment, but elevated risk suggests caution"
            elif bearish_count >= 2:
                return "Avoid", "Negative signals combined with high risk"
            else:
                return "Hold", "Mixed signals with high risk - wait for better entry"
        
        # Normal risk resolution
        if bullish_count >= 3:
            return "Buy", "Strong bullish consensus across multiple indicators"
        elif bullish_count == 2 and neutral_count >= 1:
            return "Buy", "Mostly positive signals with some neutral indicators"
        elif bearish_count >= 3:
            return "Sell", "Strong bearish consensus"
        elif bearish_count == 2 and neutral_count >= 1:
            return "Sell", "Mostly negative signals"
        elif bullish_count == 2 and bearish_count == 1:
            return "Hold", "Mixed signals - bullish technical/fundamental but bearish sentiment"
        elif bearish_count == 2 and bullish_count == 1:
            return "Hold", "Mixed signals - caution advised"
        else:
            return "Hold", "Neutral or mixed signals - wait for clearer direction"
    
    def determine_recommendation(self, combined_score, biases, risk_level):
        """Determine final recommendation based on combined score and conflicts."""
        # First, resolve conflicts
        conflict_recommendation, conflict_reason = self.resolve_conflicts(biases, risk_level)
        
        # Then, use score as secondary filter
        if combined_score >= 70:
            if conflict_recommendation == "Sell":
                return "Hold", conflict_reason
            return "Buy", "Strong overall score supports bullish position"
        elif combined_score >= 55:
            if conflict_recommendation == "Sell":
                return "Hold", conflict_reason
            return conflict_recommendation, conflict_reason
        elif combined_score >= 45:
            return "Hold", "Moderate score suggests waiting for better entry/exit"
        elif combined_score >= 30:
            if conflict_recommendation == "Buy":
                return "Hold", "Low score but some positive signals - caution advised"
            return "Sell", "Weak overall score with negative signals"
        else:
            return "Sell", "Very weak overall score"
    
    def calculate_confidence(self, scores, biases):
        """Calculate confidence score based on agreement between agents."""
        # Check agreement in biases
        unique_biases = set(biases)
        
        if len(unique_biases) == 1:
            # All agents agree
            confidence = 85
        elif len(unique_biases) == 2:
            # Some disagreement
            confidence = 65
        else:
            # High disagreement
            confidence = 45
        
        # Adjust based on score consistency
        score_range = max(scores) - min(scores)
        if score_range < 20:
            confidence += 10  # Scores are close
        elif score_range > 40:
            confidence -= 10  # Scores are far apart
        
        # Ensure confidence is in valid range
        confidence = max(30, min(95, confidence))
        
        return round(confidence, 2)
    
    def analyze(self, symbol):
        """Run all agents and generate final decision."""
        print(f"\n{'='*60}")
        print(f"Analyzing {symbol} with InvestIQ Multi-Agent System")
        print(f"{'='*60}\n")
        
        # Run all agents
        print("[*] Running Fundamental Analysis...")
        fundamental_analysis = self.fundamental_analyst.analyze(symbol)
        print(self.fundamental_analyst.format_output(fundamental_analysis))
        
        print("\n[*] Running Sentiment Analysis...")
        sentiment_analysis = self.sentiment_analyst.analyze(symbol)
        print(self.sentiment_analyst.format_output(sentiment_analysis))
        
        print("\n[*] Running Technical Analysis...")
        technical_analysis = self.technical_analyst.analyze(symbol)
        print(self.technical_analyst.format_output(technical_analysis))
        
        print("\n[*] Running Risk Analysis...")
        risk_analysis = self.risk_manager.analyze(symbol)
        print(self.risk_manager.format_output(risk_analysis))
        
        # Extract scores and biases
        fundamental_score = fundamental_analysis['score']
        sentiment_score = sentiment_analysis['score']
        technical_score = technical_analysis['score']
        risk_score = self.normalize_risk_score(risk_analysis['risk_level'])
        
        scores = [fundamental_score, sentiment_score, technical_score, risk_score]
        biases = [
            fundamental_analysis['bias'],
            sentiment_analysis['bias'],
            technical_analysis['bias']
        ]
        
        # Combine scores
        combined_score = self.combine_scores(
            fundamental_score,
            sentiment_score,
            technical_score,
            risk_score
        )
        
        # Determine recommendation
        recommendation, reason = self.determine_recommendation(
            combined_score,
            biases,
            risk_analysis['risk_level']
        )
        
        # Calculate confidence
        confidence = self.calculate_confidence(scores, biases)
        
        # Compile final decision
        final_decision = {
            'symbol': symbol,
            'recommendation': recommendation,
            'confidence': confidence,
            'combined_score': combined_score,
            'reason': reason,
            'agent_scores': {
                'fundamental': fundamental_score,
                'sentiment': sentiment_score,
                'technical': technical_score,
                'risk': risk_score
            },
            'agent_biases': {
                'fundamental': fundamental_analysis['bias'],
                'sentiment': sentiment_analysis['bias'],
                'technical': technical_analysis['bias'],
                'risk': risk_analysis['risk_level']
            },
            'detailed_analysis': {
                'fundamental': fundamental_analysis,
                'sentiment': sentiment_analysis,
                'technical': technical_analysis,
                'risk': risk_analysis
            }
        }
        
        return final_decision
    
    def format_final_output(self, decision):
        """Format final decision output."""
        output = f"\n{'='*60}\n"
        output += "FINAL DECISION\n"
        output += f"{'='*60}\n\n"
        output += f"Symbol: {decision['symbol']}\n"
        output += f"=> Recommendation: {decision['recommendation']}\n"
        output += f"=> Confidence: {decision['confidence']}%\n"
        output += f"=> Combined Score: {decision['combined_score']}/100\n"
        output += f"=> Reason:\n   {decision['reason']}\n\n"
        
        output += "Agent Breakdown:\n"
        output += f"  - Fundamental: {decision['agent_scores']['fundamental']}/100 ({decision['agent_biases']['fundamental']})\n"
        output += f"  - Sentiment: {decision['agent_scores']['sentiment']}/100 ({decision['agent_biases']['sentiment']})\n"
        output += f"  - Technical: {decision['agent_scores']['technical']}/100 ({decision['agent_biases']['technical']})\n"
        output += f"  - Risk: {decision['agent_biases']['risk']}\n"
        
        return output

