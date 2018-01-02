from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.cache import never_cache
from django.shortcuts import render 
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth import login as login_user
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from .forms import SignUpForm
from .forms import LanguageForm
from .forms import UserForm
from .models import *
from django.urls import reverse
from django.http import HttpResponseRedirect
import random
import re
from django.db.models import Q
from django.utils.safestring import mark_safe
import polly.gale_church as gale_church 
from googletrans import Translator
import csv
from django.templatetags.static import static
from django.template import RequestContext

# Create your views here.
from django.contrib.auth.views import *
from .forms import ContactForm


def contact(request):
    user_name = request.GET.get('user_name', None)
    if user_name == None:
        user_name = 'AnonymousUser'
    form_class = ContactForm
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            contact_name = request.POST.get(
                'contact_name'
            , '')
            contact_email = request.POST.get(
                'contact_email'
            , '')
            form_content = request.POST.get('content', '')
            # Email the profile with the 
            # contact information
            template = get_template('contact_template.txt')
            context = {
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            }
            content = template.render(context)
            email = EmailMessage(
                "New contact form submission",
                content,
                "Your website" +'',
                ['youremail@gmail.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return render(request, 'contact.html', {'form': form, 'message': 'success','user_name':user_name, 'login_form':AuthenticationForm(),'signup_form':SignUpForm()})           
            #return redirect('contact_me')
        return render(request, 'contact.html', {'form': form, 'message': 'failure','user_name':user_name, 'login_form':AuthenticationForm(),'signup_form':SignUpForm()})
    return render(request, 'contact.html', {
        'form': form_class, 'message': '', 'user_name':user_name, 'login_form':AuthenticationForm(),'signup_form':SignUpForm()
    })

def my_password_reset(request, template_name='registration/password_reset_form.html'):
    return password_reset(request, template_name, extra_context={'login_form':AuthenticationForm(),'signup_form':SignUpForm()})

def my_password_reset_done(request, template_name='registration/password_reset_done.html'):
    return password_reset_done(request, template_name, extra_context={'login_form':AuthenticationForm(),'signup_form':SignUpForm()})

def my_password_reset_confirm(request, uidb64, token, template_name='registration/password_reset_confirm.html'):
    return password_reset_confirm(request, uidb64, token, template_name, extra_context={'login_form':AuthenticationForm(),'signup_form':SignUpForm()})

def my_password_reset_complete(request, template_name='registration/password_reset_complete.html'):
    return password_reset_complete(request, template_name, extra_context={'login_form':AuthenticationForm(),'signup_form':SignUpForm()})

def my_logout(request):
	print('logging out')
	return logout(request) 

def my_login(request):
	print('login hello')
	username = request.GET.get('username', None)
	password = request.GET.get('password', None)
	book_name = request.GET.get('b_name', None)
	language_native = request.GET.get('language_native', None)
	language_foreign = request.GET.get('language_foreign', None)
	print('language_foreign')
	print(language_foreign)
	section = request.GET.get('section', None)
	#username = request.POST['username']
	#password = request.POST['password']
	POST = {'username': username, 'password': password}
	f = AuthenticationForm(data=POST)
	print(username)
	print('before authenticated')
	user = authenticate(request, username=username, password=password)
	print('hello')
	if user is not None:
		print('hello_userisnotnone')
		login_user(request, user)
		langs = Book.objects.order_by('language').distinct('language').values_list('language',flat=True)
		if 'reader' in request.META['HTTP_REFERER']:
			print(book_name)	
			add_book_from_login(request)
			return JsonResponse({'move':'yes', 'url':reverse('reader', kwargs={'user_name':username, 'language_native':language_native, 'language_foreign':language_foreign, 'book_name':book_name, 'section':'0'})})
		return JsonResponse({'move':'yes', 'url':reverse('language_form', kwargs={'user_name':username, 'language_native':'all', 'language_foreign':'all', 'book_name':request.GET.get('b_name')})})
	else:
		temp = f.is_valid()
		context = {'move':'no', 'error_messages':'Please enter a correct username and password. Note that both fields may be case-sensitive.'}
		print(f.errors)
		return JsonResponse(context)

def signup(request):
	username = request.GET.get('username', None)
	password1 = request.GET.get('password1', None)
	password2 = request.GET.get('password2', None)
	email = request.GET.get('email', None)
	book_name = request.GET.get('b_name', None)
	language_native = request.GET.get('language_native', None)
	language_foreign = request.GET.get('language_foreign', None)
	section = request.GET.get('section', None)
	POST = {'username':username, 'password1':password1, 'password2':password2, 'email':email}
	f = SignUpForm(data=POST)
	if f.is_valid():
		f.save()
		username=f.cleaned_data.get('username')
		raw_password = f.cleaned_data.get('password1')
		user = authenticate(username=username, password=raw_password)
		login_user(request, user)
		if 'reader' in request.META['HTTP_REFERER']:
			add_book_from_login(request)
			return JsonResponse({'move':'yes', 'url':reverse('reader', kwargs={'user_name':username, 'language_native':language_native, 'language_foreign':language_foreign, 'book_name':book_name, 'section':'0'})})
		return JsonResponse({'move':'yes', 'url':reverse('language_form', kwargs={'user_name':username, 'language_native':'all', 'language_foreign':'all', 'book_name':request.GET.get('b_name'),})})
	else:
		msg = []
		for e in f.errors:
			m = f.errors[e][0]
			if m=='This field is required.':
				m = 'All fields are required.'
			if m not in msg:
				msg.append(m)
		context = {'move':'no', 'error_messages':msg}
		return JsonResponse(context)
	#if request.method == 'POST':
	#	form = SignUpForm(request.POST)
	#	if form.is_valid():
	#		print('form valid')
	#		form.save()
	#	else:
	#		print(form.errors)
	#		print('form invalid')
	#		return render(request, 'signup.html', {'form': SignUpForm(), 'old_form':form})
	#	username = form.cleaned_data.get('username')
	#	raw_password = form.cleaned_data.get('password1')
	#	print(request.POST)
	#	user = authenticate(username=username, password=raw_password)
	#	login_user(request, user)
	#	return HttpResponseRedirect(reverse('language_form', kwargs={'user_name':request.user.username, 'language_native':'all', 'language_foreign':'all', 'book_name':'0',}))
	#else:
	#	form = SignUpForm()
	#return render(request, 'signup.html', {'form': form})

def index(request):
	print('index hello')
	print(request)
	print(request.META)
	if request.user.is_authenticated:
		langs = Book.objects.order_by('language').distinct('language').values_list('language',flat=True) 
		#return render(request, 'index.html', {'form': LanguageForm(), 'languages':langs, 'username':request.user.username})
		print('authenticated')
		return HttpResponseRedirect(reverse('language_form', kwargs={'user_name':request.user.username, 'language_native':'all', 'language_foreign':'all', 'book_name':'0',}))
	else:
		print('index not authenticated')
		return HttpResponseRedirect(reverse('language_form', kwargs={'user_name':'AnonymousUser', 'language_native':'all', 'language_foreign':'all', 'book_name':'0',}))	
		return HttpResponseRedirect(reverse('login'))

class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return index(request)

class ContactMeView(TemplateView):
	template_name='contact.html'

class AboutPageView(TemplateView):
	template_name= "about.html"

def get_alignment(b, a, section, sectioned):
	book_object = b
	sentences_native = Sentence.objects.filter(book=book_object, section=section).order_by('index')
	if sectioned==0:
		sentences_native = Sentence.objects.filter(book=book_object, section=0).order_by('index')
	offset_native = sentences_native[0].index
	book_object = a
	sentences_foreign = Sentence.objects.filter(book=book_object, section=section).order_by('index')
	if sectioned==0:
		sentences_foreign = Sentence.objects.filter(book=book_object, section=0).order_by('index')
	sens_native = []
	sens_foreign = []
	print('getting alignment')
	for s in sentences_native:
		sens_native.append(s.text)
	for s in sentences_foreign:
		sens_foreign.append(s.text)
	pairings = gale_church.main(sens_foreign, sens_native, 'gacha')
	mappings = []
	sen_ind = 1
	for p in pairings:
		nat_for = p.split('\t')
		nat = nat_for[0]
		frn = nat_for[1]
		pairs_nat = nat.split('~~')
		pairs_frn = frn.split('~~')
		if len(pairs_nat)==1:
			tupl = []
			for pa in range(len(pairs_frn)):
				tupl.append(sen_ind+offset_native-1)
				sen_ind = sen_ind + 1
			mappings.append(tupl)
		else:
			for pa in range(len(pairs_nat)):
				mappings.append([sen_ind+offset_native-1])
			sen_ind = sen_ind + 1
	print(mappings)
	return mappings

def make_html_native(b, section, sectioned):
	if not type(b) is dict:
		book_object = Book.objects.filter(language=b.native, book_name=b.sentence.book.book_name)
	if type(b) is dict:
		book_object = Book.objects.filter(language=b['language'], book_name=b['book_name'])
	sentences = Sentence.objects.filter(book=book_object, section=section).order_by('index')
	if sectioned==0:
		sentences = Sentence.objects.filter(book=book_object, section=0).order_by('index')
	old_par = 0
	html_string = ''
	for s in range(len(sentences)):
		sen = sentences[s]
		new_par = sen.paragraph
		if new_par!=old_par:
			html_string = html_string + '<p>'
		html_string = html_string + '<span id=\"' + sen.html_id + '\">' + sen.text + ' ' + '</span>'
		old_par=new_par
	return html_string

def make_html_foreign(request, a, section, sectioned):
	if not type(a) is dict:
		sen_objects = Sentence.objects.filter(book=a.sentence.book)
	else:
		sen_objects = Sentence.objects.filter(book__book_name=a['book_name'], book__language=a['language'])
	sentences_before = 0
	if sen_objects[0].section == '0':
		sentences_before=0
	else:
		for sen_obj in sen_objects:
			chap = int(sen_obj.section)
			if chap < int(section):
				print('chap_before')
				sentences_before = sentences_before + 1
	if not type(a) is dict:
		book_object = a.sentence.book
	else:
		book_object = Book.objects.filter(book_name=a['book_name'], language=a['language'])
	sentences = Sentence.objects.filter(book=book_object, section=section).order_by('index')
	if sectioned==0:
		sentences = Sentence.objects.filter(book=book_object, section=0).order_by('index')
	old_par = 0
	html_string = ''
	for s in range(len(sentences)):
		sen = sentences[s]
		print(sen.text)
		new_par = sen.paragraph
		if new_par!=old_par:
			html_string = html_string + '<p>'
		if not type(a) is dict:
			blank = a.missing_words[sen.index-1]
		else:
			blank = a['missing_words'][sen.index-1]
		sen_text = sen.text
		if blank=='':
			html_string = html_string + '<span id=\"' + sen.html_id + '\">' + sen_text + '</span>'
			old_par=new_par
			if not type(a) is dict:
				if int(a.sentence_chapters[int(section)-1])==int(sen.index):
					a.sentence_chapters[int(section)-1] = a.sentence_chapters[int(section)-1]+1
					if a.sentence.index==int(sen.index):
						a.sentence = Sentence.objects.get(index=a.sentence_chapters[int(section)-1]+1, book__language=a.sentence.book.language, book__book_name=a.sentence.book.book_name)
					a.save()
				continue
			else:
				if int(a['sentence_chapters'][int(section)-1])==int(sen.index):
					request.session['sentence_chapters'][int(section)-1] = request.session['sentence_chapters'][int(section)-1]+1
					request.session['sentence_on'] = request.session['sentence_on']+1
				continue
		if not type(a) is dict:
			s_on = int(a.sentence_chapters[int(section)-1])
		else:
			s_on = int(a['sentence_chapters'][int(section)-1])
		print(s_on)
		print(s_on)
		print(blank)
		print(sen_text)
		words = sen_text.split()
		print(words)
		if a.sentence.book.language=='Chinese' or a.sentence.book.language=='Japanese' or a.sentence.book.language=='Korean':
			words = list(sen_text)
		words_temp = []
		for w in words:
			print(remove_punctuation(w))
			words_temp.append(remove_punctuation(w))
		blank_index = words_temp.index(blank)
		blank = words[blank_index]
		addition = ''
		if not blank[-1].isalpha():
			addition = blank[-1]
		if s_on>int(sen.index):
			insert = '<span style=\"color:#32CD32\">' + remove_punctuation(blank) + '</span><span>'+addition+'</span>'
		if s_on==int(sen.index):
			insert = '<label><input type=\'text\' style=\'width:' + str(16+6*len(blank)) + 'px\' id=\'nameInput\' onchange=\'letterpress()\' autofocus></label>'
			if not blank[-1].isalpha() or not blank[0].isalpha():
				insert = get_punc_begin(blank) + insert + get_punc_end(blank)
		if s_on<int(sen.index):
			insert = '_'*len(blank)
			if not blank[-1].isalpha() or not blank[0].isalpha():
				insert = get_punc_begin(blank) + insert + get_punc_end(blank)
		if not type(a) is dict:
			if a.completed==True:
				if s_on==int(sen.index):
					insert = '<span style=\"color:#32CD32\">' + remove_punctuation(blank) + addition + '</span>'
		html_string = html_string + '<span id=\'' + sen.html_id + '\'>'
		words[blank_index]=insert
		for w in range(len(words)):
			if a.sentence.book.language=='Chinese' or a.sentence.book.language=='Japanese' or a.sentence.book.language=='Korean':
				html_string = html_string + words[w]
			else:
				html_string = html_string + words[w] + ' '
		html_string = html_string + '</span>'
		old_par=new_par
	return html_string

def get_common_words(book):
	sentences = Sentence.objects.filter(book=book).order_by('index')
	common_dict = {}
	for s in range(len(sentences)):
		sen = sentences[s]
		words = sen.text.split()
		for w in words:
			if w in common_dict:
				common_dict[w] = common_dict[w]+1
			else:
				common_dict[w] = 1
	d = sorted(common_dict.items(), key=lambda x:x[1])
	common_words = []
	for k in range(20):
		common_words.append(d[-k][0])
	print(common_words)
	return common_words

def get_missing_words(book):
	common_words = get_common_words(book)
	sentences = Sentence.objects.filter(book=book).order_by('index')
	gone_words = []
	for s in range(len(sentences)):
		sen = sentences[s]
		if len(split_into_sentences(sen.text))==0:
			gone_words.append('')
			continue
		words = sen.text.split()
		if book.language == 'Chinese' or book.language=='Japanese' or book.language=='Korean':
			words = list(sen.text)
		not_valid=True
		counter = 0
		while(not_valid):
			counter = counter + 1
			if counter>1000:
				gone_words.append('')
				word = ''
				break
			word = random.choice(words)
			if (is_valid_word(word, common_words)):
				not_valid = False
		if word=='':
			continue
		word = remove_punctuation(word)
		if(len(word)>20):
			print(word)
		gone_words.append(word)
	print(gone_words)
	return gone_words
		
def is_valid_word(word, common_words):
	if word=='':
		return(False)
	if word==' ':
		return(False)
	if len(word)>20:
		return(False)
	if word in common_words:
		return(False)
	for letter in range(len(word)):
		if letter > 0 and letter < len(word)-1:
			if word[letter-1].isalpha() and not word[letter].isalpha() and word[letter+1].isalpha():
				return(False)
	for letter in word:
		if letter.isalpha():
			return(True)
	return(False)

@never_cache
def reader(request, section, user_name, book_name, language_native, language_foreign):
	next_sec = ''
	next_book = ''
	book_name = re.sub("&#39;", "'", book_name)
	book_name = get_full_book_name(book_name)
	user_name = request.user.username
	if user_name == '':
		user_name = 'AnonymousUser'
	print('reader is happening')
	print(user_name)
	print(book_name)
	if request.user.is_authenticated():
		user_profile = Profile.objects.get(user__username=user_name)
		book_instances = Book_Instance.objects.filter(sentence__book__book_name=book_name, native=language_native, sentence__book__language=language_foreign, profile=user_profile)
		latest_iter = 0
		if section=='1111111111': #and 'reader' in request.META['HTTP_REFERER']:
			print('referred')
			return addBookFromView(request, section, user_name, book_name, language_native, language_foreign)
		book_instances = Book_Instance.objects.filter(sentence__book__book_name=book_name, native=language_native, sentence__book__language=language_foreign, profile=user_profile)
		if len(book_instances)>0:
			latest_iter = 1
			for bo in book_instances:
				inst = bo.iteration
				if inst > latest_iter:
					latest_iter = inst
	b_new = Book.objects.get(book_name=book_name, language=language_foreign)
	if len(b_new.collection) > 1:	
		print('debug')
		books_in_col = Book.objects.filter(collection=b_new.collection, language=language_foreign)
		b_names = []
		b_orders = []
		for b in books_in_col:
			b_names.append(b.book_name)
			b_orders.append(b.order)
		b_names = [x for _,x in sorted(zip(b_orders,b_names))]
		cur_book = b_names.index(book_name)
		next_book = ''
		if cur_book != len(b_names)-1:
			next_book = b_names[cur_book+1]
			conts = Book_Instance.objects.filter(sentence__book__book_name=next_book, native=language_native, sentence__book__language=language_foreign, profile__user__username=user_name, completed=False)
			if len(conts)>0:
				next_sec = conts[0].sentence.section
			else:
				next_sec = '1111111111'
	if request.user.is_authenticated():
		new_book = Book_Instance.objects.get(sentence__book__book_name=book_name, native=language_native, sentence__book__language=language_foreign, profile=user_profile, iteration=latest_iter)
		print(section)
		print(latest_iter)
		print(new_book.sentence.index)
		if section=='1111111111' or section=='0':
			section = new_book.sentence.section
		iter = latest_iter
	else:
		iter = 1
		if section=='1111111111' or section=='0':
			section = '1'
	book_subset = Sentence.objects.filter(book__book_name=book_name, book__language=language_foreign)
	num_sections = book_subset.order_by('section').values('section').distinct().count()
	if num_sections==1:
		sectioned = 0	
	else:
		sectioned=1
	pagins = pagination(section, num_sections)
	print(pagins)
	with open('static/stories.csv', 'rt', encoding='utf8') as f:
		reader = csv.reader(f)
		titles = list(reader)
		languages = titles[1]
	column_for = languages.index(language_foreign)
	column_nat = languages.index(language_native)
	for t in titles:
		if remove_punc_all(re.sub(re.escape("*comma*"), ",", t[0]).strip()) == remove_punc_all("_".join(book_name.split()).strip()):
			foreign_title = re.sub("_", " ", t[column_for])
			native_title = re.sub("_", " ", t[column_nat])
			foreign_title = re.sub(re.escape("*comma*"), ",", foreign_title)
			native_title = re.sub(re.escape("*comma*"), ",", native_title)
	if request.user.is_authenticated():
		nat_html = make_html_native(new_book, section, sectioned)
		for_html = make_html_foreign(request, new_book, section, sectioned)
		sentences_native = Sentence.objects.filter(book=b_new, section=section).order_by('index')
		offset_native = sentences_native[0].index
		sentence_on = new_book.sentence_chapters[int(section)-1]
		offset = sentence_on - offset_native + 1
		if user_profile.helper == 'on':
			highlight = 'on'
		else:
			highlight = 'off'
		if new_book.sentence_chapters[int(section)-1]-1 >= len(new_book.missing_words):
			cur_word = ''
		else:
			cur_word = new_book.missing_words[new_book.sentence_chapters[int(section)-1]-1]
		second_id = new_book.sentence.book.language[0:3]+str(new_book.sentence_chapters[int(section)-1])
	else:
		request.session['sentence_on'] = 1
		d_nat = {'language':language_native, 'book_name':book_name}
		nat_html = make_html_native(d_nat, section, sectioned)
		missing_words = get_missing_words(b_new)
		sen_objects = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign)
		num_sections = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign).order_by('section').values('section').distinct().count()
		chapter_starts = [0]*num_sections
		if sen_objects[0].section != 0:
			for n in range(num_sections):
				sens = Sentence.objects.filter(book__book_name=book_name, book__language=language_foreign, section=n+1).order_by('index')
				chapter_starts[n]=sens[0].index
		if sen_objects[0].section == 0:
			chapter_starts = [1]
		sentence_chapters = chapter_starts
		request.session['sentence_chapters']=sentence_chapters
		d_for = {'language':language_foreign, 'book_name':book_name, 'missing_words':missing_words, 'sentence_chapters':sentence_chapters}
		for_html = make_html_foreign(request, d_for, section, sectioned)
		sentences_native = Sentence.objects.filter(book=b_new, section=section).order_by('index')
		if len(sentences_native)==0:
			sentences_native = Sentence.objects.filter(book=b_new, section=0).order_by('index')
		offset_native = sentences_native[0].index
		sentence_on = request.session['sentence_on']
		offset = sentence_on - offset_native + 1
		sentence_on = sentence_on + offset_native - 1
		request.session['sentence_on']=sentence_on
		request.session['highlight']='off'
		request.session['missing_words']=missing_words
		cur_word = missing_words[sentence_on-1]
		highlight = 'off'
		second_id = b_new.language[0:3]+str(sentence_chapters[int(section)-1])
	print('cur_word')
	print(cur_word)
	authed = request.user.is_authenticated()
	#if book_name[0]=='"':
	#	b_name = "'" + book_name[1:len(book_name)+1]
	#if book_name[len(book_name)-1]=='"':
	#	b_name = book_name[0:len(book_name)-1] + "'"
	#print(b_name)
	context = {
		'login_form': AuthenticationForm(),
		'signup_form': SignUpForm(),
		'authed': authed,
		'next_sec': next_sec,
                'next_book': next_book,
		'highlight': highlight,
		'second_id': second_id,
		'collection': b_new.collection,
		'user_name': user_name,
                'lang_foreign': language_foreign,
                'lang_native': language_native,
		'text_native': nat_html,
		'text_foreign': for_html,
		'book_name': re.sub('"', '&#39;', b_new.book_name),
                'section_names': b_new.section_name,
		'section_count': num_sections,
                'section_on': section,
		'iteration': iter,
		'before': pagins[0],
		'result': pagins[1],
		'after': pagins[2],
		'current_word': cur_word,
		'mappings': get_alignment(Book.objects.get(book_name=book_name, language=language_native), Book.objects.get(book_name=book_name, language=language_foreign), section, sectioned),
		'foreign_title': foreign_title,
		'native_title': native_title,
		'second_index': offset,
	}
	return render(request, 'reader.html', context)

