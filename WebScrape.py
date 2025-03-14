from bs4 import BeautifulSoup
import requests
import re

class Page:
    def __init__(self, id):
        self.id = id
        self.url = f"https://www.ceneo.pl/{id}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/"
        }
        
    def connect(self):
        try:
            self.base_page = requests.get(self.url, headers=self.headers)
            
            return {"code": 0}
        except:
            return {"code": 1}
        
    def get_product_name(self):
        self.page = self.base_page
        self.soup = BeautifulSoup(self.page.text, features="html.parser")
        self.name = self.soup.find("h1", class_ = "product-top__product-info__name js_product-h1-link js_product-force-scroll js_searchInGoogleTooltip default-cursor")
        if self.name:
            self.code = 0
            self.name = self.name.text
        else:
            self.code = 1
            
        if not self.code:
            return {"code": self.code,
                    "result": self.name}
        else:
            return {"code": self.code}
    
    def get_comments_amount(self):
        self.page = self.base_page
        self.soup = BeautifulSoup(self.page.text, features="html.parser")
        self.amount = self.soup.find("a", class_ = "product-review__link link link--accent js_reviews-link js_clickHash js_seoUrl")
        if self.amount:
            self.code = 0
            self.amount = self.amount.find("span")
            self.amount = self.amount.text
        else: 
            self.code = 1
        
        if not self.code:
            return {"code": self.code,
                    "result": self.amount}
        else:
            return {"code": self.code}
        
    def get_next_page(self, page):
        self.page = page
        self.soup = BeautifulSoup(self.page.text, features="html.parser")
        self.pages = self.soup.find_all("a", class_ = "pagination__item")
        if self.pages:
            self.code = 0
            self.current = 1
            for page in self.pages:
                if page.text.isdigit():
                    if self.current < int(page.text):
                        self.current = int(page.text)
        else:
            self.code = 1
            
        if not self.code:
            return {"code": self.code,
                    "result": self.current}
        else:
            return {"code": self.code}
        
    def get_comments(self):
        self.page = requests.get(f"{self.url}#tab=reviews", headers=self.headers)
        self.soup = BeautifulSoup(self.page.text, features="html.parser")
        self.comment_section = self.soup.find("div", class_ = "js_product-reviews js_reviews-hook js_product-reviews-container")
        
        if self.comment_section:
            self.code1 = 0
            self.comments = self.comment_section.find_all("div", class_="user-post user-post__card js_product-review")
        else: self.code1 = 1
        
        if not self.code1:
            self.n_page = 1
            self.n_pages = self.get_next_page(self.page)
            if not self.n_pages["code"]:
                self.n_pages = self.n_pages["result"]
                        
                while self.n_page < self.n_pages:
                    self.n_page += 1
                    self.page = requests.get(f"{self.url}/opinie-{self.n_page}", headers=self.headers)
                    self.soup = BeautifulSoup(self.page.text, features="html.parser")
                    self.comment_section = self.soup.find("div", class_ = "js_product-reviews js_reviews-hook js_product-reviews-container")
                    if self.comment_section:
                        self.comments += self.comment_section.find_all("div", class_="user-post user-post__card js_product-review")
                        
                        self.n_pages = self.get_next_page(self.page)
                        if not self.n_pages["code"]:
                            self.n_pages = self.n_pages["result"]
                        else: break
                    else: break
        
        if not self.code1:
            return {"code": self.code1,
                    "result": self.comments}
        else:
            return {"code": self.code1}
    
    def format_comments(self):
        self.comments = self.get_comments()
        if not self.comments["code"]:
            self.code = 0
            self.comments = self.comments["result"]
            self.opinions = []
            for comment in self.comments:
                self.comment_data = self.get_comment_data(comment)
                self.opinions.append(self.comment_data)
        else: self.code = 1
            
        if not self.code:
            return {"code": self.code,
                    "result": self.opinions}
        else:
            return {"code": self.code}    
            
    def get_comment_data(self, opinion):
        self.review = {}
        self.review["id"] = self.get_id(opinion)
        self.review["author"] = self.get_author(opinion)
        self.review["recommendation"] = self.get_recommendation(opinion)
        self.review["score"] = self.get_score(opinion)
        self.review["content"] = self.get_content(opinion)
        self.review["advantages"] = self.get_advantages(opinion)
        self.review["disadvantages"] = self.get_disadvantages(opinion)
        self.review["likes"] = self.get_likes(opinion)
        self.review["dislikes"] = self.get_dislikes(opinion)
        self.review["publish time"] = self.get_publish_time(opinion)
        self.review["purchase time"] = self.get_purchase_time(opinion)
        
        return self.review
        
        
    def get_id(self, opinion):
        self.id = re.findall("\\d+", str(opinion.find("div", class_ = "js_product-review-form-hook")))
        if len(self.id):
            self.id = self.id[0]
        else: self.id = None
        
        return self.id
    
    def get_author(self, opinion):
        self.author = opinion.find("span", class_ = "user-post__author-name")
        if self.author:
            self.author = self.author.text.strip()
        else: self.author = None
        
        return self.author
    
    def get_recommendation(self, opinion):
        self.recommendation = opinion.find("span", class_ = "user-post__author-recomendation")
        if self.recommendation:
            self.recommendation = self.recommendation.text.strip()
        else: self.recommendation = None
        
        return self.recommendation
    
    def get_score(self, opinion):
        self.score = opinion.find("span", class_ = "user-post__score-count")
        if self.score:
            self.score = float(self.score.text[:-2].replace(",", "."))
        else: self.score = None
        
        return self.score
    
    def get_content(self, opinion):
        self.content = opinion.find("div", class_ = "user-post__text")
        if self.content:
            self.content = self.content.text.strip()
        else: self.content = None
        
        return self.content
    
    def get_advantages(self, opinion):
        self.advantages = opinion.find_all("div", class_ = "review-feature__item review-feature__item--positive")
        if self.advantages:
            self.advantages = [advantage.text for advantage in self.advantages]
        else: self.advantages = None
        
        return self.advantages
    
    def get_disadvantages(self, opinion):
        self.disadvantages = opinion.find_all("div", class_ = "review-feature__item review-feature__item--negative")
        if self.disadvantages:
            self.disadvantages = [disadvantage.text for disadvantage in self.disadvantages]
        else: self.disadvantages = None
        
        return self.disadvantages
    
    def get_likes(self, opinion):
        self.likes = opinion.find("button", class_ = "vote-yes js_product-review-vote js_vote-yes")
        if self.likes:
            self.likes = re.findall("\\d+", re.findall("data-total-vote=\"\\d+\"", str(self.likes))[0])[0]
        else: self.likes = None
        
        return self.likes
    
    def get_dislikes(self, opinion):
        self.dislikes = opinion.find("button", class_ = "vote-yes js_product-review-vote js_vote-yes")
        if self.dislikes:
            self.dislikes = re.findall("\\d+", re.findall("data-total-vote=\"\\d+\"", str(self.dislikes))[0])[0]
        else: self.dislikes = None
        
        return self.dislikes
    
    def get_publish_time(self, opinion):
        self.publish_date = opinion.find_all("time")
        if self.publish_date:
            self.publish_date = re.findall("\".+ .+\"", str(self.publish_date[0]))[0][1:-1]
        else:
            self.publish_date = None
        
        return self.publish_date
    
    def get_purchase_time(self, opinion):
        self.purchase_date = opinion.find_all("time")
        if len(self.purchase_date) == 2:
            self.purchase_date = re.findall("\".+ .+\"", str(self.purchase_date[1]))[0][1:-1]
        else:
            self.purchase_date = None
        
        return self.purchase_date