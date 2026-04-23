import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

urls_albumes = [
    "https://open.spotify.com/album/3goLwu2fkSSmghikOcVufU", "https://open.spotify.com/album/5tY5Hafl8siFkPnxyllYVR", 
    "https://open.spotify.com/album/5p10PqUVm787QcnqKmiVZF", "https://open.spotify.com/album/3SUEJULSGgBDG1j4GQhfYY", 
    "https://open.spotify.com/album/0avVU24xBfXW7ItE0xtzN2", "https://open.spotify.com/album/5wtVvVmUynbA3Yj1Pqys8w", 
    "https://open.spotify.com/album/2ha4ucrONN0cihLMkP02Ch", "https://open.spotify.com/album/4JQVXceKAkVXlkCxh1CY0f", 
    "https://open.spotify.com/album/5TZtxHs23y0ckhY6RqL8d3", "https://open.spotify.com/album/50uChhk7AKkzDKytDixjYW", 
    "https://open.spotify.com/album/44mKxp7RB6x5O19VWqEXEm", "https://open.spotify.com/album/4czxiqSwyeZK7y5r9GNWXP", 
    "https://open.spotify.com/album/492U88qanlQnFgsfvwVHe8", "https://open.spotify.com/album/3zbiiu3JTibw0esC7eoMXr", 
    "https://open.spotify.com/album/6UHVdZCYgXo8xeSCw4RXp5", "https://open.spotify.com/album/5omNd3Mkij9C3ZeW19rRmv", 
    "https://open.spotify.com/album/6jbtHi5R0jMXoliU2OS0lo", "https://open.spotify.com/album/6rFyXU9FiGytyYqfbwYO09", 
    "https://open.spotify.com/album/3ZuV4xSFJnWDncgMICfFmX", "https://open.spotify.com/album/7B70Z32Ha84aMT6TOnW410", 
    "https://open.spotify.com/album/4KEOAWBMpvJrIZ7tQfx44i", "https://open.spotify.com/album/1sETl1onOh3oZIAMn9Kfyo", 
    "https://open.spotify.com/album/3XV0gPorxF6TtGScGJChxG", "https://open.spotify.com/album/6B2RRiDJFXHojfPxKja5Mx", 
    "https://open.spotify.com/album/3844bY26oeSkqd06th4EYp", "https://open.spotify.com/album/7qJZgNj9IMy9onoTe5uhZc", 
    "https://open.spotify.com/album/23irnvaijPHVE7682D4G3f", "https://open.spotify.com/album/4bxHLppgdmaYJk0yfdcP0l", 
    "https://open.spotify.com/album/355bjCHzRJztCzaG5Za4gq", "https://open.spotify.com/album/6dOSikKvJSaL1F6i4SFmqY", 
    "https://open.spotify.com/album/2O7Zu2OPZzqehwh1wiO764", "https://open.spotify.com/album/5gBeXfX0ZfaiDWirzSNeIk", 
    "https://open.spotify.com/album/7mGsUwMuhsKiOKx9X9k7tj"
]

def obtener_escuchas_individuales(url_track):
    """Entra a la canción solo para sacar el número de escuchas"""
    driver.get(url_track)
    time.sleep(4)
    try:
        # Buscamos el contador de reproducciones (playcount)
        escuchas = driver.find_element(By.XPATH, "//span[@data-testid='playcount']").text
        return escuchas
    except:
        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, "main span[data-encore-id='text']")
            for el in elementos:
                val = el.text.replace(".", "").replace(",", "").replace(" ", "")
                if val.isdigit() and int(val) > 1000:
                    return el.text
        except:
            return "0"
    return "0"

# --- PROCESO PRINCIPAL ---
try:
    driver.get(urls_albumes[0])
    input("\nACEPTA COOKIES Y DALE AL ENTER PARA EMPEZAR EL SCRAPING...")

    base_datos_final = []

    for url_alb in urls_albumes:
        driver.get(url_alb)
        time.sleep(4)
        
        try:
            nombre_album = driver.find_element(By.CSS_SELECTOR, "main h1").text
        except:
            nombre_album = "Desconocido REVISAR"
            
        print(f"\n Buscando en el disco: {nombre_album}")
        
        filas = driver.find_elements(By.CSS_SELECTOR, "main [data-testid='tracklist-row']")
        temp_album_data = []
        
        for fila in filas:
            try:
                # 1. Título y Link
                titulo = fila.find_element(By.CSS_SELECTOR, "div[data-encore-id='text'], a[href*='/track/']").text
                link_track = fila.find_element(By.CSS_SELECTOR, "a[href*='/track/']").get_attribute("href")
                
                # 2. Duración (Suele ser el último elemento de texto con formato de tiempo en la fila)
                duracion = "0:00"
                elementos_texto = fila.find_elements(By.CSS_SELECTOR, "div[data-encore-id='text']")
                for el in elementos_texto:
                    if ":" in el.text and len(el.text) <= 5: # Filtro para formato M:SS
                        duracion = el.text
                
                # 3. Colaboraciones
                artistas_links = fila.find_elements(By.CSS_SELECTOR, "a[href*='/artist/']")
                colabs = [a.text for a in artistas_links if "Rosalía" not in a.text and a.text != ""]
                colab_str = ", ".join(colabs) if colabs else "Solo Rosalía"
                
                temp_album_data.append({
                    "Álbum": nombre_album,
                    "Canción": titulo,
                    "Colaboraciones": colab_str,
                    "Duración": duracion,
                    "URL": link_track
                })
            except:
                continue
        
        # PASO 2: Navegar para las escuchas
        print(f"   -> Entrando en {len(temp_album_data)} tracks para ver escuchas...")
        for item in temp_album_data:
            item["Escuchas"] = obtener_escuchas_individuales(item["URL"])
            print(f"       {item['Canción']} [{item['Duración']}]: {item['Escuchas']}")
            # Limpiamos URL antes de guardar
            track_temp_url = item.pop("URL") 
            base_datos_final.append(item)

    # GUARDAR
    df = pd.DataFrame(base_datos_final)
    df.to_csv("rosalia_data_completa_final.csv", index=False, encoding='utf-8-sig')
    print("\n 'rosalia_data_completa_final.csv'")

except Exception as e:
    print(f"Error detectado: {e}")
finally:
    driver.quit()