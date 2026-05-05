"""
Script de test du module preprocessing avec affichage du texte nettoyé
VERSION CORRIGÉE: Fix de l'erreur KeyError 'nb_tokens'
"""

import json
from preprocessing import TextPreprocessor, LanguageDetector, TextCleaner, Tokenizer
from test_corpus import get_corpus, get_corpus_statistics, get_corpus_by_language


def test_language_detection():
    """Test de la détection de langue sur tout le corpus"""
    print("\n" + "="*70)
    print("TEST 1: DÉTECTION DE LANGUE")
    print("="*70)
    
    corpus = get_corpus()
    detector = LanguageDetector()
    
    correct = 0
    total = 0
    errors = []
    
    for item in corpus:
        expected_lang = item['language']
        detected = detector.detect(item['text'])
        detected_lang = detected['language']
        confidence = detected['confidence']
        
        total += 1
        if detected_lang == expected_lang:
            correct += 1
        else:
            errors.append({
                'id': item['id'],
                'expected': expected_lang,
                'detected': detected_lang,
                'confidence': confidence,
                'text': item['text'][:60] + "..."
            })
    
    accuracy = (correct / total) * 100
    
    print(f"\nRésultats globaux:")
    print(f"  Total de textes: {total}")
    print(f"  Détections correctes: {correct}")
    print(f"  Détections incorrectes: {total - correct}")
    print(f"  Précision: {accuracy:.1f}%")
    
    if errors:
        print(f"\nErreurs de détection ({len(errors)}):")
        for error in errors[:5]:  # Afficher max 5 erreurs
            print(f"  - ID {error['id']}: attendu={error['expected']}, "
                  f"détecté={error['detected']} (conf={error['confidence']:.2f})")
            print(f"    Texte: {error['text']}")
    
    return accuracy


def test_text_cleaning_DETAILED():
    """Test du nettoyage de texte AVEC AFFICHAGE DÉTAILLÉ"""
    print("\n" + "="*70)
    print("TEST 2: NETTOYAGE DE TEXTE (AVEC DÉTAILS)")
    print("="*70)
    
    corpus = get_corpus()
    cleaner = TextCleaner()
    
    print(f"\n📊 Traitement de {len(corpus)} textes...\n")
    
    # Afficher TOUS les textes avec avant/après
    for i, item in enumerate(corpus, 1):
        original = item['text']
        cleaned = cleaner.clean(original)
        
        print(f"\n{'─'*70}")
        print(f"Texte {i} (ID: {item['id']}) - Catégorie: {item['category']}")
        print(f"{'─'*70}")
        
        print(f"🔴 AVANT (Original):")
        print(f"   {original}")
        
        print(f"\n✅ APRÈS (Nettoyé):")
        print(f"   {cleaned}")
        
        reduction = len(original) - len(cleaned)
        reduction_percent = (reduction / len(original)) * 100 if len(original) > 0 else 0
        
        print(f"\n📈 Statistiques:")
        print(f"   Taille: {len(original)} → {len(cleaned)} caractères")
        print(f"   Réduction: {reduction} caractères ({reduction_percent:.1f}%)")
        
        # Analyser quoi a été supprimé
        if 'http' in original or 'www.' in original:
            print(f"   ✓ URLs supprimées")
        if '@' in original:
            print(f"   ✓ Emails supprimés")
        if any(c.isupper() for c in original) and all(c.islower() or not c.isalpha() for c in cleaned):
            print(f"   ✓ Convertis en minuscules")
    
    print(f"\n{'='*70}")
    print(f"✅ NETTOYAGE COMPLET: {len(corpus)} textes traités")
    print(f"{'='*70}")


