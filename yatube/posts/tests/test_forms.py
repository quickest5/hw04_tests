# Задание
# В проекте Yatube напишите тесты,
# которые проверяют, что
# при отправке валидной формы со
# страницы создания поста
# reverse('posts:create_post') создаётся новая
#  запись в базе данных;

# при отправке валидной формы со
# страницы редактирования поста
#  reverse('posts:post_edit', args=('post_id',))
#  происходит изменение поста с post_id в
#  базе данных.
# Это задание будет проверено в конце спринта
#  вместе с домашней работой
from posts.forms import PostForm
from posts.models import Post, Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

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
        posts_count = Post.objects.all().count()
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
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тест текс1т',
                author=self.user.id,
                group=self.group.id,
            ).exists()
        )
        self.assertEqual(response.status_code, 200)
