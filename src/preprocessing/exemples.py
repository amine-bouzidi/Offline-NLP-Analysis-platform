"""
Exemples pratiques d'utilisation du module preprocessing
"""

from preprocessing import (
    preprocess_text, 
    TextPreprocessor, 
    LanguageDetector, 
    TextCleaner, 
    Tokenizer
)


def exemple_1_utilisation_simple():
    """Exemple basique d'utilisation"""
    print("\n" + "="*60)
    print("EXEMPLE 1 : Utilisation simple")
    print("="*60)
    
    text = """
    Découvrez notre nouvelle offre sur https://www.example.com !
    Contactez-nous à contact@example.com pour plus d'informations.
    Prix exceptionnels : 299€ au lieu de 499€ !!!
    """
    
    print(f"\nTexte original:\n{text}")
    
    result = preprocess_text(text, remove_stopwords=True)
    
    print(f"\nRésultats:")
    print(f"  Langue détectée: {result['language']} (confiance: {result['language_confidence']:.1%})")
    print(f"  Texte nettoyé: {result['cleaned_text'][:100]}...")
    print(f"  Nombre de mots: {len(result['tokens'])}")
    print(f"  Mots (sans stopwords): {result['tokens']}")


def exemple_2_detection_multilingue():
    """Détection de langue sur plusieurs textes"""
    print("\n" + "="*60)
    print("EXEMPLE 2 : Détection multilingue")
    print("="*60)
    
    texts = {
        'fr': "La programmation Python est très populaire dans le domaine de l'intelligence artificielle.",
        'en': "Python programming is very popular in the field of artificial intelligence.",
        'es': "La programación Python es muy popular en el campo de la inteligencia artificial.",
        'de': "Python-Programmierung ist im Bereich der künstlichen Intelligenz sehr beliebt.",
        'ar': "برمجة بايثون شائعة جدًا في مجال الذكاء الاصطناعي."
    }
    
    detector = LanguageDetector()
    
    print("\nDétection de langue pour différents textes:")
    for expected_lang, text in texts.items():
        result = detector.detect(text)
        status = "✓" if result['language'] == expected_lang else "✗"
        print(f"{status} {expected_lang}: {result['language']} (conf: {result['confidence']:.1%})")
        print(f"   Texte: {text[:60]}...")


def exemple_3_nettoyage_options():
    """Différentes options de nettoyage"""
    print("\n" + "="*60)
    print("EXEMPLE 3 : Options de nettoyage")
    print("="*60)
    
    text = "Visitez https://example.com! Email: test@email.com. Prix: 99.99€. Tél: 01-23-45-67-89."
    
    cleaner = TextCleaner()
    
    print(f"\nTexte original:\n  {text}")
    
    # Option 1 : Nettoyage standard
    print("\n1. Nettoyage standard:")
    cleaned = cleaner.clean(text)
    print(f"   {cleaned}")
    
    # Option 2 : Garder les URLs et emails
    print("\n2. Garder URLs et emails:")
    cleaned = cleaner.clean(text, {'remove_urls': False, 'remove_emails': False})
    print(f"   {cleaned}")
    
    # Option 3 : Supprimer aussi la ponctuation
    print("\n3. Supprimer aussi la ponctuation:")
    cleaned = cleaner.clean(text, {'remove_punctuation': True})
    print(f"   {cleaned}")
    
    # Option 4 : Supprimer les chiffres
    print("\n4. Supprimer les chiffres:")
    cleaned = cleaner.clean(text, {'remove_numbers': True})
    print(f"   {cleaned}")
    
    # Option 5 : Garder les majuscules
    print("\n5. Garder les majuscules:")
    cleaned = cleaner.clean(text, {'lowercase': False})
    print(f"   {cleaned}")


