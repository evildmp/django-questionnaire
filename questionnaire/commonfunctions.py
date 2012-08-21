'''
@author: ayoola_al

'''
from models import Questionnaire,QuestionGroup,QuestionAnswer
from django.shortcuts import get_object_or_404
from django.db.models import Max
from operator import itemgetter
from itertools import groupby

'''
stores common  functions that are reuse across the application 
'''

def get_processed_questionsanswers(user,questionnaire_id,questiongroup_id=None,mode=None):
    '''
    the fuction will return dictionary of processed data to the calling view ,
    the views can the use the data as required or/and passed the data to template
    reason for this to avoid code duplcation in the views -DRY principle
    this fuction first check if questionnaire and questiongroup exists and do some custom data processing based on the mode
    the mode value are passed as string by the views to this function -can be 'edit','display','trail','detail' mode
    these parameters are optional depending on calling view or mode e.g detail mode does not require questiongroup_id
    hence why parameter variables are initialised as None
    
    mode:'edit' 
    edit mode return data that will allow user to edit his/her recent answers to given question group 
    and also  using groups_list links to navigate and  edit answers for other questiongroups in the  given questionnaire if user changes their mind or wishes 
    @return: the user most recent question and answers for given questiongroup in a given  questionnaire
    user has previously answered/attempted  the given questionnaire question group
    Then retrieve the most recent questions and answer  to be used as initial data i.e use to pre-populate the edit form 
    this function it does this by retrieving:
    1. all the  most recent questionanswer objects ids group by unique question and answer_set pair - recent_questionanswers_list
    2. Then  filter out all question and answer objects in the given questionnaire-questiongroup for this user that occur in the recent_questionanswers_list
       by checking if they exist in the all the most recent questionanswer objects list 
       will give only the question and answers that are recent for this user i.e user_recent_questionanswers_objs
    
    intial data:
    multiplechoicefield require as list as initial data  hence intial data custom processing 
    
    mode : 'trail' 
    if mode ="trail" the data return will allow a user(request.user) to see another registered user's trail of question and answer 
    it return dictionary data i.e trail of all questions and answers that registered user has answered
    for given questiongroup in a questionnaire for a given user_id 
    
    
    @return: all questions and answers the user has answered for given questionnaire
     sort the questionanswers and group the data based on question_id for display purpose
    
    mode: 'display'
    display mode return data that will allow user to see his or her recent question and answer for the given question group
    return dictionary data of  user most recent questions and answers the user has answered for display/viewing purpose only 
    it is not edit mode hence its not rendered with a form
    if Mode is "display"
    @return : the user most recent question and answers for given questiongroup in a given  questionnaire
    for display purpose
    
    mode: 'detail'
    detail mode return data that will allow user to see links to questionanswer 
    @return: all questiongroups list in given questionnaire 
     questiongroups list is then passed to template by view questionnaire_detail_list view  
     and used by template to build links to both edit and display questionanswer for the  given  questionnaire
      
    '''
    
    this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    this_questiongroup=None
    if questiongroup_id is not None:
        this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
    
#===============================================================================
#given that max id of a given object  represent  most recent created object  .
#Max is django built-in function- aggregation function
# .values -get the values for question and answer_set  pair and .annotate(Max(id) )-  will group the objects by their Max id
# only unique questionanswer  objects with maximum id are retrieved which represent the recent questionanswers for each question and answer_set pair .
# it will look for questionanswer objs  with same question and answer_set  pair ,aggregate each unique  question and answer_set .
# which will group the  objects by their common data values and return for each group the questionanswer with maximum id .
# This represent the all most recent questionAnswer objects id
#flatten the queryset  to a list containing only ids of the all most recent questionanswer  objects.
# user_recent_questionanswers_objs retrieve user questionanswer that exist in the most recent questionanswer  objects

#===============================================================================
    all_thisuser_questionanswers_objs=QuestionAnswer.objects.all().filter(answer_set__user=user,answer_set__questionnaire=this_questionnaire,answer_set__questiongroup=this_questiongroup)
    recent_questionanswers_list=QuestionAnswer.objects.values('question','answer_set').annotate(Max('id')).values_list('id__max',flat=True)  
    user_recent_questionanswers_objs=all_thisuser_questionanswers_objs.filter(id__in=recent_questionanswers_list) 
 
#===========================================================================
#retrieve all ordered questiongroup objects in this questionnaire and put a list
# group list are passed to template by the view -using groups_list as links user can navigate and  edit answers for other questiongroups in the  given questionnaire if user changes their mind /made a mistake
#===========================================================================
    orderedgroups=this_questionnaire.get_ordered_groups()   
    groups_list=[(x.questiongroup) for x in orderedgroups]     


    if mode =='edit':
#===============================================================================
#  unpack user_recent_questionanswers_objs for initial data to prepopolate  form for edit mode
#  mulplechoicefield expect a list of strings initial data otherwise it will throw error- enter valid list value
# boolean field initial data is set as True (i.e checked) to allow user to dynamical change the value 
# when creating the form we set booleanfield initial value to True and required = False to allow dynamic change of value to etheir False or True
# Note all fields is required by default (django's default) 
#for details see source https://docs.djangoproject.com/en/dev/ref/forms/fields/#booleanfield
#===============================================================================
        initial_data=dict()
        for x in user_recent_questionanswers_objs:
                        
                if x.question.field_type =='booleanfield':
                    x.answer=True
                if x.question.field_type == 'multiplechoicefield':
                    if ',' in x.answer:
                        x.answer = [str(y.strip()) for y in x.answer.split(',')]
                    else :
                        x.answer=[str(x.answer)]

                initial_data[str(x.question.id)]= x.answer

        return {'initial_data':initial_data ,'questionnaire':this_questionnaire,'questiongroup':this_questiongroup,'groups_list':groups_list,}
         
         
    elif mode == 'trail':
#===============================================================================
#   unpack all questionanswer objects for display of all questionanswers  sort the question and answers  and group them based on question_id
#   user is pass to template because user is not request.user it's a register user you(request.user) is doing look up on
#===============================================================================
        questionanswer=[(questionanswer.question.id,questionanswer.question.label ,questionanswer.answer) for questionanswer in all_thisuser_questionanswers_objs]
        sorted_questionanswers= sorted(set(questionanswer),key=itemgetter(0))            
        questionanswer_list = list(map(itemgetter(0), groupby(sorted_questionanswers)))
         
        return {'questionanswer_list':questionanswer_list,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,}
        

    elif mode =='display':
#===============================================================================
# return dictionary data of most recent questions and answers the user has answered for display/viewing purpose only 
# not for edit hence its not rendered in a form 
# its called by display view 
#===============================================================================
        
        user_recent_questionanswers=[(x.question ,x.answer) for x in user_recent_questionanswers_objs]
        
        return {'questionanswers':user_recent_questionanswers,'questionnaire':this_questionnaire,'questiongroup_id':int(questiongroup_id),'groups_list':groups_list,}
        
    elif mode =='detail':
#===============================================================================
# return all quetiongroups list in given questionnaire 
# this then passed to template by the questionnaire_detail_list view  
# then used in the template to render links to both edit and display quetionanswer for this  questionnaire 
#===============================================================================
        
        return {'groups_list': groups_list, 'questionnaire':this_questionnaire,}    
    