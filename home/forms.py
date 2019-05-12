import base64
from email.mime.text import MIMEText
from json.tool import json

from django import forms
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.forms.widgets import PasswordInput
from django.template.response import SimpleTemplateResponse
from googleapiclient.discovery import build

from article.models import Author
from .utils import gmail_credentials


class AuthorSignupForm(forms.ModelForm):
    """
    Form for creating an author
    """
    first_name = forms.CharField(max_length=256)
    last_name = forms.CharField(max_length=256)
    email = forms.EmailField()
    password = forms.CharField(max_length=256, widget=PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email', '')
        if not email:
            self.add_error('email', ValidationError('could not find email'))
        self.cleaned_data['username'] = email
        super(AuthorSignupForm, self).clean(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AuthorSignupForm, self).save(commit=True)
        instance.delete()
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(email, email, password)
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        user.is_active = False

        author_group = Group.objects.filter(name='Authors')
        if author_group:
            user.groups.set(author_group)
        user.save()
        author = Author.objects.create(user=user)
        self._send_validation_email(author)
        return user

    def _send_validation_email(self, author):
        """
        Sends a validation email template to the author's email address.
        Creates a timed token for the author to claim.

        Todo: Move to a utils module later
        """
        credentials = gmail_credentials()
        # todo: change to db value
        from_email = settings.NOREPLY_EMAIL_ADDRESS
        to_email = author.user.email
        subject = 'Please verify your email address'
        email_template = SimpleTemplateResponse(
            'email/verify.html',
            {'author': author},
        )
        mime_text = MIMEText(
            email_template.render().content.decode('utf-8'),
            _subtype='html')
        mime_text['to'] = to_email
        mime_text['from'] = from_email
        mime_text['subject'] = subject
        mime_text_bytes = mime_text.as_string().encode()
        as_base64 = base64.urlsafe_b64encode(mime_text_bytes)
        raw = {'raw': as_base64.decode('utf-8')}
        
        service = build('gmail', 'v1', credentials=credentials)
        res = service.users().messages().send(userId=from_email, body=raw).execute()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']


class AuthorLoginForm(forms.Form):
    """
    Form for logging in an author, requiring an email/password combo
    """
    email = forms.EmailField()
    password = forms.CharField(max_length=256, widget=PasswordInput)
