"""
preprocessing.py
Module de prétraitement de texte — Plateforme Due Diligence KPMG
Corpus : Posts réseaux sociaux + Articles de presse
Langues : FR, AR, EN, DE, ES
"""

import re
import unicodedata
from typing import List, Dict, Optional
from collections import Counter

from langdetect import detect_langs
import spacy


# ─────────────────────────────────────────────────────────────
# Chargement des modèles spaCy
# ─────────────────────────────────────────────────────────────
SPACY_MODELS = {}

def _load_spacy(lang: str):
    model_map = {
        'fr': 'fr_core_news_sm',
        'en': 'en_core_web_sm',
        'de': 'de_core_news_sm',
        'es': 'es_core_news_sm',
    }
    if lang not in SPACY_MODELS and lang in model_map:
        try:
            SPACY_MODELS[lang] = spacy.load(model_map[lang])
        except OSError:
            SPACY_MODELS[lang] = None
    return SPACY_MODELS.get(lang)


# ─────────────────────────────────────────────────────────────
# Mots vides multilingues (avant traduction)
# ─────────────────────────────────────────────────────────────
STOPWORDS = {
    'fr': set(['le','la','les','un','une','des','de','du','à','au','aux',
               'et','ou','mais','donc','or','ni','car','est','sont','a',
               'ont','dans','sur','sous','pour','par','avec','sans','que',
               'qui','quoi','ce','cet','cette','ces','mon','ton','son',
               'ma','ta','sa','nous','vous','ils','elles','je','tu','il',
               'elle','on','se','si','ne','pas','plus','très','bien',
               'aussi','alors','encore','comme','même','tout']),
    'en': set(['the','a','an','and','or','but','in','on','at','to','for',
               'of','with','by','from','is','are','was','were','be','been',
               'have','has','had','do','does','did','will','would','shall',
               'should','may','might','can','could','not','no','so','if',
               'as','its','it','this','that','these','those','we','they',
               'he','she','i','you','my','your','his','her','our','their']),
    'de': set(['der','die','das','ein','eine','und','oder','aber','in',
               'auf','an','zu','von','mit','für','ist','sind','war',
               'ich','du','er','sie','wir','ihr','nicht','auch','als']),
    'es': set(['el','la','los','las','un','una','de','del','a','en','y',
               'o','que','por','con','para','es','son','fue','han',
               'yo','él','ella','nosotros','ellos','no','también','como']),
    'ar': set(['في','من','إلى','على','أن','هذا','كان','قد','التي','الذي',
               'مع','هو','هي','لا','ما','كل','عن','بعد','بين','أو','لم',
               'هذه','ذلك','تلك','حتى','منذ','عند','لكن','إذا','وقد']),
}

# ─────────────────────────────────────────────────────────────
# Mots vides anglais étendus (après traduction)
# Utilisés pour nettoyer les textes traduits avant encodage
# ─────────────────────────────────────────────────────────────
ENGLISH_STOPWORDS_EXTENDED = set([
    'the','of','to','and','a','in','is','it','that','was','for',
    'on','are','with','as','at','be','this','have','from','or',
    'an','but','not','by','they','we','our','their','been','has',
    'had','its','which','also','more','than','when','who','about',
    'into','can','if','do','so','what','up','out','all','one',
    'will','there','would','could','should','may','might','just',
    'how','very','even','well','still','now','here','only','both',
    'much','such','after','before','over','between','through','these',
    'those','them','him','her','his','she','he','us','you',
    'your','my','me','am','were','did','does','said','new','many',
    'most','other','some','then','first','last','while','where',
    'same','any','each','because','way','own','since','however',
    'although','whether','yet','again','further','during','without',
    'within','against','along','already','always','around','back',
    'being','below','between','come','came','down','every','few',
    'find','found','give','given','going','good','great','having',
    'here','high','however','including','indeed','instead','keep',
    'large','later','made','make','making','many','mean','need',
    'never','often','part','place','point','put','rather','really',
    'right','seen','show','small','something','take','think','though',
    'three','through','time','under','upon','used','using','very',
    'want','well','whether','which','while','work','world','years',
])


