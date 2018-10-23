from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from goods.models import *


from django.conf import settings
from fdfs_client.client import Fdfs_client

# def index(request):
#     return HttpResponse("首页")

class IndexView(View):
    def get(self,request):
        #获取商品的种类信息
        goodstype_list = GoodsType.objects.all()

        #准备数据字典
        context = {'goodstype_list':goodstype_list}
        #返回渲染
        return render(request,'test_index.html',context)



class TestView(View):
    def get(self,request):
        return render(request,'test-file.html')

    def post(self, request):
        # 创建一个Fdfs_client对象
        client_conf = settings.FDFS_CLIENT_CONF
        client = Fdfs_client(client_conf)

        # 上传文件到Fdfs dfs 系统中
        content = request.FILES["file1"]
        res = client.upload_by_buffer(content.read())
        # print('res', res)
        #
        # ret = res['Remote file_id']
        # print(ret)

        return HttpResponse(ret)
