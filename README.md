# Knowledge Management Application

A comprehensive Knowledge Management System built on Azure services that enables organizations to create and manage knowledge bases (KBs) with granular access control, automatic document indexing, powerful search capabilities, and SharePoint integration.

## Overview

This application provides:

- **Knowledge Base Management**: Create and manage multiple knowledge bases with isolated storage and indexing
- **Granular Access Control**: Configure access policies using Azure AD groups with designated content managers
- **Admin Management**: Maintain a list of admin users who are default content managers for all KBs
- **Azure Blob Storage Integration**: Store all uploaded files in dedicated containers
- **Azure AI Search Integration**: Automatically index documents for fast, full-text search
- **SharePoint Integration**: Synchronize permissions with SharePoint and import documents from SharePoint libraries
- **Programmatic Index Management**: All indexer and index operations are handled programmatically

## Features

### 1. Knowledge Base Creation
- Create isolated knowledge bases with dedicated storage and search indexes
- Each KB has its own Azure Blob Storage container
- Each KB has its own Azure AI Search index
- Optional SharePoint document library for each KB
- Automatic indexer setup for document processing

### 2. Access Control
- **Azure AD Group Integration**: Specify which Azure AD groups have read access to each KB
- **Content Managers**: Designate specific users within Azure AD groups as content managers
- **Admin Users**: Configure a list of admin users who are default content managers for all KBs
- **Owner Permissions**: KB owners have full control over their knowledge bases
- **SharePoint Permission Sync**: Automatically synchronize KB access policies with SharePoint permissions

### 3. Document Management
- Upload documents to knowledge bases
- Automatic storage in Azure Blob Storage
- Automatic indexing with Azure AI Search
- Import documents from SharePoint libraries
- Support for multiple file types (PDF, DOCX, TXT, MD, PPTX, XLSX, etc.)

### 4. SharePoint Integration
- **Automatic Library Creation**: Create SharePoint document libraries for each KB
- **Permission Synchronization**: Sync KB access policies to SharePoint permissions
- **Document Import**: Import existing documents from SharePoint to Azure Blob Storage
- **Bidirectional Access**: Users can access documents through both the app and SharePoint

### 5. Search Capabilities
- Full-text search across all documents in a knowledge base
- Filter results by KB, content type, uploader, and date
- Relevance scoring and highlighting
- Efficient indexing schema for optimal query performance

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Knowledge Management App                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │  KB Manager    │  │ Blob Storage │  │  Search Service │     │
│  │                │  │   Service    │  │                 │     │
│  └───────┬────────┘  └──────┬───────┘  └────────┬────────┘     │
│          │                  │                     │              │
│          │           ┌──────▼──────┐              │              │
│          │           │  SharePoint │              │              │
│          │           │   Service   │              │              │
│          │           └──────┬──────┘              │              │
└──────────┼──────────────────┼─────────────────────┼──────────────┘
           │                  │                     │
           │                  │                     │
    ┌──────▼──────┐    ┌──────▼──────┐     ┌───────▼────────┐
    │   Azure AD  │    │  Azure Blob │     │  Azure AI      │
    │             │    │   Storage   │     │  Search        │
    └─────────────┘    └──────┬──────┘     └────────────────┘
                              │
                       ┌──────▼──────────┐
                       │   SharePoint    │
                       │     Online      │
                       └─────────────────┘
```

## Best Practices

### Configuration Management

1. **Use Managed Identity in Production**
   - Enable managed identity for your Azure resources
   - Avoid storing credentials in code or configuration files
   - Set `USE_MANAGED_IDENTITY=true` in production environments

2. **Environment Variables**
   - Store all sensitive configuration in environment variables
   - Use Azure Key Vault for production secrets
   - Never commit credentials to source control

3. **Admin User Management**
   - Maintain a minimal list of admin users
   - Use email addresses or Azure AD object IDs for admin identification
   - Regularly review and update the admin list

### Azure Deployment Requirements

#### Required Azure Resources

1. **Azure Storage Account**
   - General-purpose v2 storage account
   - Enable hierarchical namespace for optimal performance
   - Configure appropriate firewall rules and network access

2. **Azure AI Search Service**
   - Basic tier or higher for production workloads
   - Standard tier recommended for high-volume scenarios
   - Configure appropriate replica and partition counts

3. **Azure AD (Entra ID)**
   - Registered application for authentication
   - Configured API permissions for group membership
   - Admin consent granted for required permissions

#### Managed Identity Access Requirements

When using Managed Identity, ensure the following role assignments:

1. **Storage Blob Data Contributor** on the Storage Account
   - Allows creation of containers
   - Enables upload and download of blobs
   - Required for document management

2. **Search Service Contributor** on the AI Search Service
   - Allows creation and management of indexes
   - Enables indexer creation and execution
   - Required for search functionality

3. **Search Index Data Contributor** on the AI Search Service
   - Allows document indexing operations
   - Enables search query execution
   - Required for document indexing

4. **Directory.Read.All** (Azure AD)
   - Required to read Azure AD group memberships
   - Enables group-based access control
   - Requires admin consent

#### Assigning Managed Identity Roles

Using Azure CLI:

```bash
# Get the managed identity principal ID
PRINCIPAL_ID=$(az webapp identity show --name <app-name> --resource-group <rg-name> --query principalId -o tsv)