class LanguageDetector:
    """Détecteur de langue hybride (langdetect + mots-clés)."""

    KEYWORDS = {
        'fr': ['le','la','les','de','des','un','une','et','est','dans','pour'],
        'en': ['the','of','and','to','in','is','it','that','with','for'],
        'es': ['el','la','de','que','y','en','un','los','del','se','por'],
        'de': ['der','die','und','in','den','von','zu','das','mit','sich'],
        'ar': ['في','من','إلى','على','أن','هذا','كان','قد','التي','الذي'],
    }

    def detect(self, text: str) -> Dict:
        if not text or len(text.strip()) < 5:
            return {'language': 'unknown', 'confidence': 0.0}

        words = re.findall(r'\w+', text.lower())

        kw_scores = {}
        for lang, kws in self.KEYWORDS.items():
            matches = sum(1 for w in words if w in kws)
            kw_scores[lang] = matches / len(words) if words else 0

        try:
            preds = detect_langs(text)
            ld_lang = preds[0].lang
            ld_conf = preds[0].prob
        except Exception:
            ld_lang, ld_conf = 'unknown', 0.0

        best_kw = max(kw_scores, key=kw_scores.get) if any(kw_scores.values()) else 'unknown'
        final_lang = ld_lang
        final_conf = ld_conf

        if ld_conf < 0.5 and kw_scores.get(best_kw, 0) > 0.15:
            final_lang = best_kw
            final_conf = 0.65

        return {'language': final_lang, 'confidence': round(final_conf, 2)}


class TextCleaner:
    """Nettoyage adapté aux réseaux sociaux et articles de presse."""

    DEFAULT_OPTIONS = {
        'lowercase': True,
        'remove_urls': True,
        'remove_emails': True,
        'remove_hashtags': True,
        'remove_mentions': True,
        'remove_emojis': True,
        'remove_numbers': False,
        'remove_punctuation': False,
        'remove_extra_spaces': True,
        'normalize_unicode': True,
        'min_word_length': 2,
    }

    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )

    def clean(self, text: str, options: Optional[Dict] = None) -> str:
        if not text:
            return ""

        opts = {**self.DEFAULT_OPTIONS, **(options or {})}
        t = text

        if opts['normalize_unicode']:
            t = unicodedata.normalize('NFKC', t)
        if opts['remove_urls']:
            t = re.sub(r'http[s]?://\S+|www\.\S+', ' ', t)
        if opts['remove_emails']:
            t = re.sub(r'\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b', ' ', t)
        if opts['remove_mentions']:
            t = re.sub(r'@\w+', ' ', t)
        if opts['remove_hashtags']:
            t = re.sub(r'#\w+', ' ', t)
        if opts['remove_emojis']:
            t = self.EMOJI_PATTERN.sub(' ', t)
        if opts['remove_numbers']:
            t = re.sub(r'\d+', ' ', t)
        if opts['remove_punctuation']:
            t = re.sub(r'[^\w\s]', ' ', t)
        if opts['min_word_length'] > 1:
            t = ' '.join(w for w in t.split() if len(w) >= opts['min_word_length'])
        if opts['lowercase']:
            t = t.lower()
        if opts['remove_extra_spaces']:
            t = re.sub(r'\s+', ' ', t).strip()

        return t

    def remove_stopwords(self, text: str, language: str = 'fr') -> str:
        """Supprime les stopwords selon la langue source."""
        sw = STOPWORDS.get(language, set())
        if not sw:
            return text
        return ' '.join(w for w in text.split() if w.lower() not in sw)

    def remove_english_stopwords(self, text: str) -> str:
        """
        Supprime les stopwords anglais étendus.
        À appliquer APRÈS traduction vers l'anglais,
        avant l'encodage sémantique et l'analyse des clusters.
        """
        return ' '.join(
            w for w in text.split()
            if w.lower() not in ENGLISH_STOPWORDS_EXTENDED
            and len(w) > 3
        )


