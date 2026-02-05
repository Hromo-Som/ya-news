import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


def test_news_count(client, many_news):
    """Тест проверки количества постов на станице."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    """Тест проверки сортировки постов на странице."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, many_comments, get_news_detail_url):
    """Тест проверки сортировки комментриев на странице."""
    response = client.get(get_news_detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, get_news_detail_url):
    """
    Тест проверки отсутствия формы для отправки
    комментария для анонимного пользователя.
    """
    response = client.get(get_news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, get_news_detail_url):
    """
    Тест проверки наличия формы для отправки
    комментария для авторизованного пользователя.
    """
    response = author_client.get(get_news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
