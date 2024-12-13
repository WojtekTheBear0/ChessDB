import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_fide_ratings():
    url = "https://ratings.fide.com/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all divs
        all_divs = soup.find_all('div')
        
        print("All divs found on the page:")
        for div in all_divs:
            # Print div class and content
            class_name = div.get('class', ['no-class'])
            content = div.text.strip()
            if content:  # Only print if div has content
                print(f"\nDiv class: {class_name}")
                print(f"Content: {content[:100]}...")  # Print first 100 chars of content
                print("-" * 50)

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

def main():
    print("Starting FIDE website analysis...")
    scrape_fide_ratings()

if __name__ == "__main__":
    main()



    def main():
    app = QApplication(sys.argv)
    window = ChessDBViewer() 
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()