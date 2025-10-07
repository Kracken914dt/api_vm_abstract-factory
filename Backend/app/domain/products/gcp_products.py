"""
Productos concretos de GCP para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para los servicios específicos de Google Cloud.
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class ComputeEngineInstance(VirtualMachine):
    """Implementación concreta de VM para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"gcp-vm-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-instance-{uuid.uuid4().hex[:6]}"),
            provider="gcp"
        )
        self.zone = config.get("zone", "us-central1-a")
        self.machine_type = config.get("machine_type", "e2-standard-2")
        self.boot_disk_size = config.get("boot_disk_size", 20)
        self.project_id = config.get("project_id", "my-gcp-project")
        
    def start(self) -> bool:
        """Iniciar la instancia de Compute Engine"""
        print(f"🟢 GCP: Iniciando Compute Engine instance {self.name} en zona {self.zone}")
        self.status = ResourceStatus.RUNNING
        return True
        
    def stop(self) -> bool:
        """Detener la instancia de Compute Engine"""
        print(f"🔴 GCP: Deteniendo Compute Engine instance {self.name}")
        self.status = ResourceStatus.STOPPED
        return True
        
    def resize(self, new_config: Dict[str, Any]) -> bool:
        """Cambiar el tipo de máquina de la instancia"""
        new_machine_type = new_config.get("machine_type", self.machine_type)
        print(f"🔄 GCP: Cambiando machine type de {self.machine_type} a {new_machine_type}")
        self.machine_type = new_machine_type
        return True
        
    def get_status(self) -> ResourceStatus:
        return self.status
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "zone": self.zone,
            "machine_type": self.machine_type,
            "boot_disk_size": self.boot_disk_size,
            "project_id": self.project_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class CloudSQLDatabase(Database):
    """Implementación concreta de base de datos para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"gcp-db-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-cloudsql-{uuid.uuid4().hex[:6]}"),
            provider="gcp"
        )
        self.engine = config.get("engine", "postgres")
        self.engine_version = config.get("engine_version", "13")
        self.tier = config.get("tier", "db-standard-1")
        self.region = config.get("region", "us-central1")
        self.storage_size = config.get("storage_size", 20)
        
    def create_backup(self) -> str:
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        print(f"💾 GCP: Creando backup {backup_id} para Cloud SQL {self.name}")
        return backup_id
        
    def restore_from_backup(self, backup_id: str) -> bool:
        print(f"♻️ GCP: Restaurando Cloud SQL {self.name} desde backup {backup_id}")
        return True
        
    def scale(self, new_config: Dict[str, Any]) -> bool:
        new_tier = new_config.get("tier", self.tier)
        new_storage = new_config.get("storage_size", self.storage_size)
        print(f"📈 GCP: Escalando Cloud SQL {self.name} a tier {new_tier}, storage {new_storage}GB")
        self.tier = new_tier
        self.storage_size = new_storage
        return True
        
    def get_connection_string(self) -> str:
        return f"postgresql://user:password@{self.resource_id}.gcp:5432/{self.name}"
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "tier": self.tier,
            "region": self.region,
            "storage_size": self.storage_size,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class CloudLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"gcp-lb-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-lb-{uuid.uuid4().hex[:6]}"),
            provider="gcp"
        )
        self.load_balancer_type = config.get("type", "HTTP(S)")
        self.region = config.get("region", "us-central1")
        self.backend_services = config.get("backend_services", [])
        
    def add_target(self, target_id: str, target_config: Dict[str, Any]) -> bool:
        target_info = {
            "id": target_id,
            "zone": target_config.get("zone", "us-central1-a"),
            "port": target_config.get("port", 80)
        }
        self.backend_services.append(target_info)
        print(f"➕ GCP: Añadiendo target {target_id} al Load Balancer {self.name}")
        return True
        
    def remove_target(self, target_id: str) -> bool:
        self.backend_services = [t for t in self.backend_services if t["id"] != target_id]
        print(f"➖ GCP: Removiendo target {target_id} del Load Balancer {self.name}")
        return True
        
    def configure_health_check(self, health_check_config: Dict[str, Any]) -> bool:
        print(f"🔍 GCP: Configurando health check para Load Balancer {self.name}")
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "type": self.load_balancer_type,
            "region": self.region,
            "backend_services": self.backend_services,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class CloudStorage(Storage):
    """Implementación concreta de almacenamiento para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"gcp-storage-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-bucket-{uuid.uuid4().hex[:6]}"),
            provider="gcp"
        )
        self.location = config.get("location", "US")
        self.storage_class = config.get("storage_class", "STANDARD")
        self.versioning_enabled = config.get("versioning_enabled", False)
        
    def upload_file(self, file_path: str, object_name: str) -> str:
        object_url = f"gs://{self.name}/{object_name}"
        print(f"⬆️ GCP: Subiendo {file_path} a Cloud Storage como {object_url}")
        return object_url
        
    def download_file(self, object_name: str, destination_path: str) -> bool:
        print(f"⬇️ GCP: Descargando {object_name} desde Cloud Storage bucket {self.name}")
        return True
        
    def delete_file(self, object_name: str) -> bool:
        print(f"🗑️ GCP: Eliminando {object_name} desde Cloud Storage bucket {self.name}")
        return True
        
    def set_lifecycle_policy(self, policy_config: Dict[str, Any]) -> bool:
        print(f"📋 GCP: Configurando lifecycle policy para bucket {self.name}")
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider, 
            "location": self.location,
            "storage_class": self.storage_class,
            "versioning_enabled": self.versioning_enabled,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }