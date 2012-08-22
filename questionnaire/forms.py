'''
Created on Jun 26, 2012

@author: ayoola_al

'''

from django import forms
from models import Question
from django.forms.fields import CharField,BooleanField,ChoiceField,MultipleChoiceField
from django.forms.widgets import RadioSelect 
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe



class CustomListWidget(forms.Textarea):
    '''
    create flatten custom widget use to render CustomList Field 
    displays selectoptions List as string of strings  separated by comma 
    e.g customList field [A,B,C] will be displayed and stored as A,B,C string
    '''
    def render(self, name, value, attrs=None):
        if value is not None :
            value = ','.join(str(v) for v in value)
        return super(CustomListWidget, self).render(name, value, attrs)
    

class QuestionAdminForm(forms.ModelForm):
    '''
    QuestionAdmin for creation of creation af question objects 
    overide form validation clean() method by doing custom form validation for  Question object selectoptions/choices attribute 
    ensure user enter valid selectionoptions/choices for all  field types 
    1.check selectoptions field for choicefield i.e multiplechoice ,radioselectfield and select_dropdown_field field_type 
    is not empty and are   ","  separated string
    2.check the selectioptions for Non choice field types are None or Empty i.e charfield,textfield ,booleanfield 
    if error appropriate error message will be displayed
    Questions are reuseable
    '''
    class Meta:
        model = Question
        widgets = {'selectoptions': CustomListWidget(),}

    def clean(self):
        '''
        custom clean()- validation for select options validation
        @return: cleaned_data 
        
        '''
        field_type=self.cleaned_data["field_type"]
        selectoptions = self.cleaned_data["selectoptions"]
        
        if field_type  in ['select_dropdown_field','radioselectfield','horinzontal_radioselect_field', 'multiplechoicefield'] : 
            
            if  not selectoptions:
                raise forms.ValidationError("Select Options is required for "+ str(field_type)+ " Enter valid options seperated with commas e.g No,Yes,Not Applicable")        
          
            elif  ","  not in  selectoptions :
                raise forms.ValidationError("Enter valid options seperated with comma e.g No,Yes,Not Applicable")
                
        elif field_type in ['charfield','textfield','booleanfield']:
            if selectoptions :
                raise forms.ValidationError("Select Options is not required  for " + str(field_type) + " Must Be Left Empty")
        
        return self.cleaned_data
    
    
def get_choices(question):
    '''
     @return: choices for a given question of choicesField fieldtype 
     only called/required when creating choicefields in a form
     1.it retrieves the predefined choices for given question from Question model selectoptions field 
     2. unpack/make selectoptions into a list of tuples using the key as the value 
     e.g for selectoptions [A,B,C]  the choices return will be [(A,A),(B,B),(C,C)] 
     so whatever the user selected when filling form is the actual answer stored in the database
     question.selectoptions validation is handle at the time question object creation to avoid empty choices 
     note question validation only check for empty list and comma separated strings see QuestionAdminForm clean method for detail
    
    '''

    choices_list = question.selectoptions
    try:
        choices= [(x,x) for x in choices_list]
        return choices
    except (TypeError,ValueError)  :
        ValueError('this question selectoptions %s is not valid select option must be a list e.g A,B,C' %(choices_list))
        
    '''
     By django default, each Field class assumes the value is required, so if you pass an empty value 
    -- either None or the empty string ("") -- then clean() will raise a ValidationError exception
    field attribute show_hidden_initial is set to True in all form fields so that django will store the initial form data
    and if form.has_changed it compare the initial data with the submited data 
    if form field initial data has changed when form is posted form.changed_data will store list of the fieldname in this (case question id ) that has been changed for comparison that is useful if you need to save only the changed data
    show_hidden_initial is set to True applies to all field types 
    source:https://docs.djangoproject.com/en/dev/ref/forms/fields/#required
    '''
        
class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    '''
    this class overide default radioselect widget rendering  by default radio buttons are rendered vertically 
    '''
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % x for x in self]))        
        
        
def generate_charfield():
    '''
  
     @return Charfield that has TextInput widget, this smaller than textarea widget if you require less info typed/enter into the form field
     you can set your own size attributes for the widget
     
    '''
    return CharField(max_length=100,widget=forms.TextInput(attrs={'size':'40'}),show_hidden_initial=True)

def generate_textfield():
    '''
     The field is required by default (django's default)
     @return CharField that has Textarea widget ,this allow to type/enter more info into the form field and it resizeable/expandable 
     you can set yor size attributes for the widget as you wish
     for details see source https://docs.djangoproject.com/en/dev/ref/forms/fields/
     field attribute show_hidden_initial is set to True so that if form field initial data has changed  the form.changed_data will store the fieldname  that has been changed for comparison
     that is useful if you need to save only the changed data
    '''    
    return CharField(widget = forms.Textarea(),show_hidden_initial=True)