def exemple_4_tokenisation_avancee():
    """Tokenisation et n-grammes"""
    print("\n" + "="*60)
    print("EXEMPLE 4 : Tokenisation avancée")
    print("="*60)
    
    text = """
    L'intelligence artificielle et le machine learning transforment 
    profondément notre société. Les algorithmes deviennent de plus 
    en plus sophistiqués.
    """
    
    tokenizer = Tokenizer()
    
    # Tokenisation par mots
    words = tokenizer.tokenize_words(text)
    print(f"\n1. Mots ({len(words)} tokens):")
    print(f"   {words[:10]}")
    
    # Tokenisation par phrases
    sentences = tokenizer.tokenize_sentences(text)
    print(f"\n2. Phrases ({len(sentences)} phrases):")
    for i, sentence in enumerate(sentences, 1):
        print(f"   {i}. {sentence}")
    
    # Bigrams
    bigrams = tokenizer.tokenize_ngrams(text, n=2)
    print(f"\n3. Bigrams (n=2):")
    print(f"   {bigrams[:5]}")
    
    # Trigrams
    trigrams = tokenizer.tokenize_ngrams(text, n=3)
    print(f"\n4. Trigrams (n=3):")
    print(f"   {trigrams[:5]}")
    
    # Statistiques
    stats = tokenizer.get_statistics(text)
    print(f"\n5. Statistiques:")
    print(f"   Mots: {stats['nb_words']}")
    print(f"   Phrases: {stats['nb_sentences']}")
    print(f"   Vocabulaire: {stats['vocabulary_size']} mots uniques")
    print(f"   Longueur moyenne mots: {stats['avg_word_length']:.1f} caractères")
    print(f"   Longueur moyenne phrases: {stats['avg_sentence_length']:.1f} mots")
    print(f"   Mots fréquents: {stats['most_common_words'][:5]}")


def exemple_5_pipeline_corpus():
    """Pipeline complet sur un mini-corpus"""
    print("\n" + "="*60)
    print("EXEMPLE 5 : Pipeline sur un corpus")
    print("="*60)
    
    corpus = [
        "L'intelligence artificielle révolutionne le monde de la technologie.",
        "Les robots et l'automatisation changent le marché du travail.",
        "La protection des données personnelles devient un enjeu majeur.",
        "L'énergie renouvelable est essentielle pour l'avenir de notre planète."
    ]
    
    preprocessor = TextPreprocessor()
    
    print(f"\nTraitement de {len(corpus)} textes...")
    
    results = []
    all_tokens = []
    
    for i, text in enumerate(corpus, 1):
        result = preprocessor.process(text, remove_stopwords=True)
        results.append(result)
        all_tokens.extend(result['tokens'])
        
        print(f"\nTexte {i}:")
        print(f"  Original: {text[:60]}...")
        print(f"  Langue: {result['language']}")
        print(f"  Tokens: {result['tokens'][:8]}")
        print(f"  Mots: {len(result['tokens'])}")
    
    # Analyse globale
    print("\n" + "-"*60)
    print("Analyse globale du corpus:")
    print(f"  Total mots: {len(all_tokens)}")
    print(f"  Vocabulaire unique: {len(set(all_tokens))}")
    print(f"  Diversité lexicale: {len(set(all_tokens))/len(all_tokens):.2%}")
    
    # Mots les plus fréquents du corpus
    from collections import Counter
    word_freq = Counter(all_tokens)
    print(f"  Mots les plus fréquents:")
    for word, count in word_freq.most_common(5):
        print(f"    - {word}: {count}")


def exemple_6_comparaison_langues():
    """Comparaison de textes dans différentes langues"""
    print("\n" + "="*60)
    print("EXEMPLE 6 : Comparaison de langues")
    print("="*60)
    
    texts = {
        'Français': "Les chats sont des animaux domestiques très populaires dans le monde entier.",
        'Anglais': "Cats are very popular domestic animals all around the world.",
        'Espagnol': "Los gatos son animales domésticos muy populares en todo el mundo.",
    }
    
    preprocessor = TextPreprocessor()
    
    print("\nComparaison des caractéristiques linguistiques:\n")
    print(f"{'Langue':<12} {'Mots':<8} {'Vocab':<8} {'Moy/mot':<10} {'Phrases'}")
    print("-" * 60)
    
    for lang_name, text in texts.items():
        result = preprocessor.process(text, remove_stopwords=False)
        stats = result['statistics']
        
        print(f"{lang_name:<12} {stats['nb_words']:<8} {stats['vocabulary_size']:<8} "
              f"{stats['avg_word_length']:<10.1f} {stats['nb_sentences']}")


