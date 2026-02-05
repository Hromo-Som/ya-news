from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News
from news.pytest_tests.conftest import COMMENT_TEXT, NEW_COMMENT_TEXT


def test_anonymous_user_cant_create_comment(
        client,
        get_news_detail_url,
        form_data
):
    """
    Тест проверки отсутсвия возможности
    создания комментария анонимным пользователем.
    """
    client.post(get_news_detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author_client,
        author,
        news,
        get_news_detail_url,
        form_data
):
    """
    Тест проверки наличия возможности
    создания комментария авторизованным пользователем.
    """
    response = author_client.post(get_news_detail_url, data=form_data)
    assertRedirects(response, f'{get_news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        author_client,
        get_news_detail_url
):
    """Тест возможности использования запрещенных слов в комментарии."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(get_news_detail_url, data=bad_words_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client,
        get_news_detail_url,
        comment_delete_url
):
    """Тест возможности удаления комментария автором."""
    url_to_comments = get_news_detail_url + '#comments'
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        comment_delete_url
):
    """Тест отсутствия возможности удаления комментария не автором."""
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        get_news_detail_url,
        comment_edit_url,
        form_data_comment_edit
):
    """Тест возможности редактирования комментария автором."""
    url_to_comments = get_news_detail_url + '#comments'
    response = author_client.post(comment_edit_url,
                                  data=form_data_comment_edit)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        comment_edit_url,
        form_data_comment_edit
):
    """Тест отсутствия возможности редактирования комментария не автором."""
    response = not_author_client.post(comment_edit_url,
                                      data=form_data_comment_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
