import json, requests, jwt

from django.http      import JsonResponse
from django.views     import View

from users.models import User

from my_settings import SECRET_KEY, ALGORITHM


#https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api

class KakaoSignInView(View):
    def get(self, request): 
        try:
            kakao_access_token = request.headers.get('Authorization') # 프론트에서 카카오 토큰 받아와서 넘겨줌 개이득

            headers = {'Authorization': f'Bearer {kakao_access_token}'} # 문서에 써있음

            kakao_user_info = requests.post('https://kapi.kakao.com/v2/user/me', headers=headers).json() # requests로 해당 주소로 요청을 날리면 카카오가 resoponse를 해줌.

            kakao_id  = kakao_user_info['id']
            email     = kakao_user_info['kakao_account']['email']
            nick_name = kakao_user_info['properties']['nickname']
            birthday  = kakao_user_info['kakao_account']['birthday']
            gender    = kakao_user_info['kakao_account']['gender']

            user, is_created =  User.objects.get_or_create(kakao_id = kakao_id)
            
            if is_created:
                user.email     = email
                user.nick_name = nick_name
                user.birthday  = birthday
                user.gender    = gender
                user.save()

            access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm=ALGORITHM) #우리서비스를 위한 토큰을 만들어서 발행

            return JsonResponse({'access_token': access_token}, status=200) 
        
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except Exception as error:
            return JsonResponse({'message': error}, status=400)