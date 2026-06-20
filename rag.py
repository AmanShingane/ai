import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(
    EMBEDDING_MODEL
)


class DDRRetriever:

    def __init__(self):

        self.index = None
        self.chunks = []

    def chunk_text(
        self,
        text,
        chunk_size=1000,
        overlap=200
    ):
        """
        Split text into chunks.
        """

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def create_embeddings(
        self,
        chunks
    ):
        """
        Generate embeddings.
        """

        embeddings = model.encode(
            chunks,
            convert_to_numpy=True
        )

        return embeddings

    def build_index(
        self,
        text
    ):
        """
        Build FAISS vector store.
        """

        self.chunks = self.chunk_text(text)

        embeddings = self.create_embeddings(
            self.chunks
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(
            embeddings.astype(np.float32)
        )

    def retrieve(
        self,
        query,
        top_k=5
    ):
        """
        Retrieve relevant chunks.
        """

        if self.index is None:
            raise ValueError(
                "Index not built yet."
            )

        query_embedding = model.encode(
            [query],
            convert_to_numpy=True
        )

        distances, indices = self.index.search(
            query_embedding.astype(np.float32),
            top_k
        )

        results = []

        for idx in indices[0]:

            if idx < len(self.chunks):
                results.append(
                    self.chunks[idx]
                )

        return results

    def retrieve_context(
        self,
        query,
        top_k=5
    ):
        """
        Return merged context.
        """

        chunks = self.retrieve(
            query,
            top_k
        )

        return "\n\n".join(chunks)


def build_retriever(
    inspection_text,
    thermal_text
):
    """
    Build vector store
    using both documents.
    """

    combined_text = f"""

    INSPECTION REPORT

    {inspection_text}

    THERMAL REPORT

    {thermal_text}

    """

    retriever = DDRRetriever()

    retriever.build_index(
        combined_text
    )

    return retriever


if __name__ == "__main__":

    sample_text = """
    Ceiling crack found in living room.

    Thermal hotspot of 78C
    detected near ceiling.
    """

    retriever = DDRRetriever()

    retriever.build_index(
        sample_text
    )

    results = retriever.retrieve(
        "ceiling crack"
    )

    print(results)