@never_cache
def renderWord(request):
	entered = request.GET.get('entered', None)
	section = int(request.GET.get('section', None))
	print(request.GET.get('book_name'))
	book_name = re.sub("&#39;", '"', re.sub("&quot;", "\"", request.GET.get('book_name', None)))
	#book_name = re.sub("&#39;", "'", re.sub("&quot;", "\"", request.GET.get('book_name', None)))
	#book_name = re.sub("'", '"', book_name)
	print(book_name)
	language_native = request.GET.get('language_native', None)
	language_foreign = request.GET.get('language_foreign', None)
	latest_index = request.GET.get('latest_index', None)
	if request.user.is_authenticated():
		user_name = request.user.username
		user_profile = Profile.objects.get(user__username=user_name)
		b_inst = Book_Instance.objects.get(profile__user__username=user_name, native=language_native, sentence__book__language=language_foreign, sentence__book__book_name=book_name, iteration=int(latest_index))
		sen_on = b_inst.sentence_chapters[section-1]
		wanted = b_inst.missing_words[sen_on-1]
	else:
		b_inst = {}
		sen_on = request.session['sentence_on']
		wanted = request.session['missing_words'][sen_on-1]
	new_text = ''
	print(wanted)
	for w in range(len(entered)):
		print(w)
		if entered[w].lower()==wanted[w].lower():
			new_text = new_text + entered[w]
		else:
			break
	print(new_text)
	correct = False
	if entered.lower()==wanted.lower():
		correct = True
	data = {
		'text': new_text,
		'is_correct': correct 
	}
	if correct:
		return updateWord(request, b_inst, section)
	if not correct:
		return JsonResponse(data)
