from repository.conf import settings
from repository.service.deploy import docker_control_handler
from utils.logshadler import CommonLogging

import time
import json


class UpdateController:
    '''
    接收应用初始化参数，生成模板路径，文件部署路径
    '''

    def __init__(self, app_name, docker_type, env_type, app_port):
        self.app_name = app_name
        self.docker_type = docker_type
        self.env_type = env_type
        self.app_port = app_port
        self.docker_handler = docker_control_handler.ProcedureHandler()
        self.__log_commit = CommonLogging(settings.docker_deploy_log.format(app_name=self.app_name))

    def __log_commit(self, text):
        log_write = CommonLogging(settings.docker_deploy_log.format(app_name=self.app_name))
        log_write.logging_info(text)

    # 创建docker yml 文件 cstest & real
    def create_docker_yml(self):
        args_dic = {
            'app_name': self.app_name,
            'host_port': self.app_port,
            'container_port': self.app_port,
        }
        template_file = settings.docker_yml_template.format(env_type=self.env_type, docker_type=self.docker_type)
        deploy_file = settings.docker_yum_deploy.format(env_type=self.env_type, app_name=self.app_name)
        response = self.docker_handler.render_template(template_file, deploy_file, **args_dic)

        log_text = '[创建docker yml文件]: %s' % response['message']
        self.__log_commit.logging_info(log_text)

        return response

    # 创建docker file 文件  cstest
    def create_docker_file(self):
        args_dic = {}
        template_file = settings.docker_file_template.format(docker_type=self.docker_type)
        deploy_file = settings.docker_file_deploy.format(env_type=self.env_type, app_name=self.app_name)
        response = self.docker_handler.render_template(template_file, deploy_file, **args_dic)

        log_text = '[创建docker file文件]: %s' % response['message']
        self.__log_commit.logging_info(log_text)

        return response

    # 创建 nginx 配置文件 cstest
    def create_docker_nginx_conf(self):
        config_template = {
            'default.conf': {'app_port': self.app_port},
            'mime.types': {},
            'mod.conf': {},
            'nginx.conf': {},
        }

        file_status = []

        for config_file, args_dic in config_template.items():
            template_file = settings.docker_conf_template.format(docker_type=self.docker_type, file_name=config_file)
            deploy_file = settings.docker_conf_deploy.format(app_name=self.app_name, env_type=self.env_type,
                                                             file_name=config_file)
            response = self.docker_handler.render_template(template_file, deploy_file, **args_dic)
            file_status.append(response)
            log_text = '[生成%s环境Nginx配置文件 %s]: %s' % (self.env_type, config_file, response['message'])
            self.__log_commit.logging_info(log_text)

        return file_status

    # 创建docker脚本文件  cstest & real
    def create_docker_bin_script(self, git_name):
        script_template = {
            'sync_cstest.sh': {'app_name': self.app_name, 'git_name': git_name},
            'sync_real.sh': {},
            'rollback.sh': {},
            'restart.sh': {},
        }  # 这个参数放到外面传递

        file_status = []

        for script_file, args_dic in script_template.items():
            template_file = settings.docker_bin_script_template.format(env_type=self.env_type,
                                                                       file_name=script_file)
            deploy_file = settings.docker_bin_script_deploy.format(app_name=self.app_name, env_type=self.env_type,
                                                                   file_name=script_file)
            response = self.docker_handler.render_template(template_file, deploy_file, **args_dic)

            log_text = '[生成%s环境脚本配置文件 %s]: %s' % (self.env_type, script_file, response['message'])
            self.__log_commit.logging_info(log_text)

            file_status.append(response)

        return file_status

    # 创建本地应用部署目录
    def render_app_local_path(self):
        response = self.docker_handler.crate_app_path(self.app_name)
        log_text = '[创建本地应用目录]: %s' % response['message']
        self.__log_commit.logging_info(log_text)
        return (response)

    # 更新 测试环境 allowcommand 文件
    def update_allowcommands(self, command):
        response = self.docker_handler.push_command_to_remote(command, **settings.server_config[self.env_type])
        return response

    # 发送测试环境配置文件
    def push_data_to_remote(self):
        # 将文件压缩拷贝至本地部署目录
        s_dir = settings.docker_app_project.format(app_name=self.app_name, env_type=self.env_type)
        d_dir = settings.docker_deploy_file.format(app_name=self.app_name)
        push_status = self.docker_handler.gzip_local_file(s_dir, d_dir)

        # 将文件上传至远程服务器
        local_gzip_file = '%s.zip' % (settings.docker_deploy_file.format(app_name=self.app_name))
        remote_dir = '/opt/compose-conf/cmdb/%s.zip' % self.app_name
        self.docker_handler.update_local_file_to_remote(local_gzip_file, remote_dir,
                                                        settings.server_config[self.env_type])

        # 解压操作
        command = "cd /opt/compose-conf/cmdb && unzip -o {app_name}.zip -d {app_name} && rm -f {app_name}.zip".format(
            app_name=self.app_name)
        response = self.docker_handler.push_command_to_remote(command, **settings.server_config[self.env_type])

        return response

    # 生成容器镜像 && 修改镜像名称
    def render_docker_image(self):
        command = 'sh /bak/bin/cmdb/core_scripts/init_docker_image.sh {app_name}'.format(app_name=self.app_name)
        response = self.docker_handler.push_command_to_remote(command, **settings.server_config[self.env_type])
        log_text = '[初始化容器镜像]: %s' % response['message']
        self.__log_commit.logging_info(log_text)

        return response

    # 调用HA接口，配置HA相应代理端口
    def update_haproxy_conf(self):
        command = 'python /bak/bin/cmdb_add_haproxy_conf.py {env_type} {app_name} {app_port}'.format(
            env_type=self.env_type, app_name=self.app_name, app_port=self.app_port)
        response = self.docker_handler.push_command_to_remote(command, **settings.server_config['haproxy'])
        if response['status']:
            result = json.loads(response['data']['stdout'][0])
            log_text = '[配置HA应用代理端口]: %s, HA端口为 %s' % (response['message'], result['result'])
        else:
            log_text = '[配置HA应用代理端口]: 配置失败'
        self.__log_commit.logging_info(log_text)

        return response

    # 配置测试环境nginx访问域名
    def handle_nginx_config(self):
        pass

    # 配置allowcommand 文件
    def update_allowcommands_config(self):
        pass


if __name__ == '__main__':
    update = UpdateController('my_demo_app', 'nginx', 'cstest', 8080)
    # update.render_app_local_path()
    # update.create_docker_yml()
    # command = "/bak/bin/cmdb/core_scripts/update_allowcommands.sh %s" % 'my_demo_app'
    # command = "ifconfig1"
    # update.update_allowcommands('cstest', command)
    update.push_data_to_remote()
