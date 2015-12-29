from rest_framework import generics, response, status

import urllib2
import json as simplejson
from datetime import datetime


class CourseMixin(object):

    def _get_datetime_from_epoch(self, timestamp):
        return datetime.fromtimestamp(
            int(timestamp/1000))

    def _copyf(self, datalist, key, mnth, yrs):
        list = []
        for item in datalist:
            if key in item:
                timestamp = self._get_datetime_from_epoch(item[key])
                month = datetime.today().month
                year = datetime.today().year
                if mnth is not None:
                    month = mnth
                if yrs is not None:
                    year = yrs
                if timestamp.year == int(year) and timestamp.month == int(month):
                    item[key] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    list.append(item)
        return list

    def _get_finalize_response(self, datalist, key, valuelist):
        list = []
        for course in valuelist:
            for partner in datalist['partners.v1']:
                if partner[key] in course['partnerIds']:
                    course['partner'] = partner
            for lang in datalist['languages.v1']:
                if lang[key] in course['primaryLanguages']:
                    course['language'] = lang
            for instr in datalist['instructors.v1']:
                if instr[key] in course['instructorIds']:
                    course['instructor'] = instr
            [course.pop(_key) for _key in ['primaryLanguages', 'partnerIds', 'instructorIds']]
            list.append(course)
        return list

    def _utilize_url(self, url):
        response = urllib2.urlopen(url).read()
        return simplejson.loads(response)

    def _utilize_coursera_api(self, id, month, year):
        url = 'https://api.coursera.org/api/courses.v1?includes=partnerIds,primaryLanguages,instructorIds&fields=startDate,primaryLanguages,partnerIds,instructorIds'
        if id is not None:
            url = 'https://api.coursera.org/api/courses.v1/'+id+'?includes=partnerIds,instructorIds,primaryLanguages&fields=startDate,primaryLanguages,partnerIds,instructorIds,subtitleLanguages,photoUrl,certificates,description,specializations,partnerLogo'
        result = self._utilize_url(url)
        result['courses'] = self._copyf(result['elements'], 'startDate', month, year)
        if id is not None:
            result['elements'][0]['startDate'] = self._get_datetime_from_epoch(result['elements'][0]['startDate']).strftime('%Y-%m-%d %H:%M:%S')
            result['courses'] = result['elements']
        result = self._get_finalize_response(result['linked'], 'id', result['courses'])
        return result

    def _get_partner_response(self, id):
        if id is None:
            return {'elements': ''}
        url = 'https://api.coursera.org/api/partners.v1/'+id+'?fields=description,banner,links,location'
        return self._utilize_url(url)

    def _get_instructor_response(self, id):
        if id is None:
            return {'elements': ''}
        url = 'https://api.coursera.org/api/instructors.v1/'+id+'?fields=photo,bio,fullName,title,department'
        return self._utilize_url(url)


class CourseListApi(CourseMixin, generics.GenericAPIView):
    """
    api to list down all the courses using coursera api
    """
    def get(self, request):
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        courses = self._utilize_coursera_api(None, month, year)
        response_data = {'courses': courses}
        return response.Response(response_data, status=status.HTTP_200_OK)


class CourseDetailApi(CourseMixin, generics.GenericAPIView):
    """
    api to show detail of course
    """
    def get(self, request, id):
        course = self._utilize_coursera_api(id, None, None)
        partner = self._get_partner_response(course[0]['partner']['id'] if 'partner' in course[0] else None)
        instructor = self._get_instructor_response(course[0]['instructor']['id'] if 'instructor' in course[0] else None)
        course[0]['partner'] = partner['elements']
        course[0]['instructor'] = instructor['elements']
        response_data = {'course': course}
        return response.Response(response_data, status=status.HTTP_200_OK)
