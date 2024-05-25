from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from common.widgets.base import RangeInput
from problems.consts import Gender
from problems.models import Problem


class ProblemAddNewForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = Problem
        fields = ("problem_type",
                  "problem_description",
                  "user_age",
                  "therapist_gender",
                  "therapist_name",
                  "therapist_country",
                  "is_premium",
                  )
        widgets = {"country": CountrySelectWidget()}

    def __init__(self, *args, **kwargs):
        super(ProblemAddNewForm, self).__init__(*args, **kwargs)
        self.fields['user_age'].widget.attrs['min'] = 18
        self.fields['user_age'].widget.attrs['max'] = 80


class MinMaxAgeRangeInput(RangeInput):
    min = 18
    max = 80
    step = 1


GenderWithEmpty = Gender.choices()
GenderWithEmpty.insert(0, ('', '----'))


class ProblemSearchBox(forms.Form):
    gender = forms.ChoiceField(choices=GenderWithEmpty,
                               required=False,
                               initial=Gender.Male,
                               )
    therapist_country = CountryField().formfield()

    def __init__(self, *args, **kwargs):
        super(ProblemSearchBox, self).__init__(*args, **kwargs)
        self.fields["country"].required = False
