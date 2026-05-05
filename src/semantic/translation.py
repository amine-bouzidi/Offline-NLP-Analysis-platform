"""
translation.py
Module de traduction multilingue vers l'anglais
Langues supportées : FR, AR, DE, ES → EN
"""

import os
from typing import Dict, List
from transformers import MarianMTModel, MarianTokenizer

# Configuration des modèles
TRANSLATION_MODELS = {
    'fr': 'Helsinki-NLP/opus-mt-fr-en',
    'ar': 'Helsinki-NLP/opus-mt-ar-en',
    'de': 'Helsinki-NLP/opus-mt-de-en',
    'es': 'Helsinki-NLP/opus-mt-es-en',
}

class Translator:
    """
    Traducteur multilingue vers l'anglais pour la Due Diligence KPMG.
    Utilise MarianMTModel et MarianTokenizer de manière explicite.
    """

    def __init__(self):
        self._models: Dict[str, MarianMTModel] = {}
        self._tokenizers: Dict[str, MarianTokenizer] = {}

    def _load_model(self, lang: str):
        """Charge le modèle et le tokenizer avec gestion d'erreur SentencePiece."""
        if lang not in self._models:
            model_name = TRANSLATION_MODELS.get(lang)
            if not model_name:
                return None, None
            
            print(f"  [Translation] Préparation du modèle {lang} ({model_name})...")
            
            try:
                # Chargement explicite du Tokenizer
                # On force use_fast=False pour garantir la compatibilité
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                
                self._tokenizers[lang] = tokenizer
                self._models[lang] = model
                
                print(f"  [Translation] Modèle {lang} chargé avec succès ✓")
                
            except ImportError as e:
                if "sentencepiece" in str(e).lower():
                    print("\n" + "!"*60)
                    print("ERREUR CRITIQUE : La librairie 'sentencepiece' est manquante ou mal liée.")
                    print("Action requise :")
                    print("1. pip install sentencepiece sacremoses")
                    print("2. Installez Visual C++ Redistributable : https://aka.ms/vs/17/release/vc_redist.x64.exe")
                    print("3. REDÉMARREZ votre PC.")
                    print("!"*60 + "\n")
                raise e
            except Exception as e:
                print(f"  [Translation] Erreur lors du chargement de {lang}: {str(e)}")
                return None, None
                
        return self._models[lang], self._tokenizers[lang]

    def translate(self, text: str, source_lang: str) -> Dict:
        """Traduit un texte unique vers l'anglais."""

        if not text or not text.strip():
            return {'original_text': text, 'translated_text': text, 'source_lang': source_lang, 'translated': False, 'status': 'empty'}

        if source_lang == 'en':
            return {'original_text': text, 'translated_text': text, 'source_lang': 'en', 'translated': False, 'status': 'already_english'}

        if source_lang not in TRANSLATION_MODELS:
            return {'original_text': text, 'translated_text': text, 'source_lang': source_lang, 'translated': False, 'status': f'unsupported_{source_lang}'}

        try:
            model, tokenizer = self._load_model(source_lang)
            if not model or not tokenizer:
                raise ValueError("Modèle ou Tokenizer non disponible.")

            # Tokenisation et Génération
            inputs = tokenizer(text[:512], return_tensors="pt", padding=True, truncation=True)
            translated_tokens = model.generate(**inputs)
            translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

            return {
                'original_text': text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'translated': True,
                'status': 'success'
            }

        except Exception as e:
            return {
                'original_text': text,
                'translated_text': text,
                'source_lang': source_lang,
                'translated': False,
                'status': f'error: {str(e)}'
            }

    def translate_corpus(self, corpus: List[Dict], text_key: str = 'cleaned_text', lang_key: str = 'language') -> List[Dict]:
        """Traduit un ensemble de documents avec suivi de progression."""
        print(f"\n[Translation] Début de la traduction du corpus ({len(corpus)} docs)")
        
        enriched = []
        for i, doc in enumerate(corpus):
            text = doc.get(text_key, '')
            lang = doc.get(lang_key, 'unknown')
            
            res = self.translate(text, lang)
            
            new_doc = {**doc}
            new_doc['translated_text'] = res['translated_text']
            new_doc['was_translated'] = res['translated']
            new_doc['translation_status'] = res['status']
            enriched.append(new_doc)
            
            if (i + 1) % 5 == 0:
                print(f"  [Translation] Progress: {i+1}/{len(corpus)}")
                
        return enriched

if __name__ == "__main__":
    # Test unitaire rapide
    translator = Translator()
    test_fr = "KPMG est un réseau mondial de services professionnels."
    print(f"Test FR -> EN : {translator.translate(test_fr, 'fr')['translated_text']}")