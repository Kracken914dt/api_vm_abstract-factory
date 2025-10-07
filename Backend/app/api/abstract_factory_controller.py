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
    provider: str = Field(..., description="Proveedor de cloud (aws, azure, gcp, etc.)")
    vm: Optional[Dict[str, Any]] = Field(None, description="Configuración de VM")
    database: Optional[Dict[str, Any]] = Field(None, description="Configuración de base de datos")
    load_balancer: Optional[Dict[str, Any]] = Field(None, description="Configuración de load balancer")
    storage: Optional[Dict[str, Any]] = Field(None, description="Configuración de almacenamiento")
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
def create_infrastructure(
    request: InfrastructureCreateRequest,
    service: VMService = Depends(get_vm_service)
):
    """
    Crea una infraestructura completa usando el patrón Abstract Factory.
    
    Este endpoint demuestra cómo el Abstract Factory permite crear
    familias de productos relacionados de diferentes proveedores de cloud.
    """
    try:
        # Validar que se especifique al menos un recurso
        resources_to_create = {
            "vm": request.vm,
            "database": request.database,
            "load_balancer": request.load_balancer,
            "storage": request.storage
        }
        
        active_resources = {k: v for k, v in resources_to_create.items() if v is not None}
        
        if not active_resources:
            raise HTTPException(
                status_code=400, 
                detail="At least one resource (vm, database, load_balancer, storage) must be specified"
            )
        
        # Preparar configuración para el Abstract Factory
        infrastructure_config = {
            **active_resources,
            "requested_by": request.requested_by
        }
        
        # Crear infraestructura usando el Abstract Factory
        result = service.create_infrastructure(request.provider, infrastructure_config)
        
        return InfrastructureResponse(
            success=True,
            message=f"Infrastructure created successfully using {result['provider']}",
            provider=result['provider'],
            resources_created=result['resources_created'],
            infrastructure=result['infrastructure']
        )
        
    except ValueError as e:
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id="multiple",
            provider=request.provider,
            success=False,
            details={"error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id="multiple",
            provider=request.provider,
            success=False,
            details={"error": "internal_error"}
        )
        raise HTTPException(status_code=500, detail="Internal server error")


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