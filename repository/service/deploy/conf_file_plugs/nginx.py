from repository.conf import settings
from repository.service.deploy import docker_control_handler

class NginxConfig():
    def __init__(self, docker_type, env_type):
        self.docker_type = docker_type
        self.conf_file_list =[
            'default.conf',
            'mime.types',
            'mod.conf',
            'nginx.conf',
        ]

    def default_conf(self):
        template_file = settings.docker_conf_template.format(docker_type=self.docker_type)
        docker_conf_deploy = settings.docker_file_deploy.format(env_type=self.env_type, app_name=self.app_name)

    def mime_conf(self):
        pass

    def mod_conf(self):
        pass

    def nginx_conf(self):
        pass