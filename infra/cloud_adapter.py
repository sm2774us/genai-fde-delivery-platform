"""Cloud-agnostic storage/secrets adapter interface. An FDE pod must be able
to deploy the same platform onto AWS, Azure, or GCP depending on the client's
existing landing zone; this module isolates that variance behind one
interface so application code (`app/`) never imports a cloud SDK directly."""
from __future__ import annotations

from abc import ABC, abstractmethod


class ObjectStorageAdapter(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    def get(self, key: str) -> bytes: ...


class SecretsAdapter(ABC):
    @abstractmethod
    def get_secret(self, name: str) -> str: ...


class AwsAdapter(ObjectStorageAdapter, SecretsAdapter):
    """Would wrap boto3 S3 + Secrets Manager in a real deployment."""

    def put(self, key: str, data: bytes) -> None:
        raise NotImplementedError("Wire up boto3 S3 client for production use.")

    def get(self, key: str) -> bytes:
        raise NotImplementedError("Wire up boto3 S3 client for production use.")

    def get_secret(self, name: str) -> str:
        raise NotImplementedError("Wire up boto3 Secrets Manager client for production use.")


class AzureAdapter(ObjectStorageAdapter, SecretsAdapter):
    """Would wrap azure-storage-blob + Key Vault in a real deployment."""

    def put(self, key: str, data: bytes) -> None:
        raise NotImplementedError("Wire up Azure Blob Storage client for production use.")

    def get(self, key: str) -> bytes:
        raise NotImplementedError("Wire up Azure Blob Storage client for production use.")

    def get_secret(self, name: str) -> str:
        raise NotImplementedError("Wire up Azure Key Vault client for production use.")


class GcpAdapter(ObjectStorageAdapter, SecretsAdapter):
    """Would wrap google-cloud-storage + Secret Manager in a real deployment."""

    def put(self, key: str, data: bytes) -> None:
        raise NotImplementedError("Wire up GCS client for production use.")

    def get(self, key: str) -> bytes:
        raise NotImplementedError("Wire up GCS client for production use.")

    def get_secret(self, name: str) -> str:
        raise NotImplementedError("Wire up GCP Secret Manager client for production use.")


def get_cloud_adapter(provider: str) -> ObjectStorageAdapter:
    return {"aws": AwsAdapter, "azure": AzureAdapter, "gcp": GcpAdapter}[provider]()
