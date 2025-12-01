from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    # Item type choices
    LOST = 'lost'
    FOUND = 'found'
    ITEM_TYPE_CHOICES = [
        (LOST, 'Lost Item'),
        (FOUND, 'Found Item'),
    ]
    
    # Status choices
    ACTIVE = 'active'
    RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (RESOLVED, 'Resolved'),
    ]
    
    # Category choices
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('documents', 'Documents'),
        ('jewelry', 'Jewelry'),
        ('vehicle', 'Vehicle'),
        ('pet', 'Pet'),
        ('clothing', 'Clothing'),
        ('money', 'Money/Wallet'),
        ('keys', 'Keys'),
        ('phone', 'Phone'),
        ('other', 'Other'),
    ]
    
    # Fields
    title = models.CharField(max_length=200)
    content = models.TextField()
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default=LOST)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    location = models.CharField(max_length=200, default='Kenya')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    image = models.ImageField(upload_to='post_pics/%Y/%m/%d/', null=True, blank=True)
    
    date_posted = models.DateTimeField(default=timezone.now)
    date_item_lost_found = models.DateField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return f"[{self.get_item_type_display()}] {self.title}"
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})