@never_cache
def updateWord(request, b_inst, section):
	comp = ''
	if request.user.is_authenticated():
		chaps = b_inst.sentence_chapters
		bk = b_inst.sentence.book
		sen_on = b_inst.sentence_chapters[section-1]
		next_exists = Sentence.objects.filter(index=b_inst.sentence.index+1, book = bk).count()
	else:
		chaps = request.session['sentence_chapters']
		bk = Book.objects.get(language=request.GET.get('language_foreign', None), book_name=re.sub("&#39;", "'", re.sub("&quot;", "\"", request.GET.get('book_name', None))))
		sen_on = request.session['sentence_on']
		next_exists = Sentence.objects.filter(index=sen_on+1, book=bk).count()
	sen_big = 0
	for c in range(len(chaps)):
		total_sen = Sentence.objects.filter(book=bk, section=chaps[c]).count()
		if chaps[c]<=total_sen:
			sen_big = chaps[c]
			break
	completed_var=False
	if not next_exists:
		if request.user.is_authenticated():
			b_inst.completed=True
			b_inst.save()
			curr_word = ''
			prev_word = b_inst.missing_words[b_inst.sentence.index-1]
			sen = b_inst.sentence.index
			sen_old = b_inst.sentence
			counter=0
			sen_two = sen_old
		else:
			completed_var=True
			curr_word = ''
			prev_word = request.session['missing_words'][sen_on-1]
			sen = sen_on
			sen_old = Sentence.objects.get(book=bk, index=sen_on)
			counter=0
			sen_two=sen_old
	if next_exists and request.user.is_authenticated():
		sen = sen_on
		sen_old = Sentence.objects.get(index=sen_on,book=Book.objects.get(book_name=b_inst.sentence.book.book_name, language=b_inst.sentence.book.language))
		next_sen = False
		counter = 1
		while(not next_sen):
			next_exists = Sentence.objects.filter(index=b_inst.sentence_chapters[int(section)-1]+1, book=b_inst.sentence.book, section=section).count()
			if not next_exists:
				print('handle chapter')
				print(sen_on)
				return handle_chapter_end(request, b_inst, section)
				next_sen = True
			elif len(b_inst.missing_words)==(sen) and sen==sen_big:
				print('first')
				b_inst.completed=True
				b_inst.save()
				curr_word = ''
				prev_word = b_inst.missing_words[b_inst.sentence.index-1]
			elif len(b_inst.missing_words[sen+counter-1])>0:
				print('second')
				sen_two = Sentence.objects.get(index=sen+counter, book=Book.objects.get(book_name=b_inst.sentence.book.book_name, language=b_inst.sentence.book.language))
				b_inst.sentence_chapters[section-1] = sen_two.index
				if b_inst.sentence.index == sen_on:
					b_inst.sentence = sen_two
				b_inst.save()
				next_sen = True
			else:
				counter = counter+1
		curr_word = b_inst.missing_words[b_inst.sentence.index-1]
		prev_word = b_inst.missing_words[b_inst.sentence.index-counter-1]
	if next_exists and not request.user.is_authenticated():
		sen = sen_on
		sen_old = Sentence.objects.get(index=sen_on,book=bk)
		next_sen = False
		counter = 1
		while(not next_sen):
			print(sen_on+1)
			print(bk)
			print(section)
			next_exists = Sentence.objects.filter(index=sen_on+1, book=bk).count()
			if not next_exists:
				return handle_chapter_end(request, bk, section)
				next_sen = True
			elif len(request.session['missing_words'])==(sen) and sen==sen_big:
				curr_word = ''
				prev_word = request.session['missing_words'][sen_on-1]
			elif len(request.session['missing_words'][sen+counter-1])>0:
				sen_two = Sentence.objects.get(index=sen+counter, book=bk)
				request.session['sentence_chapters'][section-1] = sen_two.index
				request.session['sentence_on'] = sen_two.index
				next_sen = True
			else:
				counter = counter+1
		curr_word = request.session['missing_words'][request.session['sentence_on']-1]
		prev_word = request.session['missing_words'][request.session['sentence_on']-counter-1]
	if request.user.is_authenticated():
		blank_one = b_inst.missing_words[sen-1]
		blank_two = b_inst.missing_words[sen+counter-1]
	else:
		blank_one = request.session['missing_words'][sen-1]
		blank_two = request.session['missing_words'][sen+counter-1]
	sen_text_one = sen_old.text
	sen_text_two = sen_two.text
	words_one = sen_text_one.split()
	words_two = sen_text_two.split()
	if b_inst.sentence.book.language == 'Chinese' or b_inst.sentence.book.language=='Japanese' or b_inst.sentence.book.language=='Korean':
		words_one = list(sen_text_one)
		words_two = list(sen_text_two)
	words_one_temp=[]
	words_two_temp=[]
	for w in words_one:
		words_one_temp.append(remove_punctuation(w))
	for w in words_two:
		words_two_temp.append(remove_punctuation(w))
	blank_index_one = words_one_temp.index(blank_one)
	blank_index_two = words_two_temp.index(blank_two)
	blank_one = words_one[blank_index_one]
	blank_two = words_two[blank_index_two]
	insert_two = '<label><input type=\'text\' style=\'width:' + str(16+6*len(blank_two)) + 'px\' id=\'nameInput\' onkeyup=\'letterpress()\' autofocus></label>'
	insert_one = '<span style=\"color:#32CD32\">' + remove_punctuation(blank_one) + '</span>'
	print(blank_one)
	print(blank_two)
	if not blank_one[-1].isalpha() or not blank_one[0].isalpha():
		print('hi blankone')
		insert_one = get_punc_begin(blank_one) + insert_one + get_punc_end(blank_one)
		print(insert_one)
	if not blank_two[-1].isalpha() or not blank_two[0].isalpha():
		print('hi blanktwo')
		insert_two = get_punc_begin(blank_two) + insert_two + get_punc_end(blank_two)
		print(insert_two)
	words_one[blank_index_one]=insert_one
	words_two[blank_index_two]=insert_two
	html_one = ''
	for w in range(len(words_one)):
		html_one = html_one + words_one[w] + ' '
	html_two = ''
	for w in range(len(words_two)):
		html_two = html_two + words_two[w] + ' '
	if request.user.is_authenticated():
		completed_var = b_inst.completed
		sentences_native = Sentence.objects.filter(book=b_inst.sentence.book, section=section).order_by('index')
		offset_native = sentences_native[0].index
		offset = sen_two.index - offset_native + 1
		highlight = 'off'
		if b_inst.profile.helper == 'on':
			highlight = 'on'
		first_id = b_inst.sentence.book.language[0:3]+str(b_inst.sentence_chapters[section-1]-counter)
		second_id = b_inst.sentence.book.language[0:3]+str(b_inst.sentence_chapters[section-1])
	else:
		if section==1 and len(chaps)==1:
			section = 0
		sentences_native = Sentence.objects.filter(book=bk, section=section).order_by('index')
		offset_native = sentences_native[0].index
		offset = sen_two.index - offset_native + 1
		highlight = request.session['highlight']
		first_id = bk.language[0:3] + str(request.session['sentence_chapters'][section-1]-counter)
		second_id = bk.language[0:3] + str(request.session['sentence_chapters'][section-1])
	output_data = {
		'highlight': highlight,
		'is_correct': True,
		'current_word': remove_punctuation(blank_two),
		'prev_word': blank_one,
		'first_id': first_id,
		'second_id': second_id,
		'first_content': html_one,
		'second_content': html_two,
		'second_index':offset,
	}
	if completed_var==True:
		output_data = {
			'is_correct': True,
			'current_word': blank_one,
			'prev_word': blank_one,
			'first_id': first_id,
			'second_id': second_id,
			'first_content':html_one,
			'second_content':html_one,
			'second_index':offset,
		}
	return JsonResponse(output_data)

