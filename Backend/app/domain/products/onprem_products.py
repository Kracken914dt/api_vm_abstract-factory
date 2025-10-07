"""
Productos concretos de OnPremise para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para infraestructura on-premise (VMware, Hyper-V, KVM, etc.).
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class OnPremiseVirtualMachine(VirtualMachine):
    """Implementación concreta de VM para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"onprem-vm-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-vm-{uuid.uuid4().hex[:6]}"),
            provider="onprem"
        )
        self.cpu_cores = config.get("cpu", 2)
        self.ram_gb = config.get("ram_gb", 4)
        self.disk_gb = config.get("disk_gb", 50)
        self.hypervisor = config.get("hypervisor", "vmware")  # vmware, hyperv, kvm, xen
        self.network_interface = config.get("nic", "eth0")
        self.host_server = config.get("host_server", "esxi-01.company.local")
        self.datastore = config.get("datastore", "datastore1")
        
    def start(self) -> bool:
        """Iniciar la VM on-premise"""
        print(f"🟢 OnPrem: Iniciando VM {self.name} en {self.hypervisor} host {self.host_server}")
        self.status = ResourceStatus.RUNNING
        return True
        
    def stop(self) -> bool:
        """Detener la VM on-premise"""
        print(f"🔴 OnPrem: Deteniendo VM {self.name} en {self.hypervisor}")
        self.status = ResourceStatus.STOPPED
        return True
        
    def resize(self, new_config: Dict[str, Any]) -> bool:
        """Cambiar las especificaciones de la VM"""
        new_cpu = new_config.get("cpu", self.cpu_cores)
        new_ram = new_config.get("ram_gb", self.ram_gb)
        new_disk = new_config.get("disk_gb", self.disk_gb)
        
        print(f"🔄 OnPrem: Redimensionando VM {self.name}: {self.cpu_cores}→{new_cpu} CPUs, {self.ram_gb}→{new_ram}GB RAM, {self.disk_gb}→{new_disk}GB disk")
        
        self.cpu_cores = new_cpu
        self.ram_gb = new_ram
        self.disk_gb = new_disk
        return True
        
    def get_status(self) -> ResourceStatus:
        return self.status
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "disk_gb": self.disk_gb,
            "hypervisor": self.hypervisor,
            "network_interface": self.network_interface,
            "host_server": self.host_server,
            "datastore": self.datastore,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OnPremiseDatabase(Database):
    """Implementación concreta de base de datos para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"onprem-db-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-db-{uuid.uuid4().hex[:6]}"),
            provider="onprem"
        )
        self.engine = config.get("engine", "postgresql")  # postgresql, mysql, oracle, sqlserver
        self.version = config.get("version", "13.0")
        self.port = config.get("port", 5432)
        self.host_server = config.get("host_server", "db-server-01.company.local")
        self.data_directory = config.get("data_directory", "/var/lib/postgresql/data")
        self.max_connections = config.get("max_connections", 100)
        
    def create_backup(self) -> str:
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        backup_path = f"/backups/{self.name}/{backup_id}.sql"
        print(f"💾 OnPrem: Creando backup {backup_id} de base de datos {self.name} → {backup_path}")
        return backup_id
        
    def restore_from_backup(self, backup_id: str) -> bool:
        backup_path = f"/backups/{self.name}/{backup_id}.sql"
        print(f"♻️ OnPrem: Restaurando base de datos {self.name} desde {backup_path}")
        return True
        
    def scale(self, new_config: Dict[str, Any]) -> bool:
        new_max_conn = new_config.get("max_connections", self.max_connections)
        print(f"📈 OnPrem: Escalando base de datos {self.name}: max_connections {self.max_connections}→{new_max_conn}")
        self.max_connections = new_max_conn
        return True
        
    def get_connection_string(self) -> str:
        return f"{self.engine}://user:password@{self.host_server}:{self.port}/{self.name}"
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "engine": self.engine,
            "version": self.version,
            "port": self.port,
            "host_server": self.host_server,
            "data_directory": self.data_directory,
            "max_connections": self.max_connections,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OnPremiseLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"onprem-lb-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-lb-{uuid.uuid4().hex[:6]}"),
            provider="onprem"
        )
        self.load_balancer_type = config.get("type", "nginx")  # nginx, haproxy, f5, citrix
        self.listen_port = config.get("listen_port", 80)
        self.algorithm = config.get("algorithm", "round_robin")  # round_robin, least_conn, ip_hash
        self.host_server = config.get("host_server", "lb-server-01.company.local")
        self.backend_servers = []
        
    def add_target(self, target_id: str, target_config: Dict[str, Any]) -> bool:
        target_info = {
            "id": target_id,
            "host": target_config.get("host", "app-server-01.company.local"),
            "port": target_config.get("port", 8080),
            "weight": target_config.get("weight", 1),
            "max_fails": target_config.get("max_fails", 3)
        }
        self.backend_servers.append(target_info)
        print(f"➕ OnPrem: Añadiendo backend {target_id} ({target_info['host']}:{target_info['port']}) al Load Balancer {self.name}")
        return True
        
    def remove_target(self, target_id: str) -> bool:
        self.backend_servers = [t for t in self.backend_servers if t["id"] != target_id]
        print(f"➖ OnPrem: Removiendo backend {target_id} del Load Balancer {self.name}")
        return True
        
    def configure_health_check(self, health_check_config: Dict[str, Any]) -> bool:
        check_path = health_check_config.get("path", "/health")
        check_interval = health_check_config.get("interval", 30)
        print(f"🔍 OnPrem: Configurando health check para Load Balancer {self.name}: {check_path} cada {check_interval}s")
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "type": self.load_balancer_type,
            "listen_port": self.listen_port,
            "algorithm": self.algorithm,
            "host_server": self.host_server,
            "backend_servers": self.backend_servers,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OnPremiseStorage(Storage):
    """Implementación concreta de almacenamiento para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            resource_id=f"onprem-storage-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-share-{uuid.uuid4().hex[:6]}"),
            provider="onprem"
        )
        self.storage_type = config.get("storage_type", "nfs")  # nfs, smb, iscsi, fc
        self.mount_point = config.get("mount_point", f"/mnt/{self.name}")
        self.capacity_gb = config.get("capacity_gb", 1000)
        self.host_server = config.get("host_server", "storage-server-01.company.local")
        self.protocol_version = config.get("protocol_version", "4.1")
        self.access_permissions = config.get("permissions", "rw")
        
    def upload_file(self, file_path: str, object_name: str) -> str:
        destination_path = f"{self.mount_point}/{object_name}"
        print(f"⬆️ OnPrem: Copiando {file_path} a {self.storage_type} share → {destination_path}")
        return destination_path
        
    def download_file(self, object_name: str, destination_path: str) -> bool:
        source_path = f"{self.mount_point}/{object_name}"
        print(f"⬇️ OnPrem: Descargando {source_path} desde {self.storage_type} share {self.name}")
        return True
        
    def delete_file(self, object_name: str) -> bool:
        file_path = f"{self.mount_point}/{object_name}"
        print(f"🗑️ OnPrem: Eliminando {file_path} desde {self.storage_type} share {self.name}")
        return True
        
    def set_lifecycle_policy(self, policy_config: Dict[str, Any]) -> bool:
        retention_days = policy_config.get("retention_days", 30)
        print(f"📋 OnPrem: Configurando política de retención de {retention_days} días para {self.name}")
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "storage_type": self.storage_type,
            "mount_point": self.mount_point,
            "capacity_gb": self.capacity_gb,
            "host_server": self.host_server,
            "protocol_version": self.protocol_version,
            "access_permissions": self.access_permissions,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }