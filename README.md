# LLM Research Paper Assistant

A full-stack Research Paper Intelligence Assistant built around retrieval-augmented generation (RAG). The application lets users organize research into persistent workspaces, upload research papers, create independent conversations, ask grounded questions across indexed documents, and receive answers with source metadata and page references.

The system is designed as a real application rather than a demo chatbot: workspace, chat, document, message, and notes data are persisted in a relational database, while document chunks and embeddings are stored in a persistent ChromaDB collection with workspace/document isolation.

## Features

### Research Workspaces
- Create, rename, pin/unpin, and delete workspaces
- Keep research papers and conversations isolated by workspace
- See document and chat counts per workspace
- Persist workspace state across application restarts

### Research Papers
- Upload PDF research papers to a selected workspace
- Validate file type, PDF signature, file size, and empty uploads
- Generate a SHA-256 file hash to prevent duplicate indexing within a workspace
- Extract page-aware text with PyPDF
- Clean and chunk document text before embedding
- Store document metadata, page counts, and chunk counts in the database
- Store embeddings and chunk metadata in persistent ChromaDB
- Remove documents from both the database/filesystem and vector store

### Conversational RAG
- Create multiple independent chats inside each workspace
- Persist user and assistant messages
- Retrieve relevant chunks from only the active workspace
- Optionally restrict retrieval to selected documents
- Use recent conversation history to resolve follow-up references
- Generate grounded responses with Gemma 3 through Ollama
- Instruct the model to avoid unsupported claims and cite factual claims as `[SOURCE N]`
- Return source metadata including filename, page, chunk identifier, and retrieval distance
- Gracefully report when no relevant evidence is available

### Notes
- Maintain persistent workspace-level research notes
- Create or update notes through the backend API
- Notes survive reloads and application restarts

### Search
- Search persisted workspace, chat, and document names
- Return results with the associated workspace for navigation

### Frontend
- React 19 + TypeScript interface
- Workspace and chat navigation
- Real document upload and removal flows
- Real chat creation, rename, pin/unpin, and deletion
- Source-aware message presentation
- Light/dark theme support
- Responsive application layout

## System Architecture

```text
                        Research Paper Intelligence Assistant

┌─────────────────────── React + TypeScript Frontend ───────────────────────┐
│                                                                           │
│  Workspaces   Chats   Documents   Notes   Search   RAG Conversation      │
│                                                                           │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │ REST API
                                ▼
┌──────────────────────────── FastAPI Backend ───────────────────────────────┐
│                                                                            │
│  Workspace APIs   Chat APIs   Document APIs   Notes/Search APIs            │
│        │               │             │                                      │
│        │               │             ▼                                      │
│        │               │      PDF Processing                               │
│        │               │      PyPDF → Cleaning → Chunking                   │
│        │               │             │                                      │
│        │               │             ▼                                      │
│        │               │      Sentence Transformers                        │
│        │               │             │                                      │
│        │               │             ▼                                      │
│        │               └──────► ChromaDB                                    │
│        │                             │                                      │
│        └─────────────────────────────┼──────────────► Retrieval             │
│                                      │                                      │
│                                      ▼                                      │
│                              Ollama + Gemma 3                               │
│                                      │                                      │
│                                      ▼                                      │
│                                Grounded Answer                              │
│                                                                            │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
                           SQLite + SQLAlchemy
                              + Alembic
```

## Document Indexing Pipeline

```text
PDF Upload
    │
    ▼
Validate PDF + size + duplicate hash
    │
    ▼
Store document metadata in database
    │
    ▼
Extract page-aware text with PyPDF
    │
    ▼
Clean extracted text
    │
    ▼
Chunk text with page metadata
    │
    ▼
Generate normalized embeddings
with Sentence Transformers
    │
    ▼
Persist chunks + metadata in ChromaDB
    │
    ▼
Mark document as ready
```

Each indexed vector retains metadata such as:

```text
document_id
workspace_id
filename
file_hash
page
chunk_index
```

This metadata is used to enforce workspace/document retrieval boundaries and to provide source references in generated answers.

## Question Answering Pipeline

```text
User Question
     │
     ▼
Persist user message
     │
     ▼
Generate query embedding
     │
     ▼
Workspace/document-scoped semantic retrieval
     │
     ▼
Retrieve relevant page-aware chunks
     │
     ▼
Combine conversation history + source passages
     │
     ▼
Gemma 3 through Ollama
     │
     ▼
Grounded answer with [SOURCE N] citations
     │
     ▼
Persist assistant response + source metadata
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| Backend | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| PDF Processing | PyPDF |
| Text Processing | LangChain |
| Embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Vector Database | ChromaDB |
| LLM | Gemma 3 |
| LLM Runtime | Ollama |
| API | REST |
| Version Control | Git, GitHub |

## Project Structure

```text
LLM-Research-Paper-Assistant/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── chats.py
│   │   │   ├── documents.py
│   │   │   └── workspaces.py
│   │   │
│   │   ├── services/
│   │   │   ├── embedding.py
│   │   │   ├── llm.py
│   │   │   ├── pdf_reader.py
│   │   │   ├── retriever.py
│   │   │   ├── text_chunker.py
│   │   │   ├── text_cleaner.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── tests/
│   │   └── test_api.py
│   │
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   └── vite-env.d.ts
│   ├── package.json
│   └── tsconfig.json
│
├── .env.example
├── .gitignore
└── README.md
```

Runtime-generated directories and local state such as `uploads/`, `chroma_db/`, `*.db`, and `.env` are excluded from version control.

## Prerequisites

Install the following before running the project:

- Python 3.11+
- Node.js and npm
- Ollama
- Git

The backend currently uses SQLite by default, so no separate database server is required for local development.

## Installation

Clone the repository:

```bash
git clone https://github.com/Sunny1112003/LLM-Research-Paper-Assistant.git
cd LLM-Research-Paper-Assistant
```

### Backend

Create and activate a virtual environment:

**Windows PowerShell**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows CMD**

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**

```bash
cd backend
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the backend directory when custom settings are required. The repository includes `.env.example` as a template.

