from deep_translator import GoogleTranslator
import sys
import datetime
import requests
import json
import arxiv
import re

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


def get_daily_papers(search_engine, algo_txt, algo_name=''):

    # output
    content = dict()
    content_to_web = dict()

    cnt = 0
    # print('looked paper: ', len(appeared_ids))
    for result in client.results(search_engine):

        paper_id = result.get_short_id()
        paper_title = result.title
        paper_url = result.pdf_url

        code_url = base_url + paper_id
        paper_abstract = result.summary.replace("\n", " ")
        paper_authors = get_authors(result.authors)
        paper_first_author = get_authors(result.authors, first_author=True)
        primary_category = result.primary_category

        publish_time = result.published.date()
        update_time = result.updated.date()

        if str(publish_time) != cur_date:
            continue

        if algo_name != '其他':
            if not found_keyword(paper_title, paper_abstract, algo_txt):
                continue

        if paper_id in appeared_ids:
            continue
        else:
            appeared_ids.append(paper_id)

        # print('/n**************')
        # print('paper_id: ', paper_id)
        # print('paper_title: ', paper_title)
        # print('paper_url: ', paper_url)
        # print('paper_abstract: ', paper_abstract)
        # print('paper_authors: ', paper_authors)
        # print('primary_category: ', primary_category)
        # print('publish_time: ', publish_time)
        # print('update_time: ', update_time)
        # print('code_url: ', code_url)

        paper_title_zh_cn = GoogleTranslator(
            source='en', target='zh-CN').translate(paper_title)
        # print('paper_title_zh_cn: ', paper_title_zh_cn)
        paper_abstract_zh_cn = GoogleTranslator(
            source='en', target='zh-CN').translate(paper_abstract)

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

        f.write("## !UPDATED  -- " + cur_date + "\n\n")

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

    # 写为 markdown 格式，微信公众号等
    md_filename_dir = os.path.join(base_path, 'local', out_dir_name)
    if not os.path.exists(md_filename_dir):
        os.makedirs(md_filename_dir)
    md_filename_path = os.path.join(md_filename_dir, cur_date + '.md')
    with open(md_filename_path, "w", encoding='utf-8') as f:
        f.write("# !UPDATED  -- " + cur_date + "\n\n")
        for keyword in data.keys():
            day_content = data[keyword]
            if not day_content:
                continue

            # sort papers by date
            day_content = sort_papers(day_content)

            f.write(f">## **{keyword}**")
            f.write("\n")
            f.write('>---')
            f.write("\n")

            cnt = 1
            # |Publish Date|Title|Title_CN|Authors|Paper Abstract|PDF|Code|
            for _, v in day_content.items():
                if v is not None:

                    v_list = v.split('|')

                    # f.write('**Publish Date:** ')
                    # f.write(v_list[1])
                    # f.write('<br />')
                    # f.write("\n")

                    f.write('>>**index:** ')
                    f.write(str(cnt))
                    f.write('<br />')
                    f.write("\n")
                    cnt += 1

                    f.write('**Title:** ')
                    f.write(v_list[2])
                    f.write('<br />')
                    f.write("\n")

                    f.write('**Title_cn:** ')
                    f.write(v_list[3])
                    f.write('<br />')
                    f.write("\n")

                    f.write('**Authors:** ')
                    f.write(v_list[4])
                    f.write('<br />')
                    f.write("\n")

                    # 摘要
                    abs_en = "" + v_list[5]
                    cur_v = "<details><summary>原文: </summary>{}</details>".format(
                        abs_en)
                    f.write('**Abstract:** ')
                    f.write(cur_v)
                    # f.write('<br />')
                    f.write("\n")

                    abs_cn = "" + v_list[6]
                    cur_v = "<details><summary>译文: </summary>{}</details>".format(
                        abs_cn)
                    f.write('**Abstract_cn:** ')
                    f.write(cur_v)
                    # f.write('<br />')
                    f.write("\n")

                    f.write('**PDF:** ')
                    # f.write(v_list[4])
                    cur_t = v_list[7].split(
                        ']')[-1].replace('(', '<').replace(')', '>')
                    f.write(cur_t)
                    f.write('<br />')
                    f.write("\n")

                    f.write('**Code:** ')
                    # f.write(v_list[5])
                    cur_t = v_list[8].split(
                        ']')[-1].replace('(', '<').replace(')', '>')
                    f.write(cur_t)
                    f.write('<br />')
                    f.write("\n")

            f.write(f"\n")

    print("finished")


if __name__ == "__main__":

    print('start query arxiv paper')
    query = "cat:cs.CV"
    search_engine = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    found_num = len(list(client.results(search_engine)))
    print('found papers: ', found_num)

    keywords = dict()

    keywords["各类学习方式"] = ['zero-shot', 'few-shot', 'zero shot', 'few shot''Semi-supervised',
                          'unsupervised', 'Continual Learning', 'Incremental Learning', 'Contrastive Learning']
    keywords["分类/检测/识别/分割"] = ['Classification', 'image classification', 'video classification',
                               'object detection', 'Detection', 'object recognition', 'recognition',
                               'segment', 'segmentation', 'superresolution', 'super resolution', 'Object Tracking']
    keywords["OCR"] = ['optical character recognition', 'ocr']
    keywords["模型压缩/优化"] = ['NAS', 'Network Architecture Search', 'Pruning', 'Quantization',
                           'Knowledge Distillation', 'Distillation', 'model optimizer']
    keywords["Nerf"] = [
        "Nerf", 'Neural Radiance Fields', '3d gaussian splatting']
    keywords["生成模型"] = ['diffusion model', 'GAN',
                        'vae', 'Generative Adversarial Networ', 'generative model']
    keywords["多模态"] = ['multi-modal', 'Multimodal',
                       'mllm', 'vqa', 'vision question answer']
    keywords["LLM"] = ['llm', 'language large model']
    keywords["Transformer"] = ['transformer', 'attention', 'transformation'
                               'self-attention', 'cross-attention', 'cross attention']
    keywords["3D/CG"] = ["3D", '3D detection', '3D reconstruction', '3D understanding',
                         'rendering', 'Computer Graphics', 'Modeling', 'Animation', 'Interactive graphics']
    keywords["图像理解"] = ['Intrinsic Image Decomposition', 'Intrinsic Image', 'relighting',
                        'recolor', 'image composition', 'normal estimation', 'depth estimation', 'lighting']
    keywords["GNN"] = ["GNN", 'Graph Neural Network', 'relational reasoning']
    keywords["其他"] = ""

    data_collector = []
    for algo_name, algo_txt in keywords.items():
        print("Keyword: ", algo_name)
        data, data_web = get_daily_papers(
            search_engine, algo_txt, algo_name=algo_name)
        data_collector.append(data)
        print("\n")

    # update README.md file
    json_file = os.path.join(base_path, "tmp/cv-arxiv-daily.json")
    if ~os.path.exists(json_file):
        with open(json_file, 'w')as a:
            print("create " + json_file)

    # update json data
    update_json_file(json_file, data_collector)
    # # json data to markdown
    json_to_md(json_file)