def exemple_7_analyse_sentiment_simple():
    """Analyse simple basée sur des mots-clés"""
    print("\n" + "="*60)
    print("EXEMPLE 7 : Analyse de sentiment simple")
    print("="*60)
    
    # Mots-clés positifs et négatifs
    positive_words = {'excellent', 'super', 'génial', 'parfait', 'formidable', 
                     'magnifique', 'extraordinaire', 'merveilleux'}
    negative_words = {'mauvais', 'horrible', 'terrible', 'nul', 'médiocre',
                     'décevant', 'catastrophique'}
    
    texts = [
        "Ce produit est excellent! Je le recommande vivement. Service parfait.",
        "Très décevant. Qualité médiocre et service horrible.",
        "C'est correct, ni génial ni terrible. Prix raisonnable."
    ]
    
    preprocessor = TextPreprocessor()
    
    print("\nAnalyse de sentiment basée sur mots-clés:\n")
    
    for i, text in enumerate(texts, 1):
        result = preprocessor.process(text, remove_stopwords=False)
        tokens = set(result['tokens'])
        
        pos_count = len(tokens & positive_words)
        neg_count = len(tokens & negative_words)
        
        if pos_count > neg_count:
            sentiment = "POSITIF +"
        elif neg_count > pos_count:
            sentiment = "NÉGATIF -"
        else:
            sentiment = "NEUTRE ="
        
        print(f"Texte {i}: {sentiment}")
        print(f"  {text}")
        print(f"  Mots positifs: {pos_count}, Mots négatifs: {neg_count}\n")


def exemple_8_extraction_mots_cles():
    """Extraction de mots-clés par fréquence"""
    print("\n" + "="*60)
    print("EXEMPLE 8 : Extraction de mots-clés")
    print("="*60)
    
    text = """
    L'intelligence artificielle et le machine learning sont des technologies
    qui transforment notre société. L'intelligence artificielle permet
    d'automatiser de nombreuses tâches. Le machine learning est une branche
    de l'intelligence artificielle qui utilise des algorithmes pour apprendre
    à partir de données. Ces technologies d'intelligence artificielle ont
    de nombreuses applications dans différents domaines.
    """
    
    preprocessor = TextPreprocessor()
    result = preprocessor.process(text, remove_stopwords=True)
    
    print(f"\nTexte analysé ({len(result['tokens'])} mots après nettoyage):")
    print(f"  {text[:100]}...\n")
    
    # Extraire les mots-clés (mots les plus fréquents)
    from collections import Counter
    word_freq = Counter(result['tokens'])
    
    print("Mots-clés extraits (par fréquence):")
    for i, (word, count) in enumerate(word_freq.most_common(10), 1):
        bar = "█" * count
        print(f"  {i:2}. {word:<20} {bar} ({count})")


def main():
    """Exécuter tous les exemples"""
    print("\n" + "="*60)
    print("EXEMPLES PRATIQUES - MODULE PREPROCESSING")
    print("="*60)
    
    exemples = [
        exemple_1_utilisation_simple,
        exemple_2_detection_multilingue,
        exemple_3_nettoyage_options,
        exemple_4_tokenisation_avancee,
        exemple_5_pipeline_corpus,
        exemple_6_comparaison_langues,
        exemple_7_analyse_sentiment_simple,
        exemple_8_extraction_mots_cles
    ]
    
    for exemple in exemples:
        try:
            exemple()
        except Exception as e:
            print(f"\nErreur dans {exemple.__name__}: {e}")
    
    print("\n" + "="*60)
    print("FIN DES EXEMPLES")
    print("="*60)
    print("\nPour plus d'informations, consultez le README.md")


if __name__ == "__main__":
    main()
