from django.db.models import Model, CharField, DateTimeField, BooleanField, ForeignKey
from djangotoolbox.fields import ListField, BlobField
from django.contrib.auth.models import User

class Shortener(Model):
    """
    Model used to store URL shortening services.
    """
    def __unicode__(self):
        return "%s@%s" % (self.userName, self.shortener)
    key = CharField(max_length=60, primary_key=True)
    user = ForeignKey(User)
    shortener = CharField(max_length=30)
    userName = CharField(max_length=30)
    pubKey = CharField(max_length=128)
    priKey = CharField(max_length=128)
    other = BlobField()

class Service(Model):
    """
    Model used to store social network profiles
    """
    key = CharField(max_length=60, primary_key=True)
    user = ForeignKey(User)
    service = CharField(max_length=30)
    userName = CharField(max_length=30)
    avatar = BlobField()
    pubKey = BlobField()
    priKey = BlobField()
    other = BlobField()

class Feed(Model):
    """
    Model used to store info about the feeds themselves
    """
    user = ForeignKey(User)
    name = CharField(max_length=30)
    url = CharField(max_length=128)
    postTo = ListField()
    postType = CharField(
                         choices=(
                                     ("TDL", "Title - Description Link"),
                                     ("TL", "Title Link"),
                                     ("DL", "Description Link"),
                                     ("L", "Link")
                                   ),
                         max_length=30
                         )
    urlShortener = ForeignKey(Shortener)
    parseEngine = CharField(default="date", max_length=30)
    lastCk = DateTimeField(auto_now_add=True)
    nextCk = DateTimeField(auto_now_add=True)
    preText = BlobField()
    postText = BlobField()
    filter = BlobField() #@ReservedAssignment
    filterOn = CharField(choices=(
                                         ("TTL", "Title"),
                                         ("DSC", "Description"),
                                         ("LNK", "Link"),
                                         ("GUID", "guid")
                                        ),
                         max_length=30
                         )

    timerEngine = CharField(max_length=30)
    timerProfile = BlobField()
    lastTimerCk = DateTimeField(auto_now_add=True)

    pubsub = BooleanField()
    pubsubURL = CharField(max_length=128)

    cfMod = CharField(default="None", max_length=30)
    cfConf = BlobField()

class Entry(Model):
    """
    Model used to store info on a entry from the feed
    This is not really in use, but a UI is planned for
    showing statistics.
    """
    key = CharField(max_length=250, primary_key=True)
    feed = ForeignKey(Feed)
    date = DateTimeField()
    guid = CharField(max_length=128)
    title = BlobField()
    summary = BlobField()
    url = CharField(max_length=128)
    shortURL = CharField(max_length=30)
    posted = DateTimeField(null=True)
    other = BlobField()

class RSSItem(Model):
    """
    OMG this is not used at all!
    Planned as a buffer for some future testing mechanism
    so the user can try out all the filters they apply.
    """
    feed = ForeignKey(Feed)
    date = DateTimeField()
    guid = CharField(max_length=128)
    title = BlobField()
    summary = BlobField()
    url = CharField(max_length=128)
    feched = DateTimeField(auto_now_add=True)
