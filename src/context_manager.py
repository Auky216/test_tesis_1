import chromadb
import time

class ContextManager:
    def __init__(self, db_path: str = "./chroma_db"):
        print("[MEMORIA] Inicializando base de datos vectorial ChromaDB...")
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="project_context")
        print(f"[MEMORIA] Lista. Documentos históricos recordados: {self.collection.count()}")
        
    def add_to_context(self, task: str, code: str):
        """Guarda el código generado en la base de datos vectorial para uso futuro."""
        doc_id = f"doc_{int(time.time())}"
        self.collection.add(
            documents=[code],
            metadatas=[{"task": task}],
            ids=[doc_id]
        )
        print(f"[MEMORIA] Nuevo contexto guardado (RAG actualizado)")
        
    def retrieve_context(self, query: str, token_budget: int = 1600) -> str:
        """
        Capa 2: Recupera código relevante basándose en la consulta actual.
        """
        if self.collection.count() == 0:
            return "# No hay memoria previa en la base de datos."
            
        # Buscar similitud semántica en ChromaDB
        results = self.collection.query(query_texts=[query], n_results=1)
        
        if results and results['documents'] and results['documents'][0]:
            retrieved_code = results['documents'][0][0]
            print(f"[MEMORIA] ¡Recuerdo encontrado para inyectar al modelo!")
            return f"# --- MEMORIA RECUPERADA (RAG) ---\n# Basado en conocimiento previo:\n{retrieved_code[:800]}\n# -----------------------------------------"
        
        return "# Contexto previo no encontrado."
