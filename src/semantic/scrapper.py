
corrected_code = '''# multi_scraper_robust.py - VERSION CORRIGÉE ET STABLE
"""
Scraping multi-sources ROBUSTE corrigé :
- Twitter/X : scraping stable avec vérification connexion
- Google News : sélecteurs à jour + pagination correcte
- Comptage précis des items
- Gestion des erreurs améliorée
"""

import time
import random
import pandas as pd
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import gc
import re

# =============================================================
# CONFIGURATION
# =============================================================

CONFIG = {
    "TWITTER_EMAIL": "aminebzd15@gmail.com",
    "TWITTER_USERNAME": "bouzidi41962", 
    "TWITTER_PASSWORD": "Amineb069",
    "SEARCH_QUERY": "Uber",
    "MAX_TWEETS": 1000,  # Réduit pour test - augmente après validation
    "MAX_PRESS_ARTICLES": 100,  # Réduit pour test
    "OUTPUT_DIR": "datasets",
    "CHECKPOINT_INTERVAL": 100,
    "BATCH_SIZE": 20,
    "DRIVER_TIMEOUT": 30,
    "SCROLL_PAUSE": 2.0,  # Augmenté pour éviter le ban
    "MAX_RETRIES": 3,
    "REQUEST_DELAY": (2, 5),  # Délai aléatoire entre requêtes
}

# =============================================================
# SETUP OUTPUT + CHECKPOINT
# =============================================================

def setup_output(prefix="all_sources"):
    output_dir = Path(CONFIG["OUTPUT_DIR"])
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{prefix}_{timestamp}"
    
    return {
        "json_file": str(output_dir / f"{base_name}.json"),
        "checkpoint_dir": str(output_dir / f"{base_name}_checkpoints"),
        "stats_file": str(output_dir / f"{base_name}_stats.txt"),
        "csv_file": str(output_dir / f"{base_name}.csv")
    }

def create_checkpoint_dir(checkpoint_dir):
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

def save_checkpoint(data, checkpoint_dir, name):
    """Sauvegarde checkpoint pour recovery"""
    checkpoint_file = Path(checkpoint_dir) / f"{name}.json"
    try:
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   ✓ Checkpoint sauvegardé: {name} ({len(data)} items)")
    except Exception as e:
        print(f"   ⚠️ Erreur checkpoint: {e}")

def load_checkpoint(checkpoint_dir, name):
    """Charge checkpoint si existe"""
    checkpoint_file = Path(checkpoint_dir) / f"{name}.json"
    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"   ⚠️ Erreur chargement checkpoint: {e}")
    return None

# =============================================================
# INIT DRIVER - VERSION STABLE
# =============================================================

def init_driver(headless=False):
    """Driver optimisé et stable"""
    options = uc.ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    
    # User agent réaliste
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Réduire les logs
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"❌ Erreur création driver: {e}")
        return None

# =============================================================
# TWITTER SCRAPER - VERSION CORRIGÉE
# =============================================================

def login_twitter(driver):
    """Connexion Twitter avec vérification"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[🔐] Connexion Twitter (tentative {attempt+1}/{max_retries})...")
            driver.get("https://x.com/i/flow/login")
            wait = WebDriverWait(driver, 25)

            # Étape 1: Email
            print("   → Saisie email...")
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            email_field.clear()
            email_field.send_keys(CONFIG["TWITTER_EMAIL"])
            time.sleep(1)
            email_field.send_keys(Keys.RETURN)
            time.sleep(2)

            # Étape 2: Username (si demandé)
            try:
                username_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
                )
                print("   → Saisie username...")
                username_field.clear()
                username_field.send_keys(CONFIG["TWITTER_USERNAME"])
                time.sleep(1)
                username_field.send_keys(Keys.RETURN)
                time.sleep(2)
            except TimeoutException:
                print("   → Username non demandé")
                pass

            # Étape 3: Password
            print("   → Saisie mot de passe...")
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.clear()
            password_field.send_keys(CONFIG["TWITTER_PASSWORD"])
            time.sleep(1)
            password_field.send_keys(Keys.RETURN)
            
            # Attendre la connexion
            time.sleep(5)
            
            # Vérification connexion réussie
            if is_logged_in(driver):
                print("✅ Connexion Twitter réussie et vérifiée")
                return True
            else:
                print("   ⚠️ Connexion non confirmée, nouvelle tentative...")
                time.sleep(5)
                continue

        except Exception as e:
            print(f"   ⚠️ Tentative échouée: {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(5)
            continue

    print("❌ Échec connexion Twitter après toutes les tentatives")
    return False

def is_logged_in(driver):
    """Vérifie si l'utilisateur est connecté"""
    try:
        # Vérifier présence du bouton tweet ou avatar
        indicators = [
            '//a[@data-testid="SideNav_NewTweet_Button"]',
            '//a[@href="/compose/tweet"]',
            '//div[@data-testid="SideNav_AccountSwitcher_Button"]',
            '//a[@aria-label="Profile"]'
        ]
        for indicator in indicators:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, indicator))
                )
                return True
            except:
                continue
        return False
    except:
        return False

def search_tweets(driver, query):
    """Recherche Twitter avec vérification"""
    try:
        encoded_query = requests.utils.quote(query)
        url = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"
        print(f"   → Chargement: {url[:80]}...")
        driver.get(url)
        time.sleep(4)
        
        # Vérifier que la page a chargé
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
        print("✅ Page recherche chargée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur recherche Twitter: {e}")
        return False

def extract_tweet_data(tweet_element, driver):
    """Extrait données tweet - VERSION CORRIGÉE"""
    data = {
        "username": "",
        "handle": "",
        "date": "",
        "text": "",
        "url": "",
        "likes": "0",
        "retweets": "0"
    }
    
    try:
        # Scroll vers l'élément pour s'assurer qu'il est chargé
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet_element)
        time.sleep(0.3)
        
        # Username et handle - multiple sélecteurs
        try:
            # Méthode 1: data-testid
            user_name_div = tweet_element.find_element(By.XPATH, './/div[@data-testid="User-Name"]')
            spans = user_name_div.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 2:
                data["username"] = spans[0].text.strip()
                data["handle"] = spans[1].text.strip()
        except:
            try:
                # Méthode 2: liens profil
                user_links = tweet_element.find_elements(By.XPATH, './/a[contains(@href, "/")]')
                for link in user_links:
                    href = link.get_attribute("href") or ""
                    if "/status/" not in href and href.count("/") <= 4:
                        spans = link.find_elements(By.TAG_NAME, "span")
                        if spans:
                            data["username"] = spans[0].text.strip()
                            data["handle"] = href.split("/")[-1] if "/" in href else ""
                            break
            except:
                pass
        
        # Date
        try:
            time_elem = tweet_element.find_element(By.XPATH, './/time')
            data["date"] = time_elem.get_attribute("datetime") or ""
        except:
            pass
        
        # Texte du tweet
        try:
            text_elem = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            data["text"] = text_elem.text.strip()
        except:
            try:
                # Fallback: chercher dans les divs de texte
                text_divs = tweet_element.find_elements(By.XPATH, './/div[contains(@class, "css-")]')
                for div in text_divs:
                    text = div.text.strip()
                    if len(text) > 20 and "http" not in text[:10]:
                        data["text"] = text
                        break
            except:
                pass
        
        # URL du tweet
        try:
            status_links = tweet_element.find_elements(By.XPATH, './/a[contains(@href, "/status/")]')
            for link in status_links:
                href = link.get_attribute("href")
                if href and "/status/" in href:
                    data["url"] = href
                    break
        except:
            pass
        
        # Likes - multiple méthodes
        try:
            like_btn = tweet_element.find_element(By.XPATH, './/button[@data-testid="like"]')
            like_span = like_btn.find_element(By.XPATH, './/span[contains(@class, "css-")]')
            data["likes"] = like_span.text.strip() or "0"
        except:
            try:
                like_text = tweet_element.find_element(By.XPATH, './/button[contains(@aria-label, "Like")]')
                aria = like_text.get_attribute("aria-label") or ""
                match = re.search(r'(\\d+[\\.,]?\\d*)', aria)
                if match:
                    data["likes"] = match.group(1)
            except:
                pass
        
        # Retweets
        try:
            rt_btn = tweet_element.find_element(By.XPATH, './/button[@data-testid="retweet"]')
            rt_span = rt_btn.find_element(By.XPATH, './/span[contains(@class, "css-")]')
            data["retweets"] = rt_span.text.strip() or "0"
        except:
            try:
                rt_text = tweet_element.find_element(By.XPATH, './/button[contains(@aria-label, "Retweet")]')
                aria = rt_text.get_attribute("aria-label") or ""
                match = re.search(r'(\\d+[\\.,]?\\d*)', aria)
                if match:
                    data["retweets"] = match.group(1)
            except:
                pass
    
    except StaleElementReferenceException:
        print("   [WARN] Élément obsolète, ignoré")
    except Exception as e:
        print(f"   [WARN] Erreur extraction: {str(e)[:80]}")
    
    return data

def scrape_tweets_batch(driver, max_tweets, checkpoint_dir):
    """
    Scrape tweets avec comptage PRÉCIS
    """
    tweets = []
    seen_urls = set()  # Utiliser URL comme identifiant unique
    seen_texts = set()  # Double vérification
    no_new_count = 0
    max_no_new = 8  # Tolérance augmentée
    scroll_count = 0
    max_scrolls = max_tweets * 3  # Limite de sécurité
    
    print(f"\\n[🐦] Scraping de {max_tweets} tweets maximum...")
    print(f"   → Checkpoint tous les {CONFIG['CHECKPOINT_INTERVAL']} tweets")
    
    # Attendre le premier tweet
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
    except:
        print("❌ Aucun tweet trouvé sur la page")
        return tweets
    
    while len(tweets) < max_tweets and scroll_count < max_scrolls:
        try:
            # Récupérer tous les tweets visibles
            tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            
            if not tweet_elements:
                tweet_elements = driver.find_elements(By.TAG_NAME, "article")
            
            initial_count = len(tweets)
            new_in_scroll = 0
            
            for tweet_el in tweet_elements:
                if len(tweets) >= max_tweets:
                    break
                
                try:
                    data = extract_tweet_data(tweet_el, driver)
                    
                    # Vérifications de validité
                    if not data["text"] or len(data["text"]) < 3:
                        continue
                    
                    # Éviter les doublons (URL + texte)
                    tweet_id = data["url"] if data["url"] else data["text"][:100]
                    if tweet_id in seen_urls or data["text"][:100] in seen_texts:
                        continue
                    
                    seen_urls.add(tweet_id)
                    seen_texts.add(data["text"][:100])
                    tweets.append(data)
                    new_in_scroll += 1
                    
                    # Affichage progressif
                    if len(tweets) % 50 == 0:
                        print(f"   📊 {len(tweets)}/{max_tweets} tweets collectés")
                    
                    # Checkpoint
                    if len(tweets) % CONFIG["CHECKPOINT_INTERVAL"] == 0:
                        save_checkpoint(tweets, checkpoint_dir, "tweets_checkpoint")
                
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    if "no such element" not in str(e).lower():
                        print(f"   [WARN] Tweet ignoré: {str(e)[:60]}")
                    continue
            
            # Logique d'arrêt améliorée
            if new_in_scroll == 0:
                no_new_count += 1
                if no_new_count % 3 == 0:
                    print(f"   ⚠️  Pas de nouveaux tweets ({no_new_count}/{max_no_new})")
                
                if no_new_count >= max_no_new:
                    print(f"   → Fin de pagination atteinte après {no_new_count} scrolls vides")
                    break
            else:
                no_new_count = 0
            
            # Scroll avec délai aléatoire
            scroll_count += 1
            scroll_amount = random.randint(800, 1200)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(CONFIG["SCROLL_PAUSE"] + random.uniform(0.5, 2.0))
            
            # Cleanup mémoire
            if scroll_count % 100 == 0:
                gc.collect()
                
        except Exception as e:
            print(f"   ❌ Erreur scroll {scroll_count}: {str(e)[:80]}")
            time.sleep(3)
            continue
    
    print(f"\\n✅ {len(tweets)} tweets scrapés avec succès (sur {max_tweets} demandés)")
    return tweets

# =============================================================
# GOOGLE NEWS SCRAPER - VERSION CORRIGÉE
# =============================================================

def create_session():
    """Crée session requests avec retry et headers"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    retry = Retry(
        total=3,
        connect=3,
        backoff_factor=2.0,
        status_forcelist=(500, 502, 503, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_article_content_fast(url, session):
    """Extrait contenu article avec meilleure gestion"""
    try:
        response = session.get(url, timeout=20, allow_redirects=True)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Supprimer scripts et styles
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Extraction contenu
        content = ""
        
        # Méthode 1: article/main
        for selector in ['article', 'main', '[role="main"]', '.article-body', '.post-content', '.entry-content']:
            elem = soup.select_one(selector)
            if elem:
                paragraphs = elem.find_all('p')
                content = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                if len(content) > 200:
                    break
        
        # Méthode 2: tous les paragraphes
        if len(content) < 200:
            paragraphs = soup.find_all('p')
            content = " ".join([p.get_text(strip=True) for p in paragraphs[:8] if len(p.get_text(strip=True)) > 30])
        
        # Méthode 3: divs de texte
        if len(content) < 100:
            for div in soup.find_all('div'):
                text = div.get_text(strip=True)
                if 100 < len(text) < 2000:
                    content = text
                    break
        
        # Extraction date
        article_date = ""
        
        # JSON-LD
        try:
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld and json_ld.string:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    article_date = data.get('datePublished', data.get('date', ''))
                elif isinstance(data, list) and len(data) > 0:
                    article_date = data[0].get('datePublished', '')
        except:
            pass
        
        # Meta tags
        if not article_date:
            for prop in ['article:published_time', 'og:published_time', 'datePublished', 'DC.date.issued']:
                meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                if meta and meta.get('content'):
                    article_date = meta['content']
                    break
        
        # Time tags
        if not article_date:
            time_tags = soup.find_all('time')
            for tag in time_tags:
                article_date = tag.get('datetime', tag.get_text(strip=True))
                if article_date:
                    break
        
        return content[:800], article_date
    
    except requests.exceptions.RequestException as e:
        return "", f"RequestError: {str(e)[:50]}"
    except Exception as e:
        return "", f"Error: {str(e)[:50]}"

def scrape_articles_batch(driver, query, max_articles, checkpoint_dir):
    """
    Scrape articles Google News avec comptage PRÉCIS
    """
    articles = []
    seen_urls = set()
    session = create_session()
    page = 0
    consecutive_failures = 0
    max_failures = 5
    total_checked = 0
    
    print(f"\\n[📰] Scraping de {max_articles} articles maximum...")
    
    while len(articles) < max_articles and consecutive_failures < max_failures:
        try:
            encoded_query = requests.utils.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}&tbm=nws&start={page*10}&hl=fr"
            print(f"\\n[Page {page+1}] Chargement...")
            
            driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # Sélecteurs Google News 2024/2025
            selectors = [
                'div[data-sokoban-container]',
                'div.Gx5Zad',  # Ancien
                'div.dbsr',    # Très ancien
                'div.SoaBEf',  # Ancien
                'div.WlydOe',  # Nouveau 2024
                'article',
                'div.tF2Cxc',  # Alternative
                'div.yuRUbf',  # Résultats standard
            ]
            
            article_elements = []
            for selector in selectors:
                article_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if article_elements:
                    print(f"   ✓ Sélecteur trouvé: {selector} ({len(article_elements)} éléments)")
                    break
            
            if not article_elements:
                # Essayer avec les liens de news
                article_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "http") and .//h3]')
                if article_elements:
                    print(f"   ✓ Fallback liens trouvés: {len(article_elements)}")
            
            if not article_elements:
                print(f"   ⚠️ Aucun article trouvé sur cette page")
                consecutive_failures += 1
                page += 1
                if page > 20:  # Limite de sécurité
                    break
                continue
            
            page_articles = 0
            
            for idx, article_el in enumerate(article_elements):
                if len(articles) >= max_articles:
                    break
                
                try:
                    # Extraire URL
                    href = None
                    try:
                        href = article_el.get_attribute("href")
                    except:
                        pass
                    
                    if not href:
                        try:
                            link_el = article_el.find_element(By.TAG_NAME, "a")
                            href = link_el.get_attribute("href")
                        except:
                            links = article_el.find_elements(By.TAG_NAME, "a")
                            for link in links:
                                href = link.get_attribute("href")
                                if href and "google.com" not in href:
                                    break
                    
                    if not href or "google.com" in href or href in seen_urls:
                        continue
                    
                    seen_urls.add(href)
                    total_checked += 1
                    
                    # Titre
                    title = ""
                    try:
                        title = article_el.find_element(By.TAG_NAME, "h3").text.strip()
                    except:
                        try:
                            title = article_el.text.strip()[:200]
                        except:
                            pass
                    
                    if not title:
                        continue
                    
                    # Date affichée par Google
                    pub_date = ""
                    try:
                        date_spans = article_el.find_elements(By.CSS_SELECTOR, 'span, div')
                        for span in date_spans:
                            text = span.text.strip()
                            if any(word in text.lower() for word in ['il y a', 'hour', 'day', 'min', 'sec', '202', '/202']):
                                pub_date = text
                                break
                    except:
                        pass
                    
                    # Délai entre requêtes
                    time.sleep(random.uniform(*CONFIG["REQUEST_DELAY"]))
                    
                    # Contenu + date
                    content, article_date = extract_article_content_fast(href, session)
                    
                    if not article_date and pub_date:
                        article_date = pub_date
                    
                    # Vérifier que le contenu est valide
                    if content and len(content) > 50:
                        articles.append({
                            "title": title,
                            "text": content,
                            "url": href,
                            "date": article_date,
                            "source": "press"
                        })
                        page_articles += 1
                        consecutive_failures = 0
                        
                        if len(articles) % 25 == 0:
                            print(f"   📊 {len(articles)}/{max_articles} articles collectés")
                        
                        # Checkpoint
                        if len(articles) % CONFIG["CHECKPOINT_INTERVAL"] == 0:
                            save_checkpoint(articles, checkpoint_dir, "articles_checkpoint")
                    
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    if "no such element" not in str(e).lower():
                        print(f"      [WARN] Article {idx}: {str(e)[:60]}")
                    continue
            
            print(f"   ✓ {page_articles} nouveaux articles sur cette page (total: {len(articles)})")
            
            if page_articles == 0:
                consecutive_failures += 1
            else:
                consecutive_failures = 0
            
            page += 1
            gc.collect()
            
            # Pause entre pages
            time.sleep(random.uniform(2, 4))
        
        except Exception as e:
            print(f"   ❌ Page {page}: {str(e)[:100]}")
            consecutive_failures += 1
            time.sleep(5)
            continue
    
    session.close()
    print(f"\\n✅ {len(articles)} articles scrapés avec succès (sur {max_articles} demandés)")
    print(f"   URLs vérifiées: {total_checked}, Doublons/invalides filtrés: {total_checked - len(articles)}")
    return articles

# =============================================================
# SAVE ALL DATA - VERSION AMÉLIORÉE
# =============================================================

def save_all_data(tweets, articles, output_config):
    """Sauvegarde finale avec statistiques précises"""
    all_data = []
    
    # Tweets
    for tweet in tweets:
        tweet["source"] = "twitter"
        tweet["title"] = ""
        all_data.append(tweet)
    
    # Articles
    for article in articles:
        article["source"] = "press"
        article["username"] = ""
        article["handle"] = ""
        article["likes"] = ""
        article["retweets"] = ""
        all_data.append(article)
    
    # DataFrame
    columns = ["source", "title", "text", "date", "url", "username", "handle", "likes", "retweets"]
    df = pd.DataFrame(all_data)
    
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    
    df = df[columns]
    
    # Sauvegardes
    try:
        # JSON
        df.to_json(output_config["json_file"], orient="records", force_ascii=False, indent=2)
        
        # CSV (plus pratique pour l'analyse)
        df.to_csv(output_config["csv_file"], index=False, encoding='utf-8-sig')
        
        # Stats détaillées
        with open(output_config["stats_file"], 'w', encoding='utf-8') as f:
            f.write("="*60 + "\\n")
            f.write("RAPPORT DE SCRAPING\\n")
            f.write("="*60 + "\\n\\n")
            f.write(f"Date d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"Requête de recherche: {CONFIG['SEARCH_QUERY']}\\n\\n")
            f.write("RÉSULTATS:\\n")
            f.write("-"*40 + "\\n")
            f.write(f"Tweets demandés:     {CONFIG['MAX_TWEETS']:>8}\\n")
            f.write(f"Tweets obtenus:      {len(tweets):>8}\\n")
            f.write(f"Taux tweets:         {len(tweets)/CONFIG['MAX_TWEETS']*100 if CONFIG['MAX_TWEETS'] > 0 else 0:.1f}%\\n\\n")
            f.write(f"Articles demandés:   {CONFIG['MAX_PRESS_ARTICLES']:>8}\\n")
            f.write(f"Articles obtenus:    {len(articles):>8}\\n")
            f.write(f"Taux articles:       {len(articles)/CONFIG['MAX_PRESS_ARTICLES']*100 if CONFIG['MAX_PRESS_ARTICLES'] > 0 else 0:.1f}%\\n\\n")
            f.write(f"TOTAL ITEMS:         {len(df):>8}\\n")
            f.write("-"*40 + "\\n\\n")
            f.write("FICHIERS DE SORTIE:\\n")
            f.write(f"JSON: {output_config['json_file']}\\n")
            f.write(f"CSV:  {output_config['csv_file']}\\n")
        
        print(f"\\n" + "="*60)
        print("RÉSULTATS FINaux")
        print("="*60)
        print(f"Tweets:   {len(tweets)}/{CONFIG['MAX_TWEETS']} ({len(tweets)/CONFIG['MAX_TWEETS']*100:.1f}%)")
        print(f"Articles: {len(articles)}/{CONFIG['MAX_PRESS_ARTICLES']} ({len(articles)/CONFIG['MAX_PRESS_ARTICLES']*100:.1f}%)")
        print(f"TOTAL:    {len(df)} items")
        print(f"\\nFichiers sauvegardés:")
        print(f"   JSON: {output_config['json_file']}")
        print(f"   CSV:  {output_config['csv_file']}")
        print(f"   Stats: {output_config['stats_file']}")
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        # Sauvegarde d'urgence
        emergency_file = Path(output_config["json_file"]).parent / "emergency_backup.json"
        with open(emergency_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"   Sauvegarde d'urgence: {emergency_file}")

# =============================================================
# MAIN - VERSION STABLE
# =============================================================

def main():
    print("\\n" + "="*60)
    print("MULTI-SOURCE SCRAPER - VERSION CORRIGÉE")
    print("="*60)
    print(f"Recherche: '{CONFIG['SEARCH_QUERY']}'")
    print(f"Tweets max: {CONFIG['MAX_TWEETS']} | Articles max: {CONFIG['MAX_PRESS_ARTICLES']}")
    print("="*60)
    
    output_config = setup_output("scrape")
    create_checkpoint_dir(output_config["checkpoint_dir"])
    
    driver = init_driver(headless=False)
    
    if not driver:
        print("❌ Impossible de créer le driver Chrome")
        return
    
    tweets = []
    articles = []
    
    try:
        # === TWITTER ===
        print("\\n[1/2] TWITTER SCRAPING")
        print("-"*60)
        
        if login_twitter(driver):
            if search_tweets(driver, CONFIG["SEARCH_QUERY"]):
                tweets = scrape_tweets_batch(driver, CONFIG["MAX_TWEETS"], output_config["checkpoint_dir"])
            else:
                print("❌ Impossible de charger la page de recherche Twitter")
        else:
            print("❌ Connexion Twitter échouée - tweets ignorés")
        
        # === ARTICLES ===
        print("\\n[2/2] GOOGLE NEWS SCRAPING")
        print("-"*60)
        
        articles = scrape_articles_batch(
            driver, 
            CONFIG["SEARCH_QUERY"], 
            CONFIG["MAX_PRESS_ARTICLES"], 
            output_config["checkpoint_dir"]
        )
        
        # === SAUVEGARDE ===
        print("\\n[3/3] SAUVEGARDE DES DONNÉES")
        print("-"*60)
        
        save_all_data(tweets, articles, output_config)
        
        print("\\n" + "="*60)
        print("✅ SCRAPING TERMINÉ AVEC SUCCÈS")
        print("="*60)
    
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Scraping interrompu par l'utilisateur")
        print("   Sauvegarde des données collectées...")
        save_all_data(tweets, articles, output_config)
    
    except Exception as e:
        print(f"\\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        print("   Sauvegarde des données collectées...")
        save_all_data(tweets, articles, output_config)
    
    finally:
        print("\\n[🧹] Nettoyage...")
        try:
            driver.quit()
            print("✅ Driver fermé proprement")
        except Exception as e:
            print(f"⚠️ Erreur fermeture driver: {e}")
        
        gc.collect()
        print("✅ Mémoire libérée")

if __name__ == "__main__":
    main()
'''

# Sauvegarder le fichier corrigé
output_path = "C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\datasets"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(corrected_code)

print("✅ Fichier corrigé sauvegardé!")
print(f"📁 Chemin: {output_path}")
print(f"📊 Taille: {len(corrected_code)} caractères")
