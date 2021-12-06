from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group

User = get_user_model()


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        Group.objects.create(
            title='qqq',
            slug='www',
            description='eee'
        )
        Group.objects.create(
            title='ttt',
            slug='yyy',
            description='uuu'
        )
        self.client.login(username='sarah', password='12345')

    def test_profile(self):
        response = self.client.get('/sarah/')

        self.assertEqual(response.status_code, 200)

    def test_create_new_post(self):
        response = self.client.post(
            '/new/',
            data={
                'text': 'test',
                'group': 'qqq'
            },
            follow=True
        )
        self.assertRedirects(response, '/')

    def test_check_new_post(self):
        self.client.post(
            '/new/',
            data={
                'text': 'test',
                'group': 'qqq'
            },
            follow=True
        )
        response = self.client.get('/sarah/1/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/sarah/')
        self.assertEqual(len(response.context['page']), 1)

        response = self.client.get('/')
        self.assertEqual(len(response.context['page']), 1)

    def test_edit_post(self):
        self.client.post(
            '/new/',
            data={
                'text': 'test',
                'group': 'qqq'
            },
            follow=True
        )
        response = self.client.post(
            '/sarah/1/edit/',
            data={
                'text': 'check',
                'group': 'ttt'
            }
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/')
        self.assertEqual(response.context['page'][0].text, 'check')
        self.assertEqual(response.context['page'][0].group.title, 'ttt')

        response = self.client.get('/sarah/')
        self.assertEqual(response.context['page'][0].text, 'check')
        self.assertEqual(response.context['page'][0].group.title, 'ttt')
        response = self.client.get('/sarah/1/')

        self.assertEqual(response.context['post'].text, 'check')
        self.assertEqual(response.context['post'].group.title, 'ttt')


class UnauthorizedTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_new(self):
        response = self.client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')