def handle_chapter_end(request, b_inst, section):
	print('arrived')
	if not request.user.is_authenticated():
		print('not')	
		bk = b_inst
		sen_on = request.sessions['sentence_on']
		index = int(sen_on)-1
		prev_word = request.sessions['missing_words'][index]
		request.sessions['sentence_chapters'][section-1] = request.sessions['sentence_chapters'][section-1]+1
		blank_one = prev_word
		sen_text_one = Sentence.objects.get(index=sen_on,book=bk, language=bk.language).text
		words_one = sen_text_one.split()
		words_one_temp = []
		for w in words_one:
			words_one_temp.append(remove_punctuation(w))
		blank_index_one = words_one_temp.index(blank_one)
		blank_one = words_one[blank_index_one]
		insert_one = '<span style=\"color:#32CD32\">' + remove_punctuation(blank_one) + '</span>'
		if not blank_one[-1].isalpha() or not blank_one[0].isalpha():
			insert_one = get_punc_begin(blank_one) + insert_one + get_punc_end(blank_one)
		words_one[blank_index_one]=insert_one
		html_one = ''
		for w in range(len(words_one)):
			html_one = html_one + words_one[w] + ' '
		output_data = {
			'is_correct': True,
			'current_word': '',
			'prev_word': blank_one,
			'first_id': bk.language[0:3]+str(sen_on),
			'second_id': '',
			'first_content':html_one,
			'second_content':'',
			'second_index':'',
			}
		return JsonResponse(output_data)
	sen_on = b_inst.sentence_chapters[section-1]
	index = (int(sen_on)-1)
	prev_word = b_inst.missing_words[index]
	b_inst.sentence_chapters[section-1] = b_inst.sentence_chapters[section-1]+1
	if b_inst.sentence.index == sen_on:
		next_found = False
		chap = section+1
		print(chap)
		#b_inst.sentence = b_inst.sentence_chapters[section]
		#while not next_found:
			#next_index = b_inst.sentence_chapters[section]
			#total_sen = Sentence.objects.filter(book=b_inst.sentence.book, section=chap).count()
			#print(next_index)
			#print(total_sen)
			#if next_index<=total_sen:
			#	position = next_index
			#	next_found = True
			#else:
			#	chap = chap + 1
		b_inst.sentence = Sentence.objects.get(index=b_inst.sentence_chapters[section], book=b_inst.sentence.book, book__language=b_inst.sentence.book.language)
	b_inst.save()
	print(sen_on)
	blank_one = b_inst.missing_words[int(sen_on)-1]
	sen_text_one = Sentence.objects.get(index=sen_on,book=Book.objects.get(book_name=b_inst.sentence.book.book_name, language=b_inst.sentence.book.language)).text
	words_one = sen_text_one.split()
	words_one_temp = []
	for w in words_one:
		words_one_temp.append(remove_punctuation(w))
	blank_index_one = words_one_temp.index(blank_one)
	blank_one = words_one[blank_index_one]
	insert_one = '<span style=\"color:#32CD32\">' + remove_punctuation(blank_one) + '</span>'
	if not blank_one[-1].isalpha() or not blank_one[0].isalpha():
		insert_one = get_punc_begin(blank_one) + insert_one + get_punc_end(blank_one)
	words_one[blank_index_one]=insert_one
	html_one = ''
	for w in range(len(words_one)):
		html_one = html_one + words_one[w] + ' '
	print(blank_one)
	print(html_one)
	print(b_inst.sentence.book.language[0:3]+str(b_inst.sentence_chapters[section-1]))
	output_data = {
		'is_correct': True,
		'current_word': '',
		'prev_word': blank_one,
		'first_id': b_inst.sentence.book.language[0:3]+str(b_inst.sentence_chapters[section-1]-1),
		'second_id': '',
		'first_content':html_one,
		'second_content':'',
		'second_index':'',
		}
	return JsonResponse(output_data)
		

