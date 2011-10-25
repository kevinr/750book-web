from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from models import UserSubmission, File

class UserSubmissionForm(ModelForm):
    class Meta:
        model = UserSubmission
        exclude = ['state']

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
        submission.process()

    return render_to_response('bookmaker/processing.html', { 'submission': submission, 'reload': 5, },
                                context_instance=RequestContext(request))
