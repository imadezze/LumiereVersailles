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
        # Get model name from environment or use default
        self.model_name = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")

        # Determine if using local or API
        if use_local is None:
            use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

        self.use_local = use_local
        self.model = None
        self.client = None
        self.provider = None

        if self.use_local:
            self._init_local_model()
        else:
            self._init_api_client()

    def _init_local_model(self):
        """Initialize local model using sentence-transformers"""
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            print(f"🖥️ Loading {self.model_name} locally...")

            # Configure device and memory settings
            device = "cpu"  # Use CPU to avoid MPS memory issues
            if torch.cuda.is_available():
                device = "cuda"
                print("🚀 Using CUDA GPU")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                # Check available memory before using MPS
                try:
                    # Test with small tensor first
                    test_tensor = torch.randn(100, 100).to('mps')
                    del test_tensor
                    device = "mps"
                    print("🍎 Using MPS (Mac GPU)")
                except Exception:
                    print("⚠️ MPS memory limited, falling back to CPU")
                    device = "cpu"
            else:
                print("🖥️ Using CPU")

            # Load model with device specification
            self.model = SentenceTransformer(self.model_name, device=device)

            # Additional memory optimization for MPS
            if device == "mps":
                import os
                os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.7'  # Use 70% of available memory

            print("✅ Local model loaded successfully")

        except ImportError:
            raise Exception("sentence-transformers not installed. Run: pip install sentence-transformers torch")
        except Exception as e:
            raise Exception(f"Failed to load local model: {e}")

    def _init_api_client(self):
        """Initialize API client - supports Mistral AI and Nebius providers"""
        # Check if using Mistral AI embedding API
        if self.model_name in ["mistral-embed", "Linq-AI-Research/Linq-Embed-Mistral"]:
            # Use Mistral AI API
            try:
                from mistralai import Mistral
            except ImportError:
                raise Exception("mistralai package not installed. Run: pip install mistralai")

            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise Exception("No MISTRAL_API_KEY found in environment for Mistral model!")

            self.client = Mistral(api_key=api_key)
            self.provider = "mistral"
            # Always use mistral-embed for Mistral API
            if self.model_name == "Linq-AI-Research/Linq-Embed-Mistral":
                self.model_name = "mistral-embed"
            print(f"🌐 Using Mistral AI API for embeddings with model: {self.model_name}")
        else:
            # Use Nebius provider for HuggingFace models
            from huggingface_hub import InferenceClient

            hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")
            if not hf_token:
                raise Exception("No HF_TOKEN or HUGGINGFACE_API_TOKEN found in environment!")

            self.client = InferenceClient(
                provider="nebius",
                api_key=hf_token,
            )
            self.provider = "nebius"
            print(f"🌐 Using Nebius API for embeddings with model: {self.model_name}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if self.use_local:
            return self._embed_texts_local(texts)
        else:
            return self._embed_texts_api(texts)

    def _embed_texts_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings locally using sentence-transformers"""
        print(f"🖥️ Generating {len(texts)} embeddings locally...")

        # Determine batch size based on device
        device = str(self.model.device)
        if "mps" in device:
            batch_size = 8  # Smaller batches for MPS to avoid memory issues
        elif "cuda" in device:
            batch_size = 32  # Larger batches for CUDA
        else:
            batch_size = 16  # Medium batches for CPU

        print(f"   Using batch size: {batch_size} (device: {device})")

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(texts) + batch_size - 1)//batch_size
            print(f"   Processing batch {batch_num}/{total_batches}...")

            try:
                batch_embeddings = self.model.encode(
                    batch,
                    convert_to_tensor=False,
                    show_progress_bar=False
                )
                embeddings.extend(batch_embeddings.tolist())
            except RuntimeError as e:
                if "out of memory" in str(e):
                    print(f"⚠️ Memory error in batch {batch_num}, switching to CPU...")
                    # Move model to CPU and retry
                    self.model = self.model.to('cpu')
                    batch_embeddings = self.model.encode(
                        batch,
                        convert_to_tensor=False,
                        show_progress_bar=False
                    )
                    embeddings.extend(batch_embeddings.tolist())
                else:
                    raise e

        print(f"✅ Generated {len(embeddings)} embeddings locally")
        return embeddings

    def _embed_texts_api(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings via API (Mistral or Nebius)"""
        if self.provider == "mistral":
            return self._embed_texts_mistral_api(texts)
        else:
            return self._embed_texts_nebius_api(texts)

    def _embed_texts_mistral_api(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings via Mistral AI API"""
        print(f"🌐 Generating {len(texts)} embeddings via Mistral AI API...")

        embeddings = []
        api_batch_size = 5  # Try batches of 3, fallback to 1 if needed

        i = 0
        while i < len(texts):
            # Show progress every 50 items
            if (i + 1) % 50 == 0 or i == 0 or (i + 1) >= len(texts):
                print(f"   Processing {i + 1}/{len(texts)}...")

            # Try to process a small batch
            batch_end = min(i + api_batch_size, len(texts))
            batch = texts[i:batch_end]

            try:
                # Try batch processing
                response = self.client.embeddings.create(
                    model=self.model_name,
                    inputs=batch
                )

                # Extract embeddings from response
                for item in response.data:
                    embeddings.append(item.embedding)

                i = batch_end  # Move to next batch

            except Exception as e:
                error_msg = str(e).lower()

                # If batch failed due to size, try one at a time
                if "batch" in error_msg or "too large" in error_msg or "too many" in error_msg:
                    if api_batch_size > 1:
                        api_batch_size = 1  # Reduce to single processing
                        print(f"   ⚠️ Switching to single text processing...")
                        continue  # Retry with single text
                    else:
                        # Even single text failed
                        print(f"   ❌ Error processing text {i + 1}: {e}")
                        raise e
                else:
                    # Other error
                    print(f"   ❌ Error: {e}")
                    raise e

        print(f"✅ Generated {len(embeddings)} embeddings via Mistral AI API")
        return embeddings

    def _embed_texts_nebius_api(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings via Nebius provider"""
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

        print(f"✅ Generated {len(embeddings)} embeddings via Nebius API")
        return embeddings

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if self.use_local:
            embedding = self.model.encode([text], convert_to_tensor=False)
            return embedding[0].tolist()
        elif self.provider == "mistral":
            response = self.client.embeddings.create(
                model=self.model_name,
                inputs=[text]
            )
            return response.data[0].embedding
        else:
            result = self.client.feature_extraction(text, model=self.model_name)

            # Handle the nested array structure [[embedding]]
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                return result[0]  # Extract the actual embedding
            else:
                return result