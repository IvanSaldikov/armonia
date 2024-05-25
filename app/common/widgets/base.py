from django.forms import NumberInput


class RangeInput(NumberInput):
    input_type = "number"
    min = 0
    max = 100
    step = 1
    template_name = "widgets/range_input.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["min"] = self.min
        context["widget"]["max"] = self.max
        context["widget"]["step"] = self.step
        return context
