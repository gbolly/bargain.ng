from django import forms
from accounts.models import *


class UserProfileForm(forms.ModelForm):
    """This class defines a model form using the 'UserProfile' model.
    """

    class Meta:
        """This class modifies the UserProfileForm class.
        Attributes:
            model: A model from which to construct the form.
            field: A tuple of the form fields that are fillable.
        """
        model = UserProfile
        fields = ('phonenumber', 'location', 'alternative_contact_name', 'alternative_contact_phonenumber')
