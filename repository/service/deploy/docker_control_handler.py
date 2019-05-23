import os
from utils.response import BaseResponse
from repository.conf import settings
import paramiko
import shutil


class ProcedureHandler:
    def __init__(self):
        self.response = BaseResponse()

    # 用于将模板中的特殊标签转换为正确的格式
    def __replace_template_tag(self, file_data):
        file_data = file_data.replace('[[[', '{')
        file_data = file_data.replace(']]]', '}')
        return file_data

    # 读取文件
    def __file_load(self, file):
        f = open(file, 'r')
        file_data = f.read()
        f.close()
        return file_data

    # 写入文件
    def __file_push(self, file, data):
        f = open(file, 'w')
        data = self.__replace_template_tag(data)
        f.write(data)
        f.close()

    # 文件压缩
    def __tar_zip_files(self, source, target_file):
        source_file_path = ('D:/MyProject/AutoDeploy/repository/data/app/my_demo_app/cstest')
        target_dir = ('D:/MyProject/AutoDeploy/repository/data/deploy/my_demo_app')
        shutil.make_archive(target_file, 'zip', root_dir=source)

    # paramiko 远程命令执行
    def __paramiko_handler(self, command, **kwargs):
        result = {}
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**kwargs)
        stdin, stdout, stderr = ssh.exec_command(command)
        result['stdout'] = stdout.readlines()
        result['stderr'] = stderr.readlines()
        ssh.close()

        return result

    def __remote_scp(self, s_dir, d_dir, host, port, username, password):
        t = paramiko.Transport((host, port))
        t.connect(username=username, password=password)  # 登录远程服务器
        sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议
        sftp.put(s_dir, d_dir)
        t.close()

    def render_template(self, template_file, deploy_file, **kwargs):
        '''
        根据指定参数渲染生成本地配置文件
        :param template_file, deploy_file, template_args
        :return: self.response {'message': None, 'data': None, 'error': None, 'status': True}
        '''
        try:
            get_file = self.__file_load(template_file)
            render_file = get_file.format(**kwargs)
            # 将渲染完成的文件写入至应用目录
            self.__file_push(deploy_file, render_file)
            self.response.message = '模板文件创建成功'
        except Exception as e:
            self.response.status = False
            self.response.message = '%s, %s' % (template_file, e)

        return self.response.__dict__

    def crate_app_path(self, app_name):
        '''
        创建本地应用目录
        :param app_name: 'my_demo_app'
        :return: self.response {'message': None, 'data': None, 'error': None, 'status': True}
        '''
        try:
            for dir in settings.docker_compose_dir_list:
                os.makedirs(dir.format(app_name=app_name))
            self.response.message = '应用目录创建完成'
        except os.error as e:
            self.response.message = e
        except Exception as e:
            self.response.status = False
            self.response.message = e

        return self.response.__dict__

    def push_command_to_remote(self, command, **kwargs):
        '''
        更新远程服务器配置文件
        :param host, commands, args
        :return: self.response {'message': None, 'data': None, 'error': None, 'status': True}
        '''
        try:
            self.response.data = self.__paramiko_handler(command, **kwargs)
            self.response.message = '完成'
        except Exception as e:
            self.response.status = False
            self.response.message = e

        return self.response.__dict__

    def gzip_local_file(self, s_dir, d_dir):
        try:
            self.response.data = self.__tar_zip_files(s_dir, d_dir)
        except Exception as e:
            self.response.status = False
            self.response.message = e

        return self.response.__dict__

    def update_local_file_to_remote(self, s_dir, d_dir, server_config):
        '''
        更新远程服务器配置文件
        :param
        :return: self.response {'message': None, 'data': None, 'error': None, 'status': True}
        '''
        self.__remote_scp(
            s_dir,
            d_dir,
            server_config['hostname'],
            server_config['port'],
            server_config['username'],
            server_config['password'],
        )

if __name__ == "__main__":
    handler = ProcedureHandler()
    # a = handler.push_command_to_remote(command='ifconfig')
    # print(a.__dict__)
    #handler.tar_zip_files(1,1)