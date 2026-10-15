# RAG Retrieval Evaluation

## 1. Objective

The purpose of this evaluation is to compare two retrieval approaches
used in the AI Notebook Assistant.

The comparison focuses on retrieval relevance, response time,
answer quality, and citation accuracy.

## 2. Experimental Setup

### Source Document

The evaluation uses a single text document containing explanations
of machine learning, neural networks, natural language processing,
retrieval-augmented generation, and retrieval evaluation.

### Test Questions

Six questions are used to test factual retrieval, multi-step explanations,
concept differentiation, cross-section reasoning, specific technical
details, and evaluation terminology.

### Retrieval Approaches

- Approach A: [Name and description]
- Approach B: [Name and description]

### Configuration

- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector database:** ChromaDB
- **Number of retrieved chunks:** 3 (`top_k = 3`)
- **Chunking configuration:** LangChain text splitter; chunk size and overlap need to be verified against the implementation.
- **Language model:** `llama-3.3-70b-versatile` (Groq)
- **Test environment:** Local development environment

## 3. Evaluation Criteria

### Retrieval Relevance

Whether the retrieved chunks contain information needed to answer
the question.

### Answer Quality

Whether the generated answer is correct, relevant, complete, and
supported by the retrieved evidence.

### Citation Accuracy

Whether the cited sources correctly identify the evidence supporting
the answer.

### Latency

Retrieval latency is measured separately from total answer-generation
latency whenever the application exposes both measurements.

## 4. Results

### Question 1

**Question:** What are the three common approaches to machine learning, and how does supervised learning differ from unsupervised learning?

**Expected evidence:** ai_research_notes.txt

**Approach A:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick.
- Answer: 
The notes list three common approaches to machine learning:

1. **Supervised learning**  
2. **Unsupervised learning**  
3. **Reinforcement learning**

**How supervised learning differs from unsupervised learning**

- **Supervised learning** works with **labeled training data**. Each example in the dataset includes the correct output (e.g., an image labeled “cat” or “dog”), and the model learns to map inputs to those given labels so it can predict the correct label for new, unseen data.

- **Unsupervised learning** works with **unlabeled data**. Because there are no explicit target labels, the model’s goal is to discover hidden structure in the data—such as grouping similar items together (clustering) or finding underlying patterns (dimensionality reduction).
- Answer quality: I think this answers the question clearly with nice example. I hope there was more explanation on Reinforcement learning.
- Citation quality: Good but could be better since they only state that those information is from note.

**Approach B:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick but a little bit lower compare to approach A
- Answer:
The notes list **three common approaches to machine learning**:

1. **Supervised learning**  
2. **Unsupervised learning**  
3. **Reinforcement learning**

**How supervised learning differs from unsupervised learning**

- **Supervised learning** trains a model on **labeled data**—each training example includes the correct output (e.g., images labeled “cat” or “dog”). The model learns to map inputs to those known outputs so it can predict labels for new, unseen data.

- **Unsupervised learning** works with **unlabeled data**. Since there are no explicit target labels, the model’s goal is to discover underlying structure, such as grouping similar items (clustering) or extracting hidden features, rather than predicting a predefined label.
- Answer quality: Good. It is basically the same answer quality as option A.
- Citation quality: Good. It is basically the same quality as option A.

**Comparison:** Option B tool slightly longer but answers were the bacially the same.


### Question 2

**Question:** Explain how a RAG system processes a user’s question before generating an answer.
**Expected evidence:** ai_research_notes.txt

**Approach A:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick
- Answer:
A Retrieval‑Augmented Generation (RAG) system follows a defined pipeline that turns a user’s query into a grounded answer:

1. **Question embedding** – When the user asks a question, the system first converts that question into a numerical vector (an *embedding*) that captures its semantic meaning.  
2. **Similarity search** – The question embedding is then used to query a *vector database* that stores embeddings of previously‑ingested document passages. The database returns the passages whose vectors are most similar to the query vector.  
3. **Passage retrieval** – Those retrieved passages (often short chunks created during the earlier *chunking* step) are handed to the language model as additional context.  
4. **Answer generation** – The language model generates its response, conditioning on both the original question and the retrieved passages.  

