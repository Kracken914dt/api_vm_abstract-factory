from __future__ import annotations
from typing import Dict, Any
from app.domain.schemas import VMDTO, ProviderEnum, VMUpdateRequest
from app.domain.factories.base import VirtualMachineFactory
import uuid

class OracleVMFactory(VirtualMachineFactory):
    def validate_params(self, params: Dict[str, Any]) -> None:
        required = ["compute_shape", "compartment_id", "availability_domain", "subnet_id", "image_id"]
        missing = [k for k in required if k not in params]
        if missing:
            raise ValueError(f"Missing Oracle params: {missing}")
    
    def provision(self, name: str, params: Dict[str, Any]) -> VMDTO:
        self.validate_params(params)
        vm_id = f"oracle-{uuid.uuid4()}"
        specs = {
            "compute_shape": params["compute_shape"],
            "compartment_id": params["compartment_id"], 
            "availability_domain": params["availability_domain"],
            "subnet_id": params["subnet_id"],
            "image_id": params["image_id"],
        }
        return VMDTO(
            id=vm_id, name=name, provider=ProviderEnum.oracle, 
            status="stopped", specs=specs
        )
    
    def update(self, vm: VMDTO, changes: VMUpdateRequest) -> VMDTO:
        # Oracle-specific update logic
        if changes.name:
            vm.name = changes.name
        if changes.cpu:
            vm.specs["cpu"] = changes.cpu
        if changes.ram_gb:
            vm.specs["ram_gb"] = changes.ram_gb
        # Oracle puede requerir cambio de compute_shape para CPU/RAM
        return vm
    
    def apply_action(self, vm: VMDTO, action: str) -> VMDTO:
        if action == "start":
            vm.status = "running"
        elif action == "stop": 
            vm.status = "stopped"
        elif action == "restart":
            vm.status = "running"
        else:
            raise ValueError("Invalid action")
        return vm