# SimAlign: Similarity Based Word Aligner
This project contains python wrappers to easily generate word alignments using SimALign.

* Paper: https://arxiv.org/pdf/2004.08728.pdf
* Official GitHub: https://github.com/cisnlp/simalign

## Batch size and hyperparameters
The default batch size (100) should be fine for most GPUs. If you get OOM errors, you can reduce it or run SimAlign in the CPU. If 
you want to modify the batch size edit line 66 of [generate_alignments.py](generate_alignments.py).
We use the itermax matching method, in our experimentation it was the method that produced the best results. 
If you want to modify the method to generate alignments edit line 65 of [generate_alignments.py](generate_alignments.py).
You can also modify other hyperparameters in this file. 

## Installation
See the official repository for installation instructions: https://github.com/cisnlp/simalign#installation-and-usage
In short, you can install the package using pip:
```commandline
pip install simalign
```
If you find problems with the installation you can try installing it directly from the source code:
```commandline
pip install --upgrade git+https://github.com/cisnlp/simalign.git#egg=simalign
```

You are ready to go when you can open a Python shell and import the package:
```python
import simalign
```

You can test the installation by running this Python code (source: https://github.com/cisnlp/simalign#installation-and-usage):
```python
from simalign import SentenceAligner

# making an instance of our model.
# You can specify the embedding model and all alignment settings in the constructor.
myaligner = SentenceAligner(model="bert", token_type="bpe", matching_methods="mai")

# The source and target sentences should be tokenized to words.
src_sentence = ["This", "is", "a", "test", "."]
trg_sentence = ["Das", "ist", "ein", "Test", "."]

# The output is a dictionary with different matching methods.
# Each method has a list of pairs indicating the indexes of aligned words (The alignments are zero-indexed).
alignments = myaligner.get_word_aligns(src_sentence, trg_sentence)

for matching_method in alignments:
    print(matching_method, ":", alignments[matching_method])
```
####Expected output:
```python
mwmf (Match): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
inter (ArgMax): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
itermax (IterMax): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
```


