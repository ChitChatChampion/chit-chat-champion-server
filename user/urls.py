from django.urls import path

from user import views

# set to help identify which app we are
# creating the url from when we use the reverse function
app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("me/", views.ManageUserView.as_view(), name="me"),
    path("config/", views.ManageUserConfigView.as_view(), name="config"),
]