def test_tokenization():
    """Test de la tokenisation"""
    print("\n" + "="*70)
    print("TEST 3: TOKENISATION")
    print("="*70)
    
    corpus = get_corpus()
    tokenizer = Tokenizer()
    
    # Statistiques globales
    total_words = 0
    total_sentences = 0
    total_vocabulary = set()
    
    print(f"\n📊 Analyse de {len(corpus)} textes...\n")
    
    for i, item in enumerate(corpus[:10], 1):  # Afficher détails pour les 10 premiers
        text = item['text']
        words = tokenizer.tokenize_words(text)
        sentences = tokenizer.tokenize_sentences(text)
        stats = tokenizer.get_statistics(text)
        
        total_words += len(words)
        total_sentences += len(sentences)
        total_vocabulary.update(words)
        
        print(f"\n{'─'*70}")
        print(f"Texte {i} (ID: {item['id']})")
        print(f"{'─'*70}")
        print(f"Original: {text[:80]}...")
        print(f"\n📊 Tokenisation:")
        print(f"   Mots: {stats['nb_words']}")
        print(f"   Phrases: {stats['nb_sentences']}")
        print(f"   Caractères: {stats['nb_chars']}")
        print(f"   Vocabulaire unique: {stats['vocabulary_size']}")
        print(f"   Longueur moyenne des mots: {stats['avg_word_length']:.1f}")
        print(f"   Longueur moyenne des phrases: {stats['avg_sentence_length']:.1f}")
        print(f"\n📝 Tokens: {words[:10]}")
        if len(words) > 10:
            print(f"   ... et {len(words) - 10} autres")
    
    print(f"\n{'='*70}")
    print("Statistiques globales du corpus:")
    print(f"{'='*70}")
    print(f"  Nombre total de mots: {total_words:,}")
    print(f"  Nombre total de phrases: {total_sentences}")
    print(f"  Taille du vocabulaire: {len(total_vocabulary):,} mots uniques")
    print(f"  Moyenne mots/texte: {total_words/len(corpus):.1f}")
    print(f"  Moyenne phrases/texte: {total_sentences/len(corpus):.1f}")


def test_full_pipeline_DETAILED():
    """Test du pipeline complet AVEC AFFICHAGE DÉTAILLÉ"""
    print("\n" + "="*70)
    print("TEST 4: PIPELINE COMPLET (AVEC DÉTAILS)")
    print("="*70)
    
    corpus = get_corpus()
    preprocessor = TextPreprocessor()
    
    results = []
    
    print(f"\n📊 Traitement de {len(corpus)} textes...\n")
    
    for i, item in enumerate(corpus, 1):
        result = preprocessor.process(
            item['text'],
            detect_language=True,
            remove_stopwords=True
        )
        
        results.append({
            'id': item['id'],
            'expected_lang': item['language'],
            'detected_lang': result['language'],
            'confidence': result['language_confidence'],
            'original_length': result['original_length'],
            'cleaned_length': result['cleaned_length'],
            'nb_tokens': len(result['tokens']),  # ✅ CORRIGÉ: Utiliser len() au lieu de result['nb_tokens']
            'nb_sentences': len(result['sentences']),  # ✅ CORRIGÉ: Utiliser len() au lieu de result['nb_sentences']
        })
        
        # Afficher TOUS les détails
        print(f"\n{'─'*70}")
        print(f"Texte {i}/{len(corpus)} (ID: {item['id']}) - {item['category']}")
        print(f"{'─'*70}")
        
        print(f"\n📝 ORIGINAL:")
        print(f"   {item['text']}")
        
        print(f"\n✅ NETTOYÉ:")
        print(f"   {result['cleaned_text']}")
        
        print(f"\n🌍 LANGUE:")
        status = "✓" if result['language'] == item['language'] else "✗"
        print(f"   {status} Attendue: {item['language']}")
        print(f"   {status} Détectée: {result['language']}")
        print(f"   Confiance: {result['language_confidence']:.1%}")
        
        # ✅ CORRIGÉ: Utiliser len(result['tokens']) au lieu de result['nb_tokens']
        print(f"\n📊 STATISTIQUES:")
        print(f"   Longueur: {result['original_length']} → {result['cleaned_length']} caractères (-{100 - int(result['cleaned_length']/result['original_length']*100)}%)")
        print(f"   Tokens: {len(result['tokens'])}")
        print(f"   Phrases: {len(result['sentences'])}")
        print(f"   Mots (sans stopwords): {result['tokens'][:8]}")
        if len(result['tokens']) > 8:
            print(f"   ... et {len(result['tokens']) - 8} autres")
    
    print(f"\n{'='*70}")
    print("RÉSUMÉ GLOBAL DU TRAITEMENT")
    print(f"{'='*70}")
    
    # Statistiques globales
    total_reduction = sum(r['original_length'] - r['cleaned_length'] for r in results)
    total_original = sum(r['original_length'] for r in results)
    avg_reduction = (total_reduction / total_original) * 100
    
    correct_detections = sum(1 for r in results if r['expected_lang'] == r['detected_lang'])
    detection_accuracy = (correct_detections / len(results)) * 100
    
    print(f"  Précision détection de langue: {detection_accuracy:.1f}%")
    print(f"  Réduction moyenne de taille: {avg_reduction:.1f}%")
    print(f"  Nombre moyen de tokens par texte: "
          f"{sum(r['nb_tokens'] for r in results) / len(results):.1f}")
    
    return results


