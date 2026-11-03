from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Azure OpenAI
    azure_openai_endpoint: str = "https://aispire-t04-ai-grhkzgybcisec.openai.azure.com/"
    azure_openai_api_version: str = "2024-02-01"
    chat_deployment: str = "chat"
    embed_deployment: str = "embedding"

    # Azure AI Search
    search_endpoint: str = "https://aispire-t04-search-grhkzgybcisec.search.windows.net"
    search_index_jobs: str = "jobs"
    search_index_taxonomy: str = "taxonomy"

    # Azure Cosmos DB
    cosmos_endpoint: str = "https://aispire-t04-cosmos-grhkzgybcisec.documents.azure.com:443/"
    cosmos_db: str = "hidden-talent"
    cosmos_container_candidates: str = "candidates"
    cosmos_container_matches: str = "matches"

    # Storage
    storage_account_url: str = "https://staispire04grhkzgybcisec.blob.core.windows.net"
    storage_container: str = "datasets"

    # API Configuration
    api_base_url: str = "http://localhost:8000"
    prompt_version: str = "v1"


settings = Settings()
