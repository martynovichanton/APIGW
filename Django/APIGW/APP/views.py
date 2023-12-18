from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views import View

class IndexF5(View):
    def get(self, request):
        return render(request, 'APP/indexf5.html')

class IndexForti(View):
    def get(self, request):
        return render(request, 'APP/indexforti.html')