@never_cache
def col_library(request, user_name, language_native, language_foreign, book_name):
	if request.user.is_authenticated():
		user_name = request.user.username
	else:
		user_name = 'AnonymousUser'
	print(book_name)
	book_name = re.sub("&#39;", "'", book_name)
	book_name = get_full_book_name(book_name)
	print(book_name)
	#prof = User.objects.get(username=user_name)
	books_native_subset = Book.objects.filter(language=language_native, collection=book_name)
	books_native = []
	for b in books_native_subset:
		books_native.append(b.book_name)
	books_foreign_subset = Book.objects.filter(language=language_foreign, collection=book_name)
	books_foreign = []
	for b in books_foreign_subset:
		books_foreign.append(b.book_name)
		category = b.book_name
	print('filtered')
	books_both = set.intersection(set(books_native),set(books_foreign))
	if language_native == 'all':
		books_both = set(books_foreign)
	if language_foreign =='all':
		books_both = set(books_native)
	books_names_both = []
	if language_native=='all' and language_foreign=='all':
		print('language is all')
		books_subset = Book.objects.filter(collection=book_name)
		for b in books_subset:
			book = Book.objects.filter(book_name=b.book_name)[0]
			if not book.book_name in books_names_both:
				books_names_both.append(book.book_name)
	else:
		books_names_both = books_both
	book_orders = []
	for b in list(books_names_both):
		book_orders.append(Book.objects.filter(book_name=b)[0].order)
	books_both_orders = book_orders
	print('intersection')
	conts = Book_Instance.objects.filter(profile__user__username=user_name, completed=False, native=language_native, sentence__book__language=language_foreign, sentence__book__collection=book_name)
	print('conts')
	book_names = []
	book_orders = []
	for cont in conts:
		b_name = cont.sentence.book.book_name
		if b_name not in book_names:
			book_orders.append(cont.sentence.book.order)
			book_names.append(b_name)
	conts_again = Book_Instance.objects.filter(profile__user__username=user_name, completed=True, native=language_native, sentence__book__language=language_foreign, sentence__book__collection=book_name)
	conts = book_names
	conts_orders = book_orders
	conts.sort()
	book_names = []
	book_orders = []
	for cont in conts_again:
		b_name = cont.sentence.book.book_name
		if b_name not in book_names:
			book_orders.append(cont.sentence.book.order)
			book_names.append(b_name)
	conts_again = book_names
	conts_again_orders = book_orders
	new_books_html = ''
	conts_html = ''
	conts_again_html = ''
	conts = [x for _,x in sorted(zip(conts_orders,conts))]
	conts_again = [x for _,x in sorted(zip(conts_again_orders,conts_again))]
	books_names_both = [x for _,x in sorted(zip(books_both_orders,books_names_both))]
	new_books_names = list(books_names_both)
	if len(new_books_names)>0:
		author = Book.objects.filter(collection = book_name)[0].author
	col_n = ''
	for c in range(len(conts)):
		completed = 'not_done'
		conts_html = conts_html + '<div class=\"book_div\" id=\"' + remove_punc_all(conts[c]) + '\"><div class=\"inner_book_div\"><a href=\"/' + user_name + '/' + language_native + '/' + language_foreign + '/' + re.sub("'", "&#39;", re.sub('"',"&#34;",conts[c])) + '/0/reader/\" id=\'a_id\'><img id=\'book_image\' src=\'/static/images/' + re.sub("'","&#39;",re.sub(" ", "", "_".join(conts[c].strip().split()))) + '.jpg\'> <div class=\'close_icon\' onclick=\"removeBook(\'' + re.sub("'","*apos*",re.sub("\"", "*q*", conts[c])) + '\'); return false\"><img src=\'/static/icons/close_icon.png\'/></div><div class=\'banner ' + completed + '\'><img src=\'/static/icons/banner.png\'></img></div><div class=\'col_overlay\'></div><div class=\'circle not_col\'><span class=\'not_col\' id=\'col_num\'>'+col_n+'</span></div></a></div>'
		conts_html = conts_html + '<p> ' + re.sub("'", '&#39;', conts[c]) + '</p> <p> ' + author + '</p>'
		languages_html = ''
		this_langs = Book.objects.filter(book_name=conts[c]).order_by('language').distinct('language').values_list('language',flat=True)
		for l in this_langs:
			languages_html = languages_html + '<p>' + l + '</p>'
		conts_html = conts_html + '<p style=\'overflow:visible;\'><span>Available in: <img class=\'lang_icon\' onclick=\"showlanguages(this, \'' + languages_html  + '\')\" src=\'/static/icons/info.png\' /></span></p></div>'
	for c in range(len(new_books_names)):
		completed = 'not_done'
		sec = '0'
		if new_books_names[c] in conts_again:
			completed = ''
		if new_books_names[c] not in conts and new_books_names[c] not in conts_again:
			sec = '1111111111'
		new_books_html = new_books_html + '<div class=\"book_div\" id=\"new' + remove_punc_all(new_books_names[c])+  '\"><div class=\"inner_book_div\"><a href=\"/' + user_name + '/' + language_native + '/' + language_foreign + '/' + re.sub("'", "&#39;",re.sub('"',"&#34;",new_books_names[c])) + '/' + sec + '/reader/\" id=\'a_id\'><img id=\'book_image\' src=\'/static/images/' + re.sub("'","&#39;",re.sub(" ", "", "_".join(new_books_names[c].strip().split()))) + '.jpg\' /><div class=\'banner ' + completed + '\'><img src=\'/static/icons/banner.png\'></img></div><div class=\'col_overlay\'></div><div class=\'circle not_col\'><span class=\'not_col\' id=\'col_num\'>'+col_n+'</span></div></a></div>'

		new_books_html = new_books_html + '<p> ' + re.sub("'", '&#39;', new_books_names[c]) + '</p> <p> ' + author + '</p>'
		languages_html = ''
		this_langs = Book.objects.filter(book_name=new_books_names[c]).order_by('language').distinct('language').values_list('language',flat=True)
		for l in this_langs:
			languages_html = languages_html + '<p>' + l + '</p>'
		new_books_html = new_books_html + '<p style=\'overflow:visible;\'><span>Available in: <img class=\'lang_icon\' onclick=\"showlanguages(this, \'' + languages_html  + '\')\" src=\'/static/icons/info.png\' /></span></p></div>'
	print('done')
	context = {
		'login_form': AuthenticationForm(),
		'signup_form': SignUpForm(),
		'form': LanguageForm(),
		'book_name': book_name,
		'conts_html': conts_html,
		'conts_again_html': conts_again_html,
		'new_books_html': new_books_html,
		'prof_name': user_name,
		'language_native': language_native,
		'language_foreign': language_foreign,
		}
	return render(request, 'col_library.html', context)     

