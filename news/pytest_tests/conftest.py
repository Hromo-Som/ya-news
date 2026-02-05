from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    """Создание модели пользователя 'Автор'."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создание модели пользователя 'Не автор'."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Авторизация 'Автора' в клиенте."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Авторизация 'Не автора' в клиенте."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    """Создание объекта новости."""
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def id_for_args(news):
    """Получение id конкретной новости."""
    return (news.id,)


@pytest.fixture
def many_news(db):
    """Создание множества объектов новостей."""
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    """Созадние объекта комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    comment.save()
    return comment


@pytest.fixture
def many_comments(news, author):
    """Создание множества объектов комментариев."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def get_news_detail_url(news):
    """Получение url конкретной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def form_data():
    """Возвращает данные для создания объекта комментария."""
    return {
        'text': COMMENT_TEXT
    }

@pytest.fixture
def form_data_comment_edit():
    """Возвращает данные для редактирования объекта комментария."""
    return {
        'text': NEW_COMMENT_TEXT
    }

@pytest.fixture
def comment_delete_url(comment):
    """Получение url удаления конкретного комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def comment_edit_url(comment):
    """Получение url редактирования конкретного комментария."""
    return reverse('news:edit', args=(comment.id,))
