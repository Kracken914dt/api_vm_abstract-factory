# VM Abstract Factory API (FastAPI)

API que implementa completamente el **patrón Abstract Factory** siguiendo principios **SOLID** para gestión de infraestructura cloud completa (VMs, Databases, Load Balancers, Storage) en **5 proveedores** (AWS, Azure, GCP, Oracle, On-Premise), con validación tipada por proveedor, persistencia simulada en memoria y logs de auditoría.

## ✅ **IMPLEMENTACIÓN COMPLETA - ABSTRACT FACTORY**

### 🏭 **5 Proveedores Completamente Implementados**

- ☁️ **AWS**: EC2, RDS, ALB, S3
- ☁️ **Azure**: VMs, SQL Database, Load Balancer, Blob Storage
- ☁️ **GCP**: Compute Engine, Cloud SQL, Load Balancing, Cloud Storage
- ☁️ **Oracle**: Compute, Autonomous Database, Load Balancer, Object Storage
- 🏢 **OnPremise**: VMware/Hyper-V, PostgreSQL/MySQL, Nginx/HAProxy, NFS/SMB

## 🏗️ Patrón Abstract Factory Implementado

Esta API implementa el patrón **Abstract Factory** que permite crear familias de productos relacionados (infraestructura cloud) sin especificar sus clases concretas. Cada proveedor cloud tiene su propia factory que crea productos compatibles entre sí.

## 🚀 Endpoints principales

### 🔥 **Abstract Factory Pattern** (Implementación Principal)

- **POST** `/cloud/infrastructure/create` - Crea infraestructura completa por proveedor
- **GET** `/cloud/providers` - Lista proveedores cloud disponibles
- **GET** `/health` - Estado del servicio y patrón implementado

### 🏗️ **Legacy - Factory Method Pattern** (VMs únicamente)

- **POST** `/vm/create` - Crea una VM usando Factory Method
- **PUT** `/vm/{id}` - Actualiza especificaciones de VM
- **DELETE** `/vm/{id}` - Elimina una VM
- **POST** `/vm/{id}/action` - Ejecuta acción: start|stop|restart
- **GET** `/vm/{id}` - Consulta una VM específica
- **GET** `/vm` - Lista todas las VMs
- **GET** `/api/logs` - Consulta logs de auditoría

## 🏛️ Arquitectura del Proyecto

### 🏭 **Abstract Factory Pattern** (Implementación Principal)

- **`app/domain/abstractions/`**: Interfaces abstractas para productos y factories
  - `factory.py`: CloudAbstractFactory, CloudResourceManager
  - `products.py`: VirtualMachine, Database, LoadBalancer, Storage
- **`app/domain/products/`**: Implementaciones concretas de productos cloud
  - `aws_products.py`: EC2Instance, RDSDatabase, ApplicationLoadBalancer, S3Storage
  - `azure_products.py`: AzureVM, SQLDatabase, AzureLoadBalancer, BlobStorage
  - `gcp_products.py`: ComputeEngine, CloudSQL, GCPLoadBalancer, CloudStorage
  - `oracle_products.py`: OracleCompute, AutonomousDatabase, OracleLoadBalancer, ObjectStorage
  - `onprem_products.py`: OnPremVM, OnPremDatabase, OnPremLoadBalancer, OnPremStorage
- **`app/domain/factories_concrete/`**: Factories concretas por proveedor
  - `aws_factory.py`, `azure_factory.py`, `gcp_factory.py`, `oracle_factory.py`, `onprem_factory.py`
- **`app/domain/factory_provider.py`**: Provider pattern para obtener Abstract Factories
- **`app/api/abstract_factory_controller.py`**: Controlador REST para Abstract Factory

### 🔧 **Legacy Factory Method** (Mantenido para compatibilidad)

- **`app/domain/factories/`**: Implementación original del patrón Factory Method para VMs
- **`app/api/vm_controller.py`**: Controlador REST para Factory Method

### 🏗️ **Infraestructura Core**

- **`app/main.py`**: FastAPI app con endpoints para ambos patrones
- **`app/domain/schemas/`**: Validación tipada con Pydantic por proveedor
- **`app/domain/services/`**: Lógica de negocio (VM service, Log service)
- **`app/infrastructure/`**: Repositorio en memoria y logger de auditoría
- **`app/core/`**: Inyección de dependencias

