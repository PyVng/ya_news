import pytest
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from news.models import News, Comment
from news.forms import CommentForm

@pytest.mark.django_db
def test_news_count_on_homepage(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= settings.NEWS_COUNT_ON_HOME_PAGE

@pytest.mark.django_db
def test_news_order_on_homepage(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates

@pytest.mark.django_db
def test_comments_order_on_detail_page(client, news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(news=news, author=author, text=f'Text {index}')
        comment.created = now + timedelta(days=index)
        comment.save()
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps

@pytest.mark.django_db
def test_anonymous_user_has_no_comment_form(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert 'form' not in response.context

@pytest.mark.django_db
def test_authorized_user_has_comment_form(author_client, news):
    url = reverse('news:detail', args=[news.id])
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
