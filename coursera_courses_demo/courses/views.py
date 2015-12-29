
from django.views.generic import TemplateView
import datetime


class Main(TemplateView):
    template_name = "courses/index.html"

    def get_context_data(self, **kwargs):
        context = super(Main, self).get_context_data(**kwargs)
        year = []
        month = []
        for y in range(2014, (datetime.datetime.today().year + 6)):
            year.append((y, y))
        for x in range(1, 13):
            month.append((x, datetime.date(datetime.datetime.today().year, x, 1).strftime('%B')))
        context['year'] = year
        context['month'] = month
        return context
