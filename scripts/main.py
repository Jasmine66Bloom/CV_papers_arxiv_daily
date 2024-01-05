import datetime
import requests
import json
import arxiv
import re

import os 
base_path = os.path.dirname(__file__)
import sys 
sys.path.append(base_path)

base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"

cur_date = str(datetime.date.today() + datetime.timedelta(days = -1))
out_dir_name = cur_date.split('-')[0] + '-' + cur_date.split('-')[1]
out_dir = os.path.join(base_path, '../data/', out_dir_name)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)


def get_authors(authors, first_author=False):
    output = str()
    if first_author == False:
        output = ", ".join(str(author) for author in authors)
    else:
        output = authors[0]
    return output


def sort_papers(papers):
    output = dict()
    keys = list(papers.keys())
    keys.sort(reverse=True)
    for key in keys:
        output[key] = papers[key]
    return output

appeared_ids = []
def get_daily_papers(topic, query="nlp", max_results=2):
    """
    @param topic: str
    @param query: str
    @return paper_with_code: dict
    """

    # output
    content = dict()
    content_to_web = dict()

    # content
    output = dict()

    search_engine = arxiv.Search(
        query = query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    cnt = 0
    for result in search_engine.results():
        paper_id = result.get_short_id()
        paper_title = result.title
        paper_url = result.entry_id

        code_url = base_url + paper_id
        paper_abstract = result.summary.replace("\n", " ")
        paper_authors = get_authors(result.authors)
        paper_first_author = get_authors(result.authors, first_author=True)
        primary_category = result.primary_category

        publish_time = result.published.date()
        update_time = result.updated.date()

        if paper_id in appeared_ids:
            continue
        else:
            appeared_ids.append(paper_id)

        if primary_category != 'cs.CV': continue
        if str(publish_time) != cur_date: continue

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

        
        ver_pos = paper_id.find('v')
        if ver_pos == -1:
            paper_key = paper_id
        else:
            paper_key = paper_id[0:ver_pos]

        try:
            r = requests.get(code_url).json()
            # source code link
            if "official" in r and r["official"]:
                cnt += 1
                repo_url = r["official"]["url"]
                content[
                    paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|**[link]({repo_url})**|\n"
                content_to_web[
                    paper_key] = f"- **{update_time}**, **{paper_title}**, {paper_first_author} et.al., [PDF:{paper_id}]({paper_url}), **[code]({repo_url})**\n"
            else:
                content[
                    paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|null|\n"
                content_to_web[
                    paper_key] = f"- **{update_time}**, **{paper_title}**, {paper_first_author} et.al., [PDF:{paper_id}]({paper_url})\n"

        except Exception as e:
            print(f"exception: {e} with id: {paper_key}")

    data = {topic: content}
    data_web = {topic: content_to_web}
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
    """
    @param filename: str
    @return None
    """

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
        md_filename = out_dir + '/' + cur_date + '.md'
        # md_filename = "./docs/index.md"

        # clean README.md if daily already exist else create it
    with open(md_filename, "w+") as f:
        pass

    # write data into README.md
    with open(md_filename, "a+", encoding='utf-8') as f:

        if to_web == True:
            f.write("---\n" + "layout: default\n" + "---\n\n")

        f.write("## !UPDATED  -- " + DateNow + "\n\n")

        for keyword in data.keys():
            day_content = data[keyword]
            if not day_content:
                continue
            # the head of each part
            f.write(f"## {keyword}\n\n")

            if to_web == False:
                f.write("|Publish Date|Title|Authors|PDF|Code|\n" +
                        "|---|---|---|---|---|\n")
            else:
                f.write("| Publish Date | Title | Authors | PDF | Code |\n")
                f.write(
                    "|:---------|:-----------------------|:---------|:------|:------|\n")

            # sort papers by date
            day_content = sort_papers(day_content)

            for _, v in day_content.items():
                if v is not None:
                    f.write(v)

            f.write(f"\n")

    print("finished")


if __name__ == "__main__":
    data_collector = []
    data_collector_web = []

    keywords = dict()
    # keywords["CV"] = "cat:cs.CV"
    # keywords["CVCV"] = "cat:cs.CV" + "AND" + "\"Computer Vision\""
    # keywords["CVDM"] = "cat:cs.CV" + "AND" + "\"Diffusion Model\""
    # keywords["NLP"] = "NLP" + "OR" + "\"Natural Language Processing\""

    keywords["Transformer"] = "cat:cs.CV" + "OR" + "\"transformer\"OR\"attention\""
    keywords["模型压缩/优化"] = "cat:cs.CV" + "OR" + "\"NAS\"OR\"Network Architecture Search\"OR\"Pruning\"OR\"Quantization\"OR\"Knowledge Distillation\"OR\"Distillation\"OR\"model optimizer\""
    keywords["生成模型"] = "cat:cs.CV" + "OR" + "\"diffusion model\"OR\"GAN\"OR\"vae\"OR\"Generative Adversarial Networ\""
    keywords["多模态"] = "cat:cs.CV" + "OR" + "\"multi-modal\"OR\"Multimodal\"OR\"vae\"OR\"Generative Adversarial Networ\""
    keywords["分类/检测/识别/分割"] = "cat:cs.CV" + "OR" + "\"object detection\"OR\"object recognition\"OR\"recognition\"OR\"image classification\"OR\"video classification\"OR\"segment\"OR\"segmentation\""
    keywords["OCR"] = "cat:cs.CV" + "OR" + "\"ocr\"OR\"optical character recognition\""
    keywords["Zero/Few-Shot Learning"] = "cat:cs.CV" + "OR" + "\"zero-shot\"OR\"few-shot\""
    keywords["半监督/无监督学习"] = "cat:cs.CV" + "OR" + "\"Semi-supervised\"OR\"unsupervised\""
    keywords["3D相关"] = "cat:cs.CV" + "OR" + "\"3D\"OR\"3D detection\"OR\"3D reconstruction\"OR\"3D understanding\"\rendering\""
    keywords["图像理解"] = "cat:cs.CV" + "OR" + "\"Intrinsic Image Decomposition\"OR\"Intrinsic Image\"OR\"relighting\"OR\"recolor\"OR\"\image composition\""
    keywords["Nerf"] = "cat:cs.CV" + "OR" + "\"3D\"OR\"3D detection\"OR\"3D reconstruction\"OR\"3D understanding\"OR\"3d gaussian splatting\""
    keywords["GNN"] = "cat:cs.CV" + "OR" + "\"GNN\"OR\"Graph Neural Network\""
    keywords["其他"] = "cat:cs.CV"

    #


    for topic, keyword in keywords.items():
        print("Keyword: " + topic)
        if topic == '其他': max_results = 3000
        data, data_web = get_daily_papers(topic, query=keyword, max_results=500)
        data_collector.append(data)
        data_collector_web.append(data_web)

        print("\n")

    # update README.md file
    json_file = os.path.join(base_path, "tmp/cv-arxiv-daily.json")
    if ~os.path.exists(json_file):
        with open(json_file,'w')as a:
            print("create " + json_file)

    # update json data
    update_json_file(json_file, data_collector)
    # json data to markdown
    json_to_md(json_file)

    # # update docs/index.md file
    # json_file = "./cv-arxiv-daily-web.json"
    # if ~os.path.exists(json_file):
    #     with open(json_file,'w')as a:
    #         print("create " + json_file)

    # # # update json data
    # update_json_file(json_file, data_collector)
    # # json data to markdown
    # json_to_md(json_file, to_web=True)
