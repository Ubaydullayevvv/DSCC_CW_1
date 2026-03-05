import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from blog.models import Post


@pytest.fixture
def password():
    return 'StrongPass123'


@pytest.fixture
def user(db, password):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username='author', email='author@example.com', password=password
    )


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_user_registration(client):
    response = client.post(
        reverse('users:register'),
        {
            'username': 'new_user',
            'email': 'new@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        },
    )
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard/')
    assert get_user_model().objects.filter(username='new_user').exists()


@pytest.mark.django_db
def test_user_login(client, user, password):
    response = client.post(
        reverse('users:login'),
        {'username': user.username, 'password': password},
    )
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard/')


@pytest.mark.django_db
def test_create_post(auth_client, user):
    response = auth_client.post(
        reverse('blog:post_create'),
        {'title': 'My Post', 'content': 'Awesome content'},
    )
    assert response.status_code == 302
    post = Post.objects.get(title='My Post')
    assert post.author == user


@pytest.mark.django_db
def test_update_post(auth_client, user):
    post = Post.objects.create(title='Old', content='Old body', author=user)
    response = auth_client.post(
        reverse('blog:post_update', args=[post.pk]),
        {'title': 'Updated', 'content': 'New body'},
    )
    assert response.status_code == 302
    post.refresh_from_db()
    assert post.title == 'Updated'


@pytest.mark.django_db
def test_delete_post(auth_client, user):
    post = Post.objects.create(title='Delete me', content='Body', author=user)
    response = auth_client.post(reverse('blog:post_delete', args=[post.pk]))
    assert response.status_code == 302
    assert not Post.objects.filter(pk=post.pk).exists()
