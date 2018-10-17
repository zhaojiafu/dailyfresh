from django.shortcuts import render
from django.http import *
from provinces.models import *
from django.core import serializers



#跳转到show
def show(request):
    return render(request,"provinces/show.html")

#获取所有的省份,并且转成json
def get_all_province(request):

    #获取所有的省
    province_list = Provinces.objects.all()

    #转成接收json格式,需要导入:from django.core import serializers
    content = {
        'province_list':serializers.serialize('json',province_list)
    }
    return JsonResponse(content)

# 通过改变的省份获取对应的城市
def get_city_by_id(request):
    province_id = request.GET.get('province_id')

    #获取所有的城市
    city_list = Citys.objects.filter(cprovince_id=province_id)

    print(city_list,111)
    #转成接收json格式,需要导入:from django.core import serializers
    content = {
        'city_list':serializers.serialize('json',city_list)
    }
    print(content["city_list"],222)
    return JsonResponse(content)

def get_area_by_id(request):
    city_id = request.GET.get('city_id')

    #获取所有的城市
    area_list = Areas.objects.filter(acity_id=city_id)

    print(area_list,111)
    #转成接收json格式,需要导入:from django.core import serializers
    content = {
        'area_list':serializers.serialize('json',area_list)
    }
    print(content["area_list"],222)
    return JsonResponse(content)


