from .models import Category
import re

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)



def has_shop(request):
    shop_in_request = re.findall(r"/shop/$", request.path)

    return {'has_shop_in_url': any([shop_in_request])}
