from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings

from datetime import datetime
import os
import re


@method_decorator(staff_member_required, name='dispatch')
class LogFilesView(TemplateView):
    template_name = 'admin/log_files.html'
    
    def get_log_files(self):
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        log_files = []
        
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.startswith('errors-') and filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    match = re.match(r'errors-(\d{4}-\d{2}-\d{2})\.log', filename)
                    
                    if match:
                        date_str = match.group(1)
                        try:
                            file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            
                            # Lấy kích thước file
                            size_bytes = os.path.getsize(file_path)
                            size_kb = size_bytes / 1024
                            
                            log_files.append({
                                'filename': filename,
                                'path': file_path,
                                'date': file_date,
                                'size': f'{size_kb:.2f} KB'
                            })
                        except ValueError:
                            pass
        
        log_files.sort(key=lambda x: x['date'], reverse=True)
        return log_files
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context['has_permission'] = True
        context['site_header'] = admin.site.site_header
        context['site_title'] = admin.site.site_title
        context['title'] = 'Log Files'
        context['is_nav_sidebar_enabled'] = True
        context['log_files'] = self.get_log_files()
        context['available_apps'] = admin.site.get_app_list(self.request)
        return context


@method_decorator(staff_member_required, name='dispatch')
class LogFileDetailView(TemplateView):
    template_name = 'admin/log_file_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_permission'] = True
        context['has_module_permission'] = True
        context['site_header'] = admin.site.site_header
        context['site_title'] = admin.site.site_title
        context['is_nav_sidebar_enabled'] = True
        context['available_apps'] = admin.site.get_app_list(self.request)

        filename = self.kwargs.get('filename')
        context['title'] = "File: " + filename
        
        log_path = os.path.join(settings.BASE_DIR, 'logs', filename)
        content = []
        
        if os.path.exists(log_path) and os.path.isfile(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.readlines()
            except Exception as e:
                content = [f"Error reading log file: {str(e)}"]
        else:
            content = ["Log file not found."]
            
        limit = int(self.request.GET.get('limit', 500)) * -1
            
        context['filename'] = filename
        context['content'] = content[limit:]
        return context