## 🚀 Ejecutar

1. Instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Iniciar servidor

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Documentación interactiva

http://localhost:8000/docs

## 🧪 Probar el Abstract Factory

### 🚀 Ejecutar prueba completa de todos los proveedores:

```powershell
python test_complete_abstract_factory.py
```

### 📝 Prueba específica con Postman o curl:

```powershell
# Usar los ejemplos de curl de la sección anterior
python test_postman.py  # Script de prueba con requests
```

### 🌐 Documentación interactiva:

Una vez iniciado el servidor, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### ✅ **Resultados esperados**:

- ✅ 5 proveedores funcionando: AWS, Azure, GCP, Oracle, OnPremise
- ✅ 4 tipos de recursos por proveedor: VM, Database, LoadBalancer, Storage
- ✅ Principios SOLID completamente implementados
- ✅ Patrón Abstract Factory completamente extensible
- ✅ Validación tipada por proveedor con Pydantic
- ✅ Logs de auditoría en formato JSON
- ✅ Persistencia simulada en memoria

## 🔥 Ejemplos de Uso - Abstract Factory

## 📘 Referencia Completa de Payload /cloud/infrastructure/create

El endpoint `POST /cloud/infrastructure/create` acepta este modelo base:

```json
{
  "provider": "aws|azure|gcp|oracle|onprem",
  "name": "nombre-base-infra",
  "region": "<region principal>",
  "vm_config": {
    /* requerido siempre (el controlador rellena defaults si faltan) */
  },
  "database_config": {
    /* requerido si include_database=true (defaults por proveedor) */
  },
  "load_balancer_config": {
    /* requerido si include_load_balancer=true (defaults por proveedor) */
  },
  "storage_config": {
    /* requerido si include_storage=true (defaults por proveedor) */
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "usuario"
}
```

El controlador agrega automáticamente parámetros mínimos cuando no se envían, pero si quieres control total o evitar validaciones 400, usa las tablas siguientes.

### ✅ Campos por Proveedor y Recurso

| Proveedor | Recurso                               | Campos Obligatorios                                                               | Campos Opcionales / Defaults Inyectados                             |
| --------- | ------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| AWS       | VM (`vm_config`)                      | `instance_type`, `ami`, `vpc_id`, `region`                                        | `security_groups`, `key_pair`                                       |
| AWS       | Database (`database_config`)          | `engine`, `instance_class`, `allocated_storage`, `region`                         | —                                                                   |
| AWS       | LoadBalancer (`load_balancer_config`) | `vpc_id`, `region`                                                                | `scheme` (por defecto `internet-facing`), `listeners`               |
| AWS       | Storage (`storage_config`)            | `region`                                                                          | `storage_class` (STANDARD), `versioning_enabled`                    |
| Azure     | VM                                    | `vm_size`, `image`, `resource_group`, `region`                                    | `virtual_network`, `network_security_group`                         |
| Azure     | Database                              | `tier`, `server_name`, `resource_group`, `region`                                 | `max_size_gb`                                                       |
| Azure     | LoadBalancer                          | `resource_group`, `region`                                                        | `sku` (Standard), `frontend_ip_configs`                             |
| Azure     | Storage                               | `region`                                                                          | `account_type` (Standard_LRS), `access_tier` (Hot)                  |
| GCP       | VM                                    | `machine_type`                                                                    | `zone`, `project` (el controlador agrega defaults), otros metadatos |
| GCP       | Database                              | `engine`                                                                          | `tier`, `storage_size`, `region` (si aplica)                        |
| GCP       | LoadBalancer                          | _(ninguno estricto)_                                                              | `type` (HTTP(S)), `region`/`global`                                 |
| GCP       | Storage                               | _(ninguno estricto)_                                                              | `storage_class` (STANDARD), `location` (US)                         |
| Oracle    | VM                                    | `compute_shape`, `compartment_id`, `availability_domain`, `subnet_id`, `image_id` | —                                                                   |
| Oracle    | Database                              | `workload_type`, `compartment_id`                                                 | `cpu_count`, `storage_tb`                                           |
| Oracle    | LoadBalancer                          | `compartment_id`                                                                  | `shape` (100Mbps)                                                   |
| Oracle    | Storage                               | `namespace`, `compartment_id`                                                     | `storage_tier` (Standard)                                           |
| OnPrem    | VM                                    | `cpu`, `ram_gb`, `disk_gb`, `nic`                                                 | `hypervisor` (vmware), `host_server`, `datastore`                   |
| OnPrem    | Database                              | `engine`                                                                          | `version`, `port`, `data_directory`                                 |
| OnPrem    | LoadBalancer                          | _(ninguno estricto)_                                                              | `type` (nginx), `algorithm` (round_robin), `listen_port`            |
| OnPrem    | Storage                               | `storage_type`                                                                    | `capacity_gb` (100), `protocol`, `mount_point`                      |

