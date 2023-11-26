from matplotlib.pylab import f
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from collections import Counter
from matplotlib import pyplot as plt
import mplcyberpunk
import pandas as pd
from statistics import mean

options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"')
driver = webdriver.Chrome(options=options)

class Scrape_Amazon_Games:

    def __init__(self,product,website):
        self.website = website
        self.product = product
        self.prod_review_num = Counter()

    def fetch_website(self):
        driver.get(self.website)

    def get_publisher(self):
        publisher = self.product.find_element(By.XPATH, ".//span[contains(text(), 'by')]").text
        publisher = publisher.replace('by ','')
        return publisher

    def get_review_number(self):
        number = self.product.find_element(By.XPATH, ".//span[@aria-label]//span[contains(@class,'a-size-base')]").text
        if number.isdigit():
            return int(number)

    def get_ratings(self):
        rating = self.product.find_element(By.XPATH, ".//span[contains(@aria-label,'stars')]").get_dom_attribute('aria-label')
        rating = float(rating[:3])
        return rating

    def handle_errors(self, pn, err):
        if err:
            print(f'Hello Beff Yezos! You have an error at page {pn}', f'{err}')
        else:
            print('Scrape Completed')

    def set_headers_bmp(self):
        pass

    def set_headers_sw(self):
        pass

def scrape():
    pn = 1
    section = 1
    each_publisher_ratings = {}
    set_of_all_publishers = set()
    count_of_publishers = Counter()
    publishers_no_of_reviews = Counter()
    website = 'https://www.amazon.com/s?i=videogames-intl-ship&bbn=16225016011&rh=n%3A16225016011%2Cn%3A468642%2Cn%3A6427814011%2Cn%3A6427831011'

    while True:
        wb = website + f'&page={pn}'
        try:
            driver.get(wb)
            section = 1
            products = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='puisg-col-inner']/div[@class='a-section a-spacing-small a-spacing-top-small']")))

            for product in products:
                try:
                    section += 1
                    SAG = Scrape_Amazon_Games(product, website=wb)

                    publisher = SAG.get_publisher()
                    review_num = SAG.get_review_number()
                    rating = SAG.get_ratings()

                    count_of_publishers.update([publisher])
                    set_of_all_publishers.add(publisher)

                    if review_num:
                        publishers_no_of_reviews[publisher] += review_num

                    # gets the previous publisher ratings array/list, if none exist returns empty list [] 
                    # adds the current rating to the list, 
                    # then assigns it the publisher to the new list
                    each_publisher_ratings[publisher] = each_publisher_ratings.get(publisher, []) + [rating]

                except Exception as err:
                    print(err, 'err')
                    continue
            pn += 1
        except Exception as err:
            break

    arr_of_pblishers = list(set_of_all_publishers)
    df = pd.DataFrame({
            "publisher":arr_of_pblishers, 
            "frequency": [count_of_publishers[pub] for pub in arr_of_pblishers], 
            "total_number_of_reviews": [publishers_no_of_reviews[pub] for pub in arr_of_pblishers], 
            "publisher_average_rating": [mean(each_publisher_ratings[pub]) for pub in arr_of_pblishers],
            "cumulative_awesomeness": [publishers_no_of_reviews[pub] * mean(each_publisher_ratings[pub]) for pub in arr_of_pblishers]
        })
    df.to_csv('best_game_companies.csv', mode='w', index=False)

def plot_csv():
    df = pd.read_csv('best_game_companies.csv')
    sorted_df = df.sort_values(['cumulative_awesomeness'], ascending=False)
    prod = sorted_df['publisher']
    freq = sorted_df['frequency']
    reviews = sorted_df['total_Number_Of_Reviews']
    avg_ratings = sorted_df['publisher_average_rating']
    cum_awesome = sorted_df['cumulative_awesomeness']

    plt.style.use("cyberpunk")

    # Plots cumulative awesomeness
    fig1,ax1 = plt.subplots(facecolor='#000')
    fig1.set_figheight(7)
    fig1.set_figwidth(12)
    ax1.barh(prod[:15].iloc[::-1], cum_awesome[:15].iloc[::-1], color='#f00',zorder=2)

    ax1.set_facecolor('#000')
    ax1.set_title('Best Selling Game Publisher on AMAZON')
    ax1.set_ylabel('Game Publisher')
    ax1.set_xlabel('Cumulative Awesomeness')


    # Plots Game publisher's frequencies / occurrences
    fig3,ax4 = plt.subplots(facecolor='#000')
    fig3.set_figheight(7)
    fig3.set_figwidth(12)
    ax4.barh(prod[:15].iloc[::-1], freq[:15].iloc[::-1], color='#fff',zorder=2)

    ax4.set_facecolor('#000')
    ax4.set_title('Most Frequent Game Publisher on AMAZON')
    ax4.set_ylabel('Game Publisher')
    ax4.set_xlabel('Frequency')


    # Frequency against Awesomeness
    fig2,(ax2, ax3) = plt.subplots(nrows=2,sharex=True,facecolor='#000')
    fig2.set_figheight(7)
    fig2.set_figwidth(12)
    fig2.subplots_adjust(hspace=0.3)

    ax2.set_facecolor('#000')
    ax3.set_facecolor('#000')

    ax2.plot(prod[:7], cum_awesome[:7], color='#f00', linewidth=2, label='Awesomeness/Trending')
    ax3.plot(prod[:7], freq[:7], color='#fff', linewidth=2, label='Frequency')

    ax2.set_title('Best Selling Game Publisher on AMAZON')
    ax2.set_ylabel('Awesomeness')
    ax3.set_ylabel('Frequency')

    ax2.legend()
    ax3.legend()

    mplcyberpunk.add_glow_effects(gradient_fill=True)
    mplcyberpunk.make_lines_glow(ax=ax2)
    mplcyberpunk.make_bars_glow(bars=ax1.patches, ax=ax1)
    mplcyberpunk.make_bars_glow(bars=ax4.patches, ax=ax4)
    
    plt.tight_layout()
    plt.show()