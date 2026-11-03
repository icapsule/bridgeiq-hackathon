from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI

from app.config import settings


class AzureClients:
    _instance = None

    def __init__(self):
        self.credential = DefaultAzureCredential()

        # Azure OpenAI
        token_provider = get_bearer_token_provider(
            self.credential, "https://cognitiveservices.azure.com/.default"
        )
        self.openai_client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_ad_token_provider=token_provider,
            api_version=settings.azure_openai_api_version,
        )

        # Azure AI Search Clients
        self.search_taxonomy = SearchClient(
            endpoint=settings.search_endpoint,
            index_name=settings.search_index_taxonomy,
            credential=self.credential,
        )
        self.search_jobs = SearchClient(
            endpoint=settings.search_endpoint,
            index_name=settings.search_index_jobs,
            credential=self.credential,
        )

        # Azure Cosmos DB Containers
        cosmos_client = CosmosClient(settings.cosmos_endpoint, credential=self.credential)
        self.cosmos_db = cosmos_client.get_database_client(settings.cosmos_db)
        self.container_candidates = self.cosmos_db.get_container_client(
            settings.cosmos_container_candidates
        )
        self.container_matches = self.cosmos_db.get_container_client(
            settings.cosmos_container_matches
        )

        # Azure Storage
        self.blob_service = BlobServiceClient(
            account_url=settings.storage_account_url, credential=self.credential
        )
        self.container_datasets = self.blob_service.get_container_client(
            settings.storage_container
        )

    @classmethod
    def get(cls) -> "AzureClients":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
