from django import forms
from django.utils.translation import gettext_lazy as _


class CheckboxSelectMultipleWithSelectAll(forms.CheckboxSelectMultiple):
    template_name = 'widgets/checkbox_widget.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        total_count = self.choices.queryset.count() if hasattr(self.choices, 'queryset') else len(self.choices)
        selected_count = len(value if value else [])

        context['widget']['all_selected'] = 0 < total_count == selected_count
        context['widget']['select_all_text'] = _("Выбрать всё")
        context['widget']['placeholder_text'] = _("Все")

        return context

    class Media:
        css = {
            'all': ('css/checkbox_widget.css',)
        }
        js = ('js/checkbox_widget.js',)
