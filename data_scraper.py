import requests
from bs4 import BeautifulSoup
import os

def scrape_data(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()  #ошибки HTTP мб краш
        soup = BeautifulSoup(response.text, 'html.parser')

        
        texts = []
        for paragraph in soup.find_all('p'):
            texts.append(paragraph.get_text(strip=True))
        for header in soup.find_all(['h1', 'h2', 'h3']):  #  заголовки обработка
            texts.append(header.get_text(strip=True))

        return texts  # возвращаем собранные тексты
    except Exception as e:
        print(f"Error scraping data from {url}: {e}")
        return []  # возвращаем пустой список при ошибке

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    
    # Вводим ссылки
    urls = [
        'https://www.sberbank.ru/ru/s_m_business/pro_business/lgoty-dlya-malogo-biznesa/', 
        'https://мсп.рф/services/competence-credit/promo/',
        'https://fmkk.ru/types/torgovlya/',
        'https://promote.budget.gov.ru/public/minfin/selection/view/e4b3d548-dd64-4271-b277-d57d7e2de490?showBackButton=true&competitionType=0',
        'https://мсп.рф/services/support/filter/',
        'https://promote.budget.gov.ru/public/minfin/activity',
        #'https://promote.budget.gov.ru/public/minfin/filter',
    ]

    output_file = 'templates/suda.txt'  
    
    # открываем файл для записи
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in urls:
            print(f"Scraping {url}...")
            texts = scrape_data(url, output_file)
            for text in texts:
                f.write(text + "\n")

    print(f"Data scraped successfully and saved to {output_file}")
