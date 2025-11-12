# PROJECT REPORT

## Building inverted index

### Tokenizer
The first step towards building the inverted index (or indexer whose job is to produce the inverted and forward index) was to create suitable input data for the indexer. Or, to tokenize all the words to produce terms that should serve as key values in the inverted index. To achieve the most efficient text processing with the tokenizer, the following operation order was established:
```
    - set text to lowercase
    - remove URLs (if set as the operation to conduct)
    - remove emails (if set as the operation to conduct)
    - split the text into python list of tokens list[str]
    - separate alphanumeric tokens (if set as the operation to conduct)
    - remove numbers (fully numeric tokens, if set as the operation to conduct)
    - remove the tokens with the length less than threshold
    - removing the stopwords (if set as the operation of the conflict)
    - stemming of the words (if set as the operation to conduct)
```

Additionaly, in order to reduce the time neccessary to produce the inverted index, we have decided to use pre-compiled REGEXs for the URLs and e-mails, as 
well as storing 100_000 most recent stem terms by using lru_cache. Those modifications reduced the neccessary time to produce stemmed inverted index from 60 minutes to 40 minutes.

Default settings that we have chosen for our tokenizer were following:
```
    - lowercase True
    - remove URLs True
    - remove emails True
    - separate alphanumeric True
    - remove numbers True
    - token length threshold 1
    - stemmer True
    - stopwords False
```





