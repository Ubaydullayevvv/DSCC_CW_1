from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Prefetch, QuerySet
from django.urls import reverse, reverse_lazy
from django.views import generic

from .models import Comment, Post


class PostListView(generic.ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Post]:
        return (
            Post.objects.select_related("author")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Latest Posts"
        context.setdefault("is_my_posts", False)
        return context


class PostDetailView(generic.DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self) -> QuerySet[Post]:
        return (
            Post.objects.select_related("author")
            .prefetch_related(
                "tags",
                Prefetch(
                    "comments",
                    queryset=Comment.objects.select_related("author").order_by("-created_at"),
                ),
            )
        )


class MyPostsListView(LoginRequiredMixin, PostListView):
    template_name = "blog/post_list.html"

    def get_queryset(self) -> QuerySet[Post]:
        return super().get_queryset().filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "My Posts"
        context["is_my_posts"] = True
        return context


class PostFormMixin:
    fields = ["title", "content", "tags"]
    template_name = "blog/post_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name, field in form.fields.items():
            css_class = "form-control"
            if name == "tags":
                css_class = "form-select"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
        return form


class PostCreateView(LoginRequiredMixin, PostFormMixin, generic.CreateView):
    model = Post

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Post created successfully.")
        return response

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})


class PostAuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostUpdateView(
    LoginRequiredMixin, PostAuthorRequiredMixin, PostFormMixin, generic.UpdateView
):
    model = Post

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Post updated successfully.")
        return response

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(
    LoginRequiredMixin, PostAuthorRequiredMixin, generic.DeleteView
):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Post deleted successfully.")
        return super().delete(request, *args, **kwargs)
