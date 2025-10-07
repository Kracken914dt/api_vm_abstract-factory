"""
Ejemplo de uso del patrón Abstract Factory implementado.

Este archivo demuestra cómo usar el Abstract Factory pattern para crear
infraestructura de cloud de manera consistente y escalable.
"""
from app.domain.factory_provider import create_cloud_factory, CloudProvider
from app.domain.abstractions.factory import CloudResourceManager


def demo_abstract_factory():
    """
    Demuestra el uso del patrón Abstract Factory para crear
    infraestructura en diferentes proveedores de cloud.
    """
    print("🏗️  DEMO: Abstract Factory Pattern para Cloud Infrastructure")
    print("=" * 60)
    
    # Ejemplo 1: Crear infraestructura en AWS
    print("\n1️⃣  CREANDO INFRAESTRUCTURA EN AWS")
    print("-" * 40)
    
    # Obtener la factory de AWS
    aws_factory = create_cloud_factory("aws")
    print(f"✅ Factory creada para: {aws_factory.get_provider_name()}")
    
    # Crear resource manager
    aws_manager = CloudResourceManager(aws_factory)
    
    # Configuración de infraestructura para AWS
    aws_config = {
        "vm": {
            "name": "web-server-aws",
            "config": {
                "instance_type": "t3.micro",
                "ami": "ami-0abcdef1234567890",
                "vpc_id": "vpc-12345",
                "region": "us-east-1"
            }
        },
        "database": {
            "name": "app-db-aws",
            "config": {
                "engine": "mysql",
                "instance_class": "db.t3.micro",
                "allocated_storage": 20,
                "region": "us-east-1"
            }
        },
        "storage": {
            "name": "app-storage-aws",
            "config": {
                "region": "us-east-1",
                "storage_class": "STANDARD"
            }
        }
    }
    
    # Crear infraestructura
    aws_infrastructure = aws_manager.create_infrastructure(aws_config)
    print(f"🎯 Recursos creados en AWS: {len(aws_infrastructure)}")
    
    # Mostrar detalles de los recursos creados
    for resource_type, resource in aws_infrastructure.items():
        print(f"   • {resource_type}: {resource.name} ({resource.get_resource_type()})")
    
    # Ejemplo 2: Crear infraestructura similar en Azure
    print("\n2️⃣  CREANDO INFRAESTRUCTURA EN AZURE")
    print("-" * 40)
    
    # Obtener la factory de Azure
    azure_factory = create_cloud_factory("azure")
    print(f"✅ Factory creada para: {azure_factory.get_provider_name()}")
    
    # Crear resource manager
    azure_manager = CloudResourceManager(azure_factory)
    
    # Configuración de infraestructura para Azure
    azure_config = {
        "vm": {
            "name": "web-server-azure",
            "config": {
                "vm_size": "Standard_B1s",
                "image": "UbuntuLTS",
                "resource_group": "my-rg",
                "region": "eastus"
            }
        },
        "database": {
            "name": "app-db-azure",
            "config": {
                "tier": "Basic",
                "server_name": "mydbserver",
                "resource_group": "my-rg",
                "region": "eastus"
            }
        },
        "storage": {
            "name": "appstorageazure",
            "config": {
                "region": "eastus",
                "account_type": "Standard_LRS"
            }
        }
    }
    
    # Crear infraestructura
    azure_infrastructure = azure_manager.create_infrastructure(azure_config)
    print(f"🎯 Recursos creados en Azure: {len(azure_infrastructure)}")
    
    # Mostrar detalles de los recursos creados
    for resource_type, resource in azure_infrastructure.items():
        print(f"   • {resource_type}: {resource.name} ({resource.get_resource_type()})")
    
    # Ejemplo 3: Operaciones con los recursos
    print("\n3️⃣  REALIZANDO OPERACIONES CON LOS RECURSOS")
    print("-" * 40)
    
    # Operaciones con VM de AWS
    aws_vm = aws_infrastructure["vm"]
    print(f"\n🖥️  Operaciones con VM de AWS: {aws_vm.name}")
    aws_vm.status = "stopped"  # Simular estado inicial
    aws_vm.start()
    aws_vm.resize("t3.small")
    
    # Operaciones con Database de AWS
    aws_db = aws_infrastructure["database"]
    print(f"\n🗄️  Operaciones con DB de AWS: {aws_db.name}")
    backup_id = aws_db.backup()
    aws_db.scale("db.t3.small")
    
    # Operaciones con VM de Azure
    azure_vm = azure_infrastructure["vm"]
    print(f"\n🖥️  Operaciones con VM de Azure: {azure_vm.name}")
    azure_vm.status = "stopped"  # Simular estado inicial
    azure_vm.start()
    azure_vm.resize("Standard_B2s")
    
    print("\n4️⃣  VENTAJAS DEL ABSTRACT FACTORY")
    print("-" * 40)
    print("✅ Consistencia: Misma interfaz para diferentes proveedores")
    print("✅ Escalabilidad: Fácil agregar nuevos proveedores")
    print("✅ Mantenibilidad: Cambios localizados por proveedor")
    print("✅ Testabilidad: Fácil crear mocks de factories")
    print("✅ SOLID: Cumple todos los principios")


def demo_principios_solid():
    """
    Demuestra cómo la implementación cumple con los principios SOLID.
    """
    print("\n🎯 DEMOSTRACIÓN DE PRINCIPIOS SOLID")
    print("=" * 50)
    
    print("\n🔸 SRP (Single Responsibility Principle):")
    print("   • Cada factory solo maneja un proveedor")
    print("   • Cada producto solo representa un tipo de recurso")
    print("   • CloudResourceManager solo gestiona recursos")
    
    print("\n🔸 OCP (Open-Closed Principle):")
    print("   • Agregar nuevo proveedor: crear nueva factory")
    print("   • No modificar código existente")
    print("   • Sistema cerrado para modificación, abierto para extensión")
    
    print("\n🔸 LSP (Liskov Substitution Principle):")
    print("   • Cualquier factory puede reemplazar a otra")
    print("   • Productos concretos intercambiables")
    print("   • Comportamiento consistente entre implementaciones")
    
    print("\n🔸 ISP (Interface Segregation Principle):")
    print("   • Interfaces específicas por tipo de recurso")
    print("   • No forzar implementación de métodos no usados")
    print("   • Contratos claros y enfocados")
    
    print("\n🔸 DIP (Dependency Inversion Principle):")
    print("   • Servicios dependen de abstracciones")
    print("   • No depender de implementaciones concretas")
    print("   • Inyección de dependencias usando factories")


if __name__ == "__main__":
    demo_abstract_factory()
    demo_principios_solid()