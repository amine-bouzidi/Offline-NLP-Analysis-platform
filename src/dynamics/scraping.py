from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import random

# =============================================================
# CONFIGURATION — Modifie ces valeurs
# =============================================================
TWITTER_EMAIL    = "ihaddadene.chakib@hotmail.com"       # ton email Twitter
TWITTER_USERNAME = "chakib_hdn"               # ton @username (sans @)
TWITTER_PASSWORD = "Schnumero19"           # ton mot de passe
SEARCH_QUERY     = "Uber"                       # ce qu'on cherche
MAX_TWEETS       = 100                           # nombre de tweets à extraire
OUTPUT_FILE      = "tweets_uber.csv"            # fichier de sortie
# =============================================================


def init_driver():
    """Initialise Chrome avec des options anti-détection."""
    options = webdriver.ChromeOptions()
    
    # Options pour éviter la détection bot
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1280,900")
    
    # User agent d'un vrai navigateur
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    # Masquer que c'est Selenium
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    
    return driver


def human_type(element, text):
    """Tape du texte lettre par lettre comme un humain."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def login(driver):
    print("🔐 Connexion à Twitter...")
    driver.get("https://twitter.com/i/flow/login")
    time.sleep(6)

    wait = WebDriverWait(driver, 25)

    # ── Étape 1 : Email ──
    print("  → Saisie email...")
    email_field = wait.until(
        EC.element_to_be_clickable((By.NAME, "text"))
    )
    time.sleep(1)
    email_field.click()
    time.sleep(0.5)
    email_field.clear()
    human_type(email_field, TWITTER_EMAIL)
    time.sleep(2)

    # ✅ Scroll vers le bouton et cliquer via JavaScript
    print("  → Clic sur Suivant...")
    suivant_btn = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            '//button[.//span[contains(text(),"Suivant") or contains(text(),"Next")]]'
        ))
    )
    # Scroll jusqu'au bouton
    driver.execute_script("arguments[0].scrollIntoView(true);", suivant_btn)
    time.sleep(0.5)
    # Clic via JavaScript (contourne les problèmes de clic Selenium)
    driver.execute_script("arguments[0].click();", suivant_btn)
    time.sleep(4)

    print(f"  → URL après Suivant : {driver.current_url}")
    driver.save_screenshot("debug_apres_suivant.png")

    # ── Étape 2 : Username si demandé ──
    try:
        page = driver.page_source.lower()
        if "téléphone" in page or "unusual" in page or "enter your phone" in page:
            print("  → Username/téléphone demandé !")
            username_field = wait.until(
                EC.element_to_be_clickable((By.NAME, "text"))
            )
            username_field.click()
            time.sleep(0.5)
            human_type(username_field, TWITTER_USERNAME)
            time.sleep(1)
            suivant_btn2 = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//button[.//span[contains(text(),"Suivant") or contains(text(),"Next")]]'
                ))
            )
            driver.execute_script("arguments[0].click();", suivant_btn2)
            time.sleep(3)
    except:
        print("  → Pas de demande username")

    # ── Étape 3 : Mot de passe ──
    print("  → Saisie mot de passe...")
    try:
        password_field = wait.until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )
        time.sleep(0.5)
        password_field.click()
        time.sleep(0.5)
        human_type(password_field, TWITTER_PASSWORD)
        time.sleep(1.5)

        login_btn = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                '//button[.//span[contains(text(),"Se connecter") or contains(text(),"Log in")]]'
            ))
        )
        driver.execute_script("arguments[0].click();", login_btn)
        time.sleep(5)
        print("✅ Connecté !")

    except Exception as e:
        driver.save_screenshot("debug_login.png")
        print(f"❌ Erreur → debug_login.png")
        raise


def search_tweets(driver, query):
    """Lance une recherche sur Twitter."""
    print(f"🔍 Recherche de tweets : '{query}'...")
    
    # URL de recherche directe (Latest = tweets récents)
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
    driver.get(url)
    time.sleep(4)
    print("✅ Page de recherche chargée !")


def extract_tweet_data(tweet_element):
    """
    Extrait les données d'un tweet :
    - Texte du tweet
    - Date
    - Nom d'utilisateur
    - @handle
    """
    data = {
        "username":  "",
        "handle":    "",
        "date":      "",
        "text":      "",
        "likes":     "",
        "retweets":  "",
    }
    
    try:
        # Nom affiché (ex: "Elon Musk")
        data["username"] = tweet_element.find_element(
            By.XPATH, './/div[@data-testid="User-Name"]//span[1]'
        ).text
    except:
        pass
    
    try:
        # @handle (ex: "@elonmusk")
        handle_spans = tweet_element.find_elements(
            By.XPATH, './/div[@data-testid="User-Name"]//span'
        )
        for span in handle_spans:
            if "@" in span.text:
                data["handle"] = span.text
                break
    except:
        pass
    
    try:
        # Date du tweet
        data["date"] = tweet_element.find_element(
            By.XPATH, './/time'
        ).get_attribute("datetime")[:10]  # Format YYYY-MM-DD
    except:
        pass
    
    try:
        # Texte du tweet
        data["text"] = tweet_element.find_element(
            By.XPATH, './/div[@data-testid="tweetText"]'
        ).text
    except:
        pass
    
    try:
        # Likes
        data["likes"] = tweet_element.find_element(
            By.XPATH, './/button[@data-testid="like"]//span'
        ).text
    except:
        pass
    
    try:
        # Retweets
        data["retweets"] = tweet_element.find_element(
            By.XPATH, './/button[@data-testid="retweet"]//span'
        ).text
    except:
        pass
    
    return data


def get_follower_count(driver, handle):
    """
    Va sur le profil d'un utilisateur pour récupérer
    son nombre d'abonnés.
    """
    if not handle:
        return "N/A"
    
    try:
        clean_handle = handle.replace("@", "")
        driver.get(f"https://twitter.com/{clean_handle}")
        time.sleep(2)
        
        # Cherche le nombre d'abonnés
        followers_element = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href,"followers")]//span[@class]'
            ))
        )
        return followers_element.text
    except:
        return "N/A"


def scrape_tweets(driver, max_tweets):
    """
    Scrolle et collecte les tweets jusqu'à atteindre max_tweets.
    """
    print(f"📥 Extraction de {max_tweets} tweets...")
    
    tweets_data = []
    seen_texts  = set()   # évite les doublons
    scroll_pause = 2.5
    
    while len(tweets_data) < max_tweets:
        
        # Récupère tous les tweets visibles
        tweet_elements = driver.find_elements(
            By.XPATH, '//article[@data-testid="tweet"]'
        )
        
        for tweet_el in tweet_elements:
            if len(tweets_data) >= max_tweets:
                break
            
            data = extract_tweet_data(tweet_el)
            
            # Ignore les tweets vides ou déjà vus
            if not data["text"] or data["text"] in seen_texts:
                continue
            
            seen_texts.add(data["text"])
            tweets_data.append(data)
            
            print(f"  [{len(tweets_data)}/{max_tweets}] "
                  f"{data['handle']} — {data['date']} — "
                  f"{data['text'][:50]}...")
        
        # Scroll vers le bas
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(scroll_pause + random.uniform(0, 1))
    
    return tweets_data


def save_to_csv(tweets, filename):
    """Sauvegarde les tweets dans un fichier CSV."""
    if not tweets:
        print("⚠️  Aucun tweet à sauvegarder.")
        return
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tweets[0].keys())
        writer.writeheader()
        writer.writerows(tweets)
    
    print(f"\n💾 {len(tweets)} tweets sauvegardés → {filename}")


# =============================================================
# MAIN
# =============================================================
def main():
    driver = init_driver()
    
    try:
        # 1. Connexion
        login(driver)
        
        # 2. Recherche
        search_tweets(driver, SEARCH_QUERY)
        
        # 3. Scraping des tweets
        tweets = scrape_tweets(driver, MAX_TWEETS)
        
        # 4. (Optionnel) Récupérer les abonnés
        # ⚠️  Ça prend du temps car il faut visiter chaque profil
        # Décommenter si tu veux les abonnés :
        
        # print("\n👥 Récupération des abonnés (ça prend du temps)...")
        # search_tweets(driver, SEARCH_QUERY)  # revenir à la recherche
        # for tweet in tweets:
        #     tweet["followers"] = get_follower_count(driver, tweet["handle"])
        #     print(f"  {tweet['handle']} → {tweet['followers']} abonnés")
        #     time.sleep(1)
        
        # 5. Sauvegarde CSV
        save_to_csv(tweets, OUTPUT_FILE)
        
        print("\n✅ Scraping terminé !")
        print(f"   Fichier : {OUTPUT_FILE}")
        print(f"   Tweets  : {len(tweets)}")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()