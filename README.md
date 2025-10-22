<a href="https://www.fz-juelich.de/en/ice/ice-2"><img src="https://github.com/FZJ-IEK3-VSA/README_assets/blob/main/JSA-Header.svg?raw=True" alt="Forschungszentrum Juelich Logo" width="175px"></a>

# colorful-emoji-annotations

Easy to read and edit text annotations for NLP tasks. 

Using colorful emojis is an easy and effective way to annotate text. Emoji annotations are easy to read and edit without requiring specialized software. Simply use your preferred text editor to curate your data.

## Why emojis?
They are easy to spot, distinguish, and edit — and are fun to use! Data formats used to store annotations for sequence annotation tasks are often difficult for humans to read and are usually viewed and edited with specialized software. Using emojis makes annotations easily recognizable and editable in any text editor. Ideally, use emojis that resemble the entity type (e.g., 📆,⏰️,📍,🏛️,🎨, etc.) or that are of different colors (e.g., 🍎,🥝,🍊,🍌,🍉,🍇, etc.). 

Emoji annotations are:
* **Easy to setup**: No need for special software, just use your favorite text editor.
* **Easy to read**: Colors pop out and are easy to distinguish.
* **Easy to edit**: Edits are quick and easy because emojis are just one character to move per annotation boundary. In addition, you can use the search and replace function and other features of your favorite text editor to efficiently edit many annotations.

## Limitations
* Works only for text genres in which the emojis selected as annotation boundaries are unlikely to appear in the text.
* Because the same emoji is used as start and end markers, nested or overlapping annotations of the same entity type are not supported.

## Installation
To install the package, use pip
```bash
pip install git+https://github.com/FZJ-IEK3-VSA/emoji-annotation-tool.git
```
or clone the repository and install it manually
```bash
git clone 
cd colorful-emoji-annotations
mamba env create -f requirements.yml
mamba activate emoji_annotations_env
pip install -e .
```


## Supported tasks
Emoji annotations are best suited for tasks that are typically approached with sequence labeling, such as named entity recognition (NER). You can also use them for relation extraction, template filling, or event extraction, provided that you use relation-specific tagging and only annotate one n-ary relation, template, or event per record.


## Usage
Create a new emoji annotation object using whichever emoji mapping you prefer. A mapping is a dictionary that associates entity types with emojis.

```python
from colorful_emoji_annotations import EmojiAnnotator
emoji_mapping = {
        "artwork": "🎨",
        "painter": "👨‍🎨",
        "museum": "🏛️",
        "location": "📍",
        "year": "📆",
    }
emoji_nlp = EmojiAnnotator(emoji_mapping)
```
**Convert annotated text to plain text and annnoations as char offsets.**
```python
text = "The 🎨Mona Lisa🎨 is believed to have been painted by 👨‍🎨Leonardo da Vinci👨‍🎨 between 📆1503📆 and 📆1506📆 and is now displayed in the 📍🏛️Louvre🏛️, Paris📍."
plain_text, annotations = emoji_nlp.from_inline_annotations(text)
print(plain_text)
print(annotations)
```
```bash
The Mona Lisa is believed to have been painted by Leonardo da Vinci between 1503 and 1506 and is now displayed in the Louvre, Paris.
{'artwork': [(4, 13)], 'painter': [(50, 67)], 'year': [(76, 80), (85, 89)], 'location': [(118, 131)], 'museum': [(118, 124)]}
```

**Convert plain text and annotations back to annotated text.**
```python
annotated_text = emoji_nlp.to_inline_annotations(plain_text, annotations)
print(annotated_text)
```
```bash
The 🎨Mona Lisa🎨 is believed to have been painted by 👨‍🎨Leonardo da Vinci👨‍🎨 between 📆1503📆 and 📆1506📆 and is now displayed in the 📍🏛️Louvre🏛️, Paris📍.
```

If two emoji have the same character offset, the emoji that closes the active annotation is placed first. If the order was different in the original text, the order is not preserved (e.g., "🏛️📍Louvre🏛️, Paris📍" would become "📍🏛️Louvre🏛️, Paris📍").