Notas:

1. Para **Azure**, si envías regiones abreviadas como `East`, el controlador intentará normalizar a `eastus`.
2. Para **GCP**, la validación estricta recae en `machine_type` y `engine` / `storage_class` según recurso.
3. Para **Oracle**, si falta cualquiera de los campos obligatorios en VM se retorna 400.
4. Para **OnPrem**, se validan mínimos de recursos (cpu>=1, ram_gb>=1, disk_gb>=10).

### 🔄 Defaults que el controlador rellena si faltan

| Proveedor          | Campo                   | Valor por Defecto                  |
| ------------------ | ----------------------- | ---------------------------------- |
| AWS                | `instance_type`         | `t2.micro`                         |
| AWS                | `ami`                   | `ami-0abcdef1234567890`            |
| AWS                | `vpc_id`                | `vpc-12345678`                     |
| Azure              | `vm_size`               | `Standard_B1s`                     |
| Azure              | `resource_group`        | `rg-default`                       |
| Azure              | `image`                 | `Ubuntu 20.04 LTS`                 |
| GCP                | `machine_type`          | `e2-micro` (si no enviado)         |
| GCP                | `zone`                  | `us-central1-a`                    |
| GCP                | `project`               | `demo-project`                     |
| Oracle             | `compute_shape`         | `VM.Standard2.1`                   |
| Oracle             | `compartment_id`        | `ocid.compartment.demo`            |
| Oracle             | `availability_domain`   | `AD-1`                             |
| OnPrem             | `cpu`                   | `2`                                |
| OnPrem             | `ram_gb`                | `4`                                |
| OnPrem             | `disk_gb`               | `50`                               |
| Storage (genérico) | `storage_type` (onprem) | `gp3` o `standard` según proveedor |

---

### 🧩 Ejemplos de payload COMPLETO por proveedor (todos los recursos)

#### AWS (completo)

