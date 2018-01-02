from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.utils.translation import ugettext_lazy as _

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('username', 'password')
		help_texts = {
			'username': None,
		}

class SignUpForm(UserCreationForm):
	email = forms.EmailField(max_length=254)
	error_messages = {
	'password_mismatch': _("The two password fields didn't match."),
	'username_exists': _("An account with this username already exists."),
	'email_exists': _("An account with this email already exists."),
	}
	
	def __init__(self, *args, **kwargs):
		super(UserCreationForm, self).__init__(*args, **kwargs)

		for fieldname in ['username', 'password1', 'password2']:
			self.fields[fieldname].help_text = None
	
	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2', )
		help_texts = {
			'username': None,
			'email': None,
			'password': None,
			'password1': None,
			'password2': None,
		}
			
	def clean_email(self):
		email = self.cleaned_data["email"]
		matching = User._default_manager.filter(email=email)
		if matching.count()==0:
			return email
		raise forms.ValidationError(self.error_messages['email_exists'], code='email_exists',)

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			User._default_manager.get(username=username)
		except User.DoesNotExist:
			return username
		raise forms.ValidationError(self.error_messages['username_exists'], code='username_exists',)

	def save(self, commit=True):
		user = super(SignUpForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		user.username = self.cleaned_data['username']
		if commit:
			user.save()

		return user
	

class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )

class LanguageForm(forms.Form):
	lang_list = []
	LANG_CHOICES = Book.objects.order_by('language').distinct('language').values_list('language',flat=True) 
	for lang in LANG_CHOICES:
		lang_list.append((lang, lang))
	LANG_CHOICES = lang_list
	LANG_CHOICES.insert(0, ('', '----'))
	lang_native = forms.ChoiceField(widget=forms.Select(attrs={'onchange': 'this.form.submit();'}), label='Please select languages', choices=LANG_CHOICES)
	lang_foreign = forms.ChoiceField(label='→', label_suffix='', choices=LANG_CHOICES, widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