def generate_boolean_field():
    '''
     @return Boolean field  
     The field is required by default (django's default) but we set required =False to allow dynamic change of value to etheir False or True
     initial value set to True
     If you want to include a boolean in your form that can be either True or False (e.g. a checked or unchecked checkbox), you must remember to pass in required=False 
     when creating the BooleanField.
     for details see source https://docs.djangoproject.com/en/dev/ref/forms/fields/#booleanfield
    '''    
    return BooleanField(required=False,initial=True,show_hidden_initial=True)

def generate_select_dropdown_field():
    '''
    The field is required by default (django's default)
    @return: return form ChoiceField
    choices is defaulted to empty list as the choices will be populate by get_choices() function with predefined choice method during form creation
    for details see source https://docs.djangoproject.com/en/dev/ref/forms/fields
    '''
    return ChoiceField(choices=[],show_hidden_initial=True)

def generate_horinzontal_radioselect_field():
    '''
    @return a ChoiceField that has a RadioSelect widget -if you require only one answer from atleast two or more options
    choices is defaulted to empty list as the choices will be populate by get_choices() function with predefined choice method during form creation
    rending the radio button  horizontally to render vertical change to widget=RadioSelect()
    ''' 
    return ChoiceField(widget=RadioSelect(renderer=HorizontalRadioRenderer),choices=[],show_hidden_initial=True)

def generate_radioselect_field():
    '''
    @return a ChoiceField that has a RadioSelect widget -if you require only one answer from atleast two or more options
    choices is defaulted to empty list as the choices will be populate by get_choices() function with predefined choice method during form creation
    rending the radio button  horizontally to render vertical change to widget=RadioSelect()
    ''' 
    return ChoiceField(widget=RadioSelect(),choices=[],show_hidden_initial=True)


def generate_multiplechoice_field():
    '''
    @return MultipleChoiceField that has a CheckboxSelectMultiple wideget -uses checkboxes so form user can select/check one or more answers to a question
    The field is required by default (django's default)as form user are force to select/check at least one or more of choices/option
    if left empty by user field the value will be empty list i.e Empty value: [] 
    error_messages for require error is set to display in case none of the choices is checked/selected inform
    you can set your own error messages as appropriate 
    choices is defaulted to empty list as the choices will be populate by get_choices() function with predefined choice method during form creation
     https://docs.djangoproject.com/en/dev/ref/forms/fields/#MultipleChoiceField
    '''
    return MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple(),show_hidden_initial=True,error_messages={'required': 'This question is required can not be empty select one or more answer '})



'''
 FIELD_TYPES dict stores key value mapping of all fieldtypes as keys  to thier respective generate funtions as value.
 These functions generate the formfield for the field type with or without widgets/attribute as appropriate or required
'''
FIELD_TYPES={
            'charfield': generate_charfield ,
            'textfield': generate_textfield,
            'booleanfield': generate_boolean_field,
            'select_dropdown_field':generate_select_dropdown_field,
            'radioselectfield':generate_radioselect_field,
            'horinzontal_radioselect_field':generate_horinzontal_radioselect_field,
            'multiplechoicefield':generate_multiplechoice_field,

            }

def make_question_group_form(questiongroup,questionnaire_id):
    '''
     create a dynamic questionnaire form on the fly
     @return: a type form for specific questiongroup in given questionnaire
     form created using python type syntax 
     form type  declaration:
       i.e  type('name',(Formclass,),{attrs})
       name -intended name for your form class ,
      Formclass- A tuple containing any classes it inherits from 
      attrs -attributes-A dictionary containing the attributes of the class
       
     This form  is created dynamically at run-time rather than being defined in a Python source file
     created in declarative way i.e give Django a description of a class, and let it do all the work of creating the model for us
     Internally, Django uses metaclasses to create form based on a class you provide
     in this case the form inherits from django forms.Baseform
     Note the form  is not particularly bound to any actual model
     for detail see : https://code.djangoproject.com/wiki/DynamicModels
     attributes:
     form fields are stored in a SortedDict ,a dictionary that keeps its keys in the order in which they are inserted
     https://docs.djangoproject.com/en/dev/ref/utils/#creating-a-new-sorteddict
     form data validation:  https://docs.djangoproject.com/en/dev/topics/forms/?from=olddocs
     https://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound
     source https://docs.djangoproject.com/en/dev/ref/utils/#creating-a-new-sorteddict
    '''
    fields = SortedDict([])
    orderedgroups = questiongroup.get_ordered_questions()
    
    for question in orderedgroups:
        
        if question.field_type in ['select_dropdown_field','radioselectfield','horinzontal_radioselect_field','multiplechoicefield']:
            field=FIELD_TYPES[question.field_type]()
            field.choices=get_choices(question)    
            field.label = question.label
            fields[str(question.id)]= field
        else:    
            field = FIELD_TYPES[question.field_type]()
            field.label = question.label
            fields[str(question.id)]= field

    return type('%sForm' %(str(questiongroup.name)),(forms.BaseForm,),{'base_fields':fields})



    
        