@never_cache
def text_library(request, user_name, language_native, language_foreign):
	if request.user.is_authenticated():
		user_name = request.user.username
	else:
		user_name = 'AnonymousUser'
	#if request.user.is_authenticated():
	#	prof = User.objects.get(username=user_name)
	#else:
	#form = LanguageForm(request.POST)
	#if form.is_valid():
	#	print('form is valid')
	#	language_native = form.cleaned_data.get('lang_native')
	#	language_foreign = form.cleaned_data.get('lang_foreign')
	#	print(language_native)
	#else:
	#	print('not valid')
	#	return render(request, 'language.html', {'form':LanguageForm(), 'language_native':language_native, 'language_foreign':language_foreign})
	books_native_subset = Book.objects.filter(language=language_native)
	books_native = []
	for b in books_native_subset:
		books_native.append(b.book_name)
	books_foreign_subset = Book.objects.filter(language=language_foreign)
	books_foreign = []
	for b in books_foreign_subset:
		books_foreign.append(b.book_name)
	books_both = set.intersection(set(books_native), set(books_foreign))
	if language_native == 'all':
		books_both = set(books_foreign)
	if language_foreign =='all':
		books_both = set(books_native)
	cols = []
	categories_both = []
	book_names_both = []
	if language_native=='all' and language_foreign=='all':
		print('language is all')
		books_subset = Book.objects.all()
		for b in books_subset:
			book = Book.objects.filter(book_name=b.book_name)[0]
			collection = book.collection
			if len(collection) > 1:
				cols.append(collection)
				if not collection in book_names_both:
					book_names_both.append(collection)
					categories_both.append(book.category)
			else:
				if not book.book_name in book_names_both:
					book_names_both.append(book.book_name)
					categories_both.append(book.category)
	else:
		print('gotten to else')
		for b_name in books_both:
			if language_foreign=='all':
				book = Book.objects.get(book_name=b_name, language=language_native)
			elif language_native=='all':
				book = Book.objects.get(book_name=b_name, language=language_foreign)
			else:
				book = Book.objects.get(book_name=b_name, language=language_native)
			collection = book.collection
			if len(collection) > 1:
				cols.append(collection)
				if not collection in book_names_both:
					book_names_both.append(collection)
					categories_both.append(book.category)
			else:
				book_names_both.append(b_name)
				categories_both.append(book.category)
	conts = Book_Instance.objects.filter(profile__user__username=user_name, completed=False, native=language_native, sentence__book__language=language_foreign)
	print(book_names_both)
	print(categories_both)
	book_names = []
	for cont in conts:
		collection = cont.sentence.book.collection
		if len(collection) > 1:
			cols.append(collection)
			if not collection in book_names:
				book_names.append(collection)
		else:
			b = cont.sentence.book.book_name
			if not b in book_names:
				book_names.append(b)
	book_names.sort()
	conts = book_names
	conts_again = Book_Instance.objects.filter(profile__user__username=user_name, completed=True, native=language_native, sentence__book__language=language_foreign)
	book_names = []
	for cont in conts_again:
		collection = cont.sentence.book.collection
		if len(collection) > 1:
			cols.append(collection)
			if not collection in book_names and not collection in conts:
				book_names.append(collection)
		else:
			b = cont.sentence.book.book_name
			if not b in book_names:
				book_names.append(b)
	book_names.sort()
	conts_again = book_names
	cat_old = ''
	new_books_html=''
	conts_again_html = ''
	conts_html = ''
	new_books_names = list(book_names_both)
	together = zip(categories_both, new_books_names)
	sorted_together =  sorted(together)
	new_books_names = [x[1] for x in sorted_together]
	categories_both = [x[0] for x in sorted_together]
	print(new_books_names)
	print(categories_both)
	for c in range(len(conts)):
		print(conts[c])
		author = Book.objects.filter(Q(book_name = conts[c])|Q(collection = conts[c]))[0].author
		if conts[c] not in cols:
			completed='not_done'
			conts_html = conts_html + '<div class=\"book_div\" id=\"' + remove_punc_all(conts[c])  + '\"><div class=\"inner_book_div\"><a href=\"/' + user_name + '/' + language_native + '/' + language_foreign + '/' + re.sub("'", "&#39;", re.sub('"',"&#34;",conts[c])) + '/0/reader/\" id=\'a_id\'><img id=\'book_image\' src=\'/static/images/' + re.sub("'","&#39;",re.sub(" ", "", "_".join(conts[c].strip().split()))) + '.jpg\' /> <div class=\'close_icon\' onclick=\"removeBook(\'' + re.sub("'","*apos*",re.sub("\"", "*q*", conts[c])) + '\'); return false\"><img src=\'/static/icons/close_icon.png\'/></div><div class=\'banner ' + completed + '\'><img src=\'/static/icons/banner.png\'></img></div><div class=\'overlay\'></div><div class=\'circle not_col\'><span class=\'not_col\' id=\'col_num\'>'+''+'</span></div></a></div>'
		else:
			completed='not_done'
			col_n = str(Book.objects.filter(collection = conts[c], language=language_native).count())
			if col_n == '0':
				col_n = ''
			else:
				col_n = '- ' + col_n + ' -' + '</span><span class=\'col_text\'>in this collection</span>'
			conts_html = conts_html + '<div class=\"book_div\" id=\"' + remove_punc_all(conts[c])  + '\"><div class=\"inner_book_div\"><a href=\"/' + user_name + '/collection/' + re.sub("'", "&#39;", re.sub('"',"&#34;",conts[c])) + '/' + language_native + '/' + language_foreign + '/\" id=\'a_id\'><img id=\'book_image\' src=\'/static/images/' + re.sub("'","&#39;",re.sub(" ", "", "_".join(conts[c].strip().split()))) + '.jpg\' /> <div class=\'close_icon collection\' onclick=\"removeBook(\'' + re.sub("'","*apos*",re.sub("\"", "*q*", conts[c])) + '\'); return false\"><img src=\'/static/icons/close_icon.png\'/></div><div class=\'banner ' + completed + '\'><img src=\'/static/icons/banner.png\'></img></div><div class=\'overlay\'></div><div class=\'circle collection\'><span class=\'collection\' id=\'col_num\'>'+col_n+'</span></div></a></div>'
		conts_html = conts_html + '<p> ' + re.sub("'", '&#39;', conts[c]) + '</p> <p> ' + author + '</p>'
		languages_html = ''
		this_langs = Book.objects.filter(Q(book_name=conts[c])|Q(collection=conts[c])).order_by('language').distinct('language').values_list('language',flat=True)
		for l in this_langs:
			languages_html = languages_html + '<p>' + l + '</p>'
		conts_html = conts_html + '<p style=\'overflow:visible;\'><span>Available in: <img class=\'lang_icon\' onclick=\"showlanguages(this, \'' + languages_html  + '\')\" src=\'/static/icons/info.png\' /></span></p></div>'

	for c in range(len(categories_both)):
		print(new_books_names[c])
		if cat_old!=categories_both[c]:
			if cat_old == '':
				new_books_html = new_books_html + '<div class=\'library_section\' ><div class=\'spacer\' ><span class=\'line\'></span><span class=\'category\'> ' + categories_both[c] + '</span></div>'
			else:
				new_books_html = new_books_html + '</div><div class=\'library_section\' ><div class=\'spacer\' ><span class=\'line\'></span><span class=\'category\'> ' + categories_both[c] + '</span></div>'
			cat_old = categories_both[c]
		author = Book.objects.filter(Q(book_name = new_books_names[c])|Q(collection = new_books_names[c]))[0].author
		if new_books_names[c] not in cols:
			completed = 'not_done'
			sec = '0'
			if new_books_names[c] not in conts and new_books_names[c] not in conts_again:
				sec = '1111111111'
			if new_books_names[c] in conts_again:
				completed = ''
			new_books_html = new_books_html + '<div class=\"book_div\" id=\"new' + remove_punc_all(new_books_names[c])+  '\"><div class=\"inner_book_div\"><a href=\"/' + user_name + '/' + language_native + '/' + language_foreign + '/' + re.sub("'", "&#39;", re.sub('"',"&#34;",new_books_names[c])) + '/' + sec + '/reader/\" id=\'a_id\'><img id=\'book_image\' src=\'/static/images/' + re.sub("'","&#39;",re.sub(" ", "", "_".join(new_books_names[c].strip().split()))) + '.jpg\' /><div class=\'banner ' + completed +'\'><img src=\'/static/icons/banner.png\'></img></div><div class=\'overlay\'></div><div class=\'circle not_col\'><span class=\'not_col\' id=\'col_num\'>'+''+'</span></div></a></div>'
			new_books_html = new_books_html + '<p> ' + re.sub("'", '&#39;', new_books_names[c]) + '</p> <p> ' + author + '</p>'
		else:
			print(new_books_names[c])
			completed = 'not_done'
			bks = Book_Instance.objects.filter(profile__user__username=user_name, sentence__book__collection=new_books_names[c], native=language_native, sentence__book__language=language_foreign)
			if bks.count() > 0:
				for bk in bks:
					if not bk.completed:
						completed = 'not_done'
			col_n = str(Book.objects.filter(collection = new_books_names[c], language=language_native).count())
			if language_native=='all' or language_foreign=='all':
				col_n = str(Book.objects.filter(collection = new_books_names[c]).values('book_name').distinct().count())
			if col_n == '0':
				col_n = ''
			else:
				col_n = '- ' + col_n + ' -' + '</span><span class=\'col_text\'>in this collection</span>'
			new_books_html = new_books_html + '<div class=\"book_div\" id=\"new' + remove_punc_all(new_books_names[c])+  '\"><div class=\"inner_book_div\"><a href=\"/' + user_name + '/collection/' + re.sub("'", "&#39;", re.sub('"',"&#34;",new_books_names[c])) + '/' + language_native + '/' + language_foreign + '/\" id=\'a_id\'><img id=\'book_image\' src=\'/static/images/' + re.sub("'","&#39;",re.sub(" ", "", "_".join(new_books_names[c].strip().split()))) + '.jpg\' /><div class=\'banner ' + completed + '\'><img src=\'/static/icons/banner.png\'></img></div><div class=\'overlay\'></div><div class=\'circle collection\'><span class=\'collection\' id=\'col_num\'>'+col_n+'</span></div></a></div>'
			new_books_html = new_books_html + '<p> ' + re.sub("'", '&#39;', new_books_names[c]) + '</p> <p> ' + author + '</p>'
		languages_html = ''
		this_langs = Book.objects.filter(Q(book_name=new_books_names[c])|Q(collection=new_books_names[c])).order_by('language').distinct('language').values_list('language',flat=True)
		for l in this_langs:
			languages_html = languages_html + '<p>' + l + '</p>'
		new_books_html = new_books_html + '<p style=\'overflow:visible;\'><span>Available in: <img class=\'lang_icon\' onclick=\"showlanguages(this, \'' + languages_html  + '\')\" src=\'/static/icons/info.png\' /></span></p></div>'
	new_books_html = new_books_html + '</div>'
	print(language_native)
	print(language_foreign)
	context = {
		'signup_form': SignUpForm(),
		'login_form': AuthenticationForm(),
		'form': LanguageForm(),
		'conts_html': conts_html,
		'conts_again_html': mark_safe(conts_again_html),
		#'new_books_names': mark_safe(books_both),
		#'new_books_categories': categories_both,
		'new_books_html': mark_safe(new_books_html),
		'prof_name': user_name,
		'language_native': language_native,
		'language_foreign': language_foreign,
		'languages': Book.objects.order_by('language').distinct('language').values_list('language',flat=True),
		'user_name': user_name
		}
	return render(request, 'library.html', context)

