from django import forms
from sfdr.models import Feed, Shortener

class feedForm(forms.Form):
    """
    Form for feed creation...
    This one will get replaced by an AJAX one too at some point
    TODO: Replace with JS form
    """
    class Meta:
        model = Feed

    def __init__(self, queryset, *args, **kwargs):
        super(feedForm, self).__init__(*args, **kwargs)
        self.fields['snr'].queryset = queryset
    nm = forms.CharField(
                           label="Name",
                           max_length=20,
                           min_length=2
                           )
    fd = forms.URLField(
                          label="Feed",
                          max_length=150,
                          verify_exists=False
                          )
    snr = forms.ModelChoiceField(
                          label="Shortener",
                          queryset=Shortener.objects.filter(key="")
                          )
    pre = forms.CharField(label="Text before", max_length=45, required=False)
    fmt = forms.ChoiceField(
                            label="Post formating",
                            choices=(
                                         ("TDL", "Title - Description Link"),
                                         ("TL", "Title Link"),
                                         ("DL", "Description Link"),
                                         ("L", "Link")
                                       ),
                            initial="TDL"
                            )
    post = forms.CharField(label="Text after", max_length=45, required=False)
    feed = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    fo = forms.ChoiceField(
                           label="Filter on",
                           choices=set((
                                         ("TTL", "Title"),
                                         ("DSC", "Description"),
                                         ("LNK", "Link"),
                                         ("GUID", "guid")
                                        )),
                            initial="TTL",
                            required=False
                            )
    fi = forms.CharField(label="Filter Text", required=False)
    cfM = forms.ChoiceField(
                            label="Content Filter Engine",
                            choices=(
                                         ("None", "No Content Filter"),
                                         ("EncR", "Enclosure match"),
                                         ("RegX", "Regular Expression"),
                                         ("StripR", "Flickr Stripr")
                                         ),
                            initial="None",
                            required=False
                            )