class Tokenizer:
    """Tokenisation multilingue avec support spaCy."""

    def tokenize_words(self, text: str, language: str = 'en') -> List[str]:
        nlp = _load_spacy(language)
        if nlp:
            doc = nlp(text)
            return [token.lemma_.lower() for token in doc
                    if not token.is_space and len(token.text) > 1]
        return re.findall(r'\b\w{2,}\b', text.lower())

    def tokenize_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def tokenize_ngrams(self, text: str, n: int = 2) -> List[str]:
        words = re.findall(r'\b\w{2,}\b', text.lower())
        return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]

    def get_statistics(self, text: str) -> Dict:
        words = re.findall(r'\b\w{2,}\b', text.lower())
        sentences = self.tokenize_sentences(text)
        return {
            'nb_words': len(words),
            'nb_sentences': len(sentences),
            'nb_chars': len(text),
            'vocabulary_size': len(set(words)),
            'avg_word_length': round(sum(len(w) for w in words) / len(words), 2) if words else 0,
            'avg_sentence_length': round(len(words) / len(sentences), 2) if sentences else 0,
            'most_common_words': Counter(words).most_common(10),
        }


class TextPreprocessor:
    """Pipeline complet : Détection langue → Nettoyage → Stopwords → Tokenisation."""

    def __init__(self):
        self.detector = LanguageDetector()
        self.cleaner = TextCleaner()
        self.tokenizer = Tokenizer()

    def process(self, text: str,
                clean_options: Optional[Dict] = None,
                detect_language: bool = True,
                remove_stopwords: bool = True) -> Dict:

        result = {'original_text': text, 'original_length': len(text)}

        if detect_language:
            lang_info = self.detector.detect(text)
            result['language'] = lang_info['language']
            result['language_confidence'] = lang_info['confidence']
        else:
            result['language'] = 'fr'
            result['language_confidence'] = 1.0

        cleaned = self.cleaner.clean(text, clean_options)

        if remove_stopwords:
            cleaned = self.cleaner.remove_stopwords(cleaned, result['language'])

        result['cleaned_text'] = cleaned
        result['cleaned_length'] = len(cleaned)
        result['tokens'] = self.tokenizer.tokenize_words(cleaned, result['language'])
        result['sentences'] = self.tokenizer.tokenize_sentences(cleaned)
        result['statistics'] = self.tokenizer.get_statistics(cleaned)

        return result

    def clean_translated(self, text: str) -> str:
        """
        Nettoyage post-traduction anglaise.
        Supprime les stopwords anglais étendus du texte traduit
        pour améliorer la qualité des mots-clés dans l'analyse des clusters.
        Appelé dans clustering.py après translation.py.
        """
        return self.cleaner.remove_english_stopwords(text)


def preprocess_text(text: str, **kwargs) -> Dict:
    return TextPreprocessor().process(text, **kwargs)


if __name__ == "__main__":
    samples = [
        "KPMG Algeria est une entreprise de conseil très reconnue ! https://kpmg.com #audit @kpmg",
        "KPMG Algeria is a highly recognized consulting firm with excellent services.",
        "شركة KPMG الجزائر معروفة جداً في مجال الاستشارات المالية والتدقيق.",
        "KPMG Algerien ist ein anerkanntes Beratungsunternehmen im Bereich Wirtschaftsprüfung.",
        "KPMG Argelia es una empresa de consultoría reconocida en auditoría y finanzas.",
    ]

    preprocessor = TextPreprocessor()
    print("=" * 65)
    print("TEST PREPROCESSING — DUE DILIGENCE KPMG")
    print("=" * 65)

    for text in samples:
        result = preprocessor.process(text)
        print(f"\nOriginal  : {text[:70]}")
        print(f"Langue    : {result['language']} ({result['language_confidence']:.0%})")
        print(f"Nettoyé   : {result['cleaned_text'][:70]}")
        print(f"Tokens    : {result['tokens'][:8]}")

    # Test nettoyage post-traduction
    print("\n--- Test nettoyage post-traduction ---")
    translated = "the consulting firm is recognized for its high quality audit services and compliance"
    cleaned = preprocessor.clean_translated(translated)
    print(f"Avant : {translated}")
    print(f"Après : {cleaned}")