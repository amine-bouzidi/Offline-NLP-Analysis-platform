"""
Corpus de test pour le module de prétraitement
Contient des textes en différentes langues et avec différentes caractéristiques
"""

CORPUS = [
    # Textes en français (10)
    {
        'id': 1,
        'language': 'fr',
        'text': "L'intelligence artificielle transforme notre société. Les algorithmes de machine learning permettent d'automatiser des tâches complexes.",
        'category': 'technology'
    },
    {
        'id': 2,
        'language': 'fr',
        'text': "Paris est la capitale de la France. La Tour Eiffel attire des millions de touristes chaque année. Le Louvre est le musée le plus visité au monde.",
        'category': 'geography'
    },
    {
        'id': 3,
        'language': 'fr',
        'text': "La cuisine française est réputée dans le monde entier. Le croissant, le fromage et le vin sont des symboles de la gastronomie française.",
        'category': 'culture'
    },
    {
        'id': 4,
        'language': 'fr',
        'text': "Le réchauffement climatique menace notre planète. Les émissions de CO2 doivent être réduites rapidement pour éviter une catastrophe écologique.",
        'category': 'environment'
    },
    {
        'id': 5,
        'language': 'fr',
        'text': "Victor Hugo est l'un des plus grands écrivains français. Les Misérables et Notre-Dame de Paris sont ses œuvres les plus célèbres.",
        'category': 'literature'
    },
    {
        'id': 6,
        'language': 'fr',
        'text': "Le football est le sport le plus populaire en France. L'équipe nationale a remporté la Coupe du Monde en 1998 et 2018.",
        'category': 'sports'
    },
    {
        'id': 7,
        'language': 'fr',
        'text': "La médecine moderne a fait des progrès considérables. Les vaccins ont permis d'éradiquer de nombreuses maladies mortelles.",
        'category': 'health'
    },
    {
        'id': 8,
        'language': 'fr',
        'text': "L'économie française est la troisième d'Europe. Le PIB par habitant est élevé mais les inégalités persistent.",
        'category': 'economy'
    },
    {
        'id': 9,
        'language': 'fr',
        'text': "L'éducation est un droit fondamental. L'école publique gratuite permet à tous d'accéder au savoir.",
        'category': 'education'
    },
    {
        'id': 10,
        'language': 'fr',
        'text': "Les réseaux sociaux ont changé notre façon de communiquer. Facebook, Twitter et Instagram comptent des milliards d'utilisateurs.",
        'category': 'technology'
    },
    
    # Textes en anglais (10)
    {
        'id': 11,
        'language': 'en',
        'text': "Artificial intelligence is revolutionizing the way we live and work. Machine learning algorithms can process vast amounts of data in seconds.",
        'category': 'technology'
    },
    {
        'id': 12,
        'language': 'en',
        'text': "London is the capital of England and the United Kingdom. The city is famous for Big Ben, the Tower Bridge, and Buckingham Palace.",
        'category': 'geography'
    },
    {
        'id': 13,
        'language': 'en',
        'text': "William Shakespeare is considered the greatest playwright in the English language. His works include Hamlet, Romeo and Juliet, and Macbeth.",
        'category': 'literature'
    },
    {
        'id': 14,
        'language': 'en',
        'text': "Climate change is one of the biggest challenges facing humanity. Rising temperatures are causing ice caps to melt and sea levels to rise.",
        'category': 'environment'
    },
    {
        'id': 15,
        'language': 'en',
        'text': "The internet has connected people across the globe. Social media platforms allow instant communication with anyone, anywhere.",
        'category': 'technology'
    },
    {
        'id': 16,
        'language': 'en',
        'text': "Basketball was invented in 1891 by James Naismith. The NBA is the most prestigious basketball league in the world.",
        'category': 'sports'
    },
    {
        'id': 17,
        'language': 'en',
        'text': "The human brain contains approximately 86 billion neurons. Neuroscience is helping us understand how the brain works.",
        'category': 'science'
    },
    {
        'id': 18,
        'language': 'en',
        'text': "Renewable energy sources like solar and wind power are becoming more affordable. They offer a sustainable alternative to fossil fuels.",
        'category': 'environment'
    },
    {
        'id': 19,
        'language': 'en',
        'text': "The stock market can be volatile and unpredictable. Investors should diversify their portfolios to minimize risk.",
        'category': 'economy'
    },
    {
        'id': 20,
        'language': 'en',
        'text': "Online education has made learning accessible to millions. MOOCs offer free courses from top universities around the world.",
        'category': 'education'
    },
    
    # Textes en espagnol (5)
    {
        'id': 21,
        'language': 'es',
        'text': "Madrid es la capital de España. El Museo del Prado es uno de los más importantes del mundo.",
        'category': 'geography'
    },
    {
        'id': 22,
        'language': 'es',
        'text': "Miguel de Cervantes escribió Don Quijote, una de las obras más importantes de la literatura española.",
        'category': 'literature'
    },
    {
        'id': 23,
        'language': 'es',
        'text': "El flamenco es un arte tradicional de Andalucía. Combina música, canto y baile.",
        'category': 'culture'
    },
    {
        'id': 24,
        'language': 'es',
        'text': "La paella es un plato típico de Valencia. Se prepara con arroz, azafrán y diversos ingredientes.",
        'category': 'culture'
    },
    {
        'id': 25,
        'language': 'es',
        'text': "El fútbol es el deporte más popular en España. El Real Madrid y el Barcelona son dos de los clubes más grandes del mundo.",
        'category': 'sports'
    },
    
    # Textes en allemand (5)
    {
        'id': 26,
        'language': 'de',
        'text': "Berlin ist die Hauptstadt von Deutschland. Die Stadt hat eine reiche Geschichte und Kultur.",
        'category': 'geography'
    },
    {
        'id': 27,
        'language': 'de',
        'text': "Johann Wolfgang von Goethe ist einer der bedeutendsten deutschen Dichter. Faust ist sein bekanntestes Werk.",
        'category': 'literature'
    },
    {
        'id': 28,
        'language': 'de',
        'text': "Das Oktoberfest in München ist das größte Volksfest der Welt. Millionen von Menschen besuchen es jedes Jahr.",
        'category': 'culture'
    },
    {
        'id': 29,
        'language': 'de',
        'text': "Die deutsche Autoindustrie ist weltweit führend. BMW, Mercedes und Volkswagen sind bekannte Marken.",
        'category': 'economy'
    },
    {
        'id': 30,
        'language': 'de',
        'text': "Die deutsche Sprache wird von über 100 Millionen Menschen gesprochen. Sie ist die meistgesprochene Muttersprache in der EU.",
        'category': 'language'
    },
    
    # Textes avec caractéristiques spéciales (10)
    {
        'id': 31,
        'language': 'fr',
        'text': "Visitez notre site web: https://www.example.com pour plus d'informations! Contactez-nous à contact@example.com ou au 01-23-45-67-89.",
        'category': 'test'
    },
    {
        'id': 32,
        'language': 'fr',
        'text': "PROMOTION!!! 50% de réduction sur TOUS les articles!!! Dépêchez-vous, offre limitée!!! www.promo-shopping.fr",
        'category': 'test'
    },
    {
        'id': 33,
        'language': 'en',
        'text': "Check out our new product at http://products.example.org! Email support@example.org for questions. Call 1-800-555-0123.",
        'category': 'test'
    },
    {
        'id': 34,
        'language': 'fr',
        'text': "Les chiffres montrent que 85% des utilisateurs préfèrent notre service. En 2023, nous avons servi 1,000,000 de clients avec un taux de satisfaction de 98.5%.",
        'category': 'test'
    },
    {
        'id': 35,
        'language': 'en',
        'text': "The study found that 42.7% of participants showed improvement. The data from 2024 indicates a 15% increase compared to 2023.",
        'category': 'test'
    },
    {
        'id': 36,
        'language': 'fr',
        'text': "C'est formidable! J'adore ça!!! Vraiment??? Incroyable... Mais pourquoi?",
        'category': 'test'
    },
    {
        'id': 37,
        'language': 'en',
        'text': "OMG!!! This is AMAZING!!! I can't believe it... Really??? WOW!!!",
        'category': 'test'
    },
    {
        'id': 38,
        'language': 'fr',
        'text': "Texte court.",
        'category': 'test'
    },
    {
        'id': 39,
        'language': 'en',
        'text': "Short text.",
        'category': 'test'
    },
    {
        'id': 40,
        'language': 'fr',
        'text': "Ceci est un texte qui mélange français et english words dans the same sentence pour tester la détection de language.",
        'category': 'test'
    },
    
    # Textes en arabe (5)
    {
        'id': 41,
        'language': 'ar',
        'text': "القاهرة هي عاصمة مصر. تقع على نهر النيل وهي أكبر مدينة في الوطن العربي.",
        'category': 'geography'
    },
    {
        'id': 42,
        'language': 'ar',
        'text': "اللغة العربية هي لغة القرآن الكريم. يتحدث بها أكثر من 400 مليون شخص حول العالم.",
        'category': 'language'
    },
    {
        'id': 43,
        'language': 'ar',
        'text': "العلوم والتكنولوجيا تتطور بسرعة كبيرة. الذكاء الاصطناعي يغير حياتنا اليومية.",
        'category': 'technology'
    },
    {
        'id': 44,
        'language': 'ar',
        'text': "كرة القدم هي الرياضة الأكثر شعبية في العالم العربي. المنتخبات العربية تشارك في كأس العالم.",
        'category': 'sports'
    },
    {
        'id': 45,
        'language': 'ar',
        'text': "التعليم حق أساسي لكل إنسان. المدارس والجامعات توفر الفرص للتعلم والتطور.",
        'category': 'education'
    },
]


def get_corpus():
    """Retourne le corpus complet"""
    return CORPUS


def get_corpus_by_language(language):
    """Retourne les textes d'une langue spécifique"""
    return [item for item in CORPUS if item['language'] == language]


def get_corpus_by_category(category):
    """Retourne les textes d'une catégorie spécifique"""
    return [item for item in CORPUS if item['category'] == category]


def get_corpus_statistics():
    """Retourne des statistiques sur le corpus"""
    languages = {}
    categories = {}
    
    for item in CORPUS:
        lang = item['language']
        cat = item['category']
        
        languages[lang] = languages.get(lang, 0) + 1
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        'total_texts': len(CORPUS),
        'languages': languages,
        'categories': categories
    }


if __name__ == "__main__":
    stats = get_corpus_statistics()
    print("Statistiques du corpus:")
    print(f"  Nombre total de textes: {stats['total_texts']}")
    print(f"  Langues: {stats['languages']}")
    print(f"  Catégories: {stats['categories']}")
