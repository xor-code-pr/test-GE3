# Knowledge Management Application - Deployment and Configuration Guide

This comprehensive guide provides detailed instructions for deploying and configuring the Knowledge Management Application in Azure with SharePoint integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Resource Setup](#azure-resource-setup)
3. [SharePoint Setup](#sharepoint-setup)
4. [Application Deployment](#application-deployment)
5. [Configuration](#configuration)
6. [Access Control Setup](#access-control-setup)
7. [SharePoint Permission Synchronization](#sharepoint-permission-synchronization)
8. [Indexing Schema](#indexing-schema)
9. [Operations Guide](#operations-guide)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- Python 3.8 or higher
- Azure CLI (latest version)
- pip (Python package manager)

### Azure Subscription

- Active Azure subscription
- Sufficient permissions to create resources
- Azure AD admin access for setting up application registrations
- SharePoint Online admin access (for SharePoint integration)

### Required Azure Services

1. Azure Storage Account
2. Azure AI Search Service
3. Azure AD (Entra ID) tenant
4. SharePoint Online (optional, for SharePoint integration)

## Azure Resource Setup

### 1. Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="km-app-rg"
LOCATION="eastus"
APP_NAME="km-app"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 2. Create Azure Storage Account

```bash
STORAGE_ACCOUNT_NAME="${APP_NAME}storage"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2 \
  --enable-hierarchical-namespace true

# Get storage account key (only needed if not using managed identity)
STORAGE_KEY=$(az storage account keys list \
  --account-name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query '[0].value' -o tsv)
```

### 3. Create Azure AI Search Service

```bash
SEARCH_SERVICE_NAME="${APP_NAME}-search"

# Create search service (Basic tier)
az search service create \
  --name $SEARCH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku basic

# Get search admin key (only needed if not using managed identity)
SEARCH_KEY=$(az search admin-key show \
  --service-name $SEARCH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query 'primaryKey' -o tsv)
```

### 4. Azure AD Application Registration

```bash
# Create Azure AD application
APP_ID=$(az ad app create \
  --display-name "$APP_NAME" \
  --query appId -o tsv)

# Create service principal
az ad sp create --id $APP_ID

# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)

# Create client secret (save this securely)
CLIENT_SECRET=$(az ad app credential reset \
  --id $APP_ID \
  --query password -o tsv)

# Grant API permissions for Azure AD
az ad app permission add \
  --id $APP_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions 7ab1d382-f21e-4acd-a863-ba3e13f7da61=Role

# Grant SharePoint API permissions
# Sites.ReadWrite.All (for SharePoint site management)
az ad app permission add \
  --id $APP_ID \
  --api 00000003-0000-0003-c000-000000000000 \
  --api-permissions 9492366f-7969-46a4-8d15-ed1a20078fff=Role

# Sites.Manage.All (for SharePoint permission management)
az ad app permission add \
  --id $APP_ID \
  --api 00000003-0000-0003-c000-000000000000 \
  --api-permissions 0c0bf378-bf22-4481-8f81-9e89a9b4960a=Role

# Admin consent (requires admin privileges)
az ad app permission admin-consent --id $APP_ID
```

## SharePoint Setup

### 1. Configure SharePoint Site

```bash
# Create a SharePoint site for the Knowledge Management app
# This can be done via SharePoint admin center or using PnP PowerShell

# Option 1: Using SharePoint Admin Center
# Navigate to: https://yourtenant-admin.sharepoint.com
# Create a new site or use an existing site

# Option 2: Using PnP PowerShell
Install-Module -Name PnP.PowerShell -Force -AllowClobber
Connect-PnPOnline -Url "https://yourtenant-admin.sharepoint.com" -Interactive

# Create new site collection for Knowledge Management
New-PnPSite -Type TeamSite `
  -Title "Knowledge Management" `
  -Alias "KnowledgeManagement" `
  -Description "Document libraries for Knowledge Bases"

# Record the site URL for configuration
# Example: https://yourtenant.sharepoint.com/sites/KnowledgeManagement
```

### 2. Grant Application Permissions to SharePoint

```bash
# Grant the Azure AD application access to SharePoint
# This is done through Azure AD App Registration permissions (already configured above)

# Verify application has access to SharePoint
# Test by accessing: https://yourtenant.sharepoint.com/_layouts/15/appinv.aspx
# Look up the app by Client ID and verify permissions
```

### 3. Configure SharePoint Security

```bash
# Ensure the SharePoint site allows app-only access
# Navigate to SharePoint Admin Center > Sites > Active Sites
# Select your site > Policies > App permissions
# Verify the application is listed with appropriate permissions
```

## Application Deployment

### Option 1: Azure Web App Deployment

```bash
# Create App Service Plan
az appservice plan create \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan "${APP_NAME}-plan" \
  --runtime "PYTHON:3.9"

# Enable managed identity
az webapp identity assign \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# Get managed identity principal ID
PRINCIPAL_ID=$(az webapp identity show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)
```

### Option 2: Azure Container Instance Deployment

```bash
# Create container registry
ACR_NAME="${APP_NAME}acr"
az acr create \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku Basic \
  --admin-enabled true

# Build and push Docker image
az acr build \
  --registry $ACR_NAME \
  --image km-app:latest \
  --file Dockerfile .

# Create container instance with managed identity
az container create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image "${ACR_NAME}.azurecr.io/km-app:latest" \
  --assign-identity \
  --registry-username $(az acr credential show --name $ACR_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
```

### Assign Managed Identity Permissions

```bash
# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Assign Storage Blob Data Contributor role
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee $PRINCIPAL_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Assign Search Service Contributor role
az role assignment create \
  --role "Search Service Contributor" \
  --assignee $PRINCIPAL_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Search/searchServices/$SEARCH_SERVICE_NAME"

# Assign Search Index Data Contributor role
az role assignment create \
  --role "Search Index Data Contributor" \
  --assignee $PRINCIPAL_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Search/searchServices/$SEARCH_SERVICE_NAME"
```

## Configuration

### Environment Variables

Configure the following environment variables for your deployment:

#### For Web App:

```bash
# Configure app settings
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    ADMIN_USERS="admin@example.com,superuser@example.com" \
    AZURE_STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
    AZURE_SEARCH_SERVICE_NAME="$SEARCH_SERVICE_NAME" \
    AZURE_TENANT_ID="$TENANT_ID" \
    USE_MANAGED_IDENTITY="true" \
    DATABASE_CONNECTION_STRING="sqlite:///data/knowledge_base.db" \
    MAX_FILE_SIZE_MB="100" \
    ENABLE_SHAREPOINT_SYNC="true" \
    SHAREPOINT_SITE_URL="https://yourtenant.sharepoint.com/sites/KnowledgeManagement"
```

#### For Local Development:

Create a `.env` file:

```bash
# Admin Users
ADMIN_USERS=admin@example.com,superuser@example.com

# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_ACCOUNT_KEY=your_storage_key  # Only for local dev

# Azure AI Search
AZURE_SEARCH_SERVICE_NAME=your_search_service
AZURE_SEARCH_ADMIN_KEY=your_search_key  # Only for local dev

# Azure AD
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id  # Only for local dev
AZURE_CLIENT_SECRET=your_client_secret  # Only for local dev

# SharePoint Integration
ENABLE_SHAREPOINT_SYNC=true
SHAREPOINT_SITE_URL=https://YOURTENANT.sharepoint.com/sites/KnowledgeManagement  # Replace YOURTENANT with your tenant name
SHAREPOINT_CLIENT_ID=your_client_id  # Can reuse AZURE_CLIENT_ID
SHAREPOINT_CLIENT_SECRET=your_client_secret  # Can reuse AZURE_CLIENT_SECRET

# Use managed identity in production
USE_MANAGED_IDENTITY=false  # Set to true in production

# Database
DATABASE_CONNECTION_STRING=sqlite:///knowledge_base.db

# Application Settings
MAX_FILE_SIZE_MB=100
```

### Configuration File (config.yaml)

Alternatively, create a `config.yaml` file:

```yaml
admin_users:
  - admin@example.com
  - superuser@example.com

azure:
  storage:
    account_name: your_storage_account
    # account_key: only for development
  
  search:
    service_name: your_search_service
    # admin_key: only for development
  
  ad:
    tenant_id: your_tenant_id
    # client_id: only for development
    # client_secret: only for development
  
  use_managed_identity: true  # Always true in production

application:
  max_file_size_mb: 100
  allowed_file_types:
    - .pdf
    - .docx
    - .txt
    - .md
    - .pptx
    - .xlsx

database:
  connection_string: sqlite:///knowledge_base.db
```

## Access Control Setup

### 1. Define Admin Users

Admin users are default content managers for all knowledge bases. Configure them in the `ADMIN_USERS` environment variable:

```python
# In your configuration
admin_users = [
    "admin@example.com",
    "superuser@example.com"
]
```

### 2. Create Azure AD Groups

Create Azure AD groups for organizing access:

```bash
# Create a group
GROUP_ID=$(az ad group create \
  --display-name "Engineering Team" \
  --mail-nickname "eng-team" \
  --query id -o tsv)

# Add members to the group
az ad group member add \
  --group $GROUP_ID \
  --member-id <user-object-id>
```

### 3. Configure Access Policies

When creating a knowledge base, specify Azure AD groups and content managers:

```python
from app.main import KnowledgeManagementApp

app = KnowledgeManagementApp()

# Create KB with access policies
kb = app.create_knowledge_base(
    name="Engineering Documentation",
    description="Documentation for engineering team",
    owner_id="admin@example.com",
    azure_ad_groups=[
        {
            'group_id': 'eng-team',
            'name': 'Engineering Team',
            'object_id': '<azure-ad-group-object-id>',
            'content_managers': [
                'user1@example.com',
                'user2@example.com'
            ]
        }
    ]
)
```

### Access Control Hierarchy

1. **Admin Users**: Full access to all KBs (create, read, write, delete)
2. **KB Owners**: Full access to their own KBs
3. **Content Managers**: Can upload and manage documents in assigned KBs
4. **Azure AD Group Members**: Read access to KBs assigned to their groups

## SharePoint Permission Synchronization

### Overview

The application automatically synchronizes KB access policies with SharePoint permissions, ensuring consistent access control across both systems.

### Synchronization Behavior

1. **KB Creation**: When a KB is created, a SharePoint document library is automatically created and permissions are set based on the initial access policies.

2. **Permission Updates**: When access policies are updated using `update_access_policies()`, the changes are automatically synchronized to SharePoint.

3. **Automatic Sync**: The synchronization happens automatically in the background. No manual intervention is required.

### Permission Mapping

The application maps KB access levels to SharePoint permission levels:

| KB Role | SharePoint Permission |
|---------|----------------------|
| Admin Users | Full Control |
| KB Owner | Full Control |
| Content Managers | Contribute |
| Azure AD Group Members | Read |

### Example: Creating KB with SharePoint Sync

```python
from app.main import KnowledgeManagementApp

app = KnowledgeManagementApp()

# Create KB - SharePoint library is created automatically
kb = app.create_knowledge_base(
    name="Product Documentation",
    description="All product-related documentation",
    owner_id="product-manager@example.com",
    azure_ad_groups=[
        {
            'group_id': 'product-team',
            'name': 'Product Team',
            'object_id': '<azure-ad-object-id>',
            'content_managers': ['pm@example.com']
        }
    ]
)

# SharePoint library created at:
# https://yourtenant.sharepoint.com/sites/KnowledgeManagement/KB_<kb_id>
print(f"SharePoint library: {kb.sharepoint_library_name}")
print(f"Last sync: {kb.last_sharepoint_sync}")
```

### Example: Updating Permissions

```python
from app.models import AccessPolicy, AzureADGroup, AccessLevel

# Add a new group with access
new_group = AzureADGroup(
    group_id='sales-team',
    name='Sales Team',
    object_id='<sales-group-object-id>'
)

new_policy = AccessPolicy(
    azure_ad_group=new_group,
    access_level=AccessLevel.READ,
    content_managers=['sales-lead@example.com']
)

# Update access policies - SharePoint permissions sync automatically
app.kb_manager.update_access_policies(
    kb_id=kb.kb_id,
    access_policies=[new_policy]
)

print(f"Permissions synced to SharePoint at: {kb.last_sharepoint_sync}")
```

### Verifying SharePoint Permissions

You can verify that permissions were synced correctly:

```python
# Get current SharePoint permissions for the library
if app.kb_manager.sharepoint_service:
    permissions = app.kb_manager.sharepoint_service.get_library_permissions(
        library_name=kb.sharepoint_library_name
    )
    
    for perm in permissions:
        print(f"{perm.principal_id}: {perm.role}")
```

### Importing Documents from SharePoint

```python
# Import existing documents from SharePoint library to KB
documents = app.import_from_sharepoint(
    kb_id=kb.kb_id,
    imported_by="admin@example.com"
)

print(f"Imported {len(documents)} documents from SharePoint")
for doc in documents:
    print(f"  - {doc.filename} ({doc.size_bytes} bytes)")
```

### Handling Permission Sync Failures

If permission synchronization fails during KB creation, the SharePoint library will be created but permissions won't be synced. In this case:

1. **The KB metadata will indicate the issue**:
   - `sharepoint_sync_enabled = False`
   - `sharepoint_library_name` will still be set (library exists)
   - Logs will contain error details

2. **To retry permission sync**:
   ```python
   # Update access policies - this will trigger a permission sync
   app.kb_manager.update_access_policies(
       kb_id=kb.kb_id,
       access_policies=kb.access_policies  # Use existing policies
   )
   ```

3. **Manual permission setup in SharePoint** (if needed):
   - Navigate to the SharePoint library
   - Click Settings > Library Settings > Permissions
   - Grant appropriate permissions to users and groups

## Indexing Schema

### Search Index Schema

The application creates the following index schema for each knowledge base:

```json
{
  "name": "kb-index-{kb_id}",
  "fields": [
    {
      "name": "document_id",
      "type": "Edm.String",
      "key": true,
      "searchable": false,
      "filterable": false,
      "sortable": false,
      "facetable": false
    },
    {
      "name": "filename",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "sortable": true,
      "facetable": false
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "analyzer": "standard.lucene"
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": true,
      "sortable": true
    },
    {
      "name": "kb_id",
      "type": "Edm.String",
      "searchable": false,
      "filterable": true
    },
    {
      "name": "blob_path",
      "type": "Edm.String",
      "searchable": false
    },
    {
      "name": "content_type",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "uploaded_by",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "uploaded_at",
      "type": "Edm.DateTimeOffset",
      "sortable": true,
      "filterable": true
    },
    {
      "name": "metadata",
      "type": "Edm.String",
      "searchable": true
    }
  ]
}
```

### Indexer Configuration

Automatic indexers are created for each knowledge base:

```python
# Indexer runs automatically on schedule
indexer = {
    "name": "indexer-{kb_id}",
    "dataSourceName": "datasource-{kb_id}",
    "targetIndexName": "kb-index-{kb_id}",
    "schedule": {
        "interval": "PT5M"  # Run every 5 minutes
    },
    "parameters": {
        "maxFailedItems": 10,
        "maxFailedItemsPerBatch": 5
    }
}
```

### Query Examples

#### Basic Text Search

```python
results = app.search(
    kb_id="kb-123",
    query="machine learning",
    user_id="user@example.com"
)
```

#### Filtered Search

```python
from app.search_service import SearchService

search_service = SearchService(config.azure)
results = search_service.search(
    index_name="kb-index-123",
    query="project documentation",
    filters="content_type eq 'application/pdf' and uploaded_at gt 2024-01-01",
    top=20
)
```

#### Advanced Search with Facets

```python
# Search with facets for filtering
results = search_client.search(
    search_text="architecture",
    filter="kb_id eq 'kb-123'",
    facets=["content_type", "uploaded_by"],
    top=10
)
```

## Operations Guide

### Creating a Knowledge Base

```python
from app.main import KnowledgeManagementApp

app = KnowledgeManagementApp()

kb = app.create_knowledge_base(
    name="Product Documentation",
    description="All product-related documentation",
    owner_id="product-manager@example.com",
    azure_ad_groups=[
        {
            'group_id': 'product-team',
            'name': 'Product Team',
            'object_id': 'azure-ad-object-id',
            'content_managers': ['pm@example.com']
        }
    ]
)

print(f"Created KB: {kb.kb_id}")
print(f"Blob container: {kb.blob_container_name}")
print(f"Search index: {kb.search_index_name}")
```

### Uploading Documents

```python
# Upload a single document
with open('document.pdf', 'rb') as f:
    doc = app.upload_document(
        kb_id=kb.kb_id,
        filename='document.pdf',
        file_data=f.read(),
        content_type='application/pdf',
        uploaded_by='admin@example.com',
        metadata={'category': 'technical', 'version': '1.0'}
    )

print(f"Document uploaded: {doc.document_id}")
print(f"Indexed: {doc.indexed}")
```

### Searching Documents

```python
# Search within a knowledge base
results = app.search(
    kb_id=kb.kb_id,
    query="API documentation",
    user_id="user@example.com"
)

for result in results:
    print(f"File: {result.filename}")
    print(f"Score: {result.score}")
    print(f"KB: {result.metadata['kb_id']}")
```

### Managing Access Policies

```python
from app.models import AccessPolicy, AzureADGroup, AccessLevel

# Update access policies
new_group = AzureADGroup(
    group_id='sales-team',
    name='Sales Team',
    object_id='sales-group-object-id'
)

new_policy = AccessPolicy(
    azure_ad_group=new_group,
    access_level=AccessLevel.READ,
    content_managers=['sales-lead@example.com']
)

app.kb_manager.update_access_policies(
    kb_id=kb.kb_id,
    access_policies=[new_policy]
)
```

### Monitoring Indexer Status

```python
# Check indexer status
indexer_name = f"indexer-{kb.kb_id[:20]}"
status = app.search_service.indexer_client.get_indexer_status(indexer_name)

print(f"Status: {status.status}")
print(f"Last result: {status.last_result.status}")
print(f"Items processed: {status.last_result.items_processed}")
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Problem**: "Authentication failed" when accessing Azure services

**Solution**:
- Verify managed identity is properly assigned
- Check role assignments are correct
- Ensure USE_MANAGED_IDENTITY is set correctly
- For local development, verify service principal credentials

```bash
# Check role assignments
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --all

# Test managed identity
az login --identity
az account show
```

#### 2. Indexer Failures

**Problem**: Documents not being indexed automatically

**Solution**:
- Check indexer status: `az search indexer show --service-name <name> --indexer-name <indexer>`
- Review indexer execution history
- Verify storage connection string is correct
- Ensure blob container exists and is accessible

```python
# Check indexer status programmatically
status = app.search_service.indexer_client.get_indexer_status(indexer_name)
print(f"Errors: {status.last_result.errors}")
```

#### 3. Access Denied Errors

**Problem**: Users cannot access knowledge bases

**Solution**:
- Verify Azure AD group membership
- Check access policies are configured correctly
- Ensure user has valid Azure AD object ID
- Review admin user list

#### 4. Storage Connection Issues

**Problem**: Cannot upload files to blob storage

**Solution**:
- Verify storage account name is correct
- Check network access and firewall rules
- Ensure managed identity has Storage Blob Data Contributor role
- For development, verify storage account key is valid

#### 5. Search Query Errors

**Problem**: Search queries return no results or errors

**Solution**:
- Verify index exists: `az search index show --service-name <name> --index-name <index>`
- Check documents are indexed
- Review query syntax
- Ensure user has access to the knowledge base

### Logging and Monitoring

Enable diagnostic logging for troubleshooting:

```bash
# Enable storage account logging
az monitor diagnostic-settings create \
  --name storage-logs \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME" \
  --logs '[{"category":"StorageRead","enabled":true},{"category":"StorageWrite","enabled":true}]' \
  --workspace <log-analytics-workspace-id>

# Enable search service logging
az monitor diagnostic-settings create \
  --name search-logs \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Search/searchServices/$SEARCH_SERVICE_NAME" \
  --logs '[{"category":"OperationLogs","enabled":true}]' \
  --workspace <log-analytics-workspace-id>
```

### Performance Tuning

1. **Index Optimization**
   - Adjust indexer schedule based on update frequency
   - Use appropriate field types and analyzers
   - Enable caching for frequently accessed queries

2. **Storage Optimization**
   - Use appropriate blob access tiers
   - Implement lifecycle management
   - Enable CDN for frequently accessed files

3. **Search Optimization**
   - Use appropriate search tier for workload
   - Configure replica count for high availability
   - Implement result caching

## Support and Additional Resources

- Azure Storage Documentation: https://docs.microsoft.com/azure/storage/
- Azure AI Search Documentation: https://docs.microsoft.com/azure/search/
- Azure AD Documentation: https://docs.microsoft.com/azure/active-directory/

For application-specific issues, refer to the project repository's issue tracker.
