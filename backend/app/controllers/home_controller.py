# app/controllers/home_controller.py
from app.services.dashboard_service import DashboardService

def home_redirect(usuario_logado, session_data, tenant_url):

    result, dashboard_data = DashboardService.get_dashboard_data(usuario_logado, session_data, tenant_url)

    if result:
        return dashboard_data, 200  
    else:
        return dashboard_data, 404