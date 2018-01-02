from polly.models import Sentence, Book
import os
import sys
import re

authors = {'Twenty Thousand Leagues Under the Sea ':'Jules Verne', 'Alice\'s Adventures in Wonderland ':'Lewis Carroll', 'Metamorphosis ':'Franz Kafka', 'The Adventures of Tom Sawyer ':'Mark Twain', 'The Hound of the Baskervilles ':'Arthur Conan Doyle', 'Harry Potter ':'Joanne K. Rowling', 'Grimms\' Fairy Tales ':'Jacob and Wilhelm Grimm', 'Andersen\'s Fairy Tales ':'Hans Christian Anderson', 'The Wonderful Wizard of Oz ':'L. Frank Baum', 'Aladdin and the Wonderful Lamp ':'Unknown author', 'Jack and the Beanstalk ':'Unknown author', 'Jack the Giant Killer ':'Ernest Nister', 'Puss in Boots ': 'Unknown author', 'Robin Hood ':'Unknown author', 'Robinson Crusoe ': "Unknown author", 'The Little Old Woman Who Lived in a Shoe ':'Unknown author', 'The Little Red Hen ':'Unknown author', 'The Tale of Benjamin Bunny ': 'Beatrix Potter', 'The Tale of Peter Rabbit ': 'Beatrix Potter', 'The Three Bears ': "Unknown author", 'Pinocchio ': 'C. Collodi', 'A Christmas Carol ': 'Charles Dickens', 'A Tale of Two Cities ': 'Charles Dickens', 'Candide ':'Voltaire', 'The Adventures of Sherlock Holmes ':'Arthur Conan Doyle', 'The Memoirs of Sherlock Holmes ':'Arthur Conan Doyle', 'The Return of Sherlock Holmes ':'Arthur Conan Doyle', 'Through the Looking Glass ':'Lewis Carroll', 'Don Quixote ':'Miguel de Cervantes', 'The Cask of Amontillado ':'Edgar Allan Poe', 'The Fall of the House of Usher ':'Edgar Allan Poe', 'My Life ':'Anton Chekhov', 'Anna Karenina ':'Leo Tolstoy'}

numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
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
    text = text.replace("...","…")
    text = text.replace("..","…")
    text = text.replace(". . .","…")
    text = text.replace(". .","…")
    text = text.replace("？","？<stop>")
    text = text.replace("！","！<stop>")
    text = text.replace("。","。<stop>")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

texts = 'texts_chinese'

text_files=[]
for root, dirs, files in os.walk('polly/static/texts_chinese'):
	for name in files:
		if name[0:3]!='.DS':
			text_files.append(root+'/'+name)
ordered_files = []
sections = []
book_names = []
for fname in text_files:
	directories = re.split('/', fname)
	book_file = directories[-1]
	book_elements = re.split('_',book_file)
	sectioned = False
	if (book_elements[-1][0]=='s' or book_elements[-1][0]=='c') & (book_elements[-1][1] in numbers):
		book_words = book_elements[0:-1]
		sectioned=True
		section = book_elements[-1][1:len(book_elements[-1])-4]
		sections.append(int(section))
	else:
		sections.append(1)
		book_words = book_elements[0:len(book_elements)]
		book_words[-1] = book_words[-1][0:-4]
	book_name = ''
	for word in book_words:
		book_name = book_name + word + ' '
	print(book_name)
	book_names.append(book_name)

print('before_together')

together = zip(book_names, sections, text_files)
sorted_together =  sorted(together)

book_names_sorted = [x[0] for x in sorted_together]
sections_sorted = [x[1] for x in sorted_together]
textfiles_sorted = [x[2] for x in sorted_together]

print('before_oldbook')

old_book = book_names_sorted[0]
sections_sorted_again = []
files_sorted_again = []
sections_temp = []
files_temp = []
for b in range(len(book_names_sorted)):
	if book_names_sorted[b]==old_book:
		sections_temp.append(sections_sorted[b])
		files_temp.append(textfiles_sorted[b])
	else:
		together_temp = zip(sections_temp, files_temp)
		sorted_together_temp = sorted(together_temp)
		sections_temp_sorted = [x[0] for x in sorted_together_temp]
		files_temp_sorted = [x[1] for x in sorted_together_temp]
		sections_sorted_again.extend(sections_temp_sorted)
		files_sorted_again.extend(files_temp_sorted)
		old_book=book_names_sorted[b]
		sections_temp = [sections_sorted[b]]
		files_temp= [textfiles_sorted[b]]
