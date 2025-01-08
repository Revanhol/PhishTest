from django import forms
from .models import Course, Test, Question, Answer, UserProfile, PhishingEmail, CoursePage
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'image']

class CoursePageForm(forms.ModelForm):
    class Meta:
        model = CoursePage
        fields = ['title', 'content', 'order']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['course', 'title', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['test', 'text', 'question_type']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['question', 'text', 'is_correct']

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            initial = kwargs.setdefault('initial', {})
            initial['email'] = kwargs['instance'].user.email
            initial['username'] = kwargs['instance'].user.username

    def save(self, commit=True):
        user_profile = super(UserProfileForm, self).save(commit=False)
        user = user_profile.user
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            user_profile.save()
        return user_profile

class PhishingEmailForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='Select User', required=False)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Select Group', required=False)

    class Meta:
        model = PhishingEmail
        fields = ['user', 'group', 'subject', 'message', 'attachment']

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        group = cleaned_data.get("group")

        if not user and not group:
            raise forms.ValidationError("You must select either a user or a group.")

        return cleaned_data

class TakeTestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(TakeTestForm, self).__init__(*args, **kwargs)
        for question in questions:
            if question.question_type == 'text':
                self.fields[f'question_{question.id}'] = forms.CharField(label=question.text)
            elif question.question_type == 'single_choice':
                choices = [(answer.id, answer.text) for answer in question.answers.all()]
                self.fields[f'question_{question.id}'] = forms.ChoiceField(label=question.text, choices=choices, widget=forms.RadioSelect)
            elif question.question_type == 'multiple_choice':
                choices = [(answer.id, answer.text) for answer in question.answers.all()]
                self.fields[f'question_{question.id}'] = forms.MultipleChoiceField(label=question.text, choices=choices, widget=forms.CheckboxSelectMultiple)