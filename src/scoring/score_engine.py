import numpy as np

class ScoreEngine:
    def __init__(self):
        # Poids issus de votre matrice AHP (Partie 2 du document Advisory)
        self.weights = {
            'temps': 0.52,
            'engagement': 0.26,
            'sentiment': 0.14,
            'densite': 0.08
        }
        
    def calculate_reputation_score(self, row, sentiment_score):
        """Calcule le score de risque réputationnel (0-9)"""
        # 1.1 Source (Twitter/Social = 5 selon votre grille)
        score_source = 5
        
        # 1.3 Engagement (Calculé sur le CSV)
        total_eng = int(row.get('retweet_num', 0)) + int(row.get('like_num', 0))
        if total_eng > 100: s_engag = 9
        elif total_eng >= 10: s_engag = 6
        else: s_engag = 3
        
        # 1.5 Sentiment (NLP) - Normalisé sur 9
        s_sent = sentiment_score * 9
        
        # Calcul de la Pertinence pondérée
        pertinence = (s_engag * self.weights['engagement'] + 
                      s_sent * self.weights['sentiment'] + 
                      7 * self.weights['densite']) # 7 = moyenne par défaut pour densité
        
        # Résultat final : Fiabilité x Pertinence
        return round(score_source * (pertinence / 9), 2)