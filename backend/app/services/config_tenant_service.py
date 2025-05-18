from app.repositories.config_tenant_repository import ConfigTenantRepository

class ConfigTenantService:

    @staticmethod   
    def get_config_por_tenant(tenant_url):
        return ConfigTenantRepository.get_config_por_tenant(tenant_url)

    @staticmethod   
    def get_config_por_id(id):
        return ConfigTenantRepository.get_config_por_id(id)
    
    @staticmethod
    def get_config_by_parceiro_id(parceiro_id):
        return ConfigTenantRepository.get_by_parceiro_id(parceiro_id)
    
    @staticmethod
    def get_all_configs():
        return ConfigTenantRepository.get_all()
    
    
    @staticmethod
    def create_config(data):
        return ConfigTenantRepository.create(data)
    
    @staticmethod
    def update_config(config_id, data):
        return ConfigTenantRepository.update(config_id, data)

    @staticmethod
    def delete_config(config_id):
        return ConfigTenantRepository.delete(config_id)