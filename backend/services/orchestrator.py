# Change the import line
from backend.services.llm_provider import OllamaService  # <--- CHANGED
from backend.services.nlp_engine import NLPService
from backend.core.schemas import AnalysisResult

class Orchestrator:
    def __init__(self):
        self.llm = OllamaService()  # <--- CHANGED
        self.nlp = NLPService()

    async def run_hybrid_analysis(self, text: str) -> AnalysisResult:
        # 1. Classical NLP Pass
        spacy_raw_entities = self.nlp.extract_entities(text)
        entities_str = ", ".join([f"{e['text']} ({e['label']})" for e in spacy_raw_entities])

        # 2. Enhanced Prompt
        enhanced_prompt = f"""
        Context: Named Entities detected: [{entities_str}].
        
        Analyze the text below considering the context above.
        
        Text:
        {text}
        """

        # 3. Local LLM Pass
        llm_result_dict = await self.llm.analyze_text(enhanced_prompt)
        
        return AnalysisResult(**llm_result_dict)