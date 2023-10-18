from django.db.models import Avg
from restaurant.models import *

def calculate_and_update_average_rating(restaurant):
    # Calculate the average rating for the restaurant
    avg_rating = Feedback.objects.filter(restaurant=restaurant).aggregate(Avg('rating'))['rating__avg']

    if avg_rating is not None:
        restaurant.average_rating = round(avg_rating, 1)  # Round to one decimal place
        restaurant.save()



def add_feedback(request, pk, rating, review):
    restaurant = Restaurants.objects.get(pk=pk)
    
    # Create a new Feedback instance and save it
    feedback = Feedback(restaurant=restaurant, rating=rating, review=review)
    feedback.save()
    
    # Calculate and update the average rating
    calculate_and_update_average_rating(restaurant)
    
    return Response({"message": "Feedback added successfully"})
