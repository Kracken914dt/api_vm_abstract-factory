from typing import List, Dict, Any
from datetime import datetime
from app.domain.schemas import (
    VMCreateRequest,
    VMDTO,
    VMUpdateRequest,
    VMActionRequest,
    ProviderEnum
)
from app.domain.ports import VMRepositoryPort
from app.domain.factory_provider import create_cloud_factory, CloudProvider
from app.domain.abstractions.factory import CloudResourceManager
from app.infrastructure.logger import audit_log


class VMService:
    def __init__(self, repo: VMRepositoryPort):
        self.repo = repo

    def create_vm(self, data: VMCreateRequest) -> VMDTO:
        # Usar el nuevo Abstract Factory
        try:
            provider = CloudProvider(data.provider)
            abstract_factory = create_cloud_factory(provider)
            
            # Crear VM usando Abstract Factory
            vm_config = data.params.model_dump()
            virtual_machine = abstract_factory.create_virtual_machine(vm_config)
            
            # Convertir a VMDTO para compatibilidad
            vm = VMDTO(
                id=virtual_machine.resource_id,
                name=virtual_machine.name,
                provider=ProviderEnum(data.provider),
                params=vm_config,
                status="running" if virtual_machine.status.value == "running" else "stopped",
                created_at=datetime.now()
            )
            
            self.repo.save(vm)
            audit_log(
                actor=data.requested_by or "system",
                action="create",
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details={"name": vm.name},
            )
            return vm
        except Exception as e:
            audit_log(
                actor=data.requested_by or "system",
                action="create",
                vm_id="",
                provider=data.provider,
                success=False,
                details={"error": str(e)},
            )
            raise
    
    def create_infrastructure(
        self, 
        provider_name: str,
        infrastructure_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Nuevo método que utiliza el Abstract Factory para crear infraestructura completa.
        
        Args:
            provider_name: Nombre del proveedor (aws, azure, etc.)
            infrastructure_config: Configuración de la infraestructura completa
            
        Returns:
            Diccionario con la infraestructura creada
        """
        try:
            # Obtener la factory usando el nuevo patrón Abstract Factory
            cloud_factory = create_cloud_factory(provider_name)
            
            # Crear el resource manager con la factory
            resource_manager = CloudResourceManager(cloud_factory)
            
            # Crear la infraestructura completa
            infrastructure = resource_manager.create_infrastructure(infrastructure_config)
            
            # Log de la operación exitosa
            audit_log(
                actor=infrastructure_config.get("requested_by", "system"),
                action="create_infrastructure",
                vm_id="multiple",
                provider=provider_name,
                success=True,
                details={
                    "resources_created": len(infrastructure),
                    "provider": cloud_factory.get_provider_name()
                }
            )
            
            return {
                "success": True,
                "infrastructure": infrastructure,
                "provider": cloud_factory.get_provider_name(),
                "resources_created": len(infrastructure)
            }
            
        except Exception as e:
            audit_log(
                actor=infrastructure_config.get("requested_by", "system"),
                action="create_infrastructure",
                vm_id="multiple",
                provider=provider_name,
                success=False,
                details={"error": str(e)}
            )
            raise

    def update_vm(self, vm_id: str, changes: VMUpdateRequest) -> VMDTO:
        vm = self.repo.get(vm_id)
        try:
            provider = CloudProvider(vm.provider)
            abstract_factory = create_cloud_factory(provider)
            
            # Para actualizar, necesitamos obtener la VM desde el Abstract Factory
            # y luego aplicar los cambios
            vm_config = changes.model_dump(exclude_none=True)
            
            # Actualizar los parámetros de la VM
            if changes.params:
                vm.params.update(vm_config.get('params', {}))
            
            # Simular actualización usando Abstract Factory
            # En un escenario real, aquí se llamaría a la API del proveedor
            virtual_machine = abstract_factory.create_virtual_machine(vm.params)
            virtual_machine.resize(vm_config.get('params', {}).get('instance_type', vm.params.get('instance_type')))
            
            self.repo.save(vm)
            audit_log(
                actor="system",
                action="update",
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details=changes.model_dump(exclude_none=True),
            )
            return vm
        except Exception as e:
            audit_log(
                actor="system",
                action="update",
                vm_id=vm_id,
                provider=vm.provider if vm else "unknown",
                success=False,
                details={"error": str(e)},
            )
            raise

    def delete_vm(self, vm_id: str) -> None:
        vm = self.repo.get(vm_id)
        try:
            provider = CloudProvider(vm.provider)
            abstract_factory = create_cloud_factory(provider)
            
            # Simular eliminación usando Abstract Factory
            virtual_machine = abstract_factory.create_virtual_machine(vm.params)
            virtual_machine.stop()  # Detener antes de eliminar
            
            self.repo.delete(vm_id)
            audit_log(
                actor="system",
                action="delete",
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details=None,
            )
        except Exception as e:
            audit_log(
                actor="system",
                action="delete",
                vm_id=vm_id,
                provider=vm.provider if vm else "unknown",
                success=False,
                details={"error": str(e)},
            )
            raise

    def apply_action(self, vm_id: str, action_req: VMActionRequest) -> VMDTO:
        vm = self.repo.get(vm_id)
        try:
            provider = CloudProvider(vm.provider)
            abstract_factory = create_cloud_factory(provider)
            
            # Crear la VM para aplicar acciones
            virtual_machine = abstract_factory.create_virtual_machine(vm.params)
            
            # Aplicar la acción
            if action_req.action == "start":
                virtual_machine.start()
                vm.status = "running"
            elif action_req.action == "stop":
                virtual_machine.stop()
                vm.status = "stopped"
            elif action_req.action == "restart":
                virtual_machine.stop()
                virtual_machine.start()
                vm.status = "running"
            
            self.repo.save(vm)
            audit_log(
                actor=action_req.requested_by or "system",
                action=action_req.action,
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details=None,
            )
            return vm
        except Exception as e:
            audit_log(
                actor=action_req.requested_by or "system",
                action=action_req.action,
                vm_id=vm_id,
                provider=vm.provider if vm else "unknown",
                success=False,
                details={"error": str(e)},
            )
            raise

    def get_vm(self, vm_id: str) -> VMDTO:
        return self.repo.get(vm_id)

    def list_vms(self) -> List[VMDTO]:
        return self.repo.list()