# Assign Storage Blob Data Contributor
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee $PRINCIPAL_ID \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>

# Assign Search Service Contributor
az role assignment create \
  --role "Search Service Contributor" \
  --assignee $PRINCIPAL_ID \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.Search/searchServices/<search-service-name>

# Assign Search Index Data Contributor
az role assignment create \
  --role "Search Index Data Contributor" \
  --assignee $PRINCIPAL_ID \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.Search/searchServices/<search-service-name>
```

### Security Best Practices

1. **Authentication & Authorization**
   - Always validate user permissions before operations
   - Use Azure AD for user authentication
   - Implement least-privilege access control

2. **Data Protection**
   - Enable encryption at rest for Azure Storage
   - Use HTTPS for all data transfers
   - Enable Azure Storage firewall and virtual networks

3. **Audit Logging**
   - Enable diagnostic logging for Azure Storage
   - Enable diagnostic logging for Azure AI Search
   - Monitor and alert on suspicious activities

### Performance Optimization

1. **Indexing Strategy**
   - Use automatic indexing for real-time updates
   - Configure appropriate indexer schedules
   - Monitor indexer execution and failures

2. **Search Optimization**
   - Use filters to narrow search scope
   - Implement pagination for large result sets
   - Cache frequently accessed search results

3. **Storage Optimization**
   - Use appropriate blob access tiers
   - Implement lifecycle management policies
   - Clean up deleted or obsolete documents

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd test-GE3

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your configuration:

```bash
# Admin Users (comma-separated)
ADMIN_USERS=admin@example.com,superuser@example.com

# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_ACCOUNT_KEY=your_storage_key  # Not needed with managed identity

# Azure AI Search
AZURE_SEARCH_SERVICE_NAME=your_search_service
AZURE_SEARCH_ADMIN_KEY=your_search_key  # Not needed with managed identity

# Azure AD
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id  # Not needed with managed identity
AZURE_CLIENT_SECRET=your_client_secret  # Not needed with managed identity

# SharePoint Integration (Optional)
ENABLE_SHAREPOINT_SYNC=true
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/YourSite
SHAREPOINT_CLIENT_ID=your_sharepoint_client_id  # Can reuse AZURE_CLIENT_ID
SHAREPOINT_CLIENT_SECRET=your_sharepoint_client_secret  # Can reuse AZURE_CLIENT_SECRET

# Managed Identity (recommended for production)
USE_MANAGED_IDENTITY=true

# Database
DATABASE_CONNECTION_STRING=sqlite:///knowledge_base.db

# Application Settings
MAX_FILE_SIZE_MB=100
```

### SharePoint Integration Setup

To enable SharePoint integration:

1. **Register Application in Azure AD**:
   - The same Azure AD app registration can be used for both Azure services and SharePoint
   - Ensure the following API permissions are granted:
     - `Sites.ReadWrite.All` - To create and manage SharePoint sites
     - `Sites.Manage.All` - To manage SharePoint permissions
     - `User.Read.All` - To read user information

2. **Configure SharePoint Site**:
   - Create or identify a SharePoint site for KB document libraries
   - Ensure the application has necessary permissions on the site

3. **Enable in Configuration**:
   ```bash
   ENABLE_SHAREPOINT_SYNC=true
   SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/YourSite
   ```

4. **Permission Synchronization**:
   - When a KB is created, a corresponding SharePoint library is automatically created
   - KB access policies are automatically synced to SharePoint permissions
   - Updates to access policies trigger permission sync to SharePoint

5. **Document Import**:
   ```python
   # Import documents from SharePoint to KB
   documents = app.import_from_sharepoint(kb_id, imported_by="admin@example.com")
   ```

### Usage Example

```python
from app.main import KnowledgeManagementApp

# Initialize the application
app = KnowledgeManagementApp()

# Create a knowledge base
kb = app.create_knowledge_base(
    name="Engineering Docs",
    description="Engineering documentation repository",
    owner_id="admin@example.com",
    azure_ad_groups=[
        {
            'group_id': 'eng-team',
            'name': 'Engineering Team',
            'object_id': 'azure-ad-group-object-id',
            'content_managers': ['user1@example.com']
        }
    ]
)

# Upload a document
with open('document.pdf', 'rb') as f:
    doc = app.upload_document(
        kb_id=kb.kb_id,
        filename='document.pdf',
        file_data=f.read(),
        content_type='application/pdf',
        uploaded_by='admin@example.com'
    )

# Search the knowledge base
results = app.search(
    kb_id=kb.kb_id,
    query="important information",
    user_id="user1@example.com"
)
```

## API Reference

See the [instructions.md](instructions.md) file for comprehensive API documentation and deployment guidelines.

## Support

For issues, questions, or contributions, please refer to the project's issue tracker.

## License

This project is licensed under the MIT License.
