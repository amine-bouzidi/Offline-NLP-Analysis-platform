"""
translation.py
Module de traduction multilingue vers l'anglais via Helsinki-NLP (MarianMT)
Modèles locaux — 100% offline après le premier téléchargement

Modèles utilisés :
  FR → EN : Helsinki-NLP/opus-mt-fr-en
  DE → EN : Helsinki-NLP/opus-mt-de-en
  ES → EN : Helsinki-NLP/opus-mt-es-en
  AR → EN : Helsinki-NLP/opus-mt-ar-en

Premier lancement : téléchargement automatique (~300 MB par modèle)
Lancements suivants : lecture depuis le cache HuggingFace (~/.cache/huggingface)
"""

import os
import time
import json
from typing import List, Dict, Optional

import torch
from transformers import MarianMTModel, MarianTokenizer


# ─────────────────────────────────────────────────────────────────
# CONFIGURATION DES MODÈLES
# ─────────────────────────────────────────────────────────────────

# Mapping langue → nom du modèle HuggingFace
MODEL_MAP = {
    'fr': 'Helsinki-NLP/opus-mt-fr-en',
    'de': 'Helsinki-NLP/opus-mt-de-en',
    'es': 'Helsinki-NLP/opus-mt-es-en',
    'ar': 'Helsinki-NLP/opus-mt-ar-en',
    'en': None,   # Pas besoin de traduction
}

# Langues prises en charge
SUPPORTED_LANGS = set(MODEL_MAP.keys())


# ─────────────────────────────────────────────────────────────────
# CLASSE PRINCIPALE
# ─────────────────────────────────────────────────────────────────