Default configuration:

```env
OLLAMA_MODEL=gemma3
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PATH=chroma_db
CHROMA_COLLECTION=research_papers_v3
UPLOAD_DIR=uploads
DATABASE_URL=sqlite:///./research_assistant.db
TOP_K=5
MAX_FILE_SIZE_MB=25
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

For a database URL other than the default SQLite database, set `DATABASE_URL` accordingly.

## Database Setup

The backend schema is managed with Alembic migrations.

From the `backend` directory:

```bash
alembic upgrade head
```

Check migration state:

```bash
alembic current
```

Verify that the database schema matches the migration history:

```bash
alembic check
```

For a clean local database during development:

```bash
alembic downgrade base
alembic upgrade head
```

## Ollama Setup

Install Ollama from the official website:

https://ollama.com

Pull the configured model:

```bash
ollama pull gemma3
```

Start Ollama when it is not already running:

```bash
ollama serve
```

Confirm the model is available:

```bash
ollama list
```

The backend reads the model name from `OLLAMA_MODEL`, which defaults to `gemma3`.

## Run the Backend

From the `backend` directory:

```bash
python -m uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Run the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will print the local frontend URL in the terminal. The default port is `5173`; if that port is already in use, Vite may select another available port.

## API Overview

### Health

```http
GET /health
```

Returns the service health status.

### Workspaces

```http
GET    /workspaces
POST   /workspaces
GET    /workspaces/{workspace_id}
PATCH  /workspaces/{workspace_id}
DELETE /workspaces/{workspace_id}
```

### Documents

```http
GET    /workspaces/{workspace_id}/documents
POST   /workspaces/{workspace_id}/documents
DELETE /documents/{document_id}
```

### Chats

```http
GET    /workspaces/{workspace_id}/chats
POST   /workspaces/{workspace_id}/chats
PATCH  /chats/{chat_id}
DELETE /chats/{chat_id}
GET    /chats/{chat_id}/messages
POST   /chats/{chat_id}/messages
```

### Notes

```http
GET /workspaces/{workspace_id}/notes
PUT /workspaces/{workspace_id}/notes
```

### Search

```http
GET /search?q=<query>
```

## Persistence and Isolation

The application separates durable application state from vector retrieval state.

### SQL database

SQLAlchemy models persist:

- Workspaces
- Documents
- Chats
- Messages
- Workspace notes

Relationships use cascading deletion so deleting a workspace also removes its associated application records.

### ChromaDB

ChromaDB persistently stores document chunks and embeddings together with workspace and document metadata.

Retrieval is scoped by:

- Workspace ID
- Optional document IDs

Deleting a document removes its indexed vectors. Deleting a workspace removes all vectors belonging to that workspace.

This prevents content from one workspace from leaking into another workspace's retrieval results.

### Duplicate protection

Uploaded PDFs are hashed with SHA-256. An identical file cannot be indexed more than once inside the same workspace.

## Error Handling and Validation

The API validates important document-ingestion conditions, including:

- Workspace existence
- PDF extension
- PDF file signature
- Empty uploads
- Maximum upload size
- Duplicate document hashes
- Extractable document text

When document processing fails, the application cleans up the partially stored file, vectors, and database record instead of leaving an incomplete document behind.

For PDFs without extractable text, such as scanned documents that require OCR, the backend reports that OCR is required rather than silently indexing an empty document.

## Testing

Run the backend test suite from the `backend` directory:

```bash
python -m pytest -v
```

The repository includes API tests covering:

- Health endpoint
- Workspace creation/listing
- Chat creation
- Message lifecycle

The frontend production build can be verified with:

```bash
cd frontend
npm run build
```

## Development Workflow

A recommended workflow for future changes:

```text
main
 │
 ├── feature/<change>
 │        │
 │        ├── implement
 │        ├── test
 │        ├── update documentation
 │        └── review diff
 │
 └──────────────► pull request ► merge
```

Before merging a change, run the backend tests and frontend production build.

## Limitations

The current application is a local-first research assistant.

Important current limitations:

- Ollama must be running locally for answer generation.
- The configured embedding model is downloaded and executed locally.
- PDF ingestion currently depends on extractable text; scanned PDFs require OCR support.
- Authentication and multi-user authorization are not implemented.
- Production cloud deployment configuration is not included.

## Future Improvements

Potential next steps include:

- OCR support for scanned research papers
- Stronger document metadata and filtering
- Better source inspection and document viewing
- Citation export and bibliographic utilities
- Automated research-paper summaries and comparative analysis
- Advanced retrieval evaluation and reranking
- Authentication and role-based access control
- Background document processing for larger files
- Production deployment and observability

## License

This project is licensed under the MIT License.

## Author

**Prajna Deepankar Nelapuri**

GitHub: https://github.com/Sunny1112003
