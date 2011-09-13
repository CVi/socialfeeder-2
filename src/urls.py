from django.conf.urls.defaults import * #@UnusedWildImport

handler500 = 'djangotoolbox.errorviews.server_error'
from django.contrib import admin
admin.autodiscover() #@UndefinedVariable
urlpatterns = patterns('',
    (r'^_ah/warmup$', 'djangoappengine.views.warmup'),

    (r'^$', 'sfdr.views.out.frontpage'),
    (r'^dashboard.html$', 'sfdr.views.app.dashboard'),

    (r'^feeds/add.py', 'sfdr.views.feeds.add'),
    (r'^feeds/sva.py', 'sfdr.views.feeds.sva'),
    (r'^feeds/svr.py', 'sfdr.views.feeds.svr'),
    (r'^feeds/put.py', 'sfdr.views.feeds.put'),
    (r'^feeds/store.py', 'sfdr.views.feeds.store'),
    (r'^feeds/edit/(?P<feed>\d{1,6}).py$', 'sfdr.views.feeds.edit'),
    (r'^feeds/edit/(?P<feed>\d{1,6})/cf.py$', 'sfdr.views.feeds.filterMod'),

    (r'^modules/bitly/redirect.py', 'sfdr.views.bitly.redirect'),
    (r'^modules/bitly/callback.py', 'sfdr.views.bitly.callback'),
    (r'^modules/twitter/redirect.py$', 'sfdr.views.twitter.redirect'),
    (r'^modules/twitter/callback.py$', 'sfdr.views.twitter.callback'),

    (r'^tasks/post.py$', 'sfdr.views.tasks.post'),
    (r'^tasks/posts/orophan.py$', 'sfdr.views.tasks.orophanedPosts'),
    (r'^tasks/feeds/fetch.py$', 'sfdr.views.tasks.feed'),
    (r'^tasks/feeds/orophan.py$', 'sfdr.views.tasks.orophanedFeeds'),
    (r'^tasks/feeds/timeprofile.py$', 'sfdr.views.tasks.calcTimerProfile'),
    (r'^tasks/pin/encr_rs.py$', 'sfdr.views.pin.EncR_Rs'),

    (r'^ajax/feed/(?P<feed>\d{1,6})/cf/store.json', 'sfdr.views.ajax.cfStore'),
    (r'^ajax/feed/(?P<feed>\d{1,6})/cf/get.json', 'sfdr.views.ajax.cfLoad'),
    (r'^ajax/db.json', 'sfdr.views.dashboard.json'),

    (r'^admin/', include(admin.site.urls)), #@UndefinedVariable
)
