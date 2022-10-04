from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для
        # проверки сушествующего slug
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
        # Создаем клиент
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def test_create_post(self):
        """Валидная форма создает запись в Пост."""
        posts_count = Post.objects.all().count()
        form_data = {
            'group': self.group.id,
            'author': self.user.id,
            'text': 'Тест текст',
        }

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.post.author}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тест текст',
                author=self.user.id,
                group=self.group.id,
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Пост."""
        posts_count = Post.objects.count()
        self.post = PostFormTests.post
        form_data = {
            'group': self.group.id,
            'author': self.user.id,
            'text': 'Тест текс1т',
        }

        response = self.author_client.post(
            reverse('posts:post_edit', args=(f'{self.post.pk}',)),
            data=form_data,
            follow=True
        )
        post2 = Post.objects.get(id=self.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post2.author, self.post.author)
        self.assertEqual(post2.group.pk, self.group.pk)
        self.assertEqual(post2.text, 'Тест текс1т')
        self.assertEqual(response.status_code, 200)
