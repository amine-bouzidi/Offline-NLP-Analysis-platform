# src/semantic/topic_modeling.py - VERSION FINALE POUR OPTION A
"""
Topic Modeling avec BERTopic (modèle pré-entraîné)
Fichier indépendant pour tests et comparaisons
"""

import numpy as np
from typing import List, Dict, Optional
from collections import Counter
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from bertopic import BERTopic
    from sklearn.feature_extraction.text import CountVectorizer
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False
    print("⚠️ BERTopic pas installé: pip install bertopic")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    LDA_AVAILABLE = True
except ImportError:
    LDA_AVAILABLE = False


class TopicModelingBERTopic:
    """Topic modeling avec BERTopic pré-entraîné"""
    
    def __init__(self, language: str = 'english', 
                 min_topic_size: int = 2,
                 nr_topics: Optional[int] = None):
        self.language = language
        self.min_topic_size = min_topic_size
        self.nr_topics = nr_topics
        self.model = None
        self.topics = None
        self.probs = None
        
    def fit(self, texts: List[str]) -> Dict:
        """Entraîner BERTopic sur textes"""
        if not BERTOPIC_AVAILABLE:
            raise ImportError("BERTopic non installé")
        
        print(f"[BERTopic] Initialisation modèle pré-entraîné...")
        print(f"  Corpus: {len(texts)} textes")
        print(f"  Min topic size: {self.min_topic_size}")
        
        vectorizer_model = CountVectorizer(
            max_df=0.95,
            min_df=1,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        print(f"[BERTopic] Fit sur corpus...")
        self.model = BERTopic(
            language=self.language,
            nr_topics=self.nr_topics,
            min_topic_size=self.min_topic_size,
            vectorizer_model=vectorizer_model,
            verbose=False
        )
        
        self.topics, self.probs = self.model.fit_transform(texts)
        
        n_topics = len(set(self.topics)) - (1 if -1 in self.topics else 0)
        print(f"[BERTopic] Topics découverts: {n_topics} ✓")
        
        return {
            'n_topics': n_topics,
            'topics': self.topics,
            'probabilities': self.probs,
            'topic_sizes': dict(Counter(self.topics))
        }
    
    def get_topic_info(self) -> Dict:
        """Info pour chaque topic"""
        if self.model is None:
            return {}
        
        info = {}
        topic_info_df = self.model.get_topic_info()
        
        for idx, row in topic_info_df.iterrows():
            topic_id = row['Topic']
            keywords = row.get('Representation', [])
            if isinstance(keywords, str):
                keywords = [keywords]
            
            n_docs = sum(1 for t in self.topics if t == topic_id)
            
            info[topic_id] = {
                'keywords': keywords[:5],
                'size': n_docs,
                'frequency': row.get('Frequency', 0)
            }
        
        return info


class TopicModelingLDA:
    """Topic Modeling classique avec LDA"""
    
    def __init__(self, n_topics: int = 5):
        self.n_topics = n_topics
        self.model = None
        self.vectorizer = None
        
    def fit(self, texts: List[str]) -> Dict:
        """Entraîner LDA sur textes"""
        if not LDA_AVAILABLE:
            raise ImportError("scikit-learn non installé")
        
        print(f"[LDA] Initialisation...")
        print(f"  Corpus: {len(texts)} textes")
        print(f"  Topics: {self.n_topics}")
        
        print(f"[LDA] Vectorization TF-IDF...")
        self.vectorizer = TfidfVectorizer(
            max_df=0.95,
            min_df=1,
            stop_words='english',
            ngram_range=(1, 2)
        )
        tfidf = self.vectorizer.fit_transform(texts)
        
        print(f"[LDA] Fit sur corpus...")
        self.model = LatentDirichletAllocation(
            n_components=self.n_topics,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(tfidf)
        
        topics = self.model.transform(tfidf)
        topic_ids = np.argmax(topics, axis=1)
        
        print(f"[LDA] Fit terminé ✓")
        
        return {
            'n_topics': self.n_topics,
            'topics': topic_ids,
            'probabilities': topics
        }
    
    def get_topic_terms(self, n_terms: int = 10) -> Dict:
        """Top terms pour chaque topic"""
        if self.model is None or self.vectorizer is None:
            return {}
        
        feature_names = self.vectorizer.get_feature_names_out()
        terms = {}
        
        for topic_idx, topic in enumerate(self.model.components_):
            top_indices = topic.argsort()[-n_terms:][::-1]
            top_terms = [feature_names[i] for i in top_indices]
            terms[topic_idx] = top_terms
        
        return terms


class TopicModelingComparison:
    """Comparer BERTopic vs LDA"""
    
    def __init__(self):
        self.bertopic_model = None
        self.lda_model = None
        
    def fit_both(self, texts: List[str], 
                 n_topics_lda: int = 5) -> Dict:
        """Entraîner BERTopic et LDA"""
        print("=" * 70)
        print("TOPIC MODELING COMPARISON: BERTopic vs LDA")
        print("=" * 70)
        
        print("\n[1/2] Entraînement BERTopic...")
        self.bertopic_model = TopicModelingBERTopic(
            language='english',
            min_topic_size=2
        )
        bertopic_results = self.bertopic_model.fit(texts)
        
        print("\n[2/2] Entraînement LDA...")
        self.lda_model = TopicModelingLDA(n_topics=n_topics_lda)
        lda_results = self.lda_model.fit(texts)
        
        print("\n" + "=" * 70)
        print("RÉSULTATS COMPARAISON")
        print("=" * 70)
        
        print(f"\nBERTopic: {bertopic_results['n_topics']} topics découverts automatiquement")
        print(f"LDA: {lda_results['n_topics']} topics (fixé)")
        
        return {
            'bertopic_results': bertopic_results,
            'lda_results': lda_results
        }


if __name__ == "__main__":
    texts = [
        "Machine learning and deep learning are transforming AI",
        "Neural networks are powerful for image recognition",
        "Climate change requires urgent action",
        "Global warming affects weather patterns",
        "Electric vehicles reduce carbon emissions",
        "Renewable energy is the future",
    ]
    
    print("=" * 70)
    print("TEST TOPIC MODELING")
    print("=" * 70)
    
    # Test BERTopic
    print("\n[TEST 1] BERTopic seul")
    bertopic = TopicModelingBERTopic(language='english', min_topic_size=2)
    results = bertopic.fit(texts)
    
    print(f"\nTopics découverts: {results['n_topics']}")
    print(f"Topic info: {bertopic.get_topic_info()}")
    
    # Test comparaison
    print("\n\n[TEST 2] BERTopic vs LDA")
    comparison = TopicModelingComparison()
    comp_results = comparison.fit_both(texts, n_topics_lda=3)