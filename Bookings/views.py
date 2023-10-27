from django.http import HttpResponse, Http404
from rest_framework.response import Response
from .serializers import *
from restaurant.models import *
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import viewsets





class Table_Available_Viewset(viewsets.ModelViewSet):
    queryset = Tables_Available.objects.all()
    serializer_class = Table_Serializer

class Dine_InAPI(APIView):
    def post(self,request):
        # import pdb
        # pdb.set_trace()
        serializer = Dine_in_Serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            restaurant = serializer.validated_data['restaurant']
            mealtime = serializer.validated_data['mealtime'] # have value = breakfast,lunch or dinner
            date = serializer.validated_data['date']
            table = serializer.validated_data['table']

            try:
                tables = Tables_Available.objects.get(restaurant=restaurant,date=date)

                if mealtime == 'breakfast' and table < tables.breakfast:
                    tables.breakfast -= table
                elif mealtime == 'lunch' and table < tables.lunch:
                    tables.lunch -= table
                elif mealtime == 'dinner' and table < tables.dinner:
                    tables.dinner -= table

                tables.save()
                serializer.save()

                return Response({"Message" : "Table Booked Sucessfully"})

            except:
                return Response({"Message" : "Tables not available"})
