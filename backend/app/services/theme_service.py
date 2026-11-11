
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def train_theme_model(
    feedback_texts: list[str],
    min_topic_size: int = 30
):
    """
    Discover recurring themes in customer feedback using BERTopic.
    """

    # Remove empty feedback
    documents = [
        text.strip()
        for text in feedback_texts
        if isinstance(text, str) and text.strip()
    ]

    if len(documents) < 10:
        raise ValueError(
            "At least 10 non-empty feedback entries are required."
        )

    # Load sentence embedding model
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    # Reduce embedding dimensions for clustering
    umap_model = UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric="cosine",
        random_state=42
    )

    # Group similar feedback
    hdbscan_model = HDBSCAN(
        min_cluster_size=min_topic_size,
        min_samples=10,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True
    )

    # Extract meaningful words and phrases for each theme
    vectorizer_model = CountVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=1.0
    )

    # Create BERTopic model
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        calculate_probabilities=False,
        verbose=True
    )

    # Discover topics
    topics, probabilities = topic_model.fit_transform(documents)

    return topic_model, documents, topics


def get_theme_summary(topic_model):
    """
    Return a summary of discovered themes with keywords.
    """

    topic_info = topic_model.get_topic_info()

    themes = []

    for _, row in topic_info.iterrows():
        topic_id = int(row["Topic"])

        # Ignore unassigned reviews
        if topic_id == -1:
            continue

        topic_keywords = topic_model.get_topic(topic_id)

        themes.append({
            "topic_id": topic_id,
            "theme_name": str(row["Name"]),
            "feedback_count": int(row["Count"]),
            "keywords": [
                word for word, score in topic_keywords[:10]
            ]
        })

    return themes
