from polly.models import Sentence, Book
import os
import sys
import re

meta_books = Book.objects.filter(collection='Grimms\' Fairy Tales ')
for bk in meta_books:
	bk.category = 'Children\'s Stories '
	bk.save()
meta_books = Book.objects.filter(collection='Andersen\'s Fairy Tales ')
for bk in meta_books:
        bk.category = 'Children\'s Stories '
        bk.save()
meta_books = Book.objects.filter(book_name='The Wonderful Wizard of Oz ')
for bk in meta_books:
        bk.category = 'Classic Literature '
        bk.save()
#sentences = Sentence.objects.filter(book__book_name = 'Candide ', book__language='Spanish', section=126)
#for st in sentences:
#	st.delete()
