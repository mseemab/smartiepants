from django.shortcuts import render
from django.urls import reverse
from smarttm_web.models import Meeting, User, Member, Club, Participation, Summary, Participation_Type, Attendance
from django.shortcuts import render_to_response
import pdb
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.utils import timezone
from datetime import date
from django.db.models import Avg
import math
from django.contrib.auth.decorators import login_required
from smarttm_web.forms import UserForm
from django.core.mail import send_mail
from django.template import loader
import threading
from .decorators import query_debugger, request_passes_test
# Create your views here.

def user_is_member(request):
    club_id=request.path.split('/')[2]
    return request.user.is_member(club_id)


def user_is_ec(request):
    club_id=request.path.split('/')[2]
    return request.user.is_ec(club_id)


def login_user(request):
    
    if request.method == 'POST':

        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                

                
                # create sessions.
                # Get user clubs
                
                user_clubs = user.member_user.filter(paid_status=True, active=True)
                if not len(user_clubs) == 0:
                    login(request, user)
                    UserClubData = []
                    for user_club in user_clubs:
                        UserClubData.append([user_club.club.pk, user_club.club.name])

                    request.session['UserClubs'] = UserClubData

                    request.session['SelectedClub'] = UserClubData[0]

                    request.session.modified = True
                
                    return redirect(reverse('index'))
                else:
                    messages.warning(request, 'You are not a member of any Club. Please join a club to use SMARTTM.')
                    return redirect('login_user')
            else:
                messages.warning(request, 'Your account is not activated') 
                response = redirect('login_user')
                return response
        else:
           messages.warning(request, 'Invalid email/password.') 
           response = redirect('login_user')
           return response
    else:
        
        return render(request, 'registration/login.html' )


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
        else:
            print(user_form.errors)
            registered = True
    else:
        user_form = UserForm()
    return render(request, 'registration/register.html', {'user_form': user_form, 'registered': registered})


@login_required()
def index(request):

    return redirect(reverse('club_rankings', args=(request.session['SelectedClub'][0],)))


@login_required()
@request_passes_test(user_is_member)
def set_club(request, club_id):
    user = request.user
    club = Club.objects.get(id=club_id)
    request.session['SelectedClub'] = [club.pk,club.name]
    request.session.modified = True
    return redirect(reverse('index'))


@login_required()
@request_passes_test(user_is_ec)
def import_members(request, club_id):
    
    club_obj = Club.objects.get(pk=club_id)
    if request.method == 'POST':
        import_file = request.FILES['importfile']
        try:
            club_obj.import_members(import_file)
            messages.success(request, 'Members imported.')
        except Exception as e:
            messages.warning(request, repr(e))
    return redirect(request.META.get('HTTP_REFERER'))


@query_debugger
@login_required()
@request_passes_test(user_is_member)
def club_ranking(request, club_id):
    club_obj = Club.objects.get(pk=club_id)
    club_members = club_obj.members.filter(active=True, paid_status=True)
    FromDate = ""
    ToDate = ""
    if request.method == 'POST':

        FromDate = request.POST.get("StartDate", "")
        ToDate = request.POST.get("EndDate", "")

        partication_set = club_obj.participation_set.filter(created_date__range=(FromDate, ToDate))
    else:
        partication_set = club_obj.participation_set.filter()

    partication_types = Participation_Type.objects.all()
    category_adv = partication_types.filter(category='Role-Advanced')
    category_basic = partication_types.filter(category='Role-Basic')
    summ = []

    club_member_ids = [member.pk for member in club_members]
    latest_absents = Attendance.get_latest_absents(club_member_ids)

    latest_absents_dict = {}
    for absent in latest_absents:
        latest_absents_dict[absent.member_id] = absent.count_absents

    participation_count = Participation.get_participation_count(club_member_ids)
    part_percent_dict = {}
    for part_count in participation_count:
        part_percent_dict[part_count.id] = math.ceil(
            (part_count.TotalParticipations / part_count.TotalAttendance) * 100) \
            if part_count.TotalAttendance != 0 else 0
    for club_mem in club_members:
        sum_obj = Summary()
        sum_obj.member = club_mem
        tt_count = partication_set.filter(member=club_mem,
                                          participation_type=partication_types.get(name='Table Topic')).count()
        sum_obj.tt_count = tt_count
        sum_obj.speeches_count = partication_set.filter(member=club_mem, participation_type=partication_types.get(
            name='Prepared Speech')).count()
        sum_obj.evaluation_count = partication_set.filter(member=club_mem, participation_type=partication_types.get(
            name='Evaluation')).count()
        sum_obj.ttm_count = partication_set.filter(member=club_mem,
                               participation_type=partication_types.get(name='Table Topics Master')).count()
        sum_obj.ge_count = partication_set.filter(member=club_mem,
                               participation_type=partication_types.get(name='General Evaluator')).count()
        sum_obj.toe_count = partication_set.filter(member=club_mem,
                               participation_type=partication_types.get(name='Toastmaster of the Evening')).count()
        if request.method == "POST":
            presents = Attendance.objects.filter(member=club_mem, present=True,
                                                 created_date__range=(FromDate, ToDate)).count()
            absents = Attendance.objects.filter(member=club_mem, present=False,
                                                created_date__range=(FromDate, ToDate)).count()
        else:
            presents = Attendance.objects.filter(member=club_mem, present=True).count()
            absents = Attendance.objects.filter(member=club_mem, present=False).count()

        sum_obj.attendance_percent = math.ceil(
            (presents / (presents + absents)) * 100) if presents + absents != 0 else 0
        sum_obj.tt_percent = math.ceil((tt_count / presents) * 100) if presents != 0 else 0

        try:
            sum_obj.last_absents = latest_absents_dict[club_mem.id]
        except:
            sum_obj.last_absents = 0
        try:
            sum_obj.part_percent = part_percent_dict[club_mem.id]
        except:
            sum_obj.sum_obj.part_percent = 0
        for part_type in category_adv:
            sum_obj.adv_role_count = sum_obj.adv_role_count + partication_set.filter(member=club_mem,
                                                                                     participation_type=part_type).count()
        for part_type in category_basic:
            sum_obj.basic_role_count = sum_obj.basic_role_count + partication_set.filter(member=club_mem,
                                                                                         participation_type=part_type).count()

        summ.append(sum_obj)

    # add rankings
    for i in range(len(summ) - 1, 0, -1):
        for j in range(i):
            if (summ[j].part_percent < summ[j + 1].part_percent) or (
                    (summ[j].part_percent == summ[j + 1].part_percent) and (
                    summ[j].attendance_percent > summ[j + 1].attendance_percent)):
                temp = summ[j]
                summ[j] = summ[j + 1]
                summ[j + 1] = temp

    for i in range(len(summ)):
        summ[i].ranking = i + 1
    return render(request, 'rankings.html', {'page_title': 'User Rankings for ' + club_obj.name, 'summ_set': summ,
                                             'FromDate': request.POST.get("StartDate", ""),
                                             'ToDate': request.POST.get("EndDate", "")})


@login_required()
@request_passes_test(user_is_member)
def member_detail(request, club_id, member_id):
        # Roles Performed Count
        parts = Participation.objects.filter(member_id=member_id)
        member = Member.objects.get(id=member_id)
        part_summary = member.get_part_summary()
        return render(request, 'memberdetail.html', {'part_summary': part_summary, 'parts': parts} )


@login_required()
@request_passes_test(user_is_member)
def club_management(request, club_id):
    club_obj = Club.objects.get(pk=club_id)
    club_members = club_obj.members.filter(active=True)
    return render(request, 'manageclub.html', { 'club_members' : club_members})


@login_required()
@request_passes_test(user_is_ec)
def send_participation_email(request, club_id):
    try:
        t = threading.Thread(target=email_send_thread, args=(club_id,))
        t.daemon=True
        t.start()
    except:
        pass
    messages.info(request, 'Email will be sent to the members in background.')
    return redirect(request.META.get('HTTP_REFERER'))


def email_send_thread(club_id):
    club = Club.objects.get(id=club_id)
    club_mems = Member.objects.filter(club_id=club_id, active=True)
    part_types = Participation_Type.objects.all()
    tt = part_types.get(name='Table Topic')
    speech = part_types.get(name='Prepared Speech')
    evaluation = part_types.get(name='Evaluation')
    big_three = part_types.filter(category='Role-Advanced')
    mem_list = [mem.id for mem in club_mems]
    participation_count = Participation.get_participation_count(mem_list)
    part_percent_dict = {}
    for part_count in participation_count:
        part_percent_dict[part_count.id] = [part_count.TotalParticipations]
        part_percent_dict[part_count.id].append(
            math.ceil((part_count.TotalParticipations / part_count.TotalAttendance) * 100) \
                if part_count.TotalAttendance != 0 else 0)
    for mem in club_mems:

        meets_attended = Attendance.objects.filter(member_id=mem.id, present=True).count()
        meets_total = Attendance.objects.filter(member_id=mem.id).count()
        att_percent = math.ceil((meets_attended / meets_total) * 100) if meets_total != 0 else 0
        tt_count = Participation.objects.filter(participation_type=tt, member=mem).count()
        tt_percent = math.ceil((tt_count / meets_attended) * 100) if meets_attended != 0 else 0
        speech_count = Participation.objects.filter(participation_type=speech, member=mem).count()
        evaluation_count = Participation.objects.filter(participation_type=evaluation, member=mem).count()
        big_three_count = Participation.objects.filter(participation_type__in=big_three, member=mem).count()
        part_count = part_percent_dict[mem.id][0]
        part_percent = part_percent_dict[mem.id][1]
        html_template = loader.get_template('email/participation_summary.html')
        html_message = html_template.render({
            'meets_attended': meets_attended,
            'meets_total': meets_total,
            'att_percent': att_percent,
            'tt_count': tt_count,
            'tt_percent': tt_percent,
            'speech_count': speech_count,
            'evaluation_count': evaluation_count,
            'big_three_count': big_three_count,
            'part_count': part_count,
            'part_percent': part_percent,
            'club': club.name,
            'member_name': str(mem.user.full_name)
        })
        try:
            send_mail('Participation Summary of %s' % mem.user.full_name,
                      'Participation Summary of %s' % mem.user.full_name, 'smarttm@toastmasters.pk', [mem.user.email],
                      fail_silently=True, html_message=html_message)

            mem.summary_sent_date = timezone.now()
            mem.save()
        except:
            continue