```json
{
  "provider": "aws",
  "name": "infra-aws",
  "region": "us-east-1",
  "vm_config": {
    "instance_type": "t3.medium",
    "ami": "ami-0abcdef1234567890",
    "vpc_id": "vpc-12345678",
    "security_groups": ["sg-web"],
    "key_pair": "my-key"
  },
  "database_config": {
    "engine": "mysql",
    "instance_class": "db.t3.micro",
    "allocated_storage": 20,
    "region": "us-east-1"
  },
  "load_balancer_config": {
    "vpc_id": "vpc-12345678",
    "region": "us-east-1",
    "scheme": "internet-facing"
  },
  "storage_config": {
    "region": "us-east-1",
    "storage_class": "STANDARD",
    "versioning_enabled": true
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### Azure (completo)

```json
{
  "provider": "azure",
  "name": "infra-azure",
  "region": "westus",
  "vm_config": {
    "vm_size": "Standard_B2s",
    "image": "Ubuntu 20.04 LTS",
    "resource_group": "rg-apps",
    "virtual_network": "vnet-apps",
    "network_security_group": "nsg-web"
  },
  "database_config": {
    "tier": "Basic",
    "server_name": "app-sqlsrv",
    "resource_group": "rg-apps",
    "region": "westus",
    "max_size_gb": 32
  },
  "load_balancer_config": {
    "resource_group": "rg-apps",
    "region": "westus",
    "sku": "Standard"
  },
  "storage_config": {
    "region": "westus",
    "account_type": "Standard_LRS",
    "access_tier": "Hot"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### GCP (completo)

```json
{
  "provider": "gcp",
  "name": "infra-gcp",
  "region": "us-central1",
  "vm_config": {
    "machine_type": "e2-medium",
    "zone": "us-central1-a",
    "project": "demo-project"
  },
  "database_config": {
    "engine": "postgres",
    "tier": "db-f1-micro",
    "region": "us-central1"
  },
  "load_balancer_config": {
    "type": "HTTP(S)",
    "region": "us-central1"
  },
  "storage_config": {
    "storage_class": "STANDARD",
    "location": "US"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### Oracle Cloud (completo)

```json
{
  "provider": "oracle",
  "name": "infra-oracle",
  "region": "us-ashburn-1",
  "vm_config": {
    "compute_shape": "VM.Standard2.1",
    "compartment_id": "ocid1.compartment.oc1..xxxxx",
    "availability_domain": "AD-1",
    "subnet_id": "ocid1.subnet.oc1..xxxxx",
    "image_id": "ocid1.image.oc1..xxxxx"
  },
  "database_config": {
    "workload_type": "OLTP",
    "compartment_id": "ocid1.compartment.oc1..xxxxx"
  },
  "load_balancer_config": {
    "compartment_id": "ocid1.compartment.oc1..xxxxx",
    "shape": "100Mbps"
  },
  "storage_config": {
    "namespace": "mytenantns",
    "compartment_id": "ocid1.compartment.oc1..xxxxx",
    "storage_tier": "Standard"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### On-Premise (completo)

```json
{
  "provider": "onprem",
  "name": "infra-onprem",
  "region": "datacenter-1",
  "vm_config": {
    "cpu": 4,
    "ram_gb": 8,
    "disk_gb": 120,
    "nic": "eth0",
    "hypervisor": "vmware",
    "host_server": "esxi-01",
    "datastore": "ds-main"
  },
  "database_config": {
    "engine": "postgresql",
    "version": "14",
    "port": 5432,
    "data_directory": "/data/postgres"
  },
  "load_balancer_config": {
    "type": "nginx",
    "algorithm": "round_robin",
    "listen_port": 80
  },
  "storage_config": {
    "storage_type": "nfs",
    "capacity_gb": 500,
    "protocol": "nfs",
    "mount_point": "/mnt/files"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

---

### 🩺 1. Verificar estado del servicio

```bash
curl -X GET "http://localhost:8000/health"
```

**Respuesta esperada:**

```json
{
  "status": "ok",
  "version": "2.0.0",
  "pattern": "Abstract Factory"
}
```

### 🏭 2. Listar proveedores disponibles

```bash
curl -X GET "http://localhost:8000/cloud/providers"
```

**Respuesta esperada:**

```json
{
  "supported_providers": ["aws", "azure", "gcp", "oracle", "onprem"],
  "total": 5,
  "description": "List of cloud providers supported by the Abstract Factory"
}
```

### ☁️ 3. Crear infraestructura AWS completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "aws",
       "name": "mi-infraestructura-aws",
       "region": "us-east-1",
       "vm_config": {
         "instance_type": "t3.medium",
         "ami": "ami-0abcdef123456",
         "key_pair": "my-key"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

**Respuesta esperada:**

```json
{
  "success": true,
  "message": "Infraestructura 'mi-infraestructura-aws' creada exitosamente usando AWS",
  "provider": "aws",
  "resources_created": 4,
  "infrastructure": {
    "virtual_machine": {
      "name": "mi-infraestructura-aws-vm",
      "resource_id": "i-1234567890abcdef0",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::EC2::Instance"
    },
    "database": {
      "name": "mi-infraestructura-aws-db",
      "resource_id": "db-abcdef123456789",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::RDS::DBInstance"
    },
    "load_balancer": {
      "name": "mi-infraestructura-aws-lb",
      "resource_id": "alb-123456789abcdef0",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::ElasticLoadBalancingV2::LoadBalancer"
    },
    "storage": {
      "name": "mi-infraestructura-aws-storage",
      "resource_id": "s3-bucket-789abcdef",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::S3::Bucket"
    }
  }
}
```

### 🔷 4. Crear infraestructura Azure completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "azure",
       "name": "mi-infraestructura-azure",
       "region": "westus",
       "vm_config": {
         "vm_size": "Standard_B2s",
         "image": "Ubuntu 20.04 LTS",
         "admin_username": "azureuser"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

### 🟡 5. Crear infraestructura GCP completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
        "provider": "onprem",
        "name": "mi-infraestructura-onprem",
        "region": "datacenter-1",
        "vm_config": {
          "cpu": 4,
          "ram_gb": 8,
          "disk_gb": 100,
          "nic": "eth0",
          "hypervisor": "vmware"
        },
        "include_database": true,
        "include_load_balancer": true,
        "include_storage": true
      }'
```

### 🔴 6. Crear infraestructura Oracle Cloud completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "oracle",
       "name": "mi-infraestructura-oracle",
       "region": "us-ashburn-1",
       "vm_config": {
         "compute_shape": "VM.Standard2.1",
         "compartment_id": "ocid1.compartment.demo",
         "availability_domain": "AD-1"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

### 🏢 7. Crear infraestructura On-Premise completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "onprem",
       "name": "mi-infraestructura-onprem",
       "region": "datacenter-1",
       "vm_config": {
         "cpu": 4,
         "ram_gb": 8,
         "disk_gb": 100,
         "nic": "eth0"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

### 📊 8. Consultar logs de auditoría

```bash
curl -X GET "http://localhost:8000/api/logs"
```

## 🏗️ Requests de creación tipados por proveedor (Legacy VM Factory)

La validación es estricta según `provider`. El campo `params` cambia de forma y es validado automáticamente por Pydantic.

- AWS

```json
{
  "provider": "aws",
  "name": "mi-vm-aws",
  "params": {
    "instance_type": "t2.micro",
    "region": "us-east-1",
    "vpc": "vpc-123",
    "ami": "ami-abc"
  },
  "requested_by": "alumno"
}
```

- Azure

```json
{
  "provider": "azure",
  "name": "mi-vm-azure",
  "params": {
    "size": "Standard_B1s",
    "resource_group": "rg1",
    "image": "UbuntuLTS",
    "vnet": "vnet-01"
  },
  "requested_by": "alumno"
}
```

- GCP

```json
{
  "provider": "gcp",
  "name": "mi-vm-gcp",
  "params": {
    "machine_type": "e2-micro",
    "zone": "us-central1-a",
    "base_disk": "pd-standard",
    "project": "demo-proj"
  },
  "requested_by": "alumno"
}
```

- On-Premise

```json
{
  "provider": "onpremise",
  "name": "mi-vm-onprem",
  "params": { "cpu": 4, "ram_gb": 8, "disk_gb": 50, "nic": "eth0" },
  "requested_by": "alumno"
}
```

```json
{
  "provider": "oracle",
  "name": "mi-vm-oracle",
  "params": {
    "compute_shape": "VM.Standard2.1",
    "compartment_id": "ocid1.compartment...",
    "availability_domain": "AD-1",
    "subnet_id": "ocid1.subnet...",
    "image_id": "ocid1.image..."
  },
  "requested_by": "alumno"
}
```

## Diseño y arquitectura

- Patrón: Factory Method
  - Abstracción: `app/domain/factories/base.py` (`VirtualMachineFactory`)
  - Implementaciones: `aws.py`, `azure.py`, `gcp.py`, `onprem.py`
  - Resolución: `app/domain/factories/__init__.py#get_factory(provider)`
- Validación de entrada (DTOs):
  - `app/domain/schemas/common.py`: tipos comunes (ProviderEnum, VMDTO, etc.)
  - `app/domain/schemas/{aws,azure,gcp,onpremise}.py`: params por proveedor
  - `app/domain/schemas/create_requests.py`: `VMCreateRequest` (Union discriminado por `provider`)
- Servicios y puertos:
  - Servicio: `app/domain/services.py` (orquesta casos de uso)
  - Puerto de repo (DIP): `app/domain/ports.py` (`VMRepositoryPort`)
  - Implementación repo in-memory: `app/infrastructure/repository.py`
- API/Controller: `app/api/vm_controller.py`
- App FastAPI: `app/main.py`
- Logs: `app/infrastructure/logger.py` → `Backend/logs/audit.log`

## 🎯 Principios SOLID Implementados

### 🔸 **S - Single Responsibility Principle (SRP)**

- Cada clase tiene una única responsabilidad:
  - **Productos**: Solo conocen sus propias operaciones (EC2Instance, RDSDatabase, etc.)
  - **Factories**: Solo crean productos de su proveedor específico
  - **Controllers**: Solo manejan HTTP requests/responses
  - **Services**: Solo lógica de negocio

### 🔸 **O - Open/Closed Principle (OCP)**

- **Abierto para extensión**: Agregar nuevos proveedores solo requiere:
  1. Crear nuevos productos en `app/domain/products/{nuevo}_products.py`
  2. Crear nueva factory en `app/domain/factories_concrete/{nuevo}_factory.py`
  3. Registrar en `factory_provider.py`
- **Cerrado para modificación**: No se modifica código existente

### 🔸 **L - Liskov Substitution Principle (LSP)**

- Todas las factories implementan `CloudAbstractFactory` y son intercambiables
- Todos los productos del mismo tipo (VM, Database, etc.) son intercambiables
- El cliente puede usar cualquier proveedor sin cambiar código

### 🔸 **I - Interface Segregation Principle (ISP)**

- Interfaces específicas y cohesivas:
  - `VirtualMachine`: solo operaciones de VM (start, stop, get_specs)
  - `Database`: solo operaciones de DB (backup, restore, get_connection)
  - `LoadBalancer`: solo operaciones de LB (add_target, remove_target)
  - `Storage`: solo operaciones de Storage (upload, download, list_objects)

### 🔸 **D - Dependency Inversion Principle (DIP)**

- **Abstract Factory** depende de abstracciones (`CloudAbstractFactory`)
- **Controllers** dependen de servicios (abstracción), no implementaciones
- **Services** dependen de puertos/interfaces, no de repositorios concretos
- **Productos** no dependen de implementaciones específicas de otros productos

## Persistencia y estado

- Sin BD: persistencia simulada en memoria (dict) en `app/infrastructure/repository.py`.
- Stateless: la API no guarda estado de sesión; el repositorio in-memory simula almacenamiento volátil.

## Acciones y estados de VM

- `POST /vm/{id}/action` admite `start | stop | restart` y actualiza `status` a `running` o `stopped`.

## Logging de auditoría

- Formato JSON por línea con: timestamp, actor, acción, vm_id, provider, success, details.
- No se registran credenciales ni parámetros sensibles.
- Archivo: `Backend/logs/audit.log`.

## 🔧 Extender con un nuevo proveedor

### Para Abstract Factory (Recomendado):

1. **Crear productos concretos**: `app/domain/products/{nuevo}_products.py`

   ```python
   class NuevoVM(VirtualMachine):
       def start(self): # implementar
       def stop(self): # implementar
       def get_specs(self): # implementar
   ```

2. **Crear factory concreta**: `app/domain/factories_concrete/{nuevo}_factory.py`

   ```python
   class NuevoCloudFactory(CloudAbstractFactory):
       def create_virtual_machine(self, name, config): # implementar
       def create_database(self, name, config): # implementar
   ```

3. **Registrar en provider**: `app/domain/factory_provider.py`

   ```python
   class CloudProvider(str, Enum):
       NUEVO = "nuevo"

   FACTORY_REGISTRY = {
       CloudProvider.NUEVO: NuevoCloudFactory,
   }
   ```

### Para Factory Method (Legacy - solo VMs):

1. Crear `app/domain/schemas/<nuevo>.py` con los params del proveedor.
2. Añadir su variante en `create_requests.py`.
3. Implementar `VirtualMachineFactory` en `app/domain/factories/<nuevo>.py`.
4. Registrar en `get_factory` (`app/domain/factories/__init__.py`).

## 📈 Beneficios del Abstract Factory vs Factory Method

| Aspecto           | Factory Method (Legacy)           | Abstract Factory (Actual)                     |
| ----------------- | --------------------------------- | --------------------------------------------- |
| **Productos**     | Solo VMs                          | VMs + Databases + Load Balancers + Storage    |
| **Consistencia**  | N/A                               | Productos del mismo proveedor trabajan juntos |
| **Escalabilidad** | Limitada                          | Alta - fácil añadir productos y proveedores   |
| **Mantenimiento** | Complejo para múltiples productos | Simple y organizado                           |
| **Testing**       | Difícil mockear                   | Fácil mockear factories completas             |
