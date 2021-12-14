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
        self.client.login(username='sarah', password='12345')

    def test_profile(self):
        response = self.client.get('/sarah/')

        self.assertEqual(response.status_code, 200)

    def test_create_new_post(self):
        response = self.client.post(
            '/new/',
            data={
                'text': 'test'
            },
            follow=True
        )
        self.assertRedirects(response, '/sarah/1/')

    def test_check_new_post(self):
        response = self.client.post(
            '/new/',
            data={
                'text': 'test'
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
                'text': 'test'
            },
            follow=True
        )
        response = self.client.post(
            '/sarah/1/edit/',
            data={
                'text': 'check'
            }
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/')
        self.assertEqual(response.context['page'][0].text, 'check')

        response = self.client.get('/sarah/')
        self.assertEqual(response.context['page'][0].text, 'check')

        response = self.client.get('/sarah/1/')
        self.assertEqual(response.context['post'].text, 'check')


class UnauthorizedTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_new(self):
        response = self.client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')


class PageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404(self):
        response = self.client.get('/pooogchamp/')
        self.assertEqual(response.status_code, 404)


class ImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.client.login(username='sarah', password='12345')
        with open(r'C:\Avatars\user8.jpg', 'rb') as img:
            self.client.post('/new/', data={'text': 'test', 'image': img})

    def test_post_tag(self):
        response = self.client.get('/sarah/1/')
        self.assertContains(response, '<img')

    def test_profile_tag(self):
        response = self.client.get('/sarah/')
        self.assertContains(response, '<img')

    def test_group_tag(self):
        response = self.client.get('/')
        self.assertContains(response, '<img')

    def test_nonimage_upload(self):
        with open(r'C:\Activators\help.txt', 'rb') as img:
            response = self.client.post('/new/', data={'text': 'test', 'image': img})

        self.assertContains(response,
                            'Загрузите правильное изображение. Файл, который вы загрузили, '
                            'поврежден или не является изображением.')


class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.client.login(username='sarah', password='12345')
        self.client.post(
            '/new/',
            data={
                'text': 'test'
            }
        )

    def test_case(self):
        response = self.client.get('/')
        first_html = response.content.decode('utf-8')

        self.client.post(
            '/new/',
            data={
                'text': 'test2'
            }
        )

        response = self.client.get('/')
        second_html = response.content.decode('utf-8')

        self.assertHTMLEqual(first_html, second_html)
