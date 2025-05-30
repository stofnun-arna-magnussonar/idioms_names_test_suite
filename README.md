# Idiomatic Expressions and Proper Names for English→Icelandic (WMT24 test suite submission)

This repo contains the submission of the Árni Magnússon Institute's team to the WMT24 test suite subtask, focusing on idiomatic expressions and proper names for the English→Icelandic translation direction.

Intuitively and empirically, idioms and proper names are known to be a significant challenge for modern translation models. We create two different test suites, described below.

## Idiomatic Expressions

The test suite in `idioms` evaluates the competency of MT systems in translating common English idiomatic expressions, as well as testing whether systems can distinguish between those expressions and the same phrases when used in a literal context. We consider 198 English expressions and a total of 397 ‘idiomatic’ examples and 201 ‘literal’ examples. 

To evaluate the models’ performance, we construct two ‘positive’ sets of Icelandic word forms or multiword expressions for each idiom. One set contains words that we would expect to find in a literal translation of the phrase, the other words or phrases that could be expected to appear in a suitable, non-literal translation of the idiomatic expression. In many cases, we also construct ‘negative’ sets of words that instantly lead to a sentence being marked incorrect, such as the Icelandic words for “weather” or “pink” for idiomatic translations of the phrases “under the weather” and “in the pink”. 

The idioms we used are listed in `idioms/data/idioms.json`, along with original English text examples and the positive and negative sets of words or phrases. The Icelandic translations from the systems submitted to this subtask can be found in `idioms/data/wmt24_translations.json`. Our script `idioms/score_idioms.py` scores these by marking a translation correct if it contains any of the words in the set of‘positive’ words (in any lexical form) and it contains none of the words in the set of ‘negative’ words.

As described in [our paper](https://arxiv.org/abs/2410.03394), we also manually reviewed a subset of the translations. The output of our manual review can be found in `idioms/human_evaluation/human_evaluation.tsv` and the scores according to that review are shown by running `score_manual_evaluation.py`.

## Proper Names

The test suite in `names` consists of 52 place names that should be translated into their Icelandic exonyms (and correctly inflected) and 45 pairs of Icelandic names that share a surface form between the male and female variants, so that incorrect translations impact meaning as well as readability. 

The translations of our proper names suite can be scored with the script `names/score_names.py`. The translations have been lemmatized using a lemmatizer for Icelandic and can be found in `names/translations_lemmatized`. For the Icelandic given names, the script compares them with a reference of which Icelandic lemmas should appear in the translation and in which grammatical form, `people_names_gold.txt` See our paper for discussion on the limitations of our method.

# Citation

If these test suites are of some use to you in your work, please cite:

```bibtex
@inproceedings{armannsson-etal-2024-killing,
    title = "Killing Two Flies with One Stone: An Attempt to Break {LLM}s Using {E}nglish-{I}celandic Idioms and Proper Names",
    author = "{\'A}rmannsson, Bjarki  and
      Hafsteinsson, Hinrik  and
      Jasonarson, Atli  and
      Steingr{\'i}msson, Stein{\th}{\'o}r",
    editor = "Haddow, Barry  and
      Kocmi, Tom  and
      Koehn, Philipp  and
      Monz, Christof",
    booktitle = "Proceedings of the Ninth Conference on Machine Translation",
    month = nov,
    year = "2024",
    address = "Miami, Florida, USA",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.wmt-1.31/",
    doi = "10.18653/v1/2024.wmt-1.31",
    pages = "451--458",
}
```
