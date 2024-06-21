Running the scraper will save the information about almost every game in the steam store into a json file.
The json file contains:
- title
- price (original price)
- discount_original (discounted price)
- release (release date)
- tags (categories/genres)
- link (store page)
- image

Note: The script scrapes games of ANY kind, including NSFW(!!!).
      This can be changed by using the GameTagDic.py to exclude any games with NSFW tags from the final result json file.
