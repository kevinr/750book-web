from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
import uuid

from _750booklatex import render as render_750booklatex

# I think I want to enforce the invariant that UserSubmissions can only be edited before they're processed,
# and Files can't be edited at all once created.

class UserSubmission(models.Model):
    ctime = models.DateTimeField(_("Creation Time"), auto_now_add=True)
    mtime = models.DateTimeField(_("Modification Time"), auto_now=True) 
    # refers only to user modifications, not our modifications

    nonce = models.CharField(_("Nonce"), default=lambda: str(uuid.uuid4()), editable=False, blank=True, max_length=32)

    title = models.CharField(_("Title"), default="750 Words Morning Pages", max_length=100)
    author = models.CharField(_("Author"), max_length=100)

    STATE_CHOICES = (
        ( 'NEW', 'New' ),
        ( 'PROCESSING', 'Processing' ),
        ( 'PROCESSED', 'Processed' ),
    )
    state = models.CharField(_("Current State"), max_length=20, choices=STATE_CHOICES, default='NEW')
    processing_time = models.DateTimeField(_("Processing Time"), null=True, blank=True, editable=False)
    processed_time = models.DateTimeField(_("Processed Time"), null=True, blank=True, editable=False)

    processed_url = models.CharField(_("Processed URL"), max_length=200, null=True, blank=True, editable=False)

    def __getattribute__(self, name):
        if name == 'files':
            return models.Model.__getattribute__(self, 'files')()
        else:
            return models.Model.__getattribute__(self, name)

    def files(self):
        return File.objects.filter(usersubmission=self)

    def can_process(self):
        return self.state == 'NEW'

    def is_processing(self):
        return self.state == 'PROCESSING'

    def is_processed(self):
        return self.state == 'PROCESSED'

    def mark_as_processing(self):
        self.processing_time = datetime.now()
        self.state = 'PROCESSING'
        self.save()

    def mark_as_processed(self, url):
        self.processed_time = datetime.now()
        self.processed_url = url
        self.state = 'PROCESSED'
        self.save()

    def render_to_latex(self):
        input = [f.path.file for f in self.files]
        return render_750booklatex(*input, title=self.title, author=self.author)

    def __unicode__(self):
        return "%s - %s" % (str(self.ctime), self.nonce) 

    @models.permalink
    def get_absolute_url(self):
        return ('bookmaker.views.review', (), { 'nonce': self.nonce })

class File(models.Model):
    ctime = models.DateTimeField(_("Creation Time"), auto_now_add=True)
    usersubmission = models.ForeignKey(UserSubmission, editable=False)
    filename = models.CharField(_("Original Filename"), max_length=100, editable=False)
    path = models.FileField(_("File"), max_length=100,
        upload_to=lambda x, y: datetime.now().strftime("750words-input/%Y-%m-%d/%Y-%m-%dT%H:%M:%S") + ".%s" % (str(uuid.uuid4()),) )

    def __unicode__(self):
        return self.filename or "no filename"
