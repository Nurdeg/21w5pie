# backend/services/nlp_engine.py
import spacy

class NLPService:
    def __init__(self):
        # Load the small model for speed
        self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text: str):
        doc = self.nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]