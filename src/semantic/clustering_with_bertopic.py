# clustering_with_bertopic.py - VERSION CSV INPUT
import os
import sys
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Set
from pathlib import Path
import re
from collections import defaultdict, Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from bertopic import BERTopic
import plotly.express as px

# Télécharger ressources NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

# Gestion des chemins
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Modules personnels
from src.preprocessing.preprocessing import TextPreprocessor
from src.semantic.translation import Translator
from src.semantic.semantic_encoding import SemanticEncoder

# Configuration des sorties
BASE_DIR = Path(__file__).parent.parent
OUTPUT_PATH = BASE_DIR / "outputs" / "reports"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================
# CHARGEUR CSV FLEXIBLE
# ============================================================

class CSVCorpusLoader:
    """
    Charge corpus depuis fichier CSV
    Détecte automatiquement colonnes pertinentes
    """
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.text_column = None
        self.id_column = None
        self.metadata_columns = []
    
    def load(self) -> pd.DataFrame:
        """Charge fichier CSV"""
        print(f"[CSVLoader] Chargement {self.csv_path}...")
        
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Fichier CSV non trouvé: {self.csv_path}")
        
        # Essayer différents encodages
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(self.csv_path, encoding=encoding)
                print(f"  ✓ Chargé avec encodage: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("Impossible de lire le fichier CSV (encodage incompatible)")
        
        print(f"  → {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"  → Colonnes: {list(df.columns)}")
        
        self.df = df
        return df
    
    def detect_text_column(self) -> str:
        """
        Détecte automatiquement la colonne contenant le texte
        Cherche: text, content, message, tweet, description, body, comment, etc.
        """
        if self.df is None:
            raise ValueError("DataFrame non chargé. Appelez load() d'abord")
        
        text_keywords = ['text', 'content', 'message', 'tweet', 'description', 
                        'body', 'comment', 'post', 'review', 'feedback', 'note']
        
        for col in self.df.columns:
            col_lower = col.lower()
            for keyword in text_keywords:
                if keyword in col_lower:
                    self.text_column = col
                    print(f"[CSVLoader] Colonne texte détectée: '{col}'")
                    return col
        
        # Fallback: colonne avec le plus de texte long
        max_avg_length = 0
        best_col = None
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                avg_len = self.df[col].astype(str).str.len().mean()
                if avg_len > max_avg_length:
                    max_avg_length = avg_len
                    best_col = col
        
        if best_col:
            self.text_column = best_col
            print(f"[CSVLoader] Colonne texte (par longueur): '{best_col}' (longueur moyenne: {max_avg_length:.0f})")
            return best_col
        
        raise ValueError("Impossible de détecter colonne texte. Spécifiez manuellement.")
    
    def detect_id_column(self) -> str:
        """
        Détecte colonne ID
        Cherche: id, tweet_id, document_id, post_id, etc.
        """
        if self.df is None:
            raise ValueError("DataFrame non chargé")
        
        id_keywords = ['id', 'tweet_id', 'document_id', 'post_id', 'message_id', 
                       'index', 'pk', 'primary_key']
        
        for col in self.df.columns:
            col_lower = col.lower()
            for keyword in id_keywords:
                if keyword in col_lower:
                    self.id_column = col
                    print(f"[CSVLoader] Colonne ID détectée: '{col}'")
                    return col
        
        # Fallback: première colonne ou index
        self.id_column = self.df.index.name if self.df.index.name else 'index'
        print(f"[CSVLoader] ID par défaut: index")
        return self.id_column
    
    def get_corpus(self, text_column: str = None, id_column: str = None) -> List[Dict]:
        """
        Retourne corpus au format standard
        Format: [{'id': '...', 'text': '...', 'metadata': {...}}, ...]
        """
        if self.df is None:
            raise ValueError("DataFrame non chargé")
        
        # Détecter colonnes si non spécifiées
        if not text_column:
            text_column = self.text_column or self.detect_text_column()
        if not id_column:
            id_column = self.id_column or self.detect_id_column()
        
        corpus = []
        
        for idx, row in self.df.iterrows():
            item = {
                'id': str(row[id_column]) if id_column in self.df.columns else str(idx),
                'text': str(row[text_column]),
                'metadata': {}
            }
            
            # Ajouter métadonnées supplémentaires
            for col in self.df.columns:
                if col not in [text_column, id_column]:
                    item['metadata'][col] = row[col]
            
            corpus.append(item)
        
        return corpus
    
    def get_dataframe(self) -> pd.DataFrame:
        """Retourne DataFrame chargé"""
        return self.df


# ============================================================
# DÉTECTION CLIENTS - VERSION OPTIMISÉE
# ============================================================

class AdvancedClientDetector:
    """
    Détecte clients par plusieurs méthodes:
    1. Named Entity Recognition (NER) - NLTK
    2. Majuscules et patterns linguistiques
    3. Analyse contextuelle
    4. TF-IDF scoring
    """
    
    def __init__(self):
        self.stopwords_en = set(stopwords.words('english'))
        self.stopwords_fr = set(stopwords.words('french'))
        self.all_stopwords = self.stopwords_en.union(self.stopwords_fr)
        self.org_suffixes = ['inc', 'corp', 'ltd', 'llc', 'group', 'bank', 'airlines', 'solutions', 'tech']
    
    def extract_proper_nouns(self, text: str) -> List[str]:
        """Extrait noms propres avec POS tagging"""
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            proper_nouns = []
            for word, tag in pos_tags:
                if tag == 'NNP':
                    if word.lower() not in self.all_stopwords and len(word) > 2:
                        proper_nouns.append(word)
            
            return proper_nouns
        except Exception as e:
            return []
    
    def extract_capitalized_entities(self, text: str) -> List[str]:
        """Extrait entités capitalisées"""
        entities = []
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if (match.lower() not in self.all_stopwords and 
                len(match) > 2 and 
                not re.match(r'^\d+', match)):
                entities.append(match.strip())
        
        return entities
    
    def extract_contextual_entities(self, text: str) -> List[str]:
        """Extrait entités contextuelles"""
        entities = []
        
        contextual_patterns = [
            r'(?:from|by|at|using|with|via)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:from|by|at|using|with|via)\s+([A-Z]{2,})',
            r'(?:company|brand|service|platform|app|application)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in contextual_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        return [e for e in entities if len(e) > 2]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extrait mentions et hashtags"""
        mentions = []
        
        at_mentions = re.findall(r'@([\w]+)', text)
        mentions.extend([m for m in at_mentions if len(m) > 2])
        
        hashtags = re.findall(r'#([\w]+)', text)
        mentions.extend([h for h in hashtags if len(h) > 2 and not h[0].isdigit()])
        
        return mentions
    
    def extract_all_entities(self, text: str) -> List[str]:
        all_entities = set()
        
        # 1. Priorité aux @mentions (très fiable sur Twitter pour désigner l'entreprise)
        mentions = re.findall(r'@([\w]+)', text)
        all_entities.update(mentions)

        # 2. Détection par majuscules avec vérification de suffixe entreprise
        pattern = r'\b([A-Z][\w]+(?:\s+[A-Z][\w]+)*)\b'
        matches = re.findall(pattern, text)
        for match in matches:
            m_lower = match.lower()
            # Si le nom contient un suffixe d'entreprise, on le garde en priorité
            if any(suffix in m_lower for suffix in self.org_suffixes):
                all_entities.add(match)
            # Sinon, on vérifie que ce n'est pas un stopword et que c'est assez long
            elif m_lower not in self.all_stopwords and len(match) > 3:
                all_entities.add(match)
        
        return list(all_entities)
    
    def score_entities_tfidf(self, corpus: List[str]) -> Dict[str, float]:
        """Score entités par TF-IDF"""
        entity_stats = defaultdict(lambda: {
            'frequency': 0,
            'doc_count': 0,
        })
        
        print("[TF-IDF] Calcul statistiques entités...")
        
        for text in corpus:
            entities = self.extract_all_entities(text)
            for entity in entities:
                entity_norm = entity.lower()
                entity_stats[entity_norm]['frequency'] += 1
                entity_stats[entity_norm]['doc_count'] += 1
        
        scores = {}
        total_docs = len(corpus)
        
        for entity_norm, stats in entity_stats.items():
            tf = stats['frequency']
            idf = np.log(total_docs / max(1, stats['doc_count']))
            tfidf = tf * idf
            scores[entity_norm] = tfidf
        
        max_score = max(scores.values()) if scores else 1
        normalized = {
            entity: min(1.0, score / max_score) 
            for entity, score in scores.items()
        }
        
        filtered = {
            entity: score 
            for entity, score in normalized.items() 
            if score > 0.2 and len(entity) > 2
        }
        
        print(f"[TF-IDF] {len(filtered)} entités avec score > 0.2")
        
        return filtered
    
    def detect_client_in_text(self, text: str, entity_scores: Dict[str, float]) -> Tuple[str, float]:
        """Détecte client principal dans texte"""
        entities = self.extract_all_entities(text)
        
        candidates = []
        for entity in entities:
            entity_norm = entity.lower()
            if entity_norm in entity_scores:
                candidates.append((entity, entity_scores[entity_norm]))
        
        if candidates:
            best = max(candidates, key=lambda x: x[1])
            return (best[0], best[1])
        else:
            return ('UNKNOWN', 0.0)
    
    def analyze_corpus(self, corpus: List[str]) -> Dict:
        """Analyse complète corpus"""
        print("[ClientDetector] Analyse corpus complet...")
        
        entity_scores = self.score_entities_tfidf(corpus)
        top_clients = sorted(entity_scores.items(), key=lambda x: x[1], reverse=True)[:25]
        
        print(f"[ClientDetector] Top clients:")
        for client, score in top_clients[:10]:
            print(f"  - {client}: {score:.3f}")
        
        return {
            'entity_scores': entity_scores,
            'top_clients': top_clients,
            'total_unique_entities': len(entity_scores),
        }


# ============================================================
# EXTRACTION KEYWORDS
# ============================================================

class KeywordExtractor:
    """Extrait keywords contextuels"""
    
    CONTEXTE_KEYWORDS = {
        'engagement': ['engagement', 'interaction', 'actif', 'engaged', 'active'],
        'non_clair': ['flou', 'ambigu', 'confus', 'vague', 'unclear', 'confusion'],
        'eviter': ['éviter', 'risque', 'problème', 'danger', 'warning', 'scandal'],
        
        'recommandation': ['recommande', 'suggest', 'conseil', 'advice'],
        'qualite': ['quality', 'qualité', 'excellent', 'bon', 'good'],
        'defaut': ['defaut', 'bug', 'erreur', 'probleme', 'error'],
        
        'communication': ['communication', 'support', 'aide', 'help'],
        'silence': ['silence', 'ignore', 'no response', 'ghosting'],
        'transparence': ['transparent', 'honest', 'sincere'],
    }
    
    def __init__(self):
        self.keyword_to_category = {}
        for category, keywords in self.CONTEXTE_KEYWORDS.items():
            for kw in keywords:
                self.keyword_to_category[kw.lower()] = category
    
    def extract_keywords(self, text: str) -> Dict:
        """Extrait keywords"""
        text_lower = text.lower()
        found_categories = defaultdict(list)
        
        for keyword, category in self.keyword_to_category.items():
            if re.search(rf'\b{keyword}\b', text_lower):
                found_categories[category].append(keyword)
        
        if not found_categories:
            return {
                'categories': ['non_clair'],
                'keywords': [],
                'primary_category': 'non_clair'
            }
        
        primary = list(found_categories.keys())[0]
        
        return {
            'categories': list(found_categories.keys()),
            'keywords': [kw for kws in found_categories.values() for kw in kws],
            'primary_category': primary
        }
    
    def classify_by_context(self, primary_category: str) -> str:
        """Classifie selon catégorie"""
        category_to_class = {
            'engagement': 'ENGAGER',
            'recommandation': 'ENGAGER',
            'qualite': 'ENGAGER',
            'communication': 'ENGAGER',
            'transparence': 'ENGAGER',
            
            'non_clair': 'NEUTRE',
            'silence': 'NEUTRE',
            
            'eviter': 'EVITER',
            'defaut': 'EVITER',
        }
        
        return category_to_class.get(primary_category, 'NEUTRE')


# ============================================================
# SCORING FIABILITÉ
# ============================================================

class ReliabilityScorer:
    """Score de fiabilité par client"""
    
    def __init__(self):
        self.client_data = defaultdict(lambda: {
            'ENGAGER': 0,
            'NEUTRE': 0,
            'EVITER': 0,
            'total': 0,
            'confidence_scores': [],
            'keywords_all': [],
        })
    
    def add_classification(self, client: str, classification: str, 
                          confidence: float = 1.0, keywords: List[str] = None):
        """Ajoute classification"""
        self.client_data[client][classification] += 1
        self.client_data[client]['total'] += 1
        self.client_data[client]['confidence_scores'].append(confidence)
        if keywords:
            self.client_data[client]['keywords_all'].extend(keywords)
    
    def calculate_reliability(self, client: str) -> Dict:
        """Calcule fiabilité 0-100"""
        data = self.client_data[client]
        total = data['total']
        
        if total == 0:
            return {
                'client': client,
                'reliability_score': 50.0,
                'classification': 'NEUTRE',
                'engager_pct': 0,
                'neutre_pct': 100,
                'eviter_pct': 0,
                'confidence': 0.0,
            }
        
        score = (
            (data['ENGAGER'] / total) * 40 +
            (data['NEUTRE'] / total) * 0 +
            (data['EVITER'] / total) * (-20)
        )
        
        reliability = max(0, min(100, 50 + score))
        
        engager_pct = (data['ENGAGER'] / total) * 100
        eviter_pct = (data['EVITER'] / total) * 100
        neutre_pct = (data['NEUTRE'] / total) * 100
        
        if engager_pct >= 50:
            final_class = 'ENGAGER'
        elif eviter_pct >= 50:
            final_class = 'EVITER'
        else:
            final_class = 'NEUTRE'
        
        avg_confidence = np.mean(data['confidence_scores']) if data['confidence_scores'] else 0.5
        
        keyword_counter = Counter(data['keywords_all'])
        top_keywords = [kw for kw, _ in keyword_counter.most_common(5)]
        
        return {
            'client': client,
            'reliability_score': round(reliability, 2),
            'classification': final_class,
            'engager_pct': round(engager_pct, 1),
            'neutre_pct': round(neutre_pct, 1),
            'eviter_pct': round(eviter_pct, 1),
            'total_tweets': total,
            'confidence': round(avg_confidence, 3),
            'top_keywords': top_keywords,
            'breakdown': {
                'engager': data['ENGAGER'],
                'neutre': data['NEUTRE'],
                'eviter': data['EVITER'],
            }
        }
    
    def get_all_scores(self) -> List[Dict]:
        """Retourne tous les scores"""
        return [
            self.calculate_reliability(client)
            for client in self.client_data.keys()
        ]


# ============================================================
# MAIN PLATFORM
# ============================================================

class ClientAnalysisPlatform:
    """Plateforme d'analyse clients"""
    
    def __init__(self):
        self.client_detector = AdvancedClientDetector()
        self.keyword_extractor = KeywordExtractor()
        self.reliability_scorer = ReliabilityScorer()
        self.entity_scores = {}
    
    def initialize(self, corpus: List[str]):
        """Initialise avec analyse corpus"""
        analysis = self.client_detector.analyze_corpus(corpus)
        self.entity_scores = analysis['entity_scores']
        return analysis
    
    def analyze_tweet(self, tweet_text: str, tweet_id: str) -> Dict:
        """Analyse tweet complet"""
        
        client_name, confidence = self.client_detector.detect_client_in_text(
            tweet_text, self.entity_scores
        )
        
        keywords_info = self.keyword_extractor.extract_keywords(tweet_text)
        
        classification = self.keyword_extractor.classify_by_context(
            keywords_info['primary_category']
        )
        
        self.reliability_scorer.add_classification(
            client_name,
            classification,
            confidence=confidence,
            keywords=keywords_info['keywords']
        )
        
        return {
            'tweet_id': tweet_id,
            'texte': tweet_text[:80] + '...' if len(tweet_text) > 80 else tweet_text,
            'client': client_name,
            'confidence': round(confidence, 3),
            'keywords': keywords_info['keywords'],
            'classification': classification,
        }


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    
    import argparse
    
    print("\n" + "="*80)
    print("PLATEFORME ANALYSE CLIENTS - ENTRÉE CSV")
    print("="*80)
    
    # Parser arguments
    parser = argparse.ArgumentParser(description='Analyse clients depuis CSV')
    parser.add_argument('--csv', type=str, help='Chemin fichier CSV')
    parser.add_argument('--text-column', type=str, default=None, help='Nom colonne texte')
    parser.add_argument('--id-column', type=str, default=None, help='Nom colonne ID')
    parser.add_argument('--sample', type=int, default=None, help='Nombre documents à analyser (None = tous)')
    
    args = parser.parse_args()
    
    # Si pas de CSV en argument, chercher dans uploads
    csv_path = r"C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\datasets\tweets_apple_20260501_135633.csv"
    if not csv_path:
        uploads_dir = Path('/mnt/user-data/uploads')
        csv_files = list(uploads_dir.glob('*.csv'))
        
        if csv_files:
            csv_path = str(csv_files[0])
            print(f"[Main] Fichier CSV trouvé: {csv_path}")
        else:
            raise FileNotFoundError("Aucun fichier CSV trouvé. Spécifiez --csv ou placez un fichier dans /uploads")
    
    # Charger CSV
    loader = CSVCorpusLoader(csv_path)
    df = loader.load()
    
    # Détecter colonnes
    if not args.text_column:
        args.text_column = loader.detect_text_column()
    if not args.id_column:
        args.id_column = loader.detect_id_column()
    
    # Charger corpus
    corpus_data = loader.get_corpus(args.text_column, args.id_column)
    
    # Limiter si nécessaire
    if args.sample:
        corpus_data = corpus_data[:args.sample]
    
    print(f"\n[Main] Corpus chargé: {len(corpus_data)} documents")
    
    # Prétraitement
    preprocessor = TextPreprocessor()
    translator = Translator()
    
    texts_clean = []
    print(f"\n[Phase 1] Nettoyage {len(corpus_data)} documents...")
    
    for i, item in enumerate(corpus_data):
        try:
            prep = preprocessor.process(item['text'], detect_language=True)
            trans_res = translator.translate_corpus(
                [{'cleaned_text': prep['cleaned_text']}],
                text_key='cleaned_text',
                lang_key='language'
            )[0]
            
            final = trans_res['translated_text']
            final = re.sub(r'\b\d+\b', '', final)
            final = re.sub(r'\s+', ' ', final).strip()
            texts_clean.append(final)
        except Exception as e:
            print(f"  Erreur document {i}: {e}")
            texts_clean.append("")
        
        if (i + 1) % max(1, len(corpus_data) // 10) == 0:
            print(f"  {i+1}/{len(corpus_data)} ✓")
    
    # Initialize plateforme
    print(f"\n[Phase 2] Initialisation détection clients...")
    platform = ClientAnalysisPlatform()
    init_results = platform.initialize(texts_clean)
    
    print(f"  → {init_results['total_unique_entities']} entités uniques")
    print(f"  → Top 10 clients:")
    for client, score in init_results['top_clients'][:10]:
        print(f"     • {client.upper()}: {score:.3f}")
    
    # Analyse tweets
    print(f"\n[Phase 3] Analyse {len(texts_clean)} tweets...")
    analysis_results = []
    for i, text in enumerate(texts_clean):
        analysis = platform.analyze_tweet(text, f"doc_{i}")
        analysis_results.append(analysis)
        if (i + 1) % max(1, len(texts_clean) // 10) == 0:
            print(f"  {i+1}/{len(texts_clean)} ✓")
    
    # Résultats
    print(f"\n[Phase 4] Calcul fiabilité...")
    client_reliability = platform.reliability_scorer.get_all_scores()
    
    print("\n" + "="*80)
    print("RÉSULTATS - SPECTRE FIABILITÉ PAR CLIENT")
    print("="*80)
    print(f"{'Client':<20} {'Score':<8} {'Class':<10} {'Conf':<8} {'Engager':<10} {'Éviter':<10}")
    print("-" * 80)
    
    for score_data in sorted(client_reliability, key=lambda x: x['reliability_score'], reverse=True):
        client = score_data['client'][:19]
        score = score_data['reliability_score']
        classif = score_data['classification']
        conf = score_data['confidence']
        engager = score_data['engager_pct']
        eviter = score_data['eviter_pct']
        
        if score >= 70:
            emoji = "🟢"
        elif score >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        print(f"{client:<20} {emoji} {score:<6.1f} {classif:<10} {conf:<8.3f} {engager:<9.1f}% {eviter:<9.1f}%")
    
    # Export JSON
    print(f"\n[Phase 5] Export JSON...")
    output = {
        "metadata": {
            "csv_file": os.path.basename(csv_path),
            "total_documents": len(corpus_data),
            "unique_clients": len(client_reliability),
            "text_column": args.text_column,
            "id_column": args.id_column,
        },
        "methodology": {
            "approach": "Multi-method client detection: NER + capitalization + context + TF-IDF",
            "methods": ["POS_tagging", "Capitalization", "Context", "Mentions", "TF-IDF"],
            "labels": ["ENGAGER", "NEUTRE", "EVITER"]
        },
        "clients": sorted(client_reliability, key=lambda x: x['reliability_score'], reverse=True),
        "sample_documents": analysis_results[:30],
    }
    
    output_file = OUTPUT_PATH / "due_diligence_clients.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Résultats → {output_file}")
    
    # Export CSV résumé
    csv_output = OUTPUT_PATH / "clients_summary.csv"
    summary_df = pd.DataFrame(client_reliability)
    summary_df.to_csv(csv_output, index=False)
    print(f"✓ Résumé CSV → {csv_output}")
    
    print("\n" + "="*80)
    print("✅ PIPELINE TERMINÉ")
    print("="*80)