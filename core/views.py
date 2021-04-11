from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import book, Order, orderbook, post, Subscribe, Review, Customer
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import RegisterForm, CommentForm, ReviewForm, ContactForm
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator


def is_valid_queryparam(param):
    return param != '' and param is not None


def home(request):
    context = {
        'books': book.objects.all().filter(featured=True)[:6],
        'posts': post.objects.all().order_by('post_date')[:3]
    }
    return render(request, "homepage.html", context)


def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            from_email = form.cleaned_data['your_email']
            name = form.cleaned_data['your_name']
            subject = form.cleaned_data['your_subject']
            msg = form.cleaned_data['your_message']
            message = f'email id- {from_email} \n Name-{name} \n message- {msg}'
            send_mail(subject, message, from_email, ['rohan4ucool2@gmail.com'])
            messages.info(request, "Thank You For Contacting Us.")
            return redirect(request.META['HTTP_REFERER'])
    return render(request, "contact-us.html", {'form': form})


def blog(request):
    qs = post.objects.all().order_by('-post_date')
    s_query = request.GET.get("s_p")
    cat = request.GET.get("category")
    if s_query != '' and s_query is not None:
        qs = qs.filter(post_title__icontains=s_query)

    if is_valid_queryparam(cat) and cat != 'Select Category':
        qs = qs.filter(post_category=cat)

    paginator = Paginator(qs, 3)  # Show 3 per page.

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    pop = post.objects.all().order_by('-visit')[:4]
    return render(request, 'blog.html', {'posts': posts, 'pop': pop})


def bookshelf(request):
    qs = book.objects.all()
    s_query = request.GET.get("s")
    pub = request.GET.get('publication')
    brn = request.GET.get('branch')
    price_min = request.GET.get('min_price')
    price_max = request.GET.get('max_price')
    odr_by = request.GET.get('orderby')

    def send_selected_combo(self):
        value_from_select = self.request.GET.get('branch')
        return value_from_select

    if s_query != '' and s_query is not None:
        qs = qs.filter(book_nm__icontains=s_query)

    if is_valid_queryparam(pub) and pub != 'Select Publication':
        qs = qs.filter(publisher_nm=pub)

    if is_valid_queryparam(brn) and brn != 'Select Branch':
        qs = qs.filter(branch=brn)

    if is_valid_queryparam(price_min):
        qs = qs.filter(book_price__gte=price_min)

    if is_valid_queryparam(price_max):
        qs = qs.filter(book_price__lte=price_max)

    if is_valid_queryparam(odr_by):
        qs = qs.order_by(odr_by)

    paginator = Paginator(qs, 6)  # Show 6 per page.

    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    return render(request, 'bookshelf.html', {'books': books, 'query': pub or brn})


def home_search(request):
    qs1 = book.objects.all()
    qs2 = post.objects.all()
    s_query = request.GET.get("s_h")
    pub = request.GET.get('publication')
    brn = request.GET.get('branch')

    if s_query != '' and s_query is not None:
        qs1 = qs1.filter(Q(book_nm__icontains=s_query) | Q(publisher_nm__icontains=s_query) | Q(
            branch__icontains=s_query) | Q(author_nm__icontains=s_query)).distinct()
        qs2 = qs2.filter(Q(post_title__icontains=s_query) | Q(post_auth__icontains=s_query) | Q(
            post_category__icontains=s_query) | Q(post_tag__icontains=s_query)).distinct()
    # else:
    #     qs1 = '',
    #     qs2 = ''

    if is_valid_queryparam(pub) and pub != 'Select Publication':
        qs1 = qs1.filter(publisher_nm=pub)
    if is_valid_queryparam(brn) and brn != 'Select Branch':
        qs1 = qs1.filter(branch=brn)

    context = {

        'query': s_query or pub or brn,
        'books': qs1,
        'posts': qs2
    }

    return render(request, "search.html", context)


class CartView(View):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, "cart.html", context)
        except ObjectDoesNotExist:
            return redirect("/")


@login_required
def myaccount(request):
    return render(request, "MyAccount.html")


@login_required
def orders(request):
    return render(request, "Orders.html")


@login_required
def address(request):
    return render(request, "Address.html")


