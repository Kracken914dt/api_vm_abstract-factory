"""
Controlador para el patrón Abstract Factory.
Demuestra el uso del Abstract Factory para crear familias de productos de cloud.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.domain.factory_provider import (
    create_cloud_factory, 
    get_available_providers,
    CloudProvider
)
from app.domain.abstractions.factory import CloudResourceManager
from app.core.container import get_vm_service
from app.domain.services import VMService
from app.infrastructure.logger import audit_log

router = APIRouter()


class InfrastructureCreateRequest(BaseModel):
    """Request model para crear infraestructura completa"""
    provider: str = Field(..., description="Proveedor de cloud (aws, azure, gcp, oracle, onprem)")
    name: str = Field(..., description="Nombre de la infraestructura")
    region: Optional[str] = Field("us-east-1", description="Región donde crear la infraestructura")
    vm_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de VM")
    database_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de base de datos") 
    load_balancer_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de load balancer")
    storage_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de almacenamiento")
    include_database: Optional[bool] = Field(True, description="Incluir base de datos")
    include_load_balancer: Optional[bool] = Field(True, description="Incluir load balancer")
    include_storage: Optional[bool] = Field(True, description="Incluir almacenamiento")
    requested_by: Optional[str] = Field("system", description="Usuario que solicita la creación")

    class Config:
        schema_extra = {
            "example": {
                "provider": "aws",
                "vm": {
                    "name": "web-server-vm",
                    "config": {
                        "instance_type": "t3.micro",
                        "ami": "ami-0abcdef1234567890",
                        "vpc_id": "vpc-12345",
                        "region": "us-east-1"
                    }
                },
                "database": {
                    "name": "app-database",
                    "config": {
                        "engine": "mysql",
                        "instance_class": "db.t3.micro",
                        "allocated_storage": 20,
                        "region": "us-east-1"
                    }
                },
                "load_balancer": {
                    "name": "web-lb",
                    "config": {
                        "vpc_id": "vpc-12345",
                        "region": "us-east-1",
                        "scheme": "internet-facing"
                    }
                },
                "storage": {
                    "name": "app-storage-bucket",
                    "config": {
                        "region": "us-east-1",
                        "storage_class": "STANDARD"
                    }
                },
                "requested_by": "admin"
            }
        }


class InfrastructureResponse(BaseModel):
    """Response model para operaciones de infraestructura"""
    success: bool
    message: str
    provider: Optional[str] = None
    resources_created: Optional[int] = None
    infrastructure: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/infrastructure/create", response_model=InfrastructureResponse)
def create_infrastructure(request: InfrastructureCreateRequest):
    """
    Crea una infraestructura completa usando el patrón Abstract Factory.
    
    Este endpoint demuestra cómo el Abstract Factory permite crear
    familias de productos relacionados de diferentes proveedores de cloud.
    """
    try:
        print(f"📦 Iniciando creación de infraestructura para proveedor: {request.provider}")
        
        # Obtener la factory para el proveedor
        try:
            provider_enum = CloudProvider(request.provider.lower())
            factory = create_cloud_factory(provider_enum)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Proveedor '{request.provider}' no soportado. Proveedores disponibles: {[p.value for p in CloudProvider]}"
            )
        print(f"🏭 Factory obtenida: {type(factory).__name__}")
        
        # Lista para almacenar recursos creados
        resources_created = []
        infrastructure_details = {}
        
        # Crear VM siempre (recurso base)
        vm_name = f"{request.name}-vm"
        
        # Preparar configuración de VM
        if request.vm_config:
            vm_config = request.vm_config.copy()
        else:
            vm_config = {}
        
        # Asegurar configuración mínima por proveedor
        vm_config["region"] = vm_config.get("region", request.region)
        
        if request.provider == "aws":
            # Campos requeridos por AWS factory - siempre necesarios
            if "instance_type" not in vm_config:
                vm_config["instance_type"] = "t2.micro"
            if "ami" not in vm_config:
                vm_config["ami"] = "ami-0abcdef1234567890"  
            if "vpc_id" not in vm_config:
                vm_config["vpc_id"] = "vpc-12345678"
            # Los campos opcionales como key_pair se preservan si los envió el usuario
        elif request.provider == "azure":
            vm_config.setdefault("vm_size", "Standard_B1s")
            vm_config.setdefault("resource_group", "rg-default")
            vm_config.setdefault("image", "Ubuntu 20.04 LTS")
        elif request.provider == "gcp":
            vm_config.setdefault("machine_type", "e2-micro")
            vm_config.setdefault("zone", "us-central1-a")
            vm_config.setdefault("project", "demo-project")
        elif request.provider == "oracle":
            vm_config.setdefault("compute_shape", "VM.Standard2.1")
            vm_config.setdefault("compartment_id", "ocid.compartment.demo")
            vm_config.setdefault("availability_domain", "AD-1")
        elif request.provider == "onprem":
            vm_config.setdefault("cpu", 2)
            vm_config.setdefault("ram_gb", 4)
            vm_config.setdefault("disk_gb", 50)
        
        vm = factory.create_virtual_machine(vm_name, vm_config)
        vm_info = {
            "name": vm.name,
            "resource_id": vm.resource_id,
            "region": vm.region,
            "status": vm.status.value,
            "type": vm.get_resource_type(),
            "specs": vm.get_specs()
        }
        resources_created.append("virtual_machine")
        infrastructure_details["virtual_machine"] = vm_info
        print(f"🖥️ VM creada: {vm_info}")
        
        # Crear Database si se requiere
        if request.include_database:
            db_name = f"{request.name}-db"
            db_config = request.database_config or {
                "region": request.region,
                "engine": "mysql",
                "instance_class": "db.t3.micro",
                "allocated_storage": 20
            }
            
            db = factory.create_database(db_name, db_config)
            db_info = {
                "name": db.name,
                "resource_id": db.resource_id,
                "region": db.region,
                "status": db.status.value,
                "type": db.get_resource_type(),
                "specs": db.get_specs()
            }
            resources_created.append("database")
            infrastructure_details["database"] = db_info
            print(f"🗄️ Database creada: {db_info}")
        
        # Crear Load Balancer si se requiere
        if request.include_load_balancer:
            lb_name = f"{request.name}-lb"
            lb_config = request.load_balancer_config or {
                "region": request.region,
                "load_balancer_type": "application",
                "scheme": "internet-facing"
            }
            
            # Asegurar campos requeridos por proveedor para Load Balancer
            if request.provider == "aws":
                if "vpc_id" not in lb_config:
                    lb_config["vpc_id"] = "vpc-12345678"  # Usar el mismo VPC que la VM
            
            lb = factory.create_load_balancer(lb_name, lb_config)
            lb_info = {
                "name": lb.name,
                "resource_id": lb.resource_id,
                "region": lb.region,
                "status": lb.status.value,
                "type": lb.get_resource_type(),
                "specs": lb.get_specs()
            }
            resources_created.append("load_balancer")
            infrastructure_details["load_balancer"] = lb_info
            print(f"⚖️ Load Balancer creado: {lb_info}")
        
        # Crear Storage si se requiere
        if request.include_storage:
            storage_name = f"{request.name}-storage"
            storage_config = request.storage_config or {
                "region": request.region,
                "size_gb": 100,
                "storage_type": "gp3" if request.provider == "aws" else "standard"
            }
            
            storage = factory.create_storage(storage_name, storage_config) 
            storage_info = {
                "name": storage.name,
                "resource_id": storage.resource_id,
                "region": storage.region,
                "status": storage.status.value,
                "type": storage.get_resource_type(),
                "specs": storage.get_specs()
            }
            resources_created.append("storage")
            infrastructure_details["storage"] = storage_info
            print(f"💾 Storage creado: {storage_info}")
        
        # Registrar en logs
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id=f"{request.name}-infrastructure",
            provider=request.provider,
            success=True,
            details={
                "infrastructure_name": request.name,
                "resources_created": len(resources_created),
                "pattern": "Abstract Factory"
            }
        )
        
        result = InfrastructureResponse(
            success=True,
            message=f"Infraestructura '{request.name}' creada exitosamente usando {request.provider.upper()}",
            provider=request.provider,
            resources_created=len(resources_created),
            infrastructure=infrastructure_details
        )
        
        print(f"✅ Infraestructura creada exitosamente: {len(resources_created)} recursos")
        return result
        
    except KeyError as e:
        error_msg = f"Proveedor '{request.provider}' no soportado. Proveedores disponibles: aws, azure, gcp, oracle, onprem"
        print(f"❌ Error de proveedor: {error_msg}")
        
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id="error",
            provider=request.provider,
            success=False,
            details={"error": "unsupported_provider"}
        )
        
        raise HTTPException(status_code=400, detail=error_msg)
        
    except Exception as e:
        error_msg = f"Error interno al crear infraestructura: {str(e)}"
        print(f"❌ Error interno: {error_msg}")
        
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id="error",
            provider=request.provider,
            success=False,
            details={"error": "internal_error", "details": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/providers", response_model=Dict[str, Any])
def get_supported_providers():
    """
    Obtiene la lista de proveedores de cloud soportados.
    """
    try:
        providers = get_available_providers()
        
        return {
            "supported_providers": providers,
            "total": len(providers),
            "description": "List of cloud providers supported by the Abstract Factory"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching providers")


@router.get("/providers/{provider}/info", response_model=Dict[str, Any])
def get_provider_info(provider: str):
    """
    Obtiene información específica de un proveedor.
    """
    try:
        # Crear factory para obtener información del proveedor
        factory = create_cloud_factory(provider)
        
        info = {
            "provider_name": factory.get_provider_name(),
            "provider_code": provider,
            "supported_services": [
                "Virtual Machines",
                "Databases", 
                "Load Balancers",
                "Storage"
            ]
        }
        
        # Información específica por proveedor
        if hasattr(factory, 'get_supported_regions'):
            info["supported_regions"] = list(factory.get_supported_regions())
        
        if hasattr(factory, 'get_recommended_instance_types'):
            info["recommended_instance_types"] = factory.get_recommended_instance_types()
        elif hasattr(factory, 'get_recommended_vm_sizes'):
            info["recommended_vm_sizes"] = factory.get_recommended_vm_sizes()
        
        return info
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching provider info")


@router.get("/infrastructure/examples", response_model=Dict[str, Any])
def get_infrastructure_examples():
    """
    Obtiene ejemplos de configuración de infraestructura para diferentes proveedores.
    """
    examples = {
        "aws": {
            "provider": "aws",
            "vm": {
                "name": "web-server",
                "config": {
                    "instance_type": "t3.micro",
                    "ami": "ami-0abcdef1234567890",
                    "vpc_id": "vpc-12345",
                    "region": "us-east-1",
                    "security_groups": ["sg-web-servers"]
                }
            },
            "database": {
                "name": "app-db",
                "config": {
                    "engine": "mysql",
                    "instance_class": "db.t3.micro",
                    "allocated_storage": 20,
                    "region": "us-east-1"
                }
            },
            "storage": {
                "name": "app-files",
                "config": {
                    "region": "us-east-1",
                    "storage_class": "STANDARD",
                    "versioning_enabled": True
                }
            }
        },
        "azure": {
            "provider": "azure",
            "vm": {
                "name": "web-server",
                "config": {
                    "vm_size": "Standard_B1s",
                    "image": "UbuntuLTS",
                    "resource_group": "my-rg",
                    "region": "eastus"
                }
            },
            "database": {
                "name": "app-db",
                "config": {
                    "tier": "Basic",
                    "server_name": "mydbserver",
                    "resource_group": "my-rg",
                    "region": "eastus"
                }
            },
            "storage": {
                "name": "appfiles",
                "config": {
                    "region": "eastus",
                    "account_type": "Standard_LRS",
                    "access_tier": "Hot"
                }
            }
        }
    }
    
    return {
        "description": "Example configurations for different cloud providers",
        "examples": examples
    }