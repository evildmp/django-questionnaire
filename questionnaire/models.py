'''
Created on Jul 10, 2012

@author: mzd2
@author: ayoola
'''
from django.db import models
from django.contrib.auth.models import User



class CustomListField(models.TextField):
    '''
    for creating  custom list field override some model.fields methods i.e 
    1.to_python ensure the custom field is appro
    The SubfieldBase metaclass ensures  to_python() method to be called automatically when customfield is created,
    otherwise it will not be called
    https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#the-subfieldbase-metaclass
    
    '''


    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
    
        kwargs={'default':None,'null':True,'blank':True,
                'help_text':'Enter option for select Field Type seperated with a comma e.g No ,Yes,Not Applicable '}
        
        super(CustomListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        '''
        @return: list if it exist otherwise if there value it will create a list
        Converts a value as returned by  database( or a serializer) to a Python object in this case a python list
        1.if no value i.e value is none,it will do nothing and return back to caller to handle the field validitation appropriately
        2.if the value is already  a list it returns the list
        3.if the value is string separated by token i.e (,) it convert the string  to list  e.g A,B,C will be converted to [A,B,C]
        
        '''
        if not value: return 
        if isinstance(value, list):
            return value
#        return value.split(self.token)
        return [item.strip() for item in value.split(",")]

    def get_db_prep_value(self, value,connection=None,prepared=False):
        '''
        @return string separated by token as stored in database
        '''
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])



class Question(models.Model):
    '''
    model question objects attributes
    define attributes of a question:
    1.label : the actual question  eg what is your name?
    2.field_type: type of questions or type of answers you expect or require for the question e.g 
        booleanfield -if the question answer require is True or False, this is rendered as check boxes -if checked means True (Boolean not string)
        charfield-if the question answer require typing some info in a form field 
        textfield- if the  question answer require typing more detail info in a form text field 
        select_dropdown_field- if the question answer require selecting one answer from some options  
        multiplechoicefield-if the question answer require selecting one or more answer from some options ,this options are rendered as multiplechoice checkboxes in a form
        radioselectfield-if  the question  answer require selecting only one answer from some options ,this  options are rendered as radio buttons in a form
    3.selectoptions :list of choices or options available for  question .Required for field type that is choicefields i.e select_dropdown_field,radioselectfield, multiplechoicefield
                     otherwise selectoptions is None .options stored as comma ","seperarted strings
                     e.g selectoptions for a question of field_type-radioselectfield may be 'Yes',' No' ,'Not Applicable'
                     selectoptions for a choicefield MUST be 2 or more choices/options to make sense e.g selectoptions A,B
    4.FIELD_TYPE_CHOICES: tuple of tuples stores the  available choices for question field_type as pair of key(label),value string 
                    e.g field type 'charfield' will stored as 'charfield'  
    '''
    class Meta():
        db_table ='question'
        
    FIELD_TYPE_CHOICES=(('charfield','charfield'),('textfield','textfield'),('booleanfield','boolean'),
                        ('select_dropdown_field','select_dropdown_field'),('radioselectfield','radioselectfield'),('multiplechoicefield','multiplechoicefield'))
    
    label=models.CharField('question',max_length=255)
    field_type=models.CharField(choices=FIELD_TYPE_CHOICES,max_length=100)    
    selectoptions=CustomListField()
    
    def __unicode__(self):
        return 'Question:%s FieldType:%s Selectoptions:%s' %(self.label, self.field_type,str(self.selectoptions))
    
    def save(self,*args,**kwgs):
        '''
          ensure selectoption for non choicefield is saved as None 
          only choicefields require selectoptions i.e select_dropdown_field,radioselectfield, multiplechoicefield should have options 
        '''
        if not self.id:
            if not self.field_type in ['select_dropdown_field','radioselectfield', 'multiplechoicefield'] :              
                self.selectoptions = None
            
        super(Question,self).save(*args,**kwgs)

    
class QuestionGroup(models.Model):
    '''
    reponsible for question groups ,each group set can have one to  many set of questions 
    order_info store the order or sequence the question group is to be rendered in a form .e.g  order_info = 2 will be rendered before order_info =3  
    '''
    class Meta():
        db_table ='questiongroup'
        
    name = models.CharField('questiongroupname',max_length=255,unique=True)
    questions = models.ManyToManyField(Question, through = 'Question_order')
    
    def get_ordered_questions(self):
        '''
        @return: questions in  question group ordered by order_info
        '''
        return [order.question for order in Question_order.objects.filter(questiongroup=self).order_by('order_info')]
    
    def __unicode__(self):
        return self.name
   
class Questionnaire(models.Model):
    '''
    This class models the Questionnaire and its attributes
    name : name for the questionnaire 
    questiongroups: the question groups in the named questionnaire
    questiongroups are reuseable i.e a given questiongroup can be reused in one or more questionnaire  
     
    '''
    name=models.CharField(max_length=250)
    questiongroup=models.ManyToManyField(QuestionGroup, through='QuestionGroup_order')
    
    def get_ordered_groups(self):
        '''
        @return: the questiongroups in a questionnaire order by the order_info
            
        '''
        return QuestionGroup_order.objects.filter(questionnaire=self).order_by('order_info')
    
    def __unicode__(self):
        return self.name
    
class QuestionGroup_order(models.Model):
    '''
    This class stores the ordering of the questiongroups rendered in a questinnaire
    order_info store the order or sequence the questiongroup is to be rendered in a form .e.g  order_info = 2 will be rendered before order_info =3  
    '''
    questiongroup=models.ForeignKey(QuestionGroup)
    questionnaire=models.ForeignKey(Questionnaire)
    order_info=models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.questiongroup, str(self.order_info))
    
    
class Question_order(models.Model):
    '''
    This class is responsible in storing the ordering relationship between the question and questiongroup
    order_info store the order or sequence the questions in a questiongroup is to be rendered in a form .e.g  order_info = 2 will be rendered before order_info =3  
    '''
    questiongroup =models.ForeignKey(QuestionGroup)
    question = models.ForeignKey(Question)
    order_info = models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.question, str(self.order_info))
    
    
        
class AnswerSet(models.Model):
    '''
  model store relationship for users answer for  questiongroup in a questionnaire
  associates a user to a questiongroup in a questionnaire when answers the questionnaire

    '''
    class Meta():
        db_table ='answer_set'
        
    user=models.ForeignKey(User)
    questionnaire=models.ForeignKey(Questionnaire)
    questiongroup=models.ForeignKey(QuestionGroup)
        
    def __unicode__(self):
        return 'user:%s questionnaire:%s  questiongroup:%s ' %(str(self.user), str(self.questionnaire),str(self.questiongroup)) 
        
class QuestionAnswer(models.Model):    
    '''
    This model stores questions, answers and related answer_set 
    '''
    class Meta():
        db_table ='questionanswer'
        
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=255)
    answer_set = models.ForeignKey(AnswerSet)
     
    
    def __unicode__(self):
        return 'question:%s answer:%s answer_set:%s' %(str(self.question), str(self.answer), str(self.answer_set))
    
    def save(self,*args,**kwgs):
        '''
          django multiple choicefield answers are by default a list 
          ensure answers for choicefield  questions if it is a  list are saved as  string seperated by comma e.g A,B,C
          only for choicefields  i.e select_dropdown_field,radioselectfield, multiplechoicefield 
        '''
        if not self.id:
            if isinstance(self.answer,list):
                    self.answer = ','.join(self.answer)
            
        super(QuestionAnswer,self).save(*args,**kwgs)