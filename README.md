# LLM Research Paper Assistant

A Retrieval-Augmented Generation (RAG) application that enables users to upload research papers in PDF format and ask questions about their content. The application extracts and indexes document text, retrieves the most relevant information using semantic search, and generates context-aware answers with Gemma 3 running locally through Ollama.

---

## Features

- Upload research papers in PDF format
- Extract and preprocess text from PDF documents
- Split documents into overlapping chunks using LangChain
- Generate embeddings using Sentence Transformers (`all-MiniLM-L6-v2`)
- Store and retrieve embeddings with ChromaDB
- Perform semantic search over indexed documents
- Generate answers using Gemma 3 through Ollama
- REST APIs built with FastAPI

---

## System Architecture

```text
                    Document Indexing

Research Paper (PDF)
        │
        ▼
Upload PDF
        │
        ▼
Extract Text (PyPDF)
        │
        ▼
Text Preprocessing
        │
        ▼
Text Chunking (LangChain)
        │
        ▼
Embedding Generation
(Sentence Transformers)
        │
        ▼
ChromaDB

──────────────────────────────────────────────

                  Question Answering

User Question
        │
        ▼
Question Embedding
        │
        ▼
Semantic Search (ChromaDB)
        │
        ▼
Retrieve Relevant Chunks
        │
        ▼
Prompt Construction
        │
        ▼
Gemma 3 (Ollama)
        │
        ▼
Generated Answer
```

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Backend | FastAPI |
| PDF Processing | PyPDF |
| Text Chunking | LangChain |
| Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Model Hosting | Hugging Face |
| Vector Database | ChromaDB |
| Large Language Model | Gemma 3 |
| LLM Runtime | Ollama |
| Version Control | Git & GitHub |

---

## Project Structure

```text
LLM-Research-Paper-Assistant/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   └── query.py
│   │   │
│   │   └── services/
│   │       ├── pdf_reader.py
│   │       ├── text_cleaner.py
│   │       ├── text_chunker.py
│   │       ├── embedding.py
│   │       ├── vector_store.py
│   │       ├── retriever.py
│   │       └── llm.py
│   │
│   ├── main.py
│   ├── uploads/
│   └── chroma_db/
│
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.11 or later
- Ollama
- Git

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Sunny1112003/LLM-Research-Paper-Assistant.git
cd LLM-Research-Paper-Assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Configure Ollama

Download Ollama from:

https://ollama.com

Pull the Gemma 3 model:

```bash
ollama pull gemma3
```

Start the Ollama server:

```bash
ollama serve
```

---

## Running the Application

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

Open the Swagger API documentation:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload and index a research paper |
| POST | `/query` | Retrieve relevant document context and generate an answer |

---

## RAG Workflow

1. Upload a research paper.
2. Extract and preprocess the document text.
3. Split the text into overlapping chunks.
4. Generate embeddings for each chunk.
5. Store embeddings in ChromaDB.
6. Convert the user query into an embedding.
7. Retrieve the most relevant document chunks.
8. Generate the final answer using Gemma 3.

---

## Roadmap

- [x] PDF upload
- [x] Text extraction
- [x] Text preprocessing
- [x] Text chunking
- [x] Embedding generation
- [x] ChromaDB integration
- [x] Semantic retrieval
- [x] Answer generation with Gemma 3
- [ ] React frontend
- [ ] Multi-document support
- [ ] Source citations
- [ ] Conversation history
- [ ] User authentication
- [ ] Cloud deployment

---

## Contributing

Contributions are welcome. If you would like to improve the project, please fork the repository, create a feature branch, and submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Author

**Prajna Deepankar Nelapuri**

GitHub: https://github.com/Sunny1112003
