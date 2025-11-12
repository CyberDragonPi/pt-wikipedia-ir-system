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

### Indexer

In order to build the functional search engine, several .json or .jsonl files were neccessary to produce during the indexing proces
```
    - documents_metadata.jsonl
    - documents_stats.jsonl
    - final_index.jsonl
    - forward_index.db
    - indexer_metadata.jsonl
    - offset_index.json
```

"documents_metadata.jsonl" contains global metadata of the processed text documents, doc_count, total_tokens, avg_doc_length.  
"documents_stats.jsonl" stores pairs of values in the key:value format, where key is the document_id (doc_id), while value is the length of the corresponding document.  
"final_index.jsonl" stores our inverted index, in the format term: postings_list, where postings_list is the tuple of (doc_id, freq). In order to satisfy the given memory condition, we had to stream our dataset in batches, with batch size set to 750 (out of maximum value of 1000). This allowed us to keep the memory around 1400MB, low enough for the given constraint of 2GB.





