'''
Created on 26 Jul 2012

@author: jjm20
'''
from django.test import TestCase
from questionnaire.forms import get_choices, generate_charfield, generate_textfield, generate_boolean_field, generate_select_dropdown_field, generate_radioselect_field, generate_multiplechoice_field, FIELD_TYPES, make_question_group_form,QuestionAdminForm
from questionnaire.models import Question, Questionnaire, QuestionGroup, AnswerSet, QuestionAnswer
from django.forms import Textarea, TextInput, BooleanField, ChoiceField, RadioSelect,CheckboxSelectMultiple, CharField, BaseForm
from django.forms.fields import  MultipleChoiceField
from django.contrib.auth.models import User



class QuestionAdminFormTestCase(TestCase):
    '''
     test custom QuestionAdminForm  for question creation
     1.test selectionoptions/choices is required for choicefields questions it should not be None
       if user enter leave the field empty for choicefield i.e None  validation will fail i.e form.is_valid is False 
     2.test selectionoptions should be comma seperated strings eg A,B,C for choicefields
     3.test selectoptions is not required for Non choicefields i.e charfield and textField,booleanfield 
      ie None for field_type that are NOT choicefields e.g charfield
      if user enter selectoptions for these non choicefields form validation will fail -form.is_valid is False otherwise True
    '''

    def test_selectoptions_not_required_for_booleanfield(self):
       
        questionadmintest_form=QuestionAdminForm({'label':'question_test1','field_type':'booleanfield','selectoptions':None})  
        self.assertEqual(questionadmintest_form.is_valid(), True,'selectionsoptions is NOT required for BooleanField')
       
        questionadmintest_form2=QuestionAdminForm({'label':'question_test6','field_type':'booleanfield','selectoptions': 'A,B,C'})
        self.assertEqual(questionadmintest_form2.is_valid(),False,' form data validation will be False if options is provided for booleanfield  ')
    
    def test_selectoptions_required_for_select_dropdown_field(self):
        questionadmintest_form=QuestionAdminForm({'label':'question_test2','field_type':'select_dropdown_field','selectoptions':None})  
        self.assertEqual(questionadmintest_form.is_valid(), False,'selectionsoptions is required for select_dropdown_field')
        
    def test_selectoptions_required_for_horinzontal_radioselect_field(self):
        questionadmintest_form=QuestionAdminForm({'label':'question_test3','field_type':'horinzontal_radioselect_field','selectoptions':None})  

        self.assertEqual(questionadmintest_form.is_valid(), False,'selectionsoptions is required for radioselectfield')   
    
    def test_selectoptions_required_for_radioselectfield(self):
        questionadmintest_form=QuestionAdminForm({'label':'question_test3','field_type':'radioselectfield','selectoptions':None})  

        self.assertEqual(questionadmintest_form.is_valid(), False,'selectionsoptions is required for radioselectfield')   
    
    def test_required_selectoptions_multiplechoicefield(self):
        questionadmintest_form=QuestionAdminForm({'label':'question_test4','field_type':'multiplechoicefield','selectoptions':None})  
        self.assertEqual(questionadmintest_form.is_valid(), False,'selectionsoptions is required for multiplechoicefield')   
            
    def test_delimiter_is_required_for_choicefields_selectoptions(self):
        
        questionadmintest_form=QuestionAdminForm({'label':'question_test5','field_type':'multiplechoicefield','selectoptions':'AB'})      
        self.assertEqual(questionadmintest_form.is_valid(),False,'multiplechoicefield selectionsoptions  form data validation will be false if options are not separated with delimiter i.e comma  ')
        
        questionadmintest_form2=QuestionAdminForm({'label':'question_test5','field_type':'radioselectfield','selectoptions':'A B C'})      
        self.assertEqual(questionadmintest_form2.is_valid(),False,' radioselectfield selectionsoptions  form data will not validate  if options are not separated with delimiter i.e comma  ')
        
        
        questionadmintest_form=QuestionAdminForm({'label':'question_test5','field_type':'multiplechoicefield','selectoptions':'A,B'})      
        self.assertEqual(questionadmintest_form.is_valid(),True,'multiplechoicefield selectionsoptions  form data validation will pass is option if separated with delimiter i.e comma  ')
        
        questionadmintest_form1=QuestionAdminForm({'label':'question_test5','field_type':'select_dropdown_field','selectoptions':'A,B,C'})      
        self.assertEqual(questionadmintest_form1.is_valid(),True,' select_dropdown_field selectionsoptions  form data validation will pass if option is separated with delimiter i.e comma  ')
         
        questionadmintest_form2=QuestionAdminForm({'label':'question_test5','field_type':'radioselectfield','selectoptions':'A,B,C'})      
        self.assertEqual(questionadmintest_form2.is_valid(),True,' radioselectfield selectionsoptions  form data validation will pass if option is separated with delimiter i.e comma  ')      
        
        
    def test_selectionoptions_not_required_for_non_choice_fields(self):
        
        questionadmintest_form=QuestionAdminForm({'label':'question_test7','field_type':'charfield','selectoptions': None})
        self.assertEqual(questionadmintest_form.is_valid(),True,'selectionsoptions form data validation will pass as selectoption is not required for Non choicefield  ')
        
        questionadmintest_form2=QuestionAdminForm({'label':'question_test8','field_type':'charfield','selectoptions': 'A,B'})
        self.assertEqual(questionadmintest_form2.is_valid(),False,'selectionsoptions form data validation will be False as selectoption is not required for Non choicefield  ')
        
        questionadmintest_form3=QuestionAdminForm({'label':'question_test9','field_type':'textfield','selectoptions': 'A,B'})
        self.assertEqual(questionadmintest_form3.is_valid(),False,'selectionsoptions form data validation will be False as selectoption is not required for Non choicefield  ')
        
        questionadmintest_form4=QuestionAdminForm({'label':'question_test6','field_type':'booleanfield','selectoptions': 'ABC'})
        self.assertEqual(questionadmintest_form4.is_valid(),False,'selectionsoptions form data validation will be False is option is NOT require for boolean  ')
       
        