def language_form(request, user_name, language_native, language_foreign, book_name):
	if request.user.is_authenticated():
		user_name = request.user.username
	else:
		user_name = 'AnonymousUser'
	print(book_name)
	print('language_form')
	print(request.META)
	print(language_native)
	print(language_foreign)
	native_dat='all'
	foreign_dat='all'
	if request.method=='POST':
		form = LanguageForm(request.POST)
		print('maybe')
		native_dat = form.data['lang_native']
		foreign_dat = form.data['lang_foreign']
		if native_dat=='':
			native_dat='all'
		if foreign_dat=='':
			foreign_dat='all'
		print(native_dat)
		print(foreign_dat)
		if form.is_valid():
			print('valid')
			prof = user_name
			context = {
				'prof': user_name,
				#'language_native': form.cleaned_data.get('native_language'),
				#'language_foreign': form.cleaned_data.get('foreign_language'), 
			}
			if 'HTTP_REFERER' in request.META:
				if 'collection' in request.META['HTTP_REFERER']:
					return HttpResponseRedirect(reverse('col_library', kwargs={'user_name':user_name,'language_native':form.cleaned_data.get('lang_native'), 'language_foreign':form.cleaned_data.get('lang_foreign'), 'book_name':book_name,}))
			return HttpResponseRedirect(reverse('text_library', kwargs={'user_name':user_name,'language_native':form.cleaned_data.get('lang_native'), 'language_foreign':form.cleaned_data.get('lang_foreign')}))
	print('givingup')
	if 'HTTP_REFERER' in request.META:
		if 'collection' in request.META['HTTP_REFERER']:
			return HttpResponseRedirect(reverse('col_library', kwargs={'user_name':user_name,'language_native':native_dat, 'language_foreign':foreign_dat, 'book_name':book_name,}))		
	return HttpResponseRedirect(reverse('text_library', kwargs={'user_name':user_name,'language_native':native_dat, 'language_foreign':foreign_dat}))
	return render(request, 'language.html', {'form': form, 'language_foreign':language_foreign, 'language_native':language_native})

def get_full_book_name(small_name):
	book_objects = Book.objects.all()
	for b in book_objects:
		full_name = b.book_name
		new_name = "".join(full_name.split())
		if new_name==small_name or full_name==small_name:
			return full_name
	for b in book_objects:
		full_name = b.collection
		new_name = "".join(full_name.split())
		if new_name==small_name or full_name==small_name or full_name==(small_name+' '):
			return full_name	

def get_under_book_name(small_name):
	book_objects = Book.objects.all()
	for b in book_objects:
		full_name = b.book_name.strip()
		new_name = "".join(full_name.split())
		if new_name==small_name or full_name==small_name:
			return "_".join(full_name.split())
	for c in book_objects:
		full_name = c.collection.strip()
		new_name = "".join(full_name.split())
		if new_name==small_name or full_name==small_name:
			return "_".join(full_name.split())

def remove_punc_all(word):
	new_word = ''
	for l in word:
		if l.isalpha():
			new_word = new_word + l
	return new_word

def remove_punctuation(word):
	if not is_valid_word(word, []):
		return word
	bad=False
	if not word[-1].isalpha():
		bad=True
	while bad==True:
		word = word[0:len(word)-1]
		if word[-1].isalpha():
			bad=False
	bad=False
	if not word[0].isalpha():
		bad=True
	while bad==True:
		word = word[1:len(word)]
		if word[0].isalpha():
			bad=False
	return word
def get_punc_end(word):
	if not is_valid_word(word, []):
		return ''
	bad=False
	if not word[-1].isalpha():
		bad=True
	punc = ''
	while bad==True:
		punc = word[-1]+punc
		word = word[0:len(word)-1]
		if word[-1].isalpha():
			bad=False
	return punc

def get_punc_begin(word):
	if not is_valid_word(word, []):
		return ''
	bad=False
	if not word[0].isalpha():
		bad=True
	punc = ''
	while bad==True:
		punc = punc + word[0]
		word = word[1:len(word)]
		if word[0].isalpha():
			bad=False
	return punc

