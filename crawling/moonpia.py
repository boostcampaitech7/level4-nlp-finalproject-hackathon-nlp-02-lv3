import os
import time

from bs4 import BeautifulSoup
from crawler import Crawler
import pandas as pd
from selenium.webdriver.common.by import By


class MoonpiaCrawler(Crawler):
    def __init__(self, id=454596):
        super().__init__()
        self.url = f"https://novel.munpia.com/{id}"

    def get_novel_metadata(self):
        try:
            # detail-box 요소 찾기
            element = self.find_elements(By.CLASS_NAME, "detail-box")[0]
            html_content = element.get_attribute("outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")

            title = soup.select_one("div.title-wrap a").get_text(strip=True).replace("독점", "")
            author = soup.select_one("dl.meta-author.meta a.member-trigger strong").get_text(strip=True)

            meta_etc = soup.select("dl.meta-etc.meta")
            dates = meta_etc[0].find_all("dd")
            counts = meta_etc[1].find_all("dd")

            return {
                "title": title,
                "author": author,
                "작품등록일": dates[0].get_text(strip=True),
                "최근연재일": dates[1].get_text(strip=True),
                "연재수": int(counts[0].get_text().replace(" 회", "")),
                "조회수": int(counts[1].get_text().replace(",", "")),
                "추천수": int(counts[2].get_text().replace(",", "")),
                "글자수": int(counts[3].get_text().replace(",", "")),
            }
        except Exception as e:
            print(f"메타데이터 추출 중 오류 발생: {e}")
            return None

    def get_novel_content(self):
        try:
            # ENTRY-CONTENT 요소 찾기
            entry_content = self.find_element(By.ID, "ENTRY-CONTENT")
            html_content = entry_content.get_attribute("outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")

            subinfo = soup.find("div", {"class": "subinfo"})
            subinfo_text = subinfo.get_text(strip=True) if subinfo else ""

            tcontent = soup.find("div", {"class": "tcontent"})
            tcontent_text = tcontent.get_text(strip=True) if tcontent else ""

            return {"subinfo": subinfo_text, "tcontent": tcontent_text}
        except Exception as e:
            print(f"본문 추출 중 오류 발생: {e}")
            return None

    def move_to_next_page(self):
        try:
            next_button = self.find_element(By.CSS_SELECTOR, "#MOVEPAGE a.next")
            next_url = next_button.get_attribute("href")
            self.open_url(next_url)
            return True
        except Exception as e:
            print(f"다음 페이지 이동 중 오류 발생: {e}")
            return False

    def crawl(self):
        try:
            results = []
            # 메인 페이지 열기
            self.open_url(self.url)
            novel_info = self.get_novel_metadata()
            results.append(novel_info)

            # 첫 화 페이지로 이동
            entry_url = f"{self.url}/nvAct/entryFirstView"
            self.open_url(entry_url)

            # 3페이지까지 내용 수집
            contents = []
            for i in range(3):
                time.sleep(0.1)
                content = self.get_novel_content()
                if content:
                    contents.append(content)

                # 마지막 페이지가 아니면 다음 페이지로 이동
                if i < 2 and not self.move_to_next_page():
                    break

            results.append(contents)
            return results
        finally:
            self.close()


if __name__ == "__main__":
    crawler = MoonpiaCrawler()
    metadata_file = "novel_metadata.csv"
    content_file = "novel_content.csv"

    # 400000 ~ 402227
    ids = range(450000, 455500)
    for novel_id in ids:
        try:
            time.sleep(0.1)
            crawler = MoonpiaCrawler(id=novel_id)
            data = crawler.crawl()

            if not data or len(data) != 2:
                continue

            # 메타데이터 처리
            metadata = data[0]
            if metadata:
                metadata["id"] = novel_id
                metadata_df = pd.DataFrame([metadata])

                if os.path.exists(metadata_file):
                    existing_metadata = pd.read_csv(metadata_file)
                    metadata_df = pd.concat([existing_metadata, metadata_df], ignore_index=True)

                metadata_df.to_csv(metadata_file, index=False, encoding="utf-8-sig")

            # 컨텐츠 데이터 처리
            contents = data[1]
            if contents:
                content_rows = []
                for idx, content in enumerate(contents, 1):
                    content_row = {
                        "id": novel_id,
                        "chapter": idx,
                        "subinfo": content["subinfo"],
                        "tcontent": content["tcontent"],
                    }
                    content_rows.append(content_row)

                content_df = pd.DataFrame(content_rows)

                if os.path.exists(content_file):
                    existing_content = pd.read_csv(content_file)
                    content_df = pd.concat([existing_content, content_df], ignore_index=True)

                content_df.to_csv(content_file, index=False, encoding="utf-8-sig")

        except Exception as e:
            print(f"ID {novel_id} 처리 중 오류 발생: {e}")
            continue


"""
https://novel.munpia.com/id

1. 소설 ID 획득 && 소설 상세 페이지 이동
2-1. meta-etc meta로 작품 메타 정보 수집
2-2. STORY-BOX로 작품 소개, 태그 수집
3. 첫화 보기 클릭 && 첫화 페이지 이동
4. 페이지 ID 1화~5화까지 1씩 늘리며 데이터 수집 & 저장
5. 다음 소설 ID로 이동
"""

"""
input:
```
https://novel.munpia.com/454596
```

output:
```
{
    "title": "눈뜬 천재의 KPOP",
    "author": "경우勁雨",
    "작품등록일": "2025.01.15 14:48",
    "최근연재일": "2025.01.21 12:00",
    "연재수": 10,
    "조회수": 8764,
    "추천수": 572,
    "글자수": 51811
}
```
"""


"""
input:
```
https://novel.munpia.com/454596/nvAct/entryFirstView
```

output:
```
{'subinfo': '제 1 화 Prologue.', 'tcontent': '나는 앞이 보이지 않는 상태로 평생을 살았다...'}]
```
"""
