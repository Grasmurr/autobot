from django.shortcuts import render

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json
from .models import Applicant

from django.http import HttpResponse
from django.shortcuts import render

@method_decorator(csrf_exempt, name='dispatch')
class ApplicantsView(View):
    def post(self, request):
        data = json.loads(request.body)
        Applicant.objects.create(**data)
        return JsonResponse({'status': 'ok'}, status=201)

    def get(self, request, user_id=None):
        if user_id:
            applicant = Applicant.objects.filter(user_id=user_id).values()
            return JsonResponse({'data': list(applicant)}, safe=False)
        else:
            applicants = Applicant.objects.all().values()
            return JsonResponse({'data': list(applicants)}, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ApplicantUpdateView(View):
    def post(self, request, user_id):
        data = json.loads(request.body)
        applicant, created = Applicant.objects.update_or_create(
            user_id=user_id,
            defaults=data
        )
        status_code = 201 if created else 200  # 201 Created если объект был создан, иначе 200 OK
        return JsonResponse({'status': 'ok'}, status=status_code)

    def delete(self, request, user_id):
        try:
            applicant = Applicant.objects.get(user_id=user_id)
        except Applicant.DoesNotExist:
            return JsonResponse({'error': 'Promouter not found'}, status=404)

        applicant.delete()
        return JsonResponse({'status': 'ok'}, status=200)