In short, a RAG system first **embeds** the user’s question, **retrieves** semantically similar document chunks from a vector store, and then **generates** an answer that is informed by that retrieved evidence. This process helps ground the answer in the specific collection of documents, although the system still does not guarantee that the final answer is fully correct.
- Answer quality: Good answer but very short compare to option B.
- Citation quality: Option B had proper citation that tells where exactly AI refered to answer the question.

**Approach B:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Slightly longer than option A
- Answer:
**How a Retrieval‑Augmented Generation (RAG) system handles a user’s question**

1. **Document preparation (offline)**  
   * *Ingestion & text extraction* – The system first pulls in the source documents and extracts the raw text.  
   * *Chunking* – Long documents are split into smaller, manageable passages (the notes call this “chunking”).  
   * *Embedding generation* – Each passage is transformed into a numerical vector (an **embedding**) that captures its semantic meaning.  
   * *Vector storage* – The embeddings are stored in a vector database that can perform fast similarity searches.  

2. **Question processing (online)**  
   * When a user asks a question, the question itself is turned into an embedding, just like the document chunks.  
   * The vector database is queried with this question embedding to find passages whose embeddings are **semantically similar** to the question.  

3. **Retrieval of relevant context**  
   * The top‑ranking passages (the “retrieved passages”) are returned to the system. These passages represent the external knowledge that is most likely to help answer the query.  

4. **Answer generation**  
   * The retrieved passages are fed to the language model **as context**.  
   * The model then generates a response that is **grounded** in the provided passages, rather than relying solely on its internal knowledge.  

5. **Limitations**  
   * Even though the answer is based on retrieved text, the system **does not guarantee correctness**; it may still retrieve irrelevant passages or generate statements that aren’t fully supported by the context (Source 1, lines 1‑8; Source 5).  

In short, a RAG pipeline converts the user’s question into an embedding, uses that embedding to pull semantically similar document chunks from a vector store, and then conditions the language model on those chunks to produce the final answer. This process combines the strengths of information retrieval (access to up‑to‑date, domain‑specific content) with the generative capabilities of large language models.
- Answer quality: Very well written answer. It answers the question well.
- Citation quality: Since it states someting like Source 1, lines 1‑8; Source 5 for some of the section, it has good citation quality.

**Comparison:** 
Option B had proper reference and also longer answer with summary at the bottom while option A had very short answer. 
### Question 3

**Question:** What is the difference between chunking, embeddings, and a vector database?
**Expected evidence:** ai_research_notes.txt

**Approach A:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Slightly longer than other questions.
- Answer:
**Chunking** – When a document is first ingested, it is split into many short, self‑contained pieces (often a few sentences or a paragraph). This step is called *chunking* and its purpose is to turn a long text into manageable passages that can be indexed and retrieved individually.

**Embeddings** – Each chunk (or any piece of text) is then passed through an embedding model, which converts the raw words into a fixed‑length numerical vector. The vector captures the semantic meaning of the chunk so that similar pieces of text end up with vectors that are close to each other in the vector space.

**Vector database** – The resulting vectors are stored in a *vector database* (also called a vector store). The database is optimized for fast similarity search: given a new query’s embedding, it can quickly find the stored vectors (and therefore the associated chunks) that are most alike.

**How they differ**

| Component | Role in the RAG pipeline | What it is |
|-----------|--------------------------|------------|
| **Chunking** | Pre‑processing step that creates the units of text to be indexed | A division of a long document into smaller passages |
| **Embeddings** | Transforms each passage into a numeric representation for comparison | High‑dimensional vectors that encode semantic information |
| **Vector database** | Holds the embeddings and enables rapid similarity lookup | A storage system that supports vector‑based nearest‑neighbor searches |

In short, *chunking* decides *what* text pieces will be used, *embeddings* turn those pieces into comparable numeric forms, and the *vector database* stores those numeric forms and retrieves the most relevant ones when a user’s question is embedded and queried.

