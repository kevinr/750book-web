from django.db.models import Model
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm, CharField, TextInput
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

import requests as http_requests
from xml.etree import ElementTree as ET

from models import UserSubmission, File

def _formfield_from_modelfield(model, fieldname, attrs=None, extra_attrs=None):
    assert(isinstance(model, type))
    assert(issubclass(model, Model))

    formfield = model._meta.get_field(fieldname).formfield()

    if attrs:
        formfield.widget.attrs = attrs.copy()

    if extra_attrs:
        formfield.widget.attrs.update(extra_attrs)

    return formfield

class UserSubmissionForm(ModelForm):
    class Meta:
        model = UserSubmission
        exclude = ['state']

    title = _formfield_from_modelfield(UserSubmission, 'title', extra_attrs={'autofocus': 'true'})
    author = _formfield_from_modelfield(UserSubmission, 'author', extra_attrs={'placeholder': 'your name here!'})


class FileForm(ModelForm):
    class Meta:
        model = File
        exclude = ['usersubmission']

#FileFormSet = inlineformset_factory(UserSubmission, File, fields = ['path'])

def create_update_submission(request, nonce=''):
    if nonce == '':
        editing = False
        submission = UserSubmission()
    else:
        editing = True
        submission = get_object_or_404(UserSubmission, nonce=nonce)

    if request.method == 'POST':
        form = UserSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save()
            return HttpResponseRedirect(reverse(editing and review or add_files, kwargs={'nonce': submission.nonce}))
                
    else:
        form = UserSubmissionForm(instance=submission)

    return render_to_response('bookmaker/create_update_submission.html', 
                                { 'form': form, 'editing': editing, 'submission': submission },
                                context_instance=RequestContext(request))


def add_files(request, nonce=''):
    submission = get_object_or_404(UserSubmission, nonce=nonce)
    files = File.objects.filter(usersubmission=submission)
    fileinstance = File(usersubmission=submission)

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES, instance=fileinstance)
        if form.is_valid():
           uploaded_file_instance = form.save(commit=False) 
           uploaded_file_instance.filename = request.FILES['path'].name
           uploaded_file_instance.save()
           return HttpResponseRedirect(submission.get_absolute_url())
    else:
        form = FileForm(instance = fileinstance)

    return render_to_response('bookmaker/add_files.html', 
                                { 'form': form, 'submission': submission, 'files': files },
                                context_instance=RequestContext(request))

def review(request, nonce=''):
    submission = get_object_or_404(UserSubmission, nonce=nonce)
    files = File.objects.filter(usersubmission=submission)

    if submission.is_processing():
        return HttpResponseRedirect(reverse(process, kwargs={'nonce': submission.nonce}))

    return render_to_response('bookmaker/review.html', { 'submission': submission, 'files': files, 
                                                            'processed': submission.is_processed() },
                                context_instance=RequestContext(request))

def process(request, nonce=''):
    submission = get_object_or_404(UserSubmission, nonce=nonce)

    if submission.is_processed():
        return HttpResponseRedirect(submission.get_absolute_url())
    elif request.method == 'POST' and submission.can_process():
        # XXX TODO this is better done asynchronously and with more abstraction
        # XXX TODO its current sad state is why the below line is commented out
        #submission.mark_as_processing()
        data = { 'token': 'a3841f8142f25477acd09ede082cba31',  # settings.CLSI_TOKEN,
            'latex': submission.render_to_latex(),
            'request_name': submission.nonce, }
        clsi_request = render_to_string('bookmaker/clsi_request.xml', data).encode('utf-8')
        ret = http_requests.post('http://clsi.scribtex.com/clsi/compile', data=clsi_request,
            headers={'content-type': 'text/xml; charset=utf-8'})
        assert ret.status_code == 200
        xml = ET.fromstring(ret.content)
        url = xml.find('output').find('file').get('url')
        submission.mark_as_processed(url)
        

    return render_to_response('bookmaker/processing.html', { 'submission': submission, 'reload': 5, },
                                context_instance=RequestContext(request))
