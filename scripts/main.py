import sys
import datetime
import requests
import json
import arxiv
import re

from zhipuai import ZhipuAI

import os
base_path = os.path.dirname(__file__)
sys.path.append(base_path)


base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"

max_results = 500

cur_date = str(datetime.date.today() + datetime.timedelta(days=-1))
out_dir_name = cur_date.split('-')[0] + '-' + cur_date.split('-')[1]
out_dir = os.path.join(base_path, '../data/', out_dir_name)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

client = arxiv.Client()

api_key = '1e8f0dd1b174e7b06bb3bce603856f62.qY4xvp6L8wEOJlRN'
zp_client = ZhipuAI(api_key=api_key)  # 填写您自己的APIKey

prompt = '你是一个翻译专家，你的任务是把AI技术论文的英文标题翻译为中文。\
    翻译结果必须准确、凝练、具备算法技术专业性。\
    算法相关的缩写、专有词语、简称，不需要翻译。\
    直接输出翻译后的中文标题，除了中文标题以外的其他任何内容都不要，只能输出一行。'


def call_llm(cont):
    response = zp_client.chat.completions.create(
        model="glm-4-flash",  # 填写需要调用的模型编码
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "英文为：%s" % cont}
        ],
    )
    resp = response.choices[0].message
    return resp.content


def get_authors(authors, first_author=False):
    output = str()
    if first_author == False:
        output = ", ".join(str(author) for author in authors)
    else:
        # output = authors[0]
        if len(authors) > 10:
            authors = authors[0:10]
            authors.append('et.al.')
        output = ", ".join(str(author) for author in authors)
        # if len(output) > 3:
        #     output = authors[0:3]
    return output


def sort_papers(papers):
    output = dict()
    keys = list(papers.keys())
    keys.sort(reverse=True)
    for key in keys:
        output[key] = papers[key]
    return output


def found_keyword(title, abstract, keys):
    for key in keys:
        if key.lower() in title.lower() or key.lower() in abstract.lower():
            return True
    return False


appeared_ids = []


def get_daily_papers(search_result_list, algo_txt, algo_name=''):

    # output
    content = dict()
    content_to_web = dict()

    cnt = 0
    # print('looked paper: ', len(appeared_ids))
    for result in search_result_list:

        paper_id = result['paper_id']
        paper_title = result['title'].replace('|', '').replace("\n", " ")
        while "\n" in paper_title:
            paper_title = paper_title.replace("\n", " ")
        paper_url = result['link'].replace('abs', 'pdf')

        code_url = base_url + paper_id
        paper_abstract = result['summary'].replace("\n", " ").replace('|', '')
        while "\n" in paper_abstract:
            paper_abstract = paper_abstract.replace("\n", " ")
        # paper_authors = result['authors']
        # paper_first_author = result['authors']
        paper_authors = get_authors(result['authors']).replace('|', '')
        paper_first_author = get_authors(
            result['authors'], first_author=True).replace('|', '')
        # primary_category = result.primary_category

        publish_time = result['update_time']
        update_time = result['update_time']

        if str(publish_time) != cur_date:
            continue

        if algo_name != '其他':
            if not found_keyword(paper_title, paper_abstract, algo_txt):
                continue

        if paper_id in appeared_ids:
            continue
        else:
            appeared_ids.append(paper_id)

        paper_title_zh_cn = call_llm(paper_title)
        while "\n" in paper_title_zh_cn:
            paper_title_zh_cn = paper_title_zh_cn.replace("\n", " ")
        # paper_abstract_zh_cn = GoogleTranslator(
        #     source='en', target='zh-CN').translate(paper_abstract)
        paper_abstract_zh_cn = ''

        ver_pos = paper_id.find('v')
        if ver_pos == -1:
            paper_key = paper_id
        else:
            paper_key = paper_id[0:ver_pos]
        cnt += 1

        try:
            r = requests.get(code_url).json()
            # source code link
            if "official" in r and r["official"]:
                repo_url = r["official"]["url"]
                # 'et.al.' -> ''
                content[
                    paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_title_zh_cn}|{paper_first_author}|{paper_abstract}|{paper_abstract_zh_cn}|[{paper_id}]({paper_url})|**[link]({repo_url})**|\n"
                content_to_web[
                    paper_key] = f"- **{update_time}**, **{paper_title}**, {paper_first_author}, [PDF:{paper_id}]({paper_url}), **[code]({repo_url})**\n"
            else:
                content[
                    paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_title_zh_cn}|{paper_first_author}|{paper_abstract}|{paper_abstract_zh_cn}|[{paper_id}]({paper_url})|null|\n"
                content_to_web[
                    paper_key] = f"- **{update_time}**, **{paper_title}**, {paper_first_author}, [PDF:{paper_id}]({paper_url})\n"
        except Exception as e:
            print(f"exception: {e} with id: {paper_key}")

    print('found num: ', cnt)

    data = {algo_name: content}
    data_web = {algo_name: content_to_web}
    return data, data_web