- Answer quality:  Very well written answer with table.
- Citation quality: No specific citation that indicate where information is exactly from.

**Approach B:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick
- Answer:
**Chunking, embeddings, and a vector database are three distinct steps in a RAG pipeline, each serving a different purpose** (Source 1).

| Component | What it does | How it differs from the others |
|-----------|--------------|--------------------------------|
| **Chunking** | Splits long documents into many smaller, manageable passages (or “chunks”). This makes the text easier to index and retrieve. | It operates on the raw text **before** any numerical representation is created. |
| **Embeddings** | Converts each chunk (or any piece of text) into a high‑dimensional numerical vector that captures its semantic meaning. | It is a **representation** of the chunk’s content; the output of this step is a vector, not the text itself. |
| **Vector database** | Stores all the generated embedding vectors and provides fast similarity‑search capabilities (e.g., “find the vectors closest to a query vector”). | It is the **storage and retrieval system** for the vectors; it does not perform chunking or create embeddings, it only holds and indexes them. |

In practice, a RAG system first **chunks** a document, then **embeds** each chunk, and finally puts those embeddings into a **vector database** so that, when a user asks a question, the system can retrieve semantically similar passages by searching the stored vectors.
- Answer quality:  Very well written answer with table however compare to answer A it is shorter.
- Citation quality: No specific citation that indicate where information is exactly from.

**Comparison:** 
Very similar output
### Question 4

**Question:** Why can a RAG system generate an incorrect answer even when it retrieves information from a document? Give two reasons.
**Expected evidence:** ai_research_notes.txt

**Approach A:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick
- Answer:
A RAG system can still produce a wrong answer for at least two documented reasons:

1. **Irrelevant or incomplete retrieval** – The system may pull passages that are not truly relevant to the question, or it may miss the crucial evidence that would lead to a correct answer. (Source 1, lines … “the system may retrieve irrelevant passages, fail to retrieve important evidence…”)  

2. **Generation that is not grounded in the retrieved text** – Even when passages are returned, the language model can “hallucinate” or formulate statements that are not supported by those passages, because fluent generation does not guarantee factual correctness. (Source 2, lines … “generate claims that are not supported by the retrieved context.”)

These two factors—poor retrieval quality and ungrounded generation—explain why a RAG pipeline can output an incorrect answer despite having access to the source documents.
- Answer quality: Very well written answer.
- Citation quality: This answer specify there some of the sections of answer are specifically from.

**Approach B:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick
- Answer:
A RAG pipeline does not automatically guarantee a correct answer. Even after it has pulled passages from the source collection, the final response can still be wrong for reasons such as:

1. **Irrelevant or incomplete retrieval** – The system may fetch passages that do not actually contain the needed evidence, or it may miss the crucial information altogether. When the context fed to the language model is missing or off‑topic, the model has to “fill in the gaps,” which can lead to an incorrect answer.  
   *Source 5 (and the end of Source 1) notes that “the system may retrieve irrelevant passages, fail to retrieve important evidence…”*

2. **Generation‑time hallucination** – The language model can produce statements that are not grounded in the retrieved text, even though it was given those passages as context. It may invent facts or extrapolate beyond what the retrieved passages support, resulting in an answer that is factually inaccurate.  
   *Source 5 explicitly says the system “may generate claims that are not supported by the retrieved context.”*

These two factors—faulty retrieval and ungrounded generation—explain why a RAG system can still output an incorrect answer despite having access to the relevant documents.
- Answer quality: Very well written answer.
- Citation quality: This answer specify there some of the sections of answer are specifically from.

**Comparison:** 
Both answers are equaly good.
### Question 5

**Question:** What does backpropagation calculate, and what does the optimization algorithm do afterward?
**Expected evidence:** ai_research_notes.txt

**Approach A:**
- Retrieved chunks:
- Retrieval latency: Quick
- Answer:
Backpropagation **calculates the gradients** of the loss function with respect to each weight in the network. These gradients tell the system how the loss would change if a weight were adjusted.  

