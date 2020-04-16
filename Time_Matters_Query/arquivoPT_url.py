
from newspaper import Article
from random import random
import random
from multiprocessing import Pool
from itertools import repeat
import requests
from Time_Matters_Query.arquivoPT import newspaper3k_get_text, search_statistics

class ArquivoPT_url:
    def __init__(self, max_items=50, newspaper3k=False):
        self.max_items = max_items
        self.newspaper3k=newspaper3k

    def getResult(self, url='', beginDate='', endDate='', title=True,  fullContent=False):
        domain_list = []
        import time
        start_time = time.time()
        arquivo_pt = 'http://arquivo.pt/textsearch'
        payload = {'versionHistory': url,
                       'maxItems': self.max_items,
                       'from': beginDate,
                       'to': endDate,
                       'fields': 'title,originalURL,linkToExtractedText,linkToNoFrame,linkToArchive,tstamp,date,siteSearch,snippet'}
        r = requests.get(arquivo_pt, params=payload)
        contentsJSon = r.json()
        result_list = []

        import multiprocessing

        with Pool(processes=multiprocessing.cpu_count()) as pool:
            x = pool.starmap(format_output,
            zip(contentsJSon["response_items"], repeat(self.newspaper3k), repeat(title), repeat(fullContent)))

        for item in x:
            if item[0] != {}:
                result_list.append(item[0])
            if item[1] not in domain_list and 'www.'+item[1] not in domain_list:
                domain_list.append(item[1])

        total_time = time.time() - start_time

        statistical_dict = search_statistics(total_time, len(result_list), len(domain_list), domain_list)
        final_output = [statistical_dict, result_list]
        return final_output


def format_output(item, newspaper3k, title, fullContent):
    from urllib.parse import urlparse
    domain = urlparse(item['originalURL'])

    result_tmp={}

    if newspaper3k == True and fullContent == True:
        try:
            fullContentLenght_Newspaper3K, Summary_Newspaper3k = newspaper3k_get_text(item['linkToNoFrame'])
            result_tmp['fullContentLenght_Newspaper3K'] = fullContentLenght_Newspaper3K
            result_tmp['Summary_Newspaper3k'] = Summary_Newspaper3k
        except:
            result_tmp['fullContentLenght_Newspaper3K'] = ""
            result_tmp['Summary_Newspaper3k'] = ""

    elif newspaper3k == False and fullContent==True:
        try:
            page = requests.get(item["linkToExtractedText"])
            from Time_Matters_Query import normalization
            result_tmp['fullContentLenght_Arquivo'] = page.content.decode(encoding = 'UTF-8',errors = 'strict')
        except:
            result_tmp['fullContentLenght_Arquivo'] = ''
    try:
        if title:
            result_tmp['title'] = item['title']
        res= {'crawledDate': item['tstamp'],
              'url': item["linkToArchive"],
              'domain': domain.netloc}
        result_tmp.update(res)
    except:
        return [{}, domain.netloc]
    return [result_tmp, domain.netloc]