class Translator:
    """
    Traducteur multilingue → anglais basé sur Helsinki-NLP MarianMT.

    Les modèles sont chargés à la demande (lazy loading) et mis en cache
    en mémoire pour éviter de les recharger à chaque appel.

    Usage :
        translator = Translator()
        result = translator.translate("Le cabinet a commis des erreurs.", src_lang='fr')
        print(result['translated_text'])

        # Traduire tout un corpus
        translated_corpus = translator.translate_corpus(corpus_items)
    """

    def __init__(self, cache_dir: Optional[str] = None, device: str = 'auto'):
        """
        Args:
            cache_dir : répertoire de cache des modèles (None = défaut HuggingFace)
            device    : 'auto' détecte GPU/CPU, 'cpu' force le CPU
        """
        self.cache_dir = cache_dir

        # Sélection du device
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        print(f"[Translator] Device : {self.device.upper()}")

        # Cache des modèles chargés en mémoire {lang: (tokenizer, model)}
        self._model_cache: Dict[str, tuple] = {}

    # ── Chargement des modèles ──────────────────────────────────

    def _load_model(self, src_lang: str) -> tuple:
        """
        Charge (et met en cache mémoire) le modèle pour une langue source.

        Args:
            src_lang : code langue ('fr', 'de', 'es', 'ar')

        Returns:
            (tokenizer, model)
        """
        if src_lang in self._model_cache:
            return self._model_cache[src_lang]

        model_name = MODEL_MAP.get(src_lang)
        if model_name is None:
            raise ValueError(f"Langue '{src_lang}' non prise en charge ou pas besoin de traduction.")

        print(f"[Translator] Chargement du modèle {model_name}...")
        print(f"             (Premier lancement = téléchargement ~300 MB, ensuite depuis cache)")

        start = time.time()
        tokenizer = MarianTokenizer.from_pretrained(
            model_name,
            cache_dir=self.cache_dir
        )
        model = MarianMTModel.from_pretrained(
            model_name,
            cache_dir=self.cache_dir
        ).to(self.device)
        model.eval()   # Mode inférence uniquement

        elapsed = time.time() - start
        print(f"[Translator] ✓ Modèle {src_lang}→EN chargé en {elapsed:.1f}s")

        self._model_cache[src_lang] = (tokenizer, model)
        return tokenizer, model

    def preload_models(self, languages: List[str]) -> None:
        """
        Pré-charge tous les modèles pour une liste de langues.
        Utile pour éviter les délais pendant le traitement du corpus.

        Args:
            languages : liste de codes langues (['fr', 'de', 'es', 'ar'])
        """
        print(f"[Translator] Pré-chargement des modèles pour : {languages}")
        for lang in languages:
            if lang != 'en' and lang in MODEL_MAP:
                self._load_model(lang)
        print("[Translator] ✓ Tous les modèles sont prêts.")

    # ── Traduction d'un texte ───────────────────────────────────

    def translate(self, text: str, src_lang: str,
                  max_length: int = 512,
                  batch_size: int = 1) -> Dict:
        """
        Traduit un texte vers l'anglais.

        Args:
            text       : texte source
            src_lang   : langue source ('fr', 'de', 'es', 'ar', 'en')
            max_length : longueur maximale de la sortie (tokens)
            batch_size : taille du batch (1 = un seul texte)

        Returns:
            {
              'original_text'  : str,
              'translated_text': str,
              'src_lang'       : str,
              'was_translated' : bool
            }
        """
        # Texte anglais : pas de traduction nécessaire
        if src_lang == 'en':
            return {
                'original_text': text,
                'translated_text': text,
                'src_lang': 'en',
                'was_translated': False
            }

        # Langue non supportée
        if src_lang not in MODEL_MAP:
            print(f"[Translator] ⚠ Langue '{src_lang}' non supportée — texte retourné tel quel.")
            return {
                'original_text': text,
                'translated_text': text,
                'src_lang': src_lang,
                'was_translated': False
            }

        tokenizer, model = self._load_model(src_lang)

        # Tokenisation
        # MarianMT supporte des textes longs grâce au truncation
        inputs = tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512      # Limite du modèle MarianMT
        ).to(self.device)

        # Génération de la traduction
        with torch.no_grad():
            translated_ids = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,            # Beam search pour meilleure qualité
                early_stopping=True
            )

        translated_text = tokenizer.decode(
            translated_ids[0],
            skip_special_tokens=True
        )

        return {
            'original_text': text,
            'translated_text': translated_text,
            'src_lang': src_lang,
            'was_translated': True
        }

    # ── Traduction par batch ─────────────────────────────────────

    def translate_batch(self, texts: List[str], src_lang: str,
                        max_length: int = 512) -> List[str]:
        """
        Traduit une liste de textes de la même langue en batch (plus rapide).

        Args:
            texts     : liste de textes source
            src_lang  : langue source commune à tous les textes
            max_length: longueur max de sortie

        Returns:
            Liste de textes traduits en anglais
        """
        if src_lang == 'en':
            return texts

        if src_lang not in MODEL_MAP:
            return texts

        tokenizer, model = self._load_model(src_lang)

        inputs = tokenizer(
            texts,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            translated_ids = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True
            )

        return [
            tokenizer.decode(ids, skip_special_tokens=True)
            for ids in translated_ids
        ]

    # ── Traduction d'un corpus complet ───────────────────────────

    def translate_corpus(self, corpus: List[Dict],
                          text_field: str = 'text',
                          lang_field: str = 'language',
                          batch_size: int = 8,
                          save_cache: Optional[str] = None) -> List[Dict]:
        """
        Traduit tout un corpus en anglais, langue par langue (efficacité maximale).

        Args:
            corpus     : liste de dicts avec champs text et language
            text_field : nom du champ texte dans chaque dict
            lang_field : nom du champ langue dans chaque dict
            batch_size : nombre de textes traités en parallèle par batch
            save_cache : si fourni, sauvegarde le corpus traduit en JSON

        Returns:
            Liste de dicts avec champ 'translated_text' ajouté
        """
        print(f"\n[Translator] Traduction de {len(corpus)} documents vers l'anglais...")

        # Grouper les textes par langue pour le batch processing
        by_lang: Dict[str, List[int]] = {}
        for i, item in enumerate(corpus):
            lang = item.get(lang_field, 'unknown')
            by_lang.setdefault(lang, []).append(i)

        print(f"[Translator] Répartition par langue :")
        for lang, indices in sorted(by_lang.items()):
            status = "→ traduction" if lang != 'en' else "→ déjà EN"
            print(f"  {lang.upper():4s} : {len(indices):3d} textes {status}")

        # Copie du corpus avec champ 'translated_text' initialisé
        result = [dict(item) for item in corpus]
        for item in result:
            item['translated_text'] = item.get(text_field, '')
            item['was_translated'] = False

        total_translated = 0
        start_total = time.time()

        # Traitement langue par langue
        for lang, indices in sorted(by_lang.items()):
            if lang == 'en':
                # Anglais : pas de traduction, juste copier
                for i in indices:
                    result[i]['translated_text'] = result[i][text_field]
                    result[i]['was_translated'] = False
                continue

            if lang not in MODEL_MAP:
                print(f"[Translator] ⚠ Langue '{lang}' ignorée (modèle non disponible).")
                continue

            print(f"\n[Translator] Traduction {lang.upper()}→EN ({len(indices)} textes)...")
            start_lang = time.time()

            # Traitement par batches
            for batch_start in range(0, len(indices), batch_size):
                batch_indices = indices[batch_start:batch_start + batch_size]
                batch_texts = [corpus[i][text_field] for i in batch_indices]

                translated_texts = self.translate_batch(batch_texts, src_lang=lang)

                for i, translated in zip(batch_indices, translated_texts):
                    result[i]['translated_text'] = translated
                    result[i]['was_translated'] = True

                done = batch_start + len(batch_indices)
                print(f"  {done}/{len(indices)} textes traduits...", end='\r')

            elapsed_lang = time.time() - start_lang
            total_translated += len(indices)
            print(f"  ✓ {len(indices)} textes traduits en {elapsed_lang:.1f}s        ")

        elapsed_total = time.time() - start_total
        print(f"\n[Translator] ✓ Traduction terminée : {total_translated} textes en {elapsed_total:.1f}s")

        # Sauvegarde cache JSON si demandé
        if save_cache:
            self._save_cache(result, save_cache)

        return result

    def _save_cache(self, corpus: List[Dict], filepath: str) -> None:
        """Sauvegarde le corpus traduit en JSON pour éviter de retraduire."""
        # Exclure les champs non sérialisables si nécessaire
        serializable = []
        for item in corpus:
            serializable.append({
                k: v for k, v in item.items()
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
            })
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        print(f"[Translator] Cache sauvegardé → {filepath}")

    @staticmethod
    def load_cache(filepath: str) -> List[Dict]:
        """
        Charge un corpus traduit depuis un fichier JSON cache.
        Évite de relancer la traduction si déjà faite.

        Returns:
            Liste de dicts du corpus traduit
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        print(f"[Translator] Cache chargé : {len(corpus)} documents depuis {filepath}")
        return corpus


# ─────────────────────────────────────────────────────────────────
# PIPELINE COMPLET : Corpus → Traduction → Preprocessing
# ─────────────────────────────────────────────────────────────────

def build_translated_corpus(corpus: List[Dict],
                             batch_size: int = 8,
                             cache_file: Optional[str] = 'translated_corpus_cache.json',
                             force_retranslate: bool = False) -> List[Dict]:
    """
    Pipeline complet : détecte si un cache existe, sinon traduit et sauvegarde.

    Args:
        corpus           : corpus brut (liste de dicts avec 'text' et 'language')
        batch_size       : taille des batches de traduction
        cache_file       : chemin du fichier cache JSON
        force_retranslate: ignore le cache et retraduit tout

    Returns:
        Corpus avec champ 'translated_text' (textes EN uniformes)
    """
    # Vérifier si un cache existe
    if cache_file and os.path.exists(cache_file) and not force_retranslate:
        print(f"[Pipeline] Cache détecté : {cache_file}")
        print(f"[Pipeline] Chargement depuis le cache (évite de retradire)...")
        return Translator.load_cache(cache_file)

    # Sinon : traduire
    translator = Translator()
    translated = translator.translate_corpus(
        corpus,
        batch_size=batch_size,
        save_cache=cache_file
    )
    return translated


def get_english_texts(translated_corpus: List[Dict],
                       use_translated: bool = True) -> List[str]:
    """
    Extrait la liste de textes anglais depuis un corpus traduit.

    Args:
        translated_corpus : corpus avec champ 'translated_text'
        use_translated    : si True, utilise 'translated_text', sinon 'text'

    Returns:
        Liste de chaînes anglaises
    """
    field = 'translated_text' if use_translated else 'text'
    return [item.get(field, item.get('text', '')) for item in translated_corpus]


# ─────────────────────────────────────────────────────────────────
# DÉMONSTRATION
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    from corpus_kpmg import get_corpus, get_corpus_statistics

    corpus = get_corpus()
    stats = get_corpus_statistics()

    print("=" * 60)
    print("DÉMONSTRATION — translation.py")
    print("=" * 60)
    print(f"\nCorpus KPMG : {stats['total']} textes")
    print(f"Langues : {stats['by_language']}")

    # ── Test sur un échantillon de chaque langue ───────────────
    print("\n--- Test traduction sur 1 texte par langue ---\n")

    samples = {
        lang: next(item for item in corpus if item['language'] == lang)
        for lang in ['fr', 'de', 'es', 'ar', 'en']
    }

    translator = Translator()

    for lang, item in samples.items():
        print(f"[{lang.upper()}] Original :")
        print(f"  {item['text'][:120]}...")
        result = translator.translate(item['text'], src_lang=lang)
        if result['was_translated']:
            print(f"  → EN : {result['translated_text'][:120]}...")
        else:
            print(f"  → (déjà en anglais)")
        print()

    # ── Traduction complète du corpus ──────────────────────────
    print("\n--- Traduction du corpus complet ---")
    translated = build_translated_corpus(
        corpus,
        batch_size=8,
        cache_file='translated_corpus_cache.json'
    )

    # Vérification
    en_count = sum(1 for item in translated if not item.get('was_translated'))
    translated_count = sum(1 for item in translated if item.get('was_translated'))
    print(f"\n  Textes déjà EN : {en_count}")
    print(f"  Textes traduits : {translated_count}")

    # Aperçu
    print("\n--- Aperçu de 3 traductions ---")
    examples = [item for item in translated if item.get('was_translated')][:3]
    for item in examples:
        print(f"\n  [{item['language'].upper()} → EN] Catégorie: {item['category']}")
        print(f"  Original   : {item['text'][:80]}...")
        print(f"  Traduit    : {item['translated_text'][:80]}...")

    print("\n✓ translation.py prêt — prochaine étape : intégrer dans le pipeline LDA/NMF")