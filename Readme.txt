Link: https://investiq-vu3m.onrender.com

INVESTIQ: Multi-Agent Investment Analysis System

A comprehensive financial analysis platform that combines four specialized AI agents
to provide holistic investment recommendations with confidence scoring.

┌─────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────┐
│   User Input  │
│   (CLI)       │
│               │
│ Tool          │ Purpose                    │
│ ------------- │ -------------------------- │
│ Python CLI    │ Stock symbol input         │
│ main.py       │ Entry point                │
└───────┬───────┘
        ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    DECISION ENGINE (Orchestrator)                       │
│                                                                          │
│ Tool                    │ Purpose                                       │
│ ----------------------- │ --------------------------------------------- │
│ decision_engine.py      │ Coordinates all agents                       │
│ Weighted scoring        │ Combines agent outputs (Fund:30%, Sent:20%,  │
│                         │   Tech:30%, Risk:20%)                        │
│ Conflict resolution     │ Resolves agent disagreements                 │
│ Confidence calculation  │ Measures agreement between agents            │
└───────┬─────────────────────────────────────────────────────────────────┘
        │
        ├──────────────────┬──────────────────┬──────────────────┐
        ↓                  ↓                  ↓                  ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Fundamental     │ │ Sentiment       │ │ Technical        │ │ Risk Manager    │
│ Analyst Agent  │ │ Analyst Agent   │ │ Analyst Agent   │ │ Agent           │
│                 │ │                 │ │                 │ │                 │
│ Tool            │ │ Tool            │ │ Tool            │ │ Tool            │
│ -------------- │ │ -------------- │ │ -------------- │ │ -------------- │
│ yfinance       │ │ yfinance       │ │ yfinance       │ │ yfinance       │
│ pandas         │ │ TextBlob       │ │ pandas         │ │ pandas         │
│ numpy          │ │ NLTK           │ │ numpy          │ │ numpy          │
│                 │ │                 │ │                 │ │                 │
│ Features:      │ │ Features:      │ │ Features:      │ │ Features:      │
│ - Revenue      │ │ - News fetch   │ │ - Moving       │ │ - Volatility   │
│   growth       │ │ - Sentiment    │ │   averages     │ │ - Max          │
│ - Profit       │ │   analysis     │ │ - RSI          │ │   drawdown     │
│   margin       │ │ - Polarity     │ │ - MACD         │ │ - VaR          │
│ - P/E ratio    │ │   scoring      │ │ - Support/     │ │ - Sharpe ratio │
│ - Debt-to-     │ │ - Spike        │ │   Resistance   │ │ - Position     │
│   equity       │ │   detection    │ │ - Trend        │ │   sizing       │
│ - ROE          │ │ - Trend        │ │   detection    │ │ - Stop-loss    │
│                 │ │   tracking    │ │ - Breakout     │ │   suggestions  │
│                 │ │                 │ │   detection    │ │                 │
│ Output:         │ │ Output:         │ │ Output:         │ │ Output:         │
│ Score: 0-100   │ │ Score: -1 to +1 │ │ Score: 0-100   │ │ Risk Level:     │
│ Bias: Bullish/ │ │ Bias: Bullish/  │ │ Bias: Bullish/ │ │   Very Low to   │
│   Bearish      │ │   Bearish       │ │   Bearish      │ │   Very High     │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
        │                  │                  │                  │
        └──────────────────┴──────────────────┴──────────────────┘
                              ↓
        ┌─────────────────────────────────────────────┐
        │         FINAL RECOMMENDATION                │
        │                                             │
        │ Tool              │ Purpose                 │
        │ ----------------- │ ---------------------- │
        │ Decision Engine   │ Buy/Hold/Sell          │
        │ Confidence Score  │ 0-100%                  │
        │ Combined Score    │ Weighted average       │
        │ Reasoning         │ Conflict resolution    │
        └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            TECH STACK                                   │
└─────────────────────────────────────────────────────────────────────────┘

Core Libraries:
    - Python 3.11+
    - pandas          │ Data manipulation and analysis
    - numpy           │ Numerical computations
    - yfinance        │ Financial data fetching (Yahoo Finance API)

Machine Learning & NLP:
    - torch           │ PyTorch (for transformers)
    - transformers    │ Hugging Face transformers
    - sentence-transformers │ Embedding models
    - faiss-cpu       │ Vector similarity search
    - textblob        │ Sentiment analysis
    - nltk            │ Natural language processing

Data Processing:
    - pandas          │ Time series analysis
    - numpy           │ Statistical calculations

┌─────────────────────────────────────────────────────────────────────────┐
│                         AGENT DETAILS                                   │
└─────────────────────────────────────────────────────────────────────────┘

1️⃣ FUNDAMENTAL ANALYST AGENT
   Analyzes company financial health and valuation metrics.
   
   Metrics Analyzed:
   - Revenue Growth Rate
   - Profit Margin
   - Price-to-Earnings (P/E) Ratio
   - Debt-to-Equity Ratio
   - Return on Equity (ROE)
   
   Scoring Method:
   - Normalizes each metric to 0-100 scale
   - Weighted average: Revenue(25%), Profit(25%), P/E(20%), Debt(15%), ROE(15%)
   - Generates Fundamental Score (0-100)
   - Determines bias: Bullish / Slightly Bullish / Neutral / Bearish

2️⃣ SENTIMENT ANALYST AGENT
   Captures market mood from news and social signals.
   
   Features:
   - Fetches recent news articles (last 7 days)
   - Performs sentiment analysis using TextBlob
   - Calculates sentiment polarity (-1 to +1)
   - Detects sentiment spikes (news impact)
   - Tracks sentiment trends over time
   
   Scoring Method:
   - Maps sentiment polarity to 0-100 score
   - Calculates positive/negative percentage
   - Determines bias based on average sentiment

3️⃣ TECHNICAL ANALYST AGENT
   Interprets price charts and technical indicators.
   
   Indicators Calculated:
   - Moving Averages (20-day, 50-day)
   - Relative Strength Index (RSI)
   - MACD (Moving Average Convergence Divergence)
   - Support and Resistance Levels
   - Trend Direction
   - Breakout Detection
   
   Scoring Method:
   - RSI contribution (30%): Optimal range 30-70
   - Trend contribution (40%): Uptrend/Downtrend/Sideways
   - MACD contribution (20%): Momentum signals
   - Support/Resistance (10%): Price position
   - Generates Technical Score (0-100)

4️⃣ RISK MANAGER AGENT
   Controls exposure and manages downside risk.
   
   Risk Metrics:
   - Annual Volatility (standard deviation of returns)
   - Maximum Drawdown
   - Value at Risk (VaR)
   - Sharpe Ratio (risk-adjusted return)
   - Risk-to-Reward Ratio
   
   Features:
   - Position sizing suggestions
   - Stop-loss level recommendations
   - Risk level assessment (Very Low to Very High)
   - Risk management recommendations

┌─────────────────────────────────────────────────────────────────────────┐
│                    DECISION ENGINE LOGIC                                │
└─────────────────────────────────────────────────────────────────────────┘

Weighted Combination:
   Combined Score = (Fundamental × 0.30) + (Sentiment × 0.20) + 
                    (Technical × 0.30) + (Risk × 0.20)

Conflict Resolution:
   - High risk + Bullish signals → "Hold" (cautious)
   - Strong consensus (3+ agents agree) → Strong recommendation
   - Mixed signals → "Hold" with explanation

Confidence Calculation:
   - Based on agent agreement
   - Score consistency
   - Range: 30-95%

Final Recommendation:
   - Buy: Combined score ≥ 70, positive consensus
   - Hold: Mixed signals or moderate score (45-70)
   - Sell: Combined score < 45, negative consensus

┌─────────────────────────────────────────────────────────────────────────┐
│                         USAGE                                           │
└─────────────────────────────────────────────────────────────────────────┘

Command Line:
    python src/main.py SYMBOL
    
    Example:
    python src/main.py AAPL
    python src/main.py MSFT
    python src/main.py GOOGL

Interactive Mode:
    python src/main.py
    # Enter symbol when prompted

Output Format:
    - Individual agent analysis with scores and biases
    - Final recommendation (Buy/Hold/Sell)
    - Confidence percentage
    - Combined score
    - Detailed reasoning

┌─────────────────────────────────────────────────────────────────────────┐
│                    PROJECT STRUCTURE                                   │
└─────────────────────────────────────────────────────────────────────────┘

InvestIQ/
├── src/
│   ├── main.py                 │ Entry point
│   ├── decision_engine.py      │ Orchestrates all agents
│   ├── fundamental_analyst.py │ Financial health analysis
│   ├── sentiment_analyst.py    │ News sentiment analysis
│   ├── technical_analyst.py    │ Technical indicators
│   ├── risk_manager.py         │ Risk assessment
│   ├── build_data.py           │ Data collection utility
│   ├── retriever.py            │ Vector retrieval (legacy)
│   ├── reasoner.py             │ LLM reasoning (legacy)
│   └── uncertainty.py          │ Uncertainty estimation (legacy)
├── data/                       │ Financial data storage
├── venv/                       │ Virtual environment
├── requirements.txt            │ Python dependencies
└── Readme.txt                  │ This file
