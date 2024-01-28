from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.logIn),
    path('sendotp/',views.sendOTP),
    path('verifyotp/',views.verifyOTP),
    path('verifyemail/',views.verifyEmail),
    path('verifyusername/',views.verifyUsername),
    path('changepassword/',views.changePassword),
    path('createaccount/',views.createAccount),
    path('validatetoken/',views.validateToken),
    path('getprofiledata/',views.getProfileData),
  	path('getid/',views.getId),
    path('getpost/',views.getPost),
    path('addlike/',views.addLike),
    path('checklike/',views.checkLike),
    path('addpost/',views.addPost),
    path('editpost/',views.editPost),
    path('removepost/',views.removePost),
	path('getdiscoverypost/',views.getDiscoveryPost),
    path('addfollower/',views.addFollower),
    path('checkfollower/',views.checkFollower),
    path('changeprofile/',views.changeProfile),
    path('searchusername/',views.searchUsername),
]