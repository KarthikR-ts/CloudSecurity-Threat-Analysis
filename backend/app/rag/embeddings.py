
from sentence_transformers import SentenceTransformer
import warnings

# Suppress warnings from sentence-transformers if any
warnings.filterwarnings("ignore")

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded.")
    return _model

def generate_embedding(text: str):
    """Generates a vector embedding for the given text."""
    model = get_embedding_model()
    # encode returns numpy array, convert to list for JSON/Pinecone
    return model.encode(text).tolist()
