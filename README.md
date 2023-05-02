# csc-583-search-project
## Hardware Requirements
The Python files in this for generating CLS embeddings from a Transformer network were run on a Google Collab VM with an NVidia GPU, and further processed offline on a desktop with 48GB of RAM. Some parts of this code may not run 
effectively on a system with less memory and may require you to tweak a `batchSize` setting 
`SentenceEmbeddings_CPU.py` and `SentenceEmbeddings.ipynb`


## Python Modules to install
This project was mostly built using Vanilla Python instead of a more complete data science distribution 
line Anaconda. To install the necessary Python packages used by this project, from the root directory 
run the following command

`pip install -r requirements.txt`

Alternatively, you can run the following series of pip commands

```
 pip install gensim
 pip install torch
 pip install transformers
 pip install smart_open
 pip install termcolor
 pip install annoy

```

Windows Users: in order to install annoy download `annoy-1.17.0-cp311-cp311-win_amd64.whl` from [https://www.lfd.uci.edu/~gohlke/pythonlibs/]( here ) as described at [https://www.programmersought.com/article/95834605670/]()

 Then copy it into the root directory of this repo on your local system and run `pip install annoy-1.17.0-cp311-cp311-win_amd64.whl`

## References 
https://nguyen-hoang-nguyen.medium.com/how-to-check-your-google-colab-session-for-allocated-resources-912b1af9b99a
### Word2Vec and Doc2Vec
https://github.com/clulab/gentlenlp/blob/main/notebooks/chap09_classification.ipynb
https://github.com/v1shwa/document-similarity
https://stackoverflow.com/questions/65852710/text-similarity-using-word2vec
https://www.codegram.com/blog/finding-similar-documents-with-transformers/

