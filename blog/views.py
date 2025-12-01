from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, DeleteView
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


def home(request):
    posts = Post.objects.all().order_by('-date_posted')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    item_type = request.GET.get('item_type', '')
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    status = request.GET.get('status', '')
    
    # Apply filters
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    if item_type:
        posts = posts.filter(item_type=item_type)
    
    if category:
        posts = posts.filter(category=category)
    
    if location:
        posts = posts.filter(location__icontains=location)
    
    if status:
        posts = posts.filter(status=status)
    
    # Get unique categories and locations for the filter dropdowns
    categories = Post.CATEGORY_CHOICES
    locations = Post.objects.values_list('location', flat=True).distinct()
    item_types = Post.ITEM_TYPE_CHOICES
    statuses = Post.STATUS_CHOICES
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'selected_item_type': item_type,
        'selected_category': category,
        'selected_location': location,
        'selected_status': status,
        'categories': categories,
        'locations': locations,
        'item_types': item_types,
        'statuses': statuses,
    }
    return render(request, 'blog/Home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/Home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        posts = Post.objects.all().order_by('-date_posted')
        
        # Apply filters
        search_query = self.request.GET.get('q', '')
        item_type = self.request.GET.get('item_type', '')
        category = self.request.GET.get('category', '')
        location = self.request.GET.get('location', '')
        status = self.request.GET.get('status', '')
        
        if search_query:
            posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        if item_type:
            posts = posts.filter(item_type=item_type)
        if category:
            posts = posts.filter(category=category)
        if location:
            posts = posts.filter(location__icontains=location)
        if status:
            posts = posts.filter(status=status)
        
        # Ensure each post's author has a Profile to avoid template errors when
        # templates access `post.author.profile`. Create missing profiles on the fly.
        author_ids = posts.values_list('author', flat=True).distinct()
        for uid in author_ids:
            # get_or_create is safe and idempotent
            Profile.objects.get_or_create(user_id=uid)

        return posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_item_type'] = self.request.GET.get('item_type', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_location'] = self.request.GET.get('location', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['categories'] = Post.CATEGORY_CHOICES
        context['locations'] = Post.objects.values_list('location', flat=True).distinct()
        context['item_types'] = Post.ITEM_TYPE_CHOICES
        context['statuses'] = Post.STATUS_CHOICES
        # Also ensure profiles exist for any authors shown on the page (defensive)
        author_ids = self.get_queryset().values_list('author', flat=True).distinct()
        for uid in author_ids:
            Profile.objects.get_or_create(user_id=uid)

        return context


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
        # Ensure the post author has a Profile to avoid template attribute errors
        Profile.objects.get_or_create(user=post.author)
        
        # Get related posts (same category, excluding current post)
        related_posts = Post.objects.filter(
            category=post.category
        ).exclude(pk=post.pk).order_by('-date_posted')[:3]
        context['related_posts'] = related_posts
        
        # Get author statistics
        author_posts = Post.objects.filter(author=post.author)
        context['author_posts_count'] = author_posts.count()
        context['author_lost_count'] = author_posts.filter(item_type='lost').count()
        context['author_found_count'] = author_posts.filter(item_type='found').count()
        
        return context


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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'item_type', 'category', 'location', 'status', 'date_item_lost_found', 'image']
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog-home')


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog-home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        """Add a success message when a post is deleted."""
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Post deleted successfully.')
        return response


def about(request):
    # Get all posts with images for gallery
    images = Post.objects.filter(image__isnull=False).exclude(image='').order_by('-date_posted')[:12]
    context = {
        'images': images,
    }
    return render(request, 'blog/about.html', context)


def landing(request):
    """Simple landing page that highlights the site and links to the blog home or login/register."""
    # show a few recent posts for preview
    recent_posts = Post.objects.all().order_by('-date_posted')[:6]
    context = {
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/landing.html', context)
