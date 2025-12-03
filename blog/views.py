from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Post
from users.models import Profile
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .services import PostFilterService

class HomeView(ListView):
    model = Post
    template_name = 'blog/Home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Use the service to filter posts
        queryset = PostFilterService.filter_posts(queryset, self.request.GET)
        
        # Ensure profiles exist (defensive programming)
        author_ids = queryset.values_list('author', flat=True).distinct()
        for uid in author_ids:
            Profile.objects.get_or_create(user_id=uid)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass filter parameters back to the template
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_item_type'] = self.request.GET.get('item_type', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_location'] = self.request.GET.get('location', '')
        context['selected_status'] = self.request.GET.get('status', '')
        
        # Dropdown options
        context['categories'] = Post.CATEGORY_CHOICES
        context['locations'] = Post.objects.values_list('location', flat=True).distinct()
        context['item_types'] = Post.ITEM_TYPE_CHOICES
        context['statuses'] = Post.STATUS_CHOICES
        
        return context

class AboutView(TemplateView):
    template_name = 'blog/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Post.objects.filter(image__isnull=False).exclude(image='').order_by('-date_posted')[:12]
        return context

class LandingView(TemplateView):
    template_name = 'blog/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.all().order_by('-date_posted')[:6]
        return context

# Keep existing CBVs but ensure they are clean
class PostListView(ListView):
    # This seems redundant with HomeView, but keeping it if it was used specifically elsewhere.
    # Based on original code, HomeView replaces the 'home' FBV which was the main list.
    # The original PostListView was also pointing to 'blog/Home.html'.
    # We can redirect to HomeView or keep it as an alias.
    model = Post
    template_name = 'blog/Home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = PostFilterService.filter_posts(queryset, self.request.GET)
        return queryset

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        Profile.objects.get_or_create(user=post.author)
        
        related_posts = Post.objects.filter(
            category=post.category
        ).exclude(pk=post.pk).order_by('-date_posted')[:3]
        context['related_posts'] = related_posts
        
        author_posts = Post.objects.filter(author=post.author)
        context['author_posts_count'] = author_posts.count()
        context['author_lost_count'] = author_posts.filter(item_type='lost').count()
        context['author_found_count'] = author_posts.filter(item_type='found').count()
        
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'item_type', 'category', 'location', 'status', 'date_item_lost_found', 'image']
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog-home')

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'item_type', 'category', 'location', 'status', 'date_item_lost_found', 'image']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog-home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully.')
        return super().delete(request, *args, **kwargs)
