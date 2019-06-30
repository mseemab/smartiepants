from django.urls import path
from . import views
from django.urls import path, include # new
from smarttm_web import meeting_views
urlpatterns = [
   path('meeting/<int:meeting_id>/', meeting_views.meeting, name = 'meeting_detail'),
   path('', views.index, name = 'index'),
   path('summary/', views.summary, name = 'ranking_summary'),
   path('ManageClub/', views.club_management, name = 'manage_club'),
   path('LoginUser/', views.login_user, name = 'LoginUser'),
   path('register/', views.register , name = 'register'),
   path('ClubMeetings/', meeting_views.meetings_view, name = 'meeting_summary'),
   path('MySpace', views.my_space , name = 'my_space'),
   path('SetClub/<int:club_id>/', views.set_club, name = 'SetClub'),
   path('ImportMembers/', views.ImportMembers, name = 'import_members'),
   path('AddMeeting/', meeting_views.add_meeting, name = 'add_meeting'),
   path('ImportMeetingData/', meeting_views.import_meeting_data, name = 'import_meeting_data'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]