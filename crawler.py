import requests
from bs4 import BeautifulSoup
import json
import time
def get_page_content(url):
    """Get html from url"""
    try:
        page_content = requests.get(url)

        if page_content.status_code == 200:
            soup = BeautifulSoup(page_content.text, 'html.parser')

            item = {}
            #get date
            date = soup.find('span', class_='news-time')
            if date:
                item['published_date'] = date.text.strip()
            # Get title
            title = soup.find('h1', class_='title')
            if title:
                item['title'] = title.text.strip()
            # Get content
            content = soup.find('section', id="news-content")
            if content:
                #get question
                question = content.find('strong', class_="sapo")
                if question:
                    item['question'] = question.text.strip()
                #remove question
                question.extract()
                #remove div with id= "accordionMucLuc" from content
                accordion = content.find('div', id="accordionMucLuc")
                if accordion:
                    accordion.extract()
                #get content
                # item['content'] = content.text.strip()
                parts = content.find_all(['p','h2', 'blockquote'])
                # pprint(parts)
                news_content = ""
                prev_part = None
                for part in parts[:-1]:
                    if part.name == "p":
                        if prev_part and prev_part.name == "blockquote":
                            news_content += "</ref>\n" + part.text.strip() + "\n"
                        else:
                            news_content += part.text.strip() + "\n"
                    elif part.name == "blockquote":
                        if prev_part and prev_part.name != "blockquote":
                            news_content += "<ref>" + part.text.strip() + "\n"
                        else:
                            news_content += part.text.strip() + "\n"
                    elif part.name == "h2":
                        news_content +="<subquestion>" + part.text.strip()+ "</subquestion>" + "\n"
                    else:
                        news_content += part.text.strip() + "\n"
                    prev_part = part
                # pprint(news_content)
                item['content'] = news_content
                # pprint(item)
                refs = content.find_all('a')
                item['refs'] = [ref.text.strip() for ref in refs]

            return item 
        else:
            print("Error when get page content")
            with open("./error.txt", "a", encoding="utf-8") as f:
                f.write(url + "\n")
            return {}
    except Exception as e:
        print("Error when get page content")
        with open("./error.txt", "a", encoding="utf-8") as f:
            f.write(url + "\n")
        return {}

def get_content_from_major(major):
    # page = 0
    url = f"https://thuvienphapluat.vn/hoi-dap-phap-luat/{major}?page="
    for page in range(1,120):
        url = url + str(page)
        print(url)
        page_links = requests.get(url)
        soup = BeautifulSoup(page_links.text, 'html.parser')
        
        links = soup.find_all('a', class_='title-link')
        
        if len(links) == 0:
            break
            # break
        for link in links:
            # print(link['href'])
            time.sleep(1.5)
            page_content = get_page_content(link['href'])
            if page_content != {}:
                page_content['domain'] = major
                page_content['url'] = link['href']
                page_content['crawled_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
                with open("./data_qa_new_1.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(page_content, ensure_ascii=False) + "\n")
                    
        url = f"https://thuvienphapluat.vn/hoi-dap-phap-luat/{major}?page="
        
        with open('./processed_major.txt', 'w', encoding='utf-8') as f:
            f.write(major + " " + str(page) + "\n")
            
        time.sleep(2)

def get_content_from_category(category):
    url = f"https://thuvienphapluat.vn/hoi-dap-phap-luat/chu-de/{category}?page="
    for page in range(1,100):
        url = url + str(page)
        print(url)
        page_links = requests.get(url)
        soup = BeautifulSoup(page_links.text, 'html.parser')
        links = soup.find_all('a', class_='title-link')
        
        if len(links) == 0:
            break
        
        for link in links:
            # print(link['href'])
            time.sleep(1.5)
            page_content = get_page_content(link['href'])
            if page_content != {}:
                page_content['domain'] = category
                page_content['url'] = link['href']
                page_content['crawled_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
                with open("./data_qa_new.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(page_content, ensure_ascii=False) + "\n")
                    
        url = f"https://thuvienphapluat.vn/hoi-dap-phap-luat/chu-de/{category}?page="
        
        with open('./processed_category.txt', 'w', encoding='utf-8') as f:
            f.write(category + " " + str(page) + "\n")
        
        time.sleep(2)
            

# get_content_from_major("tien-te-ngan-hang")

majors = ['tien-te-ngan-hang', 'quyen-dan-su','chung-khoan', 'so-huu-tri-tue', 'tai-chinh-nha-nuoc',
          'thu-tuc-to-tung', 'the-thao-y-te', 'giao-thong-van-tai', 'xuat-nhap-khau', 'doanh-nghiep',
          'lao-dong-tien-luong', 'bat-dong-san', 'vi-pham-hanh-chinh', 'bao-hiem', 'van-hoa-xa-hoi',
          'thuong-mai', 'trach-nhiem-hinh-su', 'xay-dung-do-thi', 'ke-toan-kiem-toan', 'thue-phi-le-phi',
          'dau-tu', 'dich-vu-phap-ly', 'tai-nguyen-moi-truong', 'cong-nghe-thong-tin', 'giao-duc',
          'bo-may-hanh-chinh', 'linh-vuc-khac']

categories = ['kinh-doanh-van-tai', 'nghia-vu-quan-su', 'thua-ke', 'thue-gia-tri-gia-tang',
              'bien-so-xe', 'thu-tuc-ly-hon', 'che-do-thai-san', 'so-bao-hiem-xa-hoi', 'the-bao-hiem-y-te',
              'tro-cap-thoi-viec', 'muc-luong-toi-thieu', 'giam-tru-gia-canh', 'thoi-han-su-dung-dat',
              'giay-khai-sinh', 'vung-nuoc-cang-bien',  'ngach-cong-chuc']


for major in majors:
    get_content_from_major(major)

# for category in categories:
#     get_content_from_category(category)


    
