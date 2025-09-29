"""
Embedding service using Qwen3-Embedding-8B (Local or API)
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class QwenEmbeddingService:
    """Embedding service using Qwen3-Embedding-8B (Local or API)"""

    def __init__(self, use_local: bool = None):
        self.model_name = "Qwen/Qwen3-Embedding-4B"

        # Determine if using local or API
        if use_local is None:
            use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

        self.use_local = use_local
        self.model = None
        self.client = None

        if self.use_local:
            self._init_local_model()
        else:
            self._init_api_client()

    def _init_local_model(self):
        """Initialize local model using sentence-transformers"""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"🖥️ Loading {self.model_name} locally...")
            self.model = SentenceTransformer(self.model_name)
            print("✅ Local model loaded successfully")
        except ImportError:
            raise Exception("sentence-transformers not installed. Run: pip install sentence-transformers")
        except Exception as e:
            raise Exception(f"Failed to load local model: {e}")

    def _init_api_client(self):
        """Initialize API client with Nebius provider"""
        from huggingface_hub import InferenceClient

        # Get token from environment
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")

        if not hf_token:
            raise Exception("No HF_TOKEN or HUGGINGFACE_API_TOKEN found in environment!")

        # Initialize client with Nebius provider
        self.client = InferenceClient(
            provider="nebius",
            api_key=hf_token,
        )
        print("🌐 Using Nebius API for embeddings")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if self.use_local:
            return self._embed_texts_local(texts)
        else:
            return self._embed_texts_api(texts)

    def _embed_texts_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings locally using sentence-transformers"""
        print(f"🖥️ Generating {len(texts)} embeddings locally...")

        # Process in batches to avoid memory issues
        batch_size = 32
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"   Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}...")

            batch_embeddings = self.model.encode(batch, convert_to_tensor=False)
            embeddings.extend(batch_embeddings.tolist())

        print(f"✅ Generated {len(embeddings)} embeddings locally")
        return embeddings

    def _embed_texts_api(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings via Nebius API"""
        print(f"🌐 Generating {len(texts)} embeddings via Nebius provider...")

        embeddings = []
        for i, text in enumerate(texts):
            if i % 50 == 0:  # Progress indicator
                print(f"   Processing {i+1}/{len(texts)}...")

            # Get embedding for single text
            result = self.client.feature_extraction(text, model=self.model_name)

            # Handle the nested array structure [[embedding]]
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                embeddings.append(result[0])  # Extract the actual embedding
            else:
                embeddings.append(result)

        print(f"✅ Generated {len(embeddings)} embeddings via API")
        return embeddings

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if self.use_local:
            embedding = self.model.encode([text], convert_to_tensor=False)
            return embedding[0].tolist()
        else:
            result = self.client.feature_extraction(text, model=self.model_name)

            # Handle the nested array structure [[embedding]]
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                return result[0]  # Extract the actual embedding
            else:
                return result