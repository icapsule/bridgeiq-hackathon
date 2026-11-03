#!/usr/bin/env python3
"""
Inspect Azure sandbox resources using DefaultAzureCredential (az login identity).
Usage:
    python scripts/inspect_azure.py
"""
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI

from app.config import settings


def inspect():
    print("=" * 60)
    print("BridgeIQ: Azure Sandbox Inspector (Team 04)")
    print("=" * 60)

    credential = DefaultAzureCredential()

    # 1. Storage Account & Datasets
    print("\n[1/4] Checking Azure Blob Storage...")
    try:
        blob_service = BlobServiceClient(account_url=settings.storage_account_url, credential=credential)
        container_client = blob_service.get_container_client(settings.storage_container)
        blobs = list(container_client.list_blobs())
        print(f"  ✓ Connected to container '{settings.storage_container}'")
        for b in blobs:
            print(f"    - {b.name} ({b.size} bytes)")
    except Exception as e:
        print(f"  ✗ Storage check failed: {e}")

    # 2. Cosmos DB
    print("\n[2/4] Checking Azure Cosmos DB...")
    try:
        cosmos_client = CosmosClient(settings.cosmos_endpoint, credential=credential)
        db = cosmos_client.get_database_client(settings.cosmos_db)
        containers = list(db.list_containers())
        print(f"  ✓ Connected to database '{settings.cosmos_db}'")
        for c in containers:
            print(f"    - Container: {c['id']}")
    except Exception as e:
        print(f"  ✗ Cosmos check failed: {e}")

    # 3. AI Search
    print("\n[3/4] Checking Azure AI Search...")
    for idx_name in [settings.search_index_jobs, settings.search_index_taxonomy]:
        try:
            search_client = SearchClient(
                endpoint=settings.search_endpoint,
                index_name=idx_name,
                credential=credential
            )
            count = search_client.get_document_count()
            print(f"  ✓ Index '{idx_name}': {count} documents")
        except Exception as e:
            print(f"  ✗ Search index '{idx_name}' check failed: {e}")

    # 4. Azure OpenAI / Foundry
    print("\n[4/4] Checking Azure OpenAI / AI Foundry...")
    try:
        # Note: in gpt-5-mini / azure-openai, test embedding call
        from azure.identity import get_bearer_token_provider
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
        
        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_ad_token_provider=token_provider,
            api_version=settings.azure_openai_api_version
        )
        emb_res = client.embeddings.create(
            input=["test connectivity"],
            model=settings.embed_deployment
        )
        vec_len = len(emb_res.data[0].embedding)
        print(f"  ✓ Azure OpenAI embedding test succeeded! Vector dimensions: {vec_len}")
    except Exception as e:
        print(f"  ✗ Azure OpenAI test failed: {e}")

    print("\n" + "=" * 60)
    print("Inspection complete.")
    print("=" * 60)


if __name__ == "__main__":
    inspect()