**Use the command line to curate annotations** by integrating `emoji_nlp.get_user_feedback()` in a Python script. This function will prompt the user to confirm or edit the annotations in the text.
```bash
Computer says 🗯️

🌶️Andalusia🌶️ has a 🍊surface area🍊 of 🍏87,597🍏 🍓square kilometres🍓.

Correct? y/n
(To edit the n-th annotation, enter its number n, e.g. '3', press enter, use the arrow keys to move it, press enter to see the changes, and press enter again to confirm the changes. To delete all annotations press 'd'.)
```
```
User input: 3 
```
```
🌶️Andalusia🌶️ has a 🔻surface area🍊 of 🍏87,597🍏 🍓square kilometres🍓.
```
```
User input: → →
```
```
🌶️Andalusia🌶️ has a su🔻rface area🍊 of 🍏87,597🍏 🍓square kilometres🍓.

Correct? y/n
```


## Comparison of NER annotation formats
Comparing different NER annotation formats, we can see that the colorful emoji annotations are much easier to read and edit than the other formats. While this small example already makes the difference obvious, it becomes even more pronounced with larger datasets.

### _Colorful emoji annotations_
```txt
🏢U.N.🏢 official 🙋Ekeus🙋 heads for 📍Baghdad📍.
```

### _CoNLL 2003 NER format_
(https://www.cnts.ua.ac.be/conll2003/ner/)
```conll
U.N.         NNP  I-NP  I-ORG 
official     NN   I-NP  O 
Ekeus        NNP  I-NP  I-PER 
heads        VBZ  I-VP  O 
for          IN   I-PP  O 
Baghdad      NNP  I-NP  I-LOC 
.            .    O     O 
```

### _brat standoff format_
(https://brat.nlplab.org/standoff.html)

```brat
T1  Organization 0 3 U.N.
T2  Person 4 10 Ekeus
T3  Location 20 28 Baghdad
```

### _XML-based formats_
```xml	
<p><EM ID="1" CATEG="ORGANIZATION">U.N.</EM> official <EM ID="2" CATEG="PERSON">Ekeus</EM> heads for <EM ID="3" CATEG="LOCATION">Baghdad</EM>.</p>
```


## Development
To update the list of supported emojis, run
```bash
python src/emoji_annotations/scripts/update_emoji_list.py
```


## About Us 

<a href="https://www.fz-juelich.de/en/ice/ice-2"><img src="https://github.com/FZJ-IEK3-VSA/README_assets/blob/main/iek3-square.png?raw=True" alt="Institute image ICE-2" width="280" align="right" style="margin:0px 10px"/></a>

We are the <a href="https://www.fz-juelich.de/en/ice/ice-2">Institute of Climate and Energy Systems (ICE) - Jülich Systems Analysis</a> belonging to the <a href="https://www.fz-juelich.de/en">Forschungszentrum Jülich</a>. Our interdisciplinary department's research is focusing on energy-related process and systems analyses. Data searches and system simulations are used to determine energy and mass balances, as well as to evaluate performance, emissions and costs of energy systems. The results are used for performing comparative assessment studies between the various systems. Our current priorities include the development of energy strategies, in accordance with the German Federal Government’s greenhouse gas reduction targets, by designing new infrastructures for sustainable and secure energy supply chains and by conducting cost analysis studies for integrating new technologies into future energy market frameworks.

## Acknowledgements

The authors would like to thank the German Federal Government, the German state governments, and the Joint Science Conference (GWK) for their funding and support as part of the NFDI4Ing consortium. Funded by the German Research Foundation (DFG) – project number: 442146713. Furthermore, this work was supported by the Helmholtz Association under the program "Energy System Design".

<p float="left">
    <a href="https://nfdi4ing.de/"><img src="https://nfdi4ing.de/wp-content/uploads/2018/09/logo.svg" alt="NFDI4Ing Logo" width="130px"></a>&emsp;<a href="https://www.helmholtz.de/en/"><img src="https://www.helmholtz.de/fileadmin/user_upload/05_aktuelles/Marke_Design/logos/HG_LOGO_S_ENG_RGB.jpg" alt="Helmholtz Logo" width="200px"></a>
</p>
