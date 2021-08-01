import json

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Sum

from arts.models  import Art
from users.models import User
from carts.models import Cart

from core.utils import login_required

class CartView(View):
    @login_required
    def get(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).select_related('art', 'art__artist', 'art__size') #쿼리 최소화

        results = [
            {
                "art_id"   : item.art_id, 
                "art_title": item.art.title, 
                "art_price": int(item.art.price),
                "artist"   : item.art.artist.name,
                "size"     : item.art.size.name,
            }
            for item in cart
        ]

        total_price = int(cart.aggregate(sum=Sum('art__price'))['sum']) 
        count       = cart.count()

        return JsonResponse({
                                'results'    : results, 
                                'total_price': total_price, 
                                'count'      : count
                            }, status=200)

    @login_required
    def post(self, request):
        try:
            data    = json.loads(request.body)
            art_id  = data['art_id']
            
            art  = Art.objects.get(id=art_id)
            user = request.user

            if Cart.objects.filter(art=art, user=user).exists():
                return JsonResponse({'message': 'BAD_REQUEST'}, status=400)
            
            Cart.objects.create(art=art, user=user)

            return JsonResponse({'message':'SUCCESS'}, status=201)

        except Art.DoesNotExist:
            return JsonResponse({'message': 'ART_DOES_NOT_EXISTS'}, status=400)

    @login_required
    def delete(self, request):
        art_id = request.GET.get('art-id', None)
        user   = request.user

        if not Cart.objects.filter(art_id=art_id, user=user).exists():
            return JsonResponse({'message': 'NOT_FOUND'}, status=404)

        Cart.objects.get(art_id=art_id, user=user).delete()
        
        return JsonResponse({'message':'SUCCESS'}, status=200)