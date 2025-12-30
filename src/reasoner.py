from transformers import pipeline

class Reasoner:
    def __init__(self):
        self.llm = pipeline(
            "text-generation",
            model="distilgpt2",
            max_new_tokens=80,        # VERY IMPORTANT
            do_sample=False
        )

    def decompose(self, question):
        prompt = f"""
Break the following investment question into 3 short analytical sub-questions.

Question: {question}

Sub-questions:
-"""
        result = self.llm(prompt)[0]["generated_text"]
        lines = result.split("\n")
        return [l for l in lines if l.strip().startswith("-")][:3]

    def generate_answer(self, question, evidence):
        context = " ".join(evidence)[:500]  # truncate context
        prompt = f"""
Evidence: {context}

Question: {question}

Short analytical answer:
"""
        return self.llm(prompt)[0]["generated_text"]
