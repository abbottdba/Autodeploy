import platform, sys
if platform.system() == 'Linux':
    sys.path.append('/app/project/AutoDeploy')
import django

from repository.service.deploy import docker_yml_control
from utils.logshadler import CommonLogging
from repository.conf import settings
import datetime

class FaucetControl:
    def __init__(self, app_name, docker_type, env_type, app_port):
        '''
        应用名称、端口号、git地址
        1、创建本地应用目录
        2、生成docker yml文件
        3、生成docker file文件
        4、生成脚本配置文件
        5、推送docker配置文件
        6、启动容器监听
        6、修改allowcommand 配置文件
        7、配置HA监听端口
        8、配置测试环境nginx配置文件
        9、推送生产配置
        10、更新allow配置文件（ansible调用）
        11、调用jenkins接口
        '''
        self.app_name = app_name
        self.docker_type = docker_type
        self.env_type = env_type
        self.app_port = app_port
        self.docker_handler = docker_yml_control.UpdateController(self.app_name, self.docker_type, self.env_type,self.app_port)

    def __log_commit(self, text):
        log_write = CommonLogging(settings.docker_deploy_log.format(app_name=self.app_name))
        log_write.logging_info(text)

    def sync_cstest(self):
        # 创建本地应用目录
        response = self.docker_handler.render_app_local_path()
        if response['status'] == False:
            return False

        # 创建docker yml
        response = self.docker_handler.create_docker_yml()
        if response['status'] == False:
            return False

        # 创建docker file
        response = self.docker_handler.create_docker_file()
        if response['status'] == False:
            return False

        # 创建测试环境执行脚本
        response = self.docker_handler.create_docker_bin_script(111)
        status_tag = True
        for response_obj in response:
            if response_obj['status'] == False:
                status_tag = False
                return False
        if status_tag == False:
            return False

        # 创建测试环境nginx配置文件
        response = self.docker_handler.create_docker_nginx_conf()
        status_tag = True
        for response_obj in response:
            if response_obj['status'] == False:
                status_tag = False
                return False
        if status_tag == False:
            return False

        # 推送本地文件到测试服务器
        response = self.docker_handler.push_data_to_remote()
        if response['status'] == False:
            return False

        # 初始化测试环境docker容器
        response = self.docker_handler.render_docker_image()
        if response['status'] == False:
            return False

        # 更新HA端口配置
        response = self.docker_handler.update_haproxy_conf()
        if response['status'] == False:
            return False

        # 更新allowcommand配置文件


if __name__ == "__main__":
    local_test = FaucetControl('this_is_testapp', 'nginx', 'cstest', 8888)
    local_test.sync_cstest()