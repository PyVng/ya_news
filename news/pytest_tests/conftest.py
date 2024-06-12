import pytest
from django.test.client import Client
from news.models import News, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='Лев Толстой', password='password')

@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(username='Читатель простой', password='password')

@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client

@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client

@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')

@pytest.fixture
def comment(author, news):
    return Comment.objects.create(news=news, author=author, text='Текст комментария')

@pytest.fixture
def client():
    return Client()

# Automatically enable db access for all tests
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture
def news_form_data():
    return {
        'title': 'Новость заголовок',
        'content': 'Содержание новости',
        'slug': 'news-slug'
    }

@pytest.fixture
def comment_form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def comment_form_data():
    return {'text': 'Новый текст комментария'}