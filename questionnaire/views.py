'''
Created on Jun 26, 2012

@author: ayoola_al

'''
from django.http import HttpResponseRedirect,Http404
from django.core.urlresolvers import reverse
from models import  Questionnaire,AnswerSet,QuestionAnswer,Question
from django.template import  RequestContext
from django.shortcuts import render_to_response
from questionnaire.forms import make_question_group_form
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from commonfunctions import get_processed_questionsanswers



def questionnaire_index (request):
    questionnaire = Questionnaire.objects.all()
    
    group_list=[x for x in questionnaire]
    
    return render_to_response('questionnaire/questionnaire_index.html',{'group_list': group_list},context_instance=RequestContext(request))
    
@login_required
def handle_next_questiongroup_form(request,questionnaire_id,questiongroup_id=None):
    
    '''
    this function renders all the questiongroups in a given questionnaire in the order given(order-info) when created(order_info)
    basically what  this view  does is iterate through the questiongroups in the questionnaire 
    and render each questiongroup form when the data is posted then pass the next questiongroup to itself 
    check the passed questiongroup_id exist in the questionnaire ,
    after the last questiongroup in the questionnaire is rendered and posted ,the user is redirected to another page- finish page
    e.g  a given questionnaire_A with[questiongrp_A,questiongrp_C,questiongrp_B], will be render as  questiongrp_A first then questiongrp_C and finally questiongrp_B
    How it does this?
    check if the user has already answered/attemtted this questiongroup in this questionnaire before by retrieving the answerset object
    (an answerset object associate the user with this questiongroup in this questionnaire and
    an answerset will also associate the  user with questionanswers objects if the user has answered/submitted this questiongroup-questionnaire before)
    if an answerset exist -
             then try to get the previous question answer data and prepopulate the form with the user's most recent answer
             there are cases where an answerset exist but questionanswer does not exist this is because the user has attempted the questiongroup-questionnare 
             but did not submit the form hence an empty/blank form will be rendered in this case empty form may show field errors for required fields
    if an answerset does not exist -
              then it will create a new blank/empty question form for this group
    When a form is posted it check the fields data and save only data in the fields that user has changed 
    otherwise it wont save the  field that has not changed 
    when saving it does not overwrite previous answer it create new answer for the question for purpose of keeping questionanswers trail
    when form is posted i.e submited  form.changed_data will store list of the fieldnames that has been changed in this case( question_id ) 
    for comparison with the initial data this is useful if you need to save only the changed data 
    for this to work properly field attribute show_hidden_initial is set to True in all form fields 
    so that django will store the initial form data
    After a form  data is saved it passed the next questiongroup to render to itself
    '''
    #===========================================================================
    # retrived ordered questiongroups in this questionnare queryset dict
    #  and unpack them to  a list of question groups 
    #  questiongroup variable  is initialise to None as  this variable will be  use to store next questiongroup to render
    #  that are retrieve from this questionnaire.get_orderoup_groups list 
    #  if questiongroup_id == None then get  the  first questiongroup object to render (which will ofcourse be group at index 0)
    #  otherwise questiongroup_id will not be None because next questiongroup_id  will be passed to the view by this same view function 
    #  if there is a questionqroup_id  passed to this view ,it then  get the questiongroup object 
    #  then create a form for the questiongroup  
     
    #===========================================================================
    
    this_questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    questiongroup=None
    orderedgroups = this_questionnaire.get_ordered_groups()
    orderedgroups_list=[x.questiongroup for x in orderedgroups ]
    
    if questiongroup_id ==None:
        questiongroup=orderedgroups_list[0]
        print "this a group"
        print questiongroup
    else:
#        questiongroup= [group for group in orderedgroups_list if group.id == questiongroup_id]     
        for group in orderedgroups_list:
            if group.id == int(questiongroup_id):
                questiongroup =group
