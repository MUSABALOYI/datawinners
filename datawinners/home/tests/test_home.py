# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponseRedirect
from django.utils import unittest
from django.test import Client
from django.conf import settings
from mock import Mock
from datawinners.home.views import switch_language, custom_home

class TestHome(unittest.TestCase):

    def setUp(self):
        self.client_stub = Client()

    def test_should_render_home_view(self):
        for url in [ '/en/home/', '/fr/home/'] :
            response = self.client_stub.get(url)
            self.assertEquals(response.status_code,200)

    def test_should_render_link_to_trial_registration(self):
        settings.TRIAL_REGISTRATION_ENABLED = True
        for url in [ '/en/home/', '/fr/home/'] :
            response = self.client_stub.get(url, follow=True)
            self.assertRegexpMatches(response.content, r'href="/register/trial"')

    def test_should_switch_language_and_reload_page(self):
        request = Mock()
        request.META = {'HTTP_REFERER': 'http://www.datawinners.com/project/subjects/2e358c46bb6c11e187d60800276384f8/'}
        request.session = {'django_language': 'en'}
        response = switch_language(request, 'fr')
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response._headers['location'][1], '/project/subjects/2e358c46bb6c11e187d60800276384f8/')
        self.assertEqual(request.session['django_language'], 'fr')

    def test_should_redirect_to_home_page_if_unauthorized(self):
        request = Mock()
        request.session = {'django_language': 'en'}
        user = Mock()
        user.is_authenticated.return_value = False
        request.user = user
        response = custom_home(request)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response._headers['location'][1], '/en/home/')


    def test_should_redirect_to_login_redirect_url_if_authorized(self):
        request = Mock()
        request.session = {'django_language': 'en'}
        user = Mock()
        user.is_authenticated.return_value = True
        request.user = user
        settings.LOGIN_REDIRECT_URL = '/dashboard'
        response = custom_home(request)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response._headers['location'][1], '/dashboard')

