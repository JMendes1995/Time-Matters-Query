
from newspaper import Article
from random import random
import random
from multiprocessing import Pool
from itertools import repeat
import requests
import multiprocessing
from itertools import chain

class ArquivoPT():
    def __init__(self, max_items=50, newspaper3k=False):
        self.max_items = max_items
        self.newspaper3k=newspaper3k

    def getResult(self, query,  domains=[], beginDate='', endDate='', title=False,snippet=True,fullContent=False, link=''):
        import time
        start_time = time.time()
        if not (domains):
            domains=['']
        else:
            random.shuffle(domains)

        with Pool(processes=multiprocessing.cpu_count()) as pool:
            results_by_domain = pool.starmap(self.getResultsByDomain,
                                             zip(domains, repeat(query),  repeat(beginDate), repeat(endDate), repeat(link)))

        results_flat_list = list(chain.from_iterable(results_by_domain))

        try:
            results_by_domain.remove({})
        except:
            pass

        with Pool(processes=multiprocessing.cpu_count()) as pool:
            result = pool.starmap(format_output,
                                             zip(results_flat_list, repeat(self.newspaper3k), repeat(title), repeat(snippet), repeat(fullContent)))
        domains_list = [item[1] for item in result]
        filter_domains_list = list(dict.fromkeys(domains_list))

        docs_info_list = [item[0] for item in result]

        all_results = []

        for dominio_list in [dominio_list for dominio_list in results_by_domain if dominio_list is not None]:
            all_results.extend(dominio_list)

        total_time = time.time( ) - start_time
        statistical_dict = search_statistics(total_time, len(docs_info_list), len(filter_domains_list), filter_domains_list)
        final_output=[statistical_dict, docs_info_list]

        return final_output

    def getResultsByDomain(self, domain, query, beginDate, endDate, link):
        if link == '':
                arquivo_pt = 'http://arquivo.pt/textsearch'
                payload = {'q': query,
                       'maxItems': self.max_items,
                       'siteSearch': domain,
                       'from': beginDate,
                       'to': endDate,
                       'itemsPerSite': self.max_items,
                       'fields': 'title,originalURL,linkToExtractedText,linkToNoFrame,linkToArchive,tstamp,date,siteSearch,snippet'}
                r = requests.get(arquivo_pt, params=payload, timeout=45)
                try:
                    contentsJSon = r.json( )
                except:
                    return {}

        else:
            r = requests.get(link)
            contentsJSon = r.json( )
        return contentsJSon['response_items']


def newspaper3k_get_text(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.text, article.summary


def format_output(item, newspaper3k, title, snippet, fullContent):
    import re
    fetched_domain = re.findall('https://(.+?)/|http://(.+?)/',item['originalURL'])
    domain = [ d for d in fetched_domain[0] if d != ""]
    result_tmp={}
    from Time_Matters_Query import normalization

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
            fullContentLenght_Arquivo = page.content.decode(encoding = 'UTF-8',errors = 'strict').replace('\xa0', '').replace('\x95', '')
            full_content_arquivo = normalization(fullContentLenght_Arquivo, contraction_expansion=False)
            result_tmp['fullContentLenght_Arquivo'] = full_content_arquivo
        except:
            result_tmp['fullContentLenght_Arquivo'] = ''
    try:
        if title:
            result_tmp['title'] = item['title'].replace('\xa0', '').replace('\x95', '')
        if snippet:
            snippet_content = normalization(item['snippet'], html_strip=True, accented_char_removal=False,
                                            contraction_expansion=False,
                                            text_lower_case=False, special_char_removal=False, remove_digits=False)

            result_tmp['snippet'] = snippet_content
        res= {'crawledDate': item['tstamp'],
              'url': item["linkToArchive"],
              'domain': domain[0]}
        result_tmp.update(res)
    except:
        return [{}, domain[0]]

    return [result_tmp, domain[0]]


def search_statistics(total_time, max_items, n_domains, domains):
    statistical_dict = {
       'time': total_time,
        'n_docs': max_items,
        'n_domains': n_domains,
        'domains': domains}
    return statistical_dict