After the gradients are obtained, the **optimization algorithm uses them to update the weights** (e.g., by moving each weight a small step in the direction that reduces the loss), thereby training the network.  

*(Source 1, lines describing backpropagation and the optimization step.)*
- Answer quality: Well written answer but quite short.
- Citation quality: This answer specify there some of the sections of answer are specifically from. 
**Approach B:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick
- Answer: **Backpropagation** computes the **gradients** of the loss function with respect to each weight in the network. These gradients tell the model how the loss would change if a weight were altered.

**The optimization algorithm** then takes those gradients and **updates the weights**—typically by moving them in the direction that reduces the loss (e.g., using gradient‑descent‑style updates).  

*Source 1, lines 6‑8: “Backpropagation calculates gradients that help determine how weights should change, while an optimization algorithm updates the weights.”*
- Answer quality: Well written answer but quite short.
- Citation quality: This answer specify there some of the sections of answer are specifically from. Also exact quote is good citation.

**Comparison:** 
Very similar results.

### Question 6

**Question:** Explain the differences between retrieval precision, recall, retrieval latency, and total answer-generation latency.
**Expected evidence:** ai_research_notes.txt

**Approach A:**
- Retrieved chunks:
- Retrieval latency: Quick
- Answer:
**Retrieval precision** – the fraction of the items the system returns that are actually relevant.  
*Formula*: precision = (number of relevant retrieved items) / (total retrieved items). It tells you how “clean” the result set is.

**Retrieval recall** – the fraction of all relevant items that the system succeeds in returning.  
*Formula*: recall = (number of relevant retrieved items) / (total relevant items in the collection). It measures how completely the system finds the needed information.

**Retrieval latency** – the elapsed time required **only** to perform the retrieval step (i.e., converting the query to an embedding, searching the vector store, and returning the top passages). It reflects the speed of the search component itself.

**Total answer‑generation latency** – the overall time from the moment the user submits a question until the system produces its final answer. It includes **retrieval latency** plus the time the language model spends generating the response (and any additional post‑processing).

In short, precision and recall are *accuracy‑oriented* metrics that evaluate *what* is retrieved, while retrieval latency and total answer‑generation latency are *speed‑oriented* metrics that evaluate *how long* the system takes—retrieval latency covering only the search phase, and total answer‑generation latency covering the entire pipeline from query to answer. (Source 1)
- Answer quality: Well written.
- Citation quality: Some of the sections have citation.

**Approach B:**
- Retrieved chunks: 5 different chunks
- Retrieval latency: Quick
- Answer:
**Retrieval precision** – The fraction of the items that the system **actually retrieved** that are relevant.  
*Formula*: precision = (number of relevant retrieved items) ÷ (total retrieved items).  
It tells you how “clean” the result set is: a high precision means most of what the system returned is useful.

**Retrieval recall** – The fraction of all **relevant items in the collection** that the system succeeded in retrieving.  
*Formula*: recall = (number of relevant retrieved items) ÷ (total relevant items in the whole collection).  
It measures how completely the system finds the needed information; high recall means few relevant items were missed.

**Retrieval latency** – The time required **just to perform the retrieval step** (i.e., turning the query into an embedding, searching the vector database, and returning the matching passages). It reflects the speed of the information‑lookup component alone.

**Total answer‑generation latency** – The overall time from the moment the user submits a question until the system produces the final answer. This includes **retrieval latency plus all downstream processing** such as passing the retrieved passages to the language model, running the generation step, and any post‑processing. It is therefore a broader measurement of end‑to‑end responsiveness.
- Answer quality: Well written
- Citation quality: No citation

**Comparison:** 
For this approach A provided answer with citation.
## 5. Summary of Results

Over all both approach provided good answers. Some of the questions had better citation quality than others but it was not from approach difference.

## 6. Discussion
Both approach take 5 different chunks and one of the last one have very low similarity score. I think chunk retrieval can be optimized to reduce cost of running.

## 7. Conclusion
For this project RAG was applied properly and both approach works equaly good.