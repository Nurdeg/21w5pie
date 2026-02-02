from backend.services.llm_provider import OllamaService
from backend.services.nlp_engine import NLPService
from backend.services.memory_store import MemoryStore
from backend.core.schemas import AnalysisResult
import ollama # Make sure to import this for the chat method

class Orchestrator:
    def __init__(self):
        self.llm = OllamaService()
        self.nlp = NLPService()
        self.memory = MemoryStore()

    async def run_hybrid_analysis(self, text: str) -> AnalysisResult:
        # 1. Classical NLP Pass
        spacy_raw_entities = self.nlp.extract_entities(text)
        entities_str = ", ".join([f"{e['text']} ({e['label']})" for e in spacy_raw_entities])

        # 2. Enhanced Prompt
        enhanced_prompt = f"""
        Context: Named Entities detected: [{entities_str}].
        Analyze the text below considering the context above.
        Text: {text}
        """

        # 3. Local LLM Pass
        llm_result_dict = await self.llm.analyze_text(enhanced_prompt)
        
        # 4. Save to Memory (Fire and forget)
        self.memory.save_analysis(text, llm_result_dict)

        return AnalysisResult(**llm_result_dict)

    def query_memory(self, query: str):
        return self.memory.search_similar(query)

    # --- NEW CHAT METHOD ---
    async def chat_with_memory(self, user_question: str) -> str:
        # 1. Search Vector DB
        results = self.memory.search_similar(user_question, n_results=5)
        
        # 2. Extract Context
        context_text = ""
        if results['documents']:
            context_text = "\n\n".join(results['documents'][0])
            
        if not context_text:
            return "I couldn't find any relevant past analyses to answer that."

        # 3. Prompt with Context
        prompt = f"""
        You are an AI assistant with access to a database of past text analyses.
        
        User Question: "{user_question}"
        
        Relevant Context from Database:
        {context_text}
        
        Instructions:
        Answer the user's question STRICTLY based on the Context above. 
        If the answer isn't in the context, say "I don't know."
        Keep the answer concise and professional.
        """

        # 4. Call Ollama directly for a chat response
        response = ollama.chat(
            model=self.llm.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response['message']['content']