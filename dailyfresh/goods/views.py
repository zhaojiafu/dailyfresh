from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from goods.models import *

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