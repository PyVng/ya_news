import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from news.models import Comment
from http import HTTPStatus

@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, comment_form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.FOUND  # 302 редирект после создания комментария
    assert Comment.objects.count() == 2  # один комментарий уже создан в фикстуре, второй создаем тестом
    new_comment = Comment.objects.latest('created')
    assert new_comment.text == comment_form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news

@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=comment_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1  # комментарий из фикстуры

@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment_form_data, comment):
    url = reverse('edit_comment', args=(comment.pk,))
    response = author_client.post(url, comment_form_data)
    assert response.status_code == HTTPStatus.FOUND  # 302 редирект после редактирования комментария
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']

@pytest.mark.django_db
def test_other_user_cant_edit_comment(reader_client, comment_form_data, comment):
    url = reverse('edit_comment', args=(comment.pk,))
    response = reader_client.pos