#===============================================================================
# this check is useful to prevent cases where the quetiongroup object is Nonetype  
# prevent None questiongroup from being passed to make_question_group_form()
#e.g someone try to manipulate the url in the browser
#===============================================================================
        if questiongroup == None:
            raise Http404
        
    questionForm = make_question_group_form(questiongroup,questionnaire_id)
    form=questionForm()
    submit="submit"
    #===========================================================================
    # check if the user has already answered this questiongroup in this questionnaire
    #  Answerset object represent association/references between a user questionanswer to a given questiongroup in a questionnaire.This answerset object created when the user first answered/attempt questions in a given questionniare questiongroup
    #  in other words if  a user has not answered questions in a questionnaire questiongroup the user will not have answerset object for the given questionnaire questiongroup
    #  if  Answerset created,the boolean variable created will be True get the previous data stored i.e user most recent answer to prepopulate the form and allow user edit previous answers (edit mode)by passing the data to the form instance this make the form bound form.is_bound will be True
    #  save only the answers data in form field  that the data  is changed by the user 
    #  syntax (if not created)if  Answerset is not created then boolean variable created is False other words means user has not answered/attempted the given questiongroup in this questionnnaire  before
    #  then create a new empty question form for this questiongroup 
    #  an Answerset obj- this_answer_set  will always be return whereever the case wheather (for a new questiongroup form or existing )
    #===========================================================================
   
    this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire,questiongroup=questiongroup)
    
    if not created:   
        processed_questionsanswers_data=get_processed_questionsanswers(request.user,questionnaire_id,questiongroup.id,mode='edit')
        initial=processed_questionsanswers_data['initial_data']
        form=questionForm(initial)
        submit="submit revision"  
    if request.method =='POST':
    
        form=questionForm(request.POST)
        if form.is_valid() and form.has_changed:        
            for question in form.changed_data: 
                answer=form.cleaned_data[question]
                this_question_answer= QuestionAnswer(question= get_object_or_404(Question, pk=question),answer=answer,answer_set=this_answer_set)
                this_question_answer.save()
#===============================================================================
#after the form is posted and changes saved  for this questiongroup form
# check to see if this questiongroup is the last one  i.e orderedgroups_list[-1] e.g slice somelist[-1] will retrieve last item in a list
# if it is the last questiongroup then redirect to finish page
# otherwise  if its not the last group then there is more questiongroup in the list  
# then get the next questiongroup index i.e this group index + 1 
# use next group index to retrieve the next questiongroup object
# pass the next questiongroup_id  to the view
#===============================================================================
            if questiongroup == orderedgroups_list[-1]:
                return HttpResponseRedirect(reverse('questionnaire_finish'))
            else:    
                nextgroupindex=orderedgroups_list.index(questiongroup) + 1
                questiongroup=orderedgroups_list[nextgroupindex]
                return HttpResponseRedirect(reverse('handle_next_questiongroup_form', kwargs = {'questionnaire_id': questionnaire_id, 'questiongroup_id' : questiongroup.id,}))
 
    return render_to_response('questionnaire/questionform.html', 
        {'form': form,'questionnaire':this_questionnaire,'questiongroup':questiongroup,'submit':submit},context_instance=RequestContext(request))
    

def finish(request):
    '''
     just a page to redirect to after sucesssful completion of question form this can be change to any page 
    '''
    return render_to_response('questionnaire/finish.html')    #you will still want to pass this through the RequestContext, which enables middleware to add things to the response  eg. context_instance=RequestContext(request)


@login_required
def display_question_answer(request,questionnaire_id,questiongroup_id):
    '''
    display a user's most recent  question and answers for given  questiongroups in a given questionnaire
    request user is user that has answered the given questionnnaire questiongroup
    '''
    processed_questionsanswers=get_processed_questionsanswers(request.user,questionnaire_id,questiongroup_id,mode='display')
    
    return render_to_response('questionnaire/display_questionanswer.html',{'questionanswer':processed_questionsanswers['questionanswers'],'questionnaire':processed_questionsanswers['questionnaire'],'questiongroup_id': int(questiongroup_id),'groups_list': processed_questionsanswers['groups_list'],},context_instance=RequestContext(request))