class FormsTestCase(TestCase):
    
    fixtures = ['test_questionnaire_fixtures.json']
    
    
    def test_get_choices_question_with_options(self):
        '''
            Assuming that we pass this function a question object that has options defined
            we should get back:
            1. A list of tuples (option text, option text)
        '''
        
        tuple_choices = [(u'Radio 1',u'Radio 1'), (u' Radio 2',u' Radio 2'), (u' Radio 3',u' Radio 3')]
        choices_question = Question.objects.get(pk=5)
        get_choices_test = get_choices(choices_question)
        self.assertEqual(get_choices_test, tuple_choices)
        
    def test_get_choices_question_without_options(self):
        '''
            If we pass this function a question object that had no options defined we should get back
            a TypeError as the function that handle prevention of NoneType Object is already fixed under the admin screen
            or upon object creation
        '''
        choices_question = Question.objects.create(label='test', field_type='select_dropdown_field', selectoptions=None)
        self.assertRaises((ValueError,TypeError), get_choices(choices_question))       
        
        
        
        
    def test_get_choices_not_a_question(self):
        '''
            If we pass this function anything other than a question object it should raise an AttributeError
            Raising AttributeError is choosen because eventhough the method error type are using TypeError and
            ValueError, the return value always shows AttributeError
        '''
        choices_question = Questionnaire.objects.get(pk=1)
        self.assertRaises(AttributeError, get_choices, choices_question)
        
    def test_generate_charfield(self):
        '''
            This should return us a Charfield with a max length of 100, and a TextInput widget
        '''
        self.assertIsInstance(generate_charfield(), CharField)
        self.assertEqual(generate_charfield().max_length, 100, 'max length return should be 100')
        self.assertIsInstance(generate_charfield().widget, TextInput)
        
    def test_generate_textfield(self):
        '''
            This should return us a Charfield without a max length specified, and using a TextArea widget
        '''
        self.assertEqual(generate_textfield().max_length, None, 'max length should be Not Set')        
        self.assertIsInstance(generate_textfield(), CharField, 'this returns a charfield!')
        self.assertIsInstance(generate_textfield().widget, Textarea)
        
        
        
    def test_generate_boolean_field(self):
        '''
            This should return a BooleanField object defaulting to false
        '''
        self.assertIsInstance(generate_boolean_field(), BooleanField, 'The return class should be boolean field')
        self.assertEqual(generate_boolean_field().initial, True, 'Default value for booleanField is True')
        
        
    def test_generate_select_dropdown_field(self):
        '''
            This should return a Charfield with the choices attribute set to an empty list (to be populated later)
        '''
        self.assertIsInstance(generate_select_dropdown_field(), ChoiceField )
        self.assertEqual(generate_select_dropdown_field().choices, [])

        
    def test_generate_radioselect_field(self):
        '''
            This should return a ChoiceField with a RadioSelect widget and the choices attribute set to an empty list
        '''
        self.assertIsInstance(generate_radioselect_field(), ChoiceField)
        self.assertIsInstance(generate_radioselect_field().widget, RadioSelect )        
        self.assertEqual(generate_radioselect_field().choices, [])
        
    def test_generate_multiplechoice_field(self):
        '''
            This should return a MultipleChoiceField with the choices attribute set to an empty list and a CheckboxSelectMultiple widget
        '''
        self.assertIsInstance(generate_multiplechoice_field(), MultipleChoiceField)
        self.assertIsInstance(generate_multiplechoice_field().widget, CheckboxSelectMultiple)
        self.assertEqual(generate_multiplechoice_field().choices, [])

     
    def test_FIELD_TYPES_dict(self):   
        '''
            charfield should map to ``generate_charfield``
            textfield should map to ``generate_textfield``
            booleanfield should map to ``generate_boolean_field``,
            select_dropdown_fieldshould map to ``generate_select_dropdown_field``,
            radioselectfield should map to ``generate_radioselect_field``,
            multiplechoicefield should map to ``generate_multiplechoice_field``,
        '''

        self.assertEqual(FIELD_TYPES['charfield'], generate_charfield)
        self.assertEqual(FIELD_TYPES['textfield'], generate_textfield)
        self.assertEqual(FIELD_TYPES['booleanfield'], generate_boolean_field)
        self.assertEqual(FIELD_TYPES['select_dropdown_field'], generate_select_dropdown_field)
        self.assertEqual(FIELD_TYPES['radioselectfield'], generate_radioselect_field)
        self.assertEqual(FIELD_TYPES['multiplechoicefield'], generate_multiplechoice_field)
        
        
class FormsTestCase_WithFixture(TestCase):
    
    fixtures = ['forms_test_fixture.json']
    
    def assertQuestionType(self, question_type,question):
            
        assertion_map = {'charfield':(CharField, TextInput,None), 
         'textfield': (CharField, Textarea, None), 
         'booleanfield': (BooleanField, None, None),
         'select_dropdown_field':(ChoiceField,None, list),
         'radioselectfield':(ChoiceField,RadioSelect, list),
         'multiplechoicefield':(MultipleChoiceField,CheckboxSelectMultiple,list)}
        
        assertions = assertion_map[question_type]
        
        
        self.assertIsInstance(question , assertions[0])
        
        if assertions[1] != None:
            self.assertIsInstance(question.widget , assertions[1])
        if assertions[2] != None:
            self.assertIsInstance(question.choices , assertions[2])

    def test_make_question_group_form(self):
        '''
            The fixture should define a questiongroup that has one of each of the question types
            This function should return a BaseForm object and interoggation of its fields should
            be done to ensure that the correct fields have been generated, eg does the first name field have 
            the correct label and is its field properly mapped according to its questiontype?
        '''
        

        test_form = make_question_group_form(QuestionGroup.objects.get(pk=1),1)
        
        
        self.assertTrue(issubclass(test_form, BaseForm))

        expected = [    ('question 1','charfield'),
                        ('question 2','textfield'),
                        ('question 3','booleanfield'),
                        ('question 4','select_dropdown_field'),
                        ('question 5','radioselectfield'),
                        ('question 6','multiplechoicefield'),]
       
        for index in range(len(test_form.base_fields)):
                
            self.assertEqual(test_form.base_fields.value_for_index(index).label, expected[index][0])
            self.assertQuestionType(expected[index][1], test_form.base_fields.value_for_index(index)) 
            
            
    
        