def update_json_file(filename, data_all):
    with open(filename, "r") as f:
        content = f.read()
        if not content:
            m = {}
        else:
            m = json.loads(content)

    json_data = m.copy()

    # update papers in each keywords
    for data in data_all:
        for keyword in data.keys():
            papers = data[keyword]

            if keyword in json_data.keys():
                json_data[keyword].update(papers)
            else:
                json_data[keyword] = papers

    with open(filename, "w") as f:
        json.dump(json_data, f)


def json_to_md(filename, to_web=False):

    DateNow = datetime.date.today()
    DateNow = str(DateNow)
    DateNow = DateNow.replace('-', '.')

    with open(filename, "r") as f:
        content = f.read()
        if not content:
            data = {}
        else:
            data = json.loads(content)

    if to_web == False:
        # md_filename = "README.md"
        md_filename = out_dir + '/' + cur_date + '.md'
    else:
        # md_filename = out_dir + '/' + cur_date + '.md'
        md_filename = "README.md"

        # clean README.md if daily already exist else create it
    with open(md_filename, "w+") as f:
        pass

    # write data into README.md
    with open(md_filename, "a+", encoding='utf-8') as f:

        if to_web == True:
            f.write("---\n" + "layout: default\n" + "---\n\n")

        # f.write("## [UPDATED]--**" + cur_date + "** (Publish Time))\n\n")
        f.write("## [UPDATED!] **" + cur_date + "** (Publish Time)\n\n")

        for keyword in data.keys():
            day_content = data[keyword]
            if not day_content:
                continue
            # the head of each part
            f.write(f"## {keyword}\n\n")

            # add |{paper_abstract}|{paper_abstract_zh_cn}
            if to_web == False:
                f.write("|Publish Date|Title|Title_CN|Authors|PDF|Code|\n" +
                        "|---|---|---|---|---|---|\n")
            # else:
            #     f.write("| Publish Date | Title | Authors | PDF | Code |\n")
            #     f.write(
            #         "|:---------|:-----------------------|:---------|:------|:------|\n")

            # sort papers by date
            day_content = sort_papers(day_content)

            for _, v in day_content.items():
                if v is not None:
                    # example: [2401.02278v1](http://arxiv.org/abs/2401.02278v1)
                    v_list = v.split('|')
                    # 5, 6 分别表示中英文摘要
                    valid_index = [1, 2, 3, 4, 5, 6, 7, 8]

                    pdf_url = v_list[7].split(
                        ']')[-1].replace('(', '<').replace(')', '>')
                    v_list[7] = pdf_url

                    new_v = ''
                    for idx in valid_index:
                        cur_v = v_list[idx]

                        if idx in [5, 6]:
                            continue
                        # if idx == 5:
                        #     abs = "原文: " + v_list[idx]
                        #     cur_v = "<details> <summary>abstract</summary>{}</details>".format(abs)
                        # if idx == 6:
                        #     abs = "译文: " + v_list[idx]
                        #     cur_v = "<details> <summary>abstract</summary>{}</details>".format(abs)

                        if idx == 1:
                            new_v = cur_v
                        else:
                            new_v = new_v + '|' + cur_v
                        # new_v = "|".join(vv for vv in v_list)
                    new_v += '\n'
                    f.write(new_v)

            f.write(f"\n")

    print("finished")


def search_arxiv():

    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    # Search parameters
    search_query = 'cat:cs.CV'  # search for electron in all fields
    # search_query = 'all:cs.CV'  # search for electron in all fields
    start = 0                       # start at the first result
    total_results = max_results              # want 20 total results
    results_per_iteration = max_results       # 5 results at a time
    wait_time = 1                   # number of seconds to wait beetween calls

    print('Searching arXiv for %s' % search_query)

    result_list = []
    idx = 0
    for i in range(start, total_results, results_per_iteration):

        # print("Results %i - %i" % (i, i+results_per_iteration))

        query = 'search_query=%s&sortBy=lastUpdatedDate&sortOrder=descending&start=%i&max_results=%i' % (
            search_query, i, results_per_iteration)
        # query = 'search_query=%s&start=%i&max_results=%i&sortOrder=descending' % (
        #     search_query, i, results_per_iteration)

        # perform a GET request using the base_url and query
        response = urllib.request.urlopen(base_url+query).read()

        # parse the response using feedparser
        feed = feedparser.parse(response)

        # Run through each entry, and print out information
        for entry in feed.entries:
            # print('idx: ', idx)
            cur_entry = {}

            paper_id = entry.id.split('/abs/')[-1]
            title = entry.title
            link = entry.link
            update_time = entry.updated.split('T')[0]
            summary = entry.summary
            # summary = ''
            authors = [name['name'] for name in entry.authors]
            # arxiv_comment = entry.arxiv_comment

            # print('\n############### %d'% idx)
            # print('paper_id: ', paper_id)
            # print('title: ', title)
            # print('link: ', link)
            # print('update_time: ', update_time)
            # print('summary: ', summary)
            # print('authors: ', authors)

            cur_entry['paper_id'] = paper_id
            cur_entry['title'] = title
            cur_entry['link'] = link
            cur_entry['update_time'] = update_time
            cur_entry['summary'] = summary
            cur_entry['authors'] = authors

            result_list.append(cur_entry)
            idx += 1

    return result_list


if __name__ == "__main__":

    print('start query arxiv paper')
    search_result_list = search_arxiv()
    print('found papers: ', len(search_result_list))

    keywords = dict()

    keywords["分类/检测/识别/分割"] = ['Classification', 'image classification', 'video classification',
                               'object detection', 'Detection', 'object recognition', 'recognition',
                               'segment', 'segmentation', 'superresolution', 'super resolution', 'Object Tracking']
    keywords["模型压缩/优化"] = ['NAS', 'Network Architecture Search', 'Pruning', 'Quantization',
                           'Knowledge Distillation', 'Distillation', 'model optimizer']
    keywords["OCR"] = ['optical character recognition', 'ocr']

    keywords["生成模型"] = ['diffusion model', 'GAN',
                        'vae', 'Generative Adversarial Networ', 'generative model']
    keywords["多模态"] = ['multi-modal', 'Multimodal',
                       'mllm', 'vqa', 'vision question answer']
    keywords["LLM"] = ['llm', 'language large model']
    keywords["Transformer"] = ['transformer', 'attention', 'transformation'
                               'self-attention', 'cross-attention', 'cross attention']

    keywords["Nerf"] = ["Nerf", 'Neural Radiance Fields']
    keywords["3DGS"] = ['3d gaussian splatting', 'gaussian splatting']
    keywords["3D/CG"] = ["3D", '3D detection', '3D reconstruction', '3D understanding',
                         'rendering', 'Computer Graphics', 'Modeling', 'Animation', 'Interactive graphics']

    keywords["各类学习方式"] = ['zero-shot', 'few-shot', 'zero shot', 'few shot', 'Semi-supervised',
                          'unsupervised', 'Continual Learning', 'Incremental Learning', 'Contrastive Learning']

    keywords["GNN"] = ["GNN", 'Graph Neural Network', 'relational reasoning']
    keywords["图像理解"] = ['Intrinsic Image Decomposition', 'Intrinsic Image', 'relighting',
                        'recolor', 'image composition', 'normal estimation', 'depth estimation', 'lighting']

    keywords["其他"] = ""

    data_collector = []
    for algo_name, algo_txt in keywords.items():
        print("Keyword: ", algo_name)
        data, data_web = get_daily_papers(
            search_result_list, algo_txt, algo_name=algo_name)
        data_collector.append(data)
        print("\n")

    # update README.md file
    json_file = os.path.join(base_path, "tmp/cv-arxiv-daily.json")
    if not os.path.exists(json_file):
        with open(json_file, 'w')as a:
            print("create " + json_file)

    # update json data
    update_json_file(json_file, data_collector)
    # # json data to markdown
    json_to_md(json_file)