def split_into_sentences(text):
    import re
    caps = "([A-Z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("？","？<stop>")
    text = text.replace("！","！<stop>")
    text = text.replace("。","。<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def pagination(page, last):
	span=7
	page=int(page)
	last=int(last)
	result=range(max(min(page-(span-1)//2,last-span+1),1), min(max(page+span//2,span),last)+1)
	if result[0]==1:
		before=0
	else:
		before=1
	if result[-1]==last:
		after=0
	else:
		after=1
	return [before, result, after]

def highlight(request):
	desired = str(request.GET.get('highlight', None))
	book_name = request.GET.get('book_name', None)
	language_foreign = request.GET.get('language_foreign', None)
	language_native = request.GET.get('language_native', None)
	section = int(request.GET.get('section', None))
	latest_index = request.GET.get('latest_index', None)
	if section=='0':
		section = '1'
	if request.user.is_authenticated():
		user_name = request.user.username
		user_profile = Profile.objects.get(user__username=user_name)
		b_inst = Book_Instance.objects.get(profile__user__username=user_name, native=language_native, sentence__book__language=language_foreign, sentence__book__book_name=book_name, iteration=int(latest_index))
		sen_on = b_inst.sentence_chapters[section-1]
		sentences_native = Sentence.objects.filter(book=b_inst.sentence.book, section=section).order_by('index')
		offset_native = sentences_native[0].index
		offset = sen_on - offset_native + 1
		if desired=='on':
			user_profile.helper = 'on'
		if desired=='off':
			user_profile.helper = 'off'
		user_profile.save()
	else:
		sen_on = request.session['sentence_on']
		sentences_native = Sentence.objects.filter(book=Book.objects.get(language=language_foreign, book_name=book_name), section=section).order_by('index')
		if len(sentences_native)==0:
			sentences_native = Sentence.objects.filter(book=Book.objects.get(language=language_foreign, book_name=book_name), section=0).order_by('index')
		offset_native = sentences_native[0].index
		offset = sen_on - offset_native + 1
		if desired=='on':
			request.session['highlight']='on'
		if desired=='off':
			request.session['highlight']='off'
	context = {
		'highlight': desired,
		'second_index': offset,
	}
	return JsonResponse(context)			

def addBookFromView(request, section, user_name, book_name, language_native, language_foreign):
        if request.user.is_authenticated():
                user_name = request.user.username
        else:
                user_name = 'AnonymousUser'
        user_profile = Profile.objects.get(user__username=user_name)
        book_instances = Book_Instance.objects.filter(sentence__book__book_name=book_name, native=language_native, sentence__book__language=language_foreign, profile=user_profile)
        latest_iter = 0
        if len(book_instances)>0:
                latest_iter = 1
                for bo in book_instances:
                        inst = bo.iteration
                        if inst > latest_iter:
                                latest_iter = inst
        print(book_name)
        print(language_foreign)
        b_new = Book.objects.get(book_name=book_name, language=language_foreign)
        iter = latest_iter+1
        print('addBook iter')
        print(iter)
        m_words = get_missing_words(b_new)
        sen_objects = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign)
        num_sections = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign).order_by('section').values('section').distinct().count()
        chapter_starts = [0]*num_sections
        print(chapter_starts)
        if sen_objects[0].section != 0:
                for n in range(num_sections):
                        sens = Sentence.objects.filter(book__book_name=book_name, book__language=language_foreign, section=n+1).order_by('index')
                        chapter_starts[n]=sens[0].index
        if sen_objects[0].section == 0:
                chapter_starts = [1]
        sentence_chapters = chapter_starts
        print(sentence_chapters)
        new_book = Book_Instance(prim_key=user_name+book_name+language_native+language_foreign+str(latest_iter+1), iteration=latest_iter+1, native=language_native, profile=user_profile, sentence=Sentence.objects.get(index=1, book=b_new), completed=False, missing_words = m_words, sentence_chapters=sentence_chapters)
        new_book.save()
        context = {
                'user_name': user_name,
                'language_native': language_native,
                'language_foreign': language_foreign,
                'book_name': "".join(new_book.sentence.book.book_name.split()),
                'section': new_book.sentence.section,
        }	

        return HttpResponseRedirect(reverse('reader', kwargs=context))

def add_book_from_login(request):
	if request.user.is_authenticated():
		user_name = request.user.username
	else:
		user_name = 'AnonymousUser'
	#user_name = request.GET.get('username', None)
	book_name = get_full_book_name(request.GET.get('b_name', None))
	language_native = request.GET.get('language_native', None)
	language_foreign = request.GET.get('language_foreign', None)
	section = request.GET.get('section', None)
	user_profile = Profile.objects.get(user__username=user_name)
	sen_on = request.session['sentence_on']
	print(language_foreign)
	print(book_name)
	book_instances = Book_Instance.objects.filter(sentence__book__book_name=book_name, native=language_native, sentence__book__language=language_foreign, profile=user_profile)
	if len(book_instances)==0:
		latest_iter = 0
		b_new = Book.objects.get(book_name=book_name, language=language_foreign)
		m_words = get_missing_words(b_new)
		sen_objects = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign)
		num_sections = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign).order_by('section').values('section').distinct().count()
		chapter_starts = [0]*num_sections
		if sen_objects[0].section != 0:
			for n in range(num_sections):
				sens = Sentence.objects.filter(book__book_name=book_name, book__language=language_foreign, section=n+1).order_by('index')
				chapter_starts[n]=sens[0].index
		if sen_objects[0].section == 0:
			chapter_starts = [1]
		sentence_chapters = chapter_starts
		new_book = Book_Instance(prim_key=user_name+book_name+language_native+language_foreign+str(latest_iter+1), iteration=latest_iter+1, native=language_native, profile=user_profile, sentence=Sentence.objects.get(index=sen_on, book=b_new), completed=False, missing_words = request.session['missing_words'], sentence_chapters=request.session['sentence_chapters'])
		new_book.save()


def addBook(request):
	book_name = request.GET.get('book_name', None)
	book_name = re.sub("&#39;", '"', re.sub("&quot;", "\"", request.GET.get('book_name', None)))
	#book_name = re.sub("'", '"', book_name)
	user_name = request.GET.get('username', None)
	if request.user.is_authenticated():
		user_name = request.user.username
	else:
		user_name = 'AnonymousUser'
	language_native = request.GET.get('language_native', None)
	language_foreign = request.GET.get('language_foreign', None)
	user_profile = Profile.objects.get(user__username=user_name)
	book_instances = Book_Instance.objects.filter(sentence__book__book_name=book_name, native=language_native, sentence__book__language=language_foreign, profile=user_profile)
	latest_iter = 0
	if len(book_instances)>0:
		latest_iter = 1
		for bo in book_instances:
			inst = bo.iteration
			if inst > latest_iter:
				latest_iter = inst
	print(book_name)
	print(language_foreign)
	b_new = Book.objects.get(book_name=book_name, language=language_foreign)
	iter = latest_iter+1
	print('addBook iter')
	print(iter)
	m_words = get_missing_words(b_new)
	sen_objects = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign)
	num_sections = Sentence.objects.filter(book__book_name = book_name, book__language=language_foreign).order_by('section').values('section').distinct().count()
	chapter_starts = [0]*num_sections
	print(chapter_starts)
	if sen_objects[0].section != 0:
		for n in range(num_sections):
			sens = Sentence.objects.filter(book__book_name=book_name, book__language=language_foreign, section=n+1).order_by('index')
			chapter_starts[n]=sens[0].index
	if sen_objects[0].section == 0:
		chapter_starts = [1]
	sentence_chapters = chapter_starts
	print(sentence_chapters)
	new_book = Book_Instance(prim_key=user_name+book_name+language_native+language_foreign+str(latest_iter+1), iteration=latest_iter+1, native=language_native, profile=user_profile, sentence=Sentence.objects.get(index=1, book=b_new), completed=False, missing_words = m_words, sentence_chapters=sentence_chapters)
	new_book.save()	
	output_data = {}
	context = {
		'user_name': user_name,
		'language_foreign': language_foreign,
		'language_native': language_native,
		'book_name': "".join(new_book.sentence.book.book_name.split()),
		'section': new_book.sentence.section,
	}
	return JsonResponse({'url':reverse('reader', kwargs=context)})

def removeBook(request):
	book_name = request.GET.get('book_name', None)
	user_name = request.GET.get('username', None)
	language_native = request.GET.get('language_native', None)
	language_foreign = request.GET.get('language_foreign', None)
	user_profile = Profile.objects.get(user__username=user_name)
	book_instances = Book_Instance.objects.filter(Q(sentence__book__book_name=book_name) | Q(sentence__book__collection=book_name), native=language_native, sentence__book__language=language_foreign, profile=user_profile)
	for b in book_instances:
		if not b.completed:
			b.delete()
	book_id = remove_punc_all(book_name)
	print('sentbookid')
	print(book_id)
	context = {'b_id':book_id}
	return JsonResponse(context)



	
