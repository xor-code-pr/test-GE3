# Knowledge Management Application - Architecture Overview

## System Architecture

The Knowledge Management Application is built with a modular architecture that integrates Azure services for storage, search, and identity management.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Knowledge Management App                    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Application Layer                      │  │
│  │  ┌────────────┐  ┌───────────────┐  ┌────────────────┐  │  │
│  │  │   Main     │  │  Example/CLI  │  │   Web API      │  │  │
│  │  │   (Core)   │  │   Interface   │  │  (Optional)    │  │  │
│  │  └────────────┘  └───────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Business Logic Layer                   │  │
│  │  ┌────────────┐  ┌───────────────┐  ┌────────────────┐  │  │
│  │  │    KB      │  │     Access    │  │   Document     │  │  │
│  │  │  Manager   │  │    Control    │  │   Processor    │  │  │
│  │  └────────────┘  └───────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Service Layer                          │  │
│  │  ┌────────────┐  ┌───────────────┐  ┌────────────────┐  │  │
│  │  │   Blob     │  │    Search     │  │      AD        │  │  │
│  │  │  Storage   │  │    Service    │  │    Service     │  │  │
│  │  │  Service   │  │               │  │   (Future)     │  │  │
│  │  └────────────┘  └───────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────┬───────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Azure Blob   │   │   Azure AI    │   │   Azure AD    │
│   Storage     │   │    Search     │   │  (Entra ID)   │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Component Details

### 1. Application Layer

#### Main Application (app/main.py)
- Entry point for the application
- Coordinates between different services
- Provides high-level API for KB operations
- Handles user and KB lifecycle

#### CLI Interface
- Command-line interface for operations
- Create KB, upload documents, search
- Administration tasks

### 2. Business Logic Layer

#### Knowledge Base Manager (app/kb_manager.py)
- Creates and manages knowledge bases
- Handles document uploads
- Manages access policies
- Coordinates storage and indexing operations
- Enforces content manager permissions

**Key Responsibilities:**
- KB lifecycle management
- Access control enforcement
- Document processing coordination
- Search query execution

#### Access Control
- Validates user permissions
- Checks Azure AD group membership
- Enforces admin privileges
- Manages content manager lists

### 3. Service Layer

#### Blob Storage Service (app/blob_storage.py)
- Manages Azure Blob Storage operations
- Creates containers for each KB
- Uploads and downloads files
- Lists and deletes blobs
- Supports managed identity authentication

**Key Operations:**
- `create_container()`: Creates KB-specific container
- `upload_file()`: Uploads document to storage
- `download_file()`: Retrieves document
- `list_files()`: Lists documents in container

#### Search Service (app/search_service.py)
- Manages Azure AI Search operations
- Creates and manages search indexes
- Configures and runs indexers
- Executes search queries
- Supports managed identity authentication

**Key Operations:**
- `create_index()`: Creates search index with schema
- `create_indexer()`: Sets up automatic indexing
- `index_document()`: Indexes single document
- `search()`: Executes search queries

### 4. Data Models (app/models.py)

#### Core Models:
- `User`: User account with admin flag
- `KnowledgeBase`: KB with policies and metadata
- `AccessPolicy`: Group access with content managers
- `AzureADGroup`: Azure AD group reference
- `Document`: Document metadata and location
- `SearchResult`: Search query result

## Data Flow

### Creating a Knowledge Base

```
User Request
    │
    ▼
┌─────────────────┐
│  KB Manager     │
└────────┬────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────────┐   ┌──────────────┐
│ Create      │   │ Create       │
│ Container   │   │ Index        │
│ (Blob)      │   │ (Search)     │
└─────────────┘   └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Create       │
                  │ Indexer      │
                  └──────────────┘
```

### Uploading a Document

```
User Upload Request
    │
    ▼
┌─────────────────┐
│ Validate        │
│ Permissions     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Upload to       │
│ Blob Storage    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Index Document  │
│ (AI Search)     │
└─────────────────┘
```

### Searching Documents

```
Search Query
    │
    ▼
┌─────────────────┐
│ Validate        │
│ KB Access       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute Search  │
│ (AI Search)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Filter Results  │
│ by KB & Access  │
└────────┬────────┘
         │
         ▼
    Return Results
```

## Security Architecture

### Authentication Flow

```
1. User authenticates with Azure AD
2. Application validates user identity
3. User's Azure AD object ID is retrieved
4. Group memberships are checked
```

### Authorization Hierarchy

```
┌──────────────────────────────────────┐
│         Admin Users                   │
│  (Full access to all KBs)            │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│         KB Owners                     │
│  (Full access to owned KBs)          │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│      Content Managers                 │
│  (Upload/manage docs in assigned KBs)│
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│    Azure AD Group Members             │
│  (Read access to group KBs)          │
└──────────────────────────────────────┘
```

### Managed Identity Flow

```
Application
    │
    ▼
Azure Managed Identity
    │
    ├──────────────────────────────────┐
    │                                  │
    ▼                                  ▼
Storage Blob Data Contributor    Search Service Contributor
(Azure Storage)                  (Azure AI Search)
```

## Storage Architecture

### Blob Storage Organization

```
Storage Account
│
├── kb-{kb_id1}/
│   ├── {doc_id1}/
│   │   └── document1.pdf
│   ├── {doc_id2}/
│   │   └── document2.docx
│   └── ...
│
├── kb-{kb_id2}/
│   ├── {doc_id3}/
│   │   └── presentation.pptx
│   └── ...
│
└── ...
```

### Search Index Organization

```
Search Service
│
├── kb-index-{kb_id1}
│   ├── Fields: document_id, filename, content, ...
│   └── Documents: [doc1, doc2, doc3, ...]
│
├── kb-index-{kb_id2}
│   ├── Fields: document_id, filename, content, ...
│   └── Documents: [doc4, doc5, ...]
│
└── ...
```

## Scalability Considerations

### Horizontal Scaling
- Multiple application instances can run simultaneously
- Azure services (Storage, Search) handle load automatically
- Stateless design enables load balancing

### Performance Optimization
- Blob storage: Use appropriate access tiers
- Search: Configure replicas for read scaling
- Indexing: Schedule indexers for off-peak times
- Caching: Implement result caching for common queries

### Resource Limits

#### Azure Storage
- 500 TB per storage account
- 20,000 requests/second per account
- Unlimited containers per account

#### Azure AI Search
- Basic tier: 15 indexes, 1 indexer
- Standard tier: 50 indexes, 200 indexers
- Document limits vary by tier

## Monitoring and Observability

### Key Metrics to Monitor

1. **Storage Metrics**
   - Container count
   - Blob count per container
   - Storage capacity used
   - Request success rate

2. **Search Metrics**
   - Query latency
   - Indexing latency
   - Queries per second
   - Index size

3. **Application Metrics**
   - KB creation rate
   - Document upload rate
   - Search query rate
   - Error rates

### Logging Strategy

```python
# Application logs
logger.info("KB created: {kb_id}")
logger.warning("Large file upload: {size}MB")
logger.error("Indexing failed: {error}")

# Azure diagnostic logs
- Storage account logs (read/write operations)
- Search service logs (queries, indexing)
- Azure AD logs (authentication)
```

## Deployment Architectures

### Option 1: Azure Web App

```
┌─────────────────────────────────────┐
│        Azure Web App                 │
│  (Python runtime)                    │
│  - Managed Identity enabled         │
│  - Auto-scaling configured          │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
Storage Account   Search Service
```

### Option 2: Azure Container Instance

```
┌─────────────────────────────────────┐
│   Azure Container Instance          │
│  (Docker container)                 │
│  - Managed Identity enabled         │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
Storage Account   Search Service
```

### Option 3: Azure Kubernetes Service

```
┌─────────────────────────────────────┐
│   Azure Kubernetes Service          │
│  ┌───────────┐  ┌───────────┐      │
│  │   Pod 1   │  │   Pod 2   │      │
│  └───────────┘  └───────────┘      │
│  - Pod Identity for authentication  │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
Storage Account   Search Service
```

## Future Enhancements

1. **Advanced Search Features**
   - Semantic search
   - Custom analyzers for domain-specific content
   - Multi-language support

2. **Content Processing**
   - OCR for scanned documents
   - Text extraction from images
   - Automatic metadata extraction

3. **Collaboration Features**
   - Document comments and annotations
   - Version control
   - Change notifications

4. **Analytics Dashboard**
   - Usage statistics
   - Popular searches
   - Content gaps analysis

5. **AI Integration**
   - Question answering over KB content
   - Document summarization
   - Intelligent recommendations

## Technology Stack

### Core Technologies
- **Language**: Python 3.8+
- **Azure SDK**: Latest stable versions
- **Authentication**: Azure Identity

### Azure Services
- **Storage**: Azure Blob Storage
- **Search**: Azure AI Search
- **Identity**: Azure AD (Entra ID)
- **Monitoring**: Azure Monitor (optional)

### Development Tools
- **Testing**: unittest, pytest
- **Code Quality**: black, flake8, mypy
- **Container**: Docker
- **CI/CD**: GitHub Actions (optional)
