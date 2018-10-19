from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    '''fast dfs 文件储存类'''

    def __init__(self):
        '''初始化'''
        self.client_conf = settings.FDFS_CLIENT_CONF
        self.base_url = settings.FDFS_URL

    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # name:你选择上传文件的名字
        # content:包含你上传文件内容的File对象

        # 创建一个Fdfs_client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到Fdfs dfs 系统中
        res = client.upload_by_buffer(content.read())

        print('res', res)

        '''
        res {
            'Local file name': '',
            'Storage IP': b '192.168.12.209',
            'Status': 'Upload successed.',
            'Remote file_id': b 'group1/M00/00/00/wKgM0VvJMHuAJeiqAABHr3RQqFs1116687',
            'Group name': b 'group1',
            'Uploaded size': '17.92KB'
        }
        '''

        if res.get('Status') != 'Upload successed.':
            #上传的文件失败
            raise Exception('上传文件到FastDFS失败')

        # 获取返回的文件ID
        filename = res.get('Remote file_id').decode()

        return filename

    def exists(self, name):
        '''Django判断文件名是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        return self.base_url + name
