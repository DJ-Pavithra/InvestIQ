"""
Uncertainty module for InvestIQ.
"""

from difflib import SequenceMatcher
import numpy as np

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def estimate_uncertainty(answers):
    scores = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            scores.append(similarity(answers[i], answers[j]))

    avg = np.mean(scores)

    if avg > 0.75:
        level = "High"
    elif avg > 0.5:
        level = "Medium"
    else:
        level = "Low"

    return round(avg, 2), level
