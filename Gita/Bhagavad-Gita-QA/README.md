---
configs:
- config_name: English
  data_files:
  - split: train
    path: English/english.csv
  default: true
- config_name: Hindi
  data_files:
  - split: train
    path: Hindi/hindi.csv
- config_name: Gujarati
  data_files:
  - split: train
    path: Gujarati/gujarati.csv
license: mit
task_categories:
- question-answering
- text-generation
language:
- en
- hi
- gu
tags:
- Spirituality
- Mythology
- Hinduism
- India
- Multillingual
size_categories:
- 10K<n<100K
---

# Bhagavad-Gita-QA-Multilingual

<p align="center">
  <img src="Krishna.png" alt="Dataset Banner" width="60%" style="border-radius:15px;" />
</p>

## Dataset Summary

**Bhagavad-Gita-QA**, is a carefully structured verse-aligned dataset that brings the timeless wisdom of the Bhagavad Gita into a modern question–answer framework.

This is the **first open dataset** that provides verse-level Q&A for the Gita with questions in **Hindi** and **Gujarati** along with English. This is not just a technical resource but also a cultural bridge, enabling new ways of studying, teaching, and exploring the Gita across languages.

The dataset was **synthetically generated using GPT-4.1**, using source dataset:[Bhagavad-Gita Dataset](https://huggingface.co/datasets/JDhruv14/Bhagavad-Gita_Dataset). 

After automated generation, entries were **manually reviewed** and **manually rectified** to reduce hallucination and improve faithfulness to the scripture’s intent.

---

## Key Features

- Verse-by-verse, question-rich — each verse spawns five purposeful questions to illuminate multiple reading modalities.
- First dataset to robustly include Hindi & Gujarati Q&A — both languages are independently authored, not translations, offering original cultural lenses on the same verses.
- Each verse is the seed for five distinct questions designed to elicit literal facts, summaries, lessons, philosophical inquiries, and attributional context.

## Citation
If you use this dataset, please cite it as:
```
@dataset{JDhruv14-Bhagavad-Gita-QA,
  title     = {Bhagavad-Gita-QA},
  author    = {Dhruv Jaradi},
  year      = {2025},
  url       = {https://huggingface.co/datasets/JDhruv14/Bhagavad-Gita-QA}
}
```