@login_required
def checkout(request):
    return render(request, "checkout.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        form = RegisterForm()
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                mail = form.cleaned_data['email']
                if User.objects.filter(email=mail).exists():
                    messages.info(
                        request, "email-id Already registered, try different one or login!")
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    form.save()
                    fnm = form.cleaned_data['first_name']
                    subject = 'Welcome to PaperBooks-Learning Redefined'
                    message = f'Hi {fnm}, thank you for registering in PaperBooks-Learning Redefined.'
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [mail]
                    send_mail(subject, message, from_email, recipient_list)
                    messages.info(request, " Sucessfully Registered ")
                    return redirect('/accounts/login')

        context = {'form': form}
        return render(request, 'register.html', context)


def logoutCust(request):
    logout(request)
    return redirect('/accounts/login')


def AMIGOS(request):
    return render(request, "ami/amigos.html")


class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    template_name = 'book_detail.html'
    model = book

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        # book.objects.filter(pk=pk).update(visit=F('visit') + 1)
        context['book_list'] = book.objects.all().order_by('visit')[:6]
        context['related'] = book.objects.all()
        return context

    def get(self, request, slug, **kwargs):
        Book = get_object_or_404(book, slug=slug)
        Book.visit += 1
        Book.save()
        return super(BookDetailView, self).get(request, slug, **kwargs)

    def post(self, request, slug, **kwargs):
        Book = get_object_or_404(book, slug=slug)
        form = ReviewForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.rate = form.cleaned_data['rate']
                form.review = form.cleaned_data['review']
                form.instance.user = request.user
                form.instance.book = Book
                form.save()
        return redirect(request.META['HTTP_REFERER'])


class PostDetailView(generic.DetailView, FormMixin):
    template_name = 'Post_detail.html'
    model = post
    form_class = CommentForm

    def get_context_data(self, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['pop'] = post.objects.all().order_by('-visit')[:4]
        context['form'] = CommentForm()
        return context

    def get(self, request, slug, **kwargs):
        Post = get_object_or_404(post, slug=slug)
        Post.visit += 1
        Post.save()
        return super(PostDetailView, self).get(request, slug, **kwargs)

    def post(self, request, slug, **kwargs):
        Post = get_object_or_404(post, slug=slug)
        form = CommentForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.instance.post = Post
                if request.user.is_authenticated:
                    form.instance.name = request.user
                form.save()
        return redirect(request.META['HTTP_REFERER'])


def LikeView(request, pk):
    Post = get_object_or_404(post, id=pk)
    Post.likes.add(request.user)
    return redirect(request.META['HTTP_REFERER'])


@login_required
def add_to_cart(request, slug):
    Book = get_object_or_404(book, slug=slug)
    order_book, created = orderbook.objects.get_or_create(
        Book=Book, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(Book__slug=Book.slug).exists():
            order_book.quantity += 1
            order_book.save()
            messages.info(
                request, " Cart updated")
        else:
            order.books.add(order_book)
            messages.info(request, "Added to your cart.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.books.add(order_book)
        messages.info(request, "Added to your cart.")
    return redirect(request.META['HTTP_REFERER'])


@login_required
def buy_now(request, slug):
    Book = get_object_or_404(book, slug=slug)
    order_book, created = orderbook.objects.get_or_create(
        Book=Book, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(Book__slug=Book.slug).exists():
            order_book.quantity += 1
            order_book.save()
        else:
            order.books.add(order_book)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.books.add(order_book)
    return redirect("core:cart")


@login_required
def remove_from_cart(request, slug):
    Book = get_object_or_404(book, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.books.filter(Book__slug=Book.slug).exists():
            order_book = orderbook.objects.filter(
                Book=Book,
                user=request.user,
                ordered=False
            )[0]
            order.books.remove(order_book)
            order_book.delete()
            return redirect(request.META['HTTP_REFERER'])


@login_required
def remove_single_item_from_cart(request, slug):
    Book = get_object_or_404(book, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.books.filter(Book__slug=Book.slug).exists():
            order_book = orderbook.objects.filter(
                Book=Book,
                user=request.user,
                ordered=False
            )[0]
            if order_book.quantity > 1:
                order_book.quantity -= 1
                order_book.save()
            else:
                order.books.remove(order_book)
            return redirect(request.META['HTTP_REFERER'])


def footer(request):
    if request.method == 'POST':
        mail = request.POST.get('email')
        qs = Subscribe.objects.filter(email=mail)
        if qs:
            messages.info(request, "Already Subscribed.")
            return redirect(request.META['HTTP_REFERER'])
        else:
            obj = Subscribe.objects.create(email=mail)
            obj.save()
            subject = f'Newsletter Subscribed'
            message = f'Thank you for subscribing our newsletter \n Regards, Amigos'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [mail]
            send_mail(subject, message, from_email, recipient_list)
            messages.info(request, "Subscribed Sucessfully.")
            return redirect(request.META['HTTP_REFERER'])
    return render(request, "footer.html", {'form': form})


@login_required
def account_details(request):
    if request.method == 'POST':
        first = request.POST.get('first_name')
        last = request.POST.get('last_name')
        mail = request.POST.get('email')
        owner = request.user
        if owner.first_name == first:
            pass
        else:
            owner.first_name = first
            owner.save()
        if owner.last_name == last:
            pass
        else:
            owner.last_name = last
            owner.save()
        messages.info(request, 'Sucessfully updated')
        return redirect(request.META['HTTP_REFERER'])
    return render(request, "AccountDetails.html")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'AccountDetails.html', {
        'form': form
    })
