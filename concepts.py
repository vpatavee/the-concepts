import json
import os
import re

from nltk import FreqDist, word_tokenize
from nltk.corpus import stopwords
from nltk.parse import stanford
from nltk.stem import WordNetLemmatizer

PATH_TO_STANFORD_PARSER = r"C:\Users\Wii\stanford-parser-full-2018-02-27\stanford-parser-full-2018-02-27"


def word_freq(parse_ppt):
    l = []
    set_of_stopwords = set(stopwords.words('english'))
    for page in parse_ppt:
        for text in page["text"]:
            for token in word_tokenize(text["text"]):
                if token not in set_of_stopwords and len(token) > 1:
                    l.append(token.lower())

    return FreqDist(l).most_common(20)


def lemmatize_concept(concept):
    lemmatizer = WordNetLemmatizer()
    res = ""
    for e in concept.split():
        res += lemmatizer.lemmatize(e) + " "
    return res.strip()


def clean_concepts(concept):
    concept = concept.lower()
    concept = re.sub("(^\d|[:,?\"./\{}\[\]])", "", concept).strip()
    articles = set(["a", "an", "the"])
    concept = lemmatize_concept(concept)
    concept = " ".join([e for e in concept.split() if e not in articles])
    set_of_stopwords = set(stopwords.words('english'))
    ans = []
    if not concept:
        return ans

    if "and" in concept:
        ans = concept.split(" and ")
    else:
        ans = [concept]
    ans = [e for e in ans if e not in set_of_stopwords and len(e) > 1 and len(e.split()) < 4 and not e.isdigit()]
    return ans


def get_NP(sent, parser):
    ans = []
    sent = sent.strip()
    if not sent:
        return ans
    sentences = parser.raw_parse_sents((sent, ""))
    for line in sentences:
        for e in line:
            for sub in e.subtrees():
                if sub.label() == "NP":
                    ans.append(" ".join(sub.leaves()))
    return ans


def is_sentence_contain_words(sent, words):
    for e in words:
        if e in word_tokenize(sent.lower()):
            return True
    return False


def lower_sentence(sent):
    sent_list = sent.split()
    res = sent_list[0] + " "
    for i in range(1, len(sent_list)):
        if sent_list[i].isupper():
            res += sent_list[i] + " "
        else:
            res += sent_list[i].lower() + " "
    return res.strip()


def get_index(parse_ppt, parser):
    concepts = {}
    pages = {}
    top_20 = [w[0] for w in word_freq(parse_ppt)]
    for page in parse_ppt:
        for text in page["text"]:
            sent = text["text"]
            sent = re.sub("[!()]", "", sent)
            # Skip sentence that does not contain most frequent words
            if not is_sentence_contain_words(sent, top_20):
                continue
            if text["type"] == "title":
                sent = lower_sentence(sent)

            concept_in_sent = set()
            for concept in get_NP(sent, parser):
                # Skip expression e.g. X=2
                if re.search("[\d=+]", concept):
                    continue
                for cleaned_concept in clean_concepts(concept):
                    concept_in_sent.add(cleaned_concept)

            # Indexing
            for cleaned_concept in concept_in_sent:
                concept_info = {"page": page["page"], "type": text["type"], "sentence": sent}
                page_info = {"concept": cleaned_concept, "location": text["type"]}
                if text["type"] == "body":
                    concept_info["level"] = text["level"]
                    page_info["sub_location"] = text["level"]
                if cleaned_concept in concepts:
                    concepts[cleaned_concept].append(concept_info)
                else:
                    concepts[cleaned_concept] = [concept_info]
                if page["page"] in pages:
                    pages[page["page"]].append(page_info)
                else:
                    pages[page["page"]] = [page_info]
    return concepts, pages


if __name__ == "__main__":
    os.environ['STANFORD_PARSER'] = PATH_TO_STANFORD_PARSER
    os.environ['STANFORD_MODELS'] = PATH_TO_STANFORD_PARSER
    parser = stanford.StanfordParser(
        model_path=r"C:\Users\Wii\stanford-parser-full-2018-02-27\stanford-parser-full-2018-02-27\edu\stanford\nlp\models\lexparser\englishPCFG.ser.gz")

    with open("parse_ppt.json", "r") as f:
        parse_ppt = json.load(f)
    idx, pages = get_index(parse_ppt, parser)
    json.dump(idx, open("index_with_level.json", "w"))
    json.dump(pages, open("concept_pages.json", "w"))