sections_sorted_again.extend(sections_temp)
files_sorted_again.extend(files_temp)

print('before_sen')

sen_index = 0
old_book = book_names_sorted[0]
for f in range(len(files_sorted_again)):
	print(files_sorted_again[f])
	directories = re.split('/', files_sorted_again[f])
	language = directories[directories.index(texts)+1]
	category = directories[directories.index(texts)+2]
	category_index = directories.index(texts)+2
	next_dir = directories[directories.index(texts)+3]
	last_dir = directories[-1]
	last_dir_parts = re.split('_', last_dir)
	order = 0
	if len(directories)==category_index+2:
		print('first if')
		collection = ''
	elif len(directories)==category_index+3:
		print('second if')
		if (last_dir_parts[-1][0]=='s' or last_dir_parts[-1][0]=='c') and last_dir_parts[-1][1] in numbers:
			collection = ''
		else:
			print('third if')
			collection = directories[-2]
			if directories[-1][0]=='*':
				print('fourth if')
				nm = re.split('\*', directories[-1])
				order = nm[1]
	elif len(directories)==category_index+4:
		print('hello harry')
		collection = directories[category_index+1]
		if directories[category_index+2][0]=='*':
			print(directories[category_index+2])
			print(re.split('\*', directories[category_index+2]))
			nm = re.split('\*', directories[category_index+2])
			order = int(nm[1])
	print('order')
	print(order)
	cat_elements = re.split('_', category)
	category = ''
	for word in cat_elements:
		category = category + word + ' '
	book_file = directories[-1]
	book_elements = re.split('_',book_file)
	print(book_elements)
	sectioned = False
	if (book_elements[-1][0]=='s' or book_elements[-1][0]=='c') & (book_elements[-1][1] in numbers):
		book_words = book_elements[1:-1]
		sectioned = True
	else:
		book_words = book_elements[1:len(book_elements)]
		book_words[-1] = book_words[-1][0:-4]
	print(book_words)
	print(files_sorted_again[f])
	with open(files_sorted_again[f]) as fi:
		content = fi.readlines()
		fi.close()
	content = [x.strip() for x in content]
	print(content[0])
	section_names = ''
	book_name = ''
	for word in book_words:
		book_name = book_name + word + ' '
	pkey = language+'_'+book_name
	print(book_name)
	if book_name in authors:
		print('found')
		author=authors[book_name]
	if collection in authors:
		author=authors[collection]
	col_words = re.split('_', collection)
	collection = ''
	for word in col_words:
		collection = collection + word + ' '
	if collection in authors:
		author=authors[collection]
	print('collection')
	print(collection)
	print(author)
	b = Book(prim_key=pkey, order=order, book_name=book_name, sectioned=sectioned, section_name=section_names, category=category, language=language, author=author, collection=collection)
	b.save()
	if (sectioned):
		section = sections_sorted_again[f]
	else:
		section = 0
	Sentence.objects.filter(book=b, section=section).delete()
	current_book = book_names_sorted[f]
	if (not current_book==old_book):
		sen_index = 0
		old_book = current_book
	par = 0
	print(sen_index)
	for p in range(len(content)):
		if content[p]=='':
			continue
		sentences = split_into_sentences(content[p])
		par = par+1
		if len(sentences)<1:
			id_text = language[0:3] + str(sen_index+1)
			text = content[p]
			if (sectioned):
				section = sections_sorted_again[f]
			else:
				section = 0
			sen_index+=1
			pkey_s = str(sen_index)+'_'+pkey
			s = Sentence(prim_key=pkey_s,index=sen_index, html_id=id_text, text=text, paragraph=par, section=section, book=b)
			s.save()
		for sen in range(len(sentences)):
			sen_index+=1
			id_text = language[0:3] + str(sen_index)
			text = sentences[sen]
			if (sectioned):
				section = sections_sorted_again[f]
			else:
				section = 0
			pkey_s = str(sen_index)+'_'+pkey
			s = Sentence(prim_key=pkey_s,index=sen_index, html_id=id_text, text=text, paragraph=par, section=section, book=b)
			s.save()

		
			
		
		
	

