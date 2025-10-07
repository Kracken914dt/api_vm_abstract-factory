"""
Productos concretos de Oracle Cloud para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para los servicios específicos de Oracle Cloud Infrastructure (OCI).
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class OracleComputeInstance(VirtualMachine):
    """Implementación concreta de VM para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"oci-vm-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-instance-{uuid.uuid4().hex[:6]}"),
            provider="oracle"
        )
        self.compute_shape = config.get("compute_shape", "VM.Standard2.1")
        self.availability_domain = config.get("availability_domain", "AD-1")
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.subnet_id = config.get("subnet_id", "ocid1.subnet.oc1..example")
        self.image_id = config.get("image_id", "ocid1.image.oc1..example")
        
    def start(self) -> bool:
        """Iniciar la instancia de Oracle Compute"""
        print(f"🟢 Oracle: Iniciando Compute instance {self.name} en AD {self.availability_domain}")
        self.status = ResourceStatus.RUNNING
        return True
        
    def stop(self) -> bool:
        """Detener la instancia de Oracle Compute"""
        print(f"🔴 Oracle: Deteniendo Compute instance {self.name}")
        self.status = ResourceStatus.STOPPED
        return True
        
    def resize(self, new_config: Dict[str, Any]) -> bool:
        """Cambiar el shape de la instancia"""
        new_shape = new_config.get("compute_shape", self.compute_shape)
        print(f"🔄 Oracle: Cambiando shape de {self.compute_shape} a {new_shape}")
        self.compute_shape = new_shape
        return True
        
    def get_status(self) -> ResourceStatus:
        return self.status
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "compute_shape": self.compute_shape,
            "availability_domain": self.availability_domain,
            "compartment_id": self.compartment_id,
            "subnet_id": self.subnet_id,
            "image_id": self.image_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OracleAutonomousDatabase(Database):
    """Implementación concreta de base de datos para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"oci-db-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-adb-{uuid.uuid4().hex[:6]}"),
            provider="oracle"
        )
        self.workload_type = config.get("workload_type", "OLTP")  # OLTP, DW, AJD, APEX
        self.cpu_count = config.get("cpu_count", 1)
        self.storage_tb = config.get("storage_tb", 1)
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.admin_password = config.get("admin_password", "SecurePass123!")
        
    def create_backup(self) -> str:
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        print(f"💾 Oracle: Creando backup {backup_id} para Autonomous Database {self.name}")
        return backup_id
        
    def restore_from_backup(self, backup_id: str) -> bool:
        print(f"♻️ Oracle: Restaurando Autonomous Database {self.name} desde backup {backup_id}")
        return True
        
    def scale(self, new_config: Dict[str, Any]) -> bool:
        new_cpu = new_config.get("cpu_count", self.cpu_count)
        new_storage = new_config.get("storage_tb", self.storage_tb)
        print(f"📈 Oracle: Escalando Autonomous Database {self.name} a {new_cpu} CPUs, {new_storage}TB storage")
        self.cpu_count = new_cpu
        self.storage_tb = new_storage
        return True
        
    def get_connection_string(self) -> str:
        return f"oracle://{self.name}_high?TNS_ADMIN=/path/to/wallet"
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "workload_type": self.workload_type,
            "cpu_count": self.cpu_count,
            "storage_tb": self.storage_tb,
            "compartment_id": self.compartment_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OracleLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"oci-lb-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-lb-{uuid.uuid4().hex[:6]}"),
            provider="oracle"
        )
        self.shape = config.get("shape", "100Mbps")  # 10Mbps, 100Mbps, 400Mbps, 8000Mbps
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.subnet_ids = config.get("subnet_ids", [])
        self.backend_sets = []
        
    def add_target(self, target_id: str, target_config: Dict[str, Any]) -> bool:
        target_info = {
            "id": target_id,
            "ip_address": target_config.get("ip_address", "10.0.0.100"),
            "port": target_config.get("port", 80),
            "weight": target_config.get("weight", 1)
        }
        self.backend_sets.append(target_info)
        print(f"➕ Oracle: Añadiendo backend {target_id} al Load Balancer {self.name}")
        return True
        
    def remove_target(self, target_id: str) -> bool:
        self.backend_sets = [t for t in self.backend_sets if t["id"] != target_id]
        print(f"➖ Oracle: Removiendo backend {target_id} del Load Balancer {self.name}")
        return True
        
    def configure_health_check(self, health_check_config: Dict[str, Any]) -> bool:
        print(f"🔍 Oracle: Configurando health check para Load Balancer {self.name}")
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "shape": self.shape,
            "compartment_id": self.compartment_id,
            "subnet_ids": self.subnet_ids,
            "backend_sets": self.backend_sets,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OracleObjectStorage(Storage):
    """Implementación concreta de almacenamiento para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"oci-storage-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-bucket-{uuid.uuid4().hex[:6]}"),
            provider="oracle"
        )
        self.namespace = config.get("namespace", "my-namespace")
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.storage_tier = config.get("storage_tier", "Standard")  # Standard, InfrequentAccess, Archive
        self.versioning_enabled = config.get("versioning_enabled", False)
        
    def upload_file(self, file_path: str, object_name: str) -> str:
        object_url = f"https://objectstorage.{self.namespace}.oraclecloud.com/n/{self.namespace}/b/{self.name}/o/{object_name}"
        print(f"⬆️ Oracle: Subiendo {file_path} a Object Storage como {object_url}")
        return object_url
        
    def download_file(self, object_name: str, destination_path: str) -> bool:
        print(f"⬇️ Oracle: Descargando {object_name} desde Object Storage bucket {self.name}")
        return True
        
    def delete_file(self, object_name: str) -> bool:
        print(f"🗑️ Oracle: Eliminando {object_name} desde Object Storage bucket {self.name}")
        return True
        
    def set_lifecycle_policy(self, policy_config: Dict[str, Any]) -> bool:
        print(f"📋 Oracle: Configurando lifecycle policy para bucket {self.name}")
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "namespace": self.namespace,
            "compartment_id": self.compartment_id,
            "storage_tier": self.storage_tier,
            "versioning_enabled": self.versioning_enabled,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }