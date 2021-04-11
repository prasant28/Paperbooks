from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.shortcuts import reverse
from tinymce import HTMLField

publication_choice = (
    ('NONE', 'NONE'),
    ('Alok Publication', 'Alok Publication'),
    ('BK Publication', 'BK Publication'),
    ('EM Publication', 'EM Publication'),
    ('Khanna Publication', 'Khanna Publication')
)
branch_choice = (
    ('NONE', 'NONE'),
    ('All', 'All'),
    ('CSE', 'CSE'),
    ('ECE', 'ECE'),
    ('EE', 'EE'),
    ('EEE', 'EEE'),
    ('MECH', 'MECH'),
    ('CIVIL', 'CIVIL')
)

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    device = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = self.device
        return str(name)


class book(models.Model):
    book_nm = models.CharField(max_length=500)
    author_nm = models.CharField(max_length=500, default='None')
    publisher_nm = models.CharField(
        choices=publication_choice, max_length=30, default='NONE')
    branch = models.CharField(choices=branch_choice,
                              max_length=10, default='NONE')
    edition = models.CharField(max_length=100, default='First Edition')
    book_price = models.FloatField(default=0)
    book_desc = HTMLField()
    stock = models.IntegerField(default=0)
    sale_price = models.FloatField(default=0)
    book_image = models.FileField(upload_to='book', default='none')
    slug = models.SlugField()
    featured = models.BooleanField(default=False)
    visit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.book_nm

    def get_absolute_url(self):
        return reverse("core:book", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_buy_now_url(self):
        return reverse("core:buy-now", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_average_rating(self):
        reviews = Review.objects.filter(
            book=self).aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg = float(reviews["avarage"])
        return avg


class orderbook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    Book = models.ForeignKey(book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.Book.book_nm}"

    def get_total_book_price(self):
        return self.quantity * self.Book.book_price


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    books = models.ManyToManyField(orderbook)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_stotal(self):
        total = 0
        for order_book in self.books.all():
            total += order_book.get_total_book_price()
        return total

    def get_total(self):
        total = 0
        for order_book in self.books.all():
            total += order_book.get_total_book_price()
            total += 40
        return total


class post(models.Model):
    post_title = models.CharField(max_length=500)
    post_auth = models.CharField(max_length=500)
    post_category = models.CharField(max_length=500)
    post_tag = models.CharField(max_length=500)
    post_date = models.DateField()
    post_image = models.FileField(upload_to='post')
    post_desc = HTMLField()
    comment_count = models.IntegerField()
    likes = models.ManyToManyField(User, related_name='post_like')
    visit = models.PositiveIntegerField(default=0)
    slug = models.SlugField()

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.post_title

    def get_absolute_url(self):
        return reverse("core:post", kwargs={
            'slug': self.slug
        })


class Comment(models.Model):
    post = models.ForeignKey(
        post, related_name="comments", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    content = models.TextField()
    rep = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return "Comment by {}".format(self.name)


class Review(models.Model):
    book = models.ForeignKey(
        book, related_name="reviews", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    rate = models.IntegerField(default=1)
    review = models.TextField()

    def __str__(self):
        return "review by {}".format(self.user.username)


class Subscribe(models.Model):
    email = models.EmailField()

    def __str__(self):
        return 'subs by {}'.format(self.email)
