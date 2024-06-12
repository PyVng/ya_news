import pytest
from django.urls import reverse
from http import HTTPStatus
from news.models import Comment
from pytest_django.asserts import assertRedirects, assertFormError

@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news, comment_form_data):
    url = reverse('news:detail', args=[news.id])
    response = client.post(url, data=comment_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_authorized_user_can_post_comment(author_client, news, comment_form_data):
    url = reverse('news:detail', args=[news.id])
    response = author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.latest('created')
    assert new_comment.text == comment_form_data['text']

@pytest.mark.django_db
def test_comment_with_prohibited_words_not_published(author_client, news):
    prohibited_words = ['редиска', 'негодяй']
    for bad_word in prohibited_words:
        comment_form_data = {'text': f'This is a {bad_word}'}
        url = reverse('news:detail', args=[news.id])
        response = author_client.post(url, data=comment_form_data)
        # Ожидаем, что форма вернет ошибку и останется на той же странице
        assert response.status_code == HTTPStatus.OK
        assertFormError(response, 'form', 'text', 'Не ругайтесь!')
        # Проверяем, что комментарий не был создан
        assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_author_can_edit_own_comment(author_client, comment, comment_form_data):
    url = reverse('news:edit', args=[comment.id])
    response = author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']

@pytest.mark.django_db
def test_author_can_delete_own_comment(author_client, comment):
    url = reverse('news:delete', args=[comment.id])
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_user_cant_edit_other_user_comment(reader_client, comment, comment_form_data):
    url = reverse('news:edit', args=[comment.id])
    response = reader_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != comment_form_data['text']

@pytest.mark.django_db
def test_user_cant_delete_other_user_comment(reader_client, comment):
    url = reverse('news:delete', args=[comment.id])
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
