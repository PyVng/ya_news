import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ]
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=[args.id] if args else None)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_pages_availability_for_author(author_client, name, comment):
    url = reverse(name, args=[comment.id])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_anonymous_user_redirect_to_login_for_comment_pages(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=[comment.id])
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)

@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_other_user_cant_access_comment_pages(reader_client, name, comment):
    url = reverse(name, args=[comment.id])
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
