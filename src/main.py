"""
Main entry point for InvestIQ - Multi-Agent Investment Analysis System.
"""

from decision_engine import DecisionEngine
import sys


def main():
    """Main function to run InvestIQ analysis."""
    print("\n" + "="*60)
    print("InvestIQ: Multi-Agent Investment Analysis System")
    print("="*60)
    print("\nThis system combines:")
    print("  - Fundamental Analysis (Financial Health)")
    print("  - Sentiment Analysis (Market Mood)")
    print("  - Technical Analysis (Price Charts & Indicators)")
    print("  - Risk Management (Exposure & Downside Control)")
    print("\n" + "="*60 + "\n")
    
    # Get symbol from user
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    else:
        symbol = input("Enter stock symbol (e.g., AAPL, MSFT, GOOGL): ").strip().upper()
    
    if not symbol:
        print("Error: No symbol provided.")
        return
    
    try:
        # Initialize decision engine
        engine = DecisionEngine()
        
        # Run analysis
        decision = engine.analyze(symbol)
        
        # Display final decision
        print(engine.format_final_output(decision))
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
