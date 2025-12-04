from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image  
import os


class PaymentAccess(models.Model):
    """Model to track which users have paid to view which posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    post = models.ForeignKey("blog.Post", on_delete=models.CASCADE, related_name="payments")
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} - {self.post} - {self.paid}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, help_text="Phone number for Mpesa payments (format: 254...)")
    image = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize the profile image if necessary. Be defensive: the default
        # image file may not exist (for example in fresh clones), so guard
        # against missing files to avoid crashing on Profile.save().
        try:
            # Only attempt to open if the file actually exists
            if hasattr(self.image, 'path') and os.path.exists(self.image.path):
                img = Image.open(self.image.path)

                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
        except Exception:
            # If anything goes wrong (missing file, PIL error), skip resizing.
            # This prevents site crashes when creating Profiles while the
            # default image hasn't been added to MEDIA_ROOT yet.
            pass


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Automatically save the Profile when the User is saved"""
    instance.profile.save()