def test_by_language():
    """Test des performances par langue"""
    print("\n" + "="*70)
    print("TEST 5: ANALYSE PAR LANGUE")
    print("="*70)
    
    corpus = get_corpus()
    preprocessor = TextPreprocessor()
    
    stats_by_lang = {}
    
    for item in corpus:
        lang = item['language']
        
        if lang not in stats_by_lang:
            stats_by_lang[lang] = {
                'count': 0,
                'correct_detections': 0,
                'total_words': 0,
                'total_vocab': set()
            }
        
        result = preprocessor.process(item['text'], detect_language=True)
        
        stats_by_lang[lang]['count'] += 1
        if result['language'] == lang:
            stats_by_lang[lang]['correct_detections'] += 1
        
        stats_by_lang[lang]['total_words'] += len(result['tokens'])
        stats_by_lang[lang]['total_vocab'].update(result['tokens'])
    
    print("\nStatistiques par langue:")
    for lang, stats in sorted(stats_by_lang.items()):
        accuracy = (stats['correct_detections'] / stats['count']) * 100
        avg_words = stats['total_words'] / stats['count']
        vocab_size = len(stats['total_vocab'])
        
        print(f"\n{lang.upper()}:")
        print(f"  Nombre de textes: {stats['count']}")
        print(f"  Précision détection: {accuracy:.1f}%")
        print(f"  Moyenne mots/texte: {avg_words:.1f}")
        print(f"  Taille vocabulaire: {vocab_size}")


def save_results(results, filename='preprocessing_results.json'):
    """Sauvegarde les résultats dans un fichier JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Résultats sauvegardés dans {filename}")


def main():
    """Fonction principale exécutant tous les tests"""
    print("="*70)
    print("TESTS DU MODULE PREPROCESSING - VERSION AMÉLIORÉE ET CORRIGÉE")
    print("Avec affichage détaillé du texte nettoyé")
    print("="*70)
    
    # Afficher les statistiques du corpus
    corpus_stats = get_corpus_statistics()
    print(f"\nStatistiques du corpus:")
    print(f"  Total: {corpus_stats['total_texts']} textes")
    print(f"  Langues: {dict(corpus_stats['languages'])}")
    print(f"  Catégories: {len(corpus_stats['categories'])} différentes")
    
    # Exécuter tous les tests
    test_language_detection()
    test_text_cleaning_DETAILED()
    test_tokenization()
    results = test_full_pipeline_DETAILED()
    test_by_language()
    
    # Sauvegarder les résultats
    save_results(results, filename=r'C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\outputs\reports\preprocessing_results.json')
    
    print("\n" + "="*70)
    print("✅ TESTS TERMINÉS AVEC SUCCÈS!")
    print("="*70)
    print("\nProchaines étapes:")
    print("  1. Analyser les résultats dans preprocessing_results.json")
    print("  2. Ajuster les paramètres si nécessaire")
    print("  3. Tester avec votre propre corpus")
    print("="*70)


if __name__ == "__main__":
    main()