@login_required
def edit_question_answer(request,questionnaire_id,questiongroup_id):
    '''
    edit a user most recent answers for a given questiongroup in a given questionnaire 
    edit mode is for editing existing/previous question answers it pre-populates form with most recent answers or empty form .
    The form rendered could be empty if the user only attempted the question but did not submit the form .
    To retrieve the recent question answer this function first try to retrieve the answerset object which represent the user previous association with this questiongroup in the given questionnaire
    answerset object was created when user first answered or attempted a quetiongroup in the given quesstionnaire
    (answerset is created by handle_next_questiongroupform view function)
    
    if the user has not attempted this questiongroup in the questionnaire before then the user will NOT have answerset/questionanswer object associating the user to this questiongroup questionnnaire
    then it will raise 404 therefore only user that attempted or answered this questiongroup questionnnaire before CAN EDIT i.e complete previous attempt (empty form) or change their answers(prepopulated form)
    when saving it checks if fields data(answer) has changed if the field has change save only the changed data  
    it does not overwrite previous answer it create new answer  for question  for purpose of keeping questionanswers trail
    when form is posted  form.changed_data will store list of the fieldname in this case( question id ) 
    that has been changed .Then if form.has_changed if compare the initial data with the submitted data 
    this is useful if you need to save only the changed data  or do some compariving before saving submitted data
    '''

    this_answer_set=get_object_or_404(AnswerSet,user=request.user,questionnaire=questionnaire_id ,questiongroup=questiongroup_id)
    
    processed_questionsanswers=get_processed_questionsanswers(request.user,questionnaire_id,questiongroup_id,mode='edit')
    editForm= make_question_group_form(processed_questionsanswers['questiongroup'],questionnaire_id)
   
    initial=processed_questionsanswers['initial_data']
    form=editForm(initial)
           
    if  request.method == "POST": 
        form=editForm(request.POST)
        
        if form.is_valid() and form.has_changed:      
            for question in form.changed_data: 
                answer=form.cleaned_data[question]    
                this_question_answer= QuestionAnswer(question= get_object_or_404(Question, pk=question),answer=answer,answer_set=this_answer_set)
                this_question_answer.save()
                                           
            return HttpResponseRedirect(reverse('questionnaire_finish'))            
     
    return render_to_response('questionnaire/edit_questionanswer_form.html', 
            {'form': form,'questionnaire':processed_questionsanswers['questionnaire'],'questiongroup_id':int(questiongroup_id),'groups_list':processed_questionsanswers['groups_list'],},context_instance=RequestContext(request))


@login_required     
def all_question_answers_for_questiongroup(request,user_id,questionnaire_id,questiongroup_id):
    
    '''
    show trail all questions and  answers for  given questiongroup in a questionnaire for a given user_id
    
    the request will be made by authorized user requesting a trail of all questionanswers info for a user  with the given user_id    
    user_id is may not be the request.user , user_id is a registered user that request.user is requesting info about
    e.g user 'A'  an admin may request qeustionanswer trail info about a given user 'B'  user_id- 2
    user is passed to template because user is may not be request.user 
    this function check if the user with user_id exits and have questionanswers objects
    then retrieve all the questionanwsers in the given questiongroup-questionnairefor the user with the given user_id 
    appropriate permission need to be set
    '''
    user =get_object_or_404(User,pk=user_id)
    processed_questionsanswers=get_processed_questionsanswers(user,questionnaire_id,questiongroup_id,mode='trail')

    return render_to_response('questionnaire/all_questionanswers.html',{'questionanswer_list':processed_questionsanswers['questionanswer_list'],'user':user,'questionnaire':processed_questionsanswers['questionnaire'],'questiongroup_id':int(questiongroup_id),'groups_list':processed_questionsanswers['groups_list'],},context_instance=RequestContext(request))


@login_required
def questionnaire_detail_list(request,questionnaire_id):
    '''
    show  detail list as links  for all questiongroups in a given questionnaire ordered by order_info
    links can be use to edit or display given  questionanswer for questiongroups in questionnaire
    '''    
    thisquestionaire_grouplist = get_processed_questionsanswers(request.user,questionnaire_id,mode='detail')
      
    return render_to_response('questionnaire/questionnaire_detail.html',{'groups_list':thisquestionaire_grouplist['groups_list'], 'questionnaire':thisquestionaire_grouplist['questionnaire'],},context_instance=RequestContext(request))
