from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()
TEST_POSTS_COUNT = 13


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug1',
            description='test-slug2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug1'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'StasBasov'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create',
            ): 'posts/create.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            )
        )
        self.assertEqual(response.context.get(
            'post').author.username, f'{self.post.author}')
        self.assertEqual(response.context.get(
            'post').text, 'Тестовый пост')
        self.assertEqual(response.context.get(
            'post').group.title, 'Тестовая группа')

    def test_form_post_create_edit_correct_context(self):
        """Шаблон form_post_create и edit
        сформированы с правильным контекстом."""
        pages = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
        ]
        for page in pages:
            response = self.author_client.get(page)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def posts_places(self):
        """
        при создании поста указать группу, то этот пост появляется
        на главной странице сайта,
        на странице выбранной группы,
        в профайле пользователя
        """
        self.group_x = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='test-slug3',
        )

        self.post = Post.objects.create(
            author=PostPagesTests.user,
            text='Тестовый пост',
            group=self.group_x
        )
        reverse_things = (
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': 'StasBasov'}
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug2'}
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug1'}
            )
        )
        for reverse_name in reverse_things:
            response = self.authorized_client.get(reverse_name)
            test_obj = response.context['object_list'][0]
            self.assertEqual(test_obj.text, 'Тестовый пост')
            self.assertEqual(test_obj.group.title, 'Тестовая группа2')
            self.assertEqual(test_obj.author.username, 'StasBasov')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug1',
            description='test-slug2',
        )
        cls.post = []
        for i in range(TEST_POSTS_COUNT):
            cls.post.append(
                Post.objects.create(
                    author=cls.user,
                    text=f'Тестовый пост {i}',
                    group=cls.group,
                )
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Stasbasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page(self):
        reverse_list = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug1'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page(self):
        reverse_list = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug1'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
