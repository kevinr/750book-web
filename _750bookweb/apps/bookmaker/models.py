from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
import uuid

# I think I want to enforce the invariant that UserSubmissions can only be edited before they're processed,
# and Files can't be edited at all once created.

class UserSubmission(models.Model):
    ctime = models.DateTimeField(_("Creation Time"), auto_now_add=True)
    mtime = models.DateTimeField(_("Modification Time"), auto_now=True)

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

    def can_process(self):
        return self.state == 'NEW'

    def is_processing(self):
        return self.state == 'PROCESSING'

    def is_processed(self):
        return self.state == 'PROCESSED'

    def process(self):
        self.processing_time = datetime.now()
        self.state = 'PROCESSING'
        self.save()

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
