from django import forms


class InviteForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Partner Username"
    )