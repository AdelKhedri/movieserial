from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from user.models import User


def folder_finder(instance, filename):
    class_name = instance.__class__.__name__.lower()
    _type = 'movies' if class_name == 'movie' else 'serials'
    folder_path = f'images/{_type}/{filename}'
    return folder_path


class Geners(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='اسلاگ')

    class Meta:
        verbose_name = 'ژانر'
        verbose_name_plural = 'ژانر ها'
        ordering = ['name']


    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='اسلاگ')

    class Meta:
        verbose_name = 'کشور'
        verbose_name_plural = 'کشور ها'
        ordering = ['name']


    def __str__(self):
        return self.name


class Agents(models.Model):
    name = models.CharField(max_length=150, verbose_name='نام')
    photo = models.ImageField(upload_to='images/actor/', blank=True, verbose_name='عکس')
    imdb_link = models.URLField(blank=True, verbose_name='ادرس imdb')
    role_types = (('actor', 'بازیگر'), ('director', 'کارگردان'))
    role = models.CharField(max_length=8, choices=role_types, default='actor', verbose_name='نقش')

    class Meta:
        verbose_name = 'عامل'
        verbose_name_plural = 'عوامل'
        ordering = ['name']


    def __str__(self):
        return f'{self.name}: {self.id}'


class BaseMedia(models.Model):
    persian_name = models.CharField(max_length=200, verbose_name='نام فارسی')
    english_name = models.CharField(max_length=200, verbose_name='نام انگلیسی')
    year_create = models.IntegerField(verbose_name='سال ساخت')
    slug = models.SlugField(unique=True, verbose_name='اسلاگ')
    countrys = models.ManyToManyField(Country, blank=True, verbose_name='کشور')
    imdb_point = models.DecimalField(max_digits=4, decimal_places=2, validators=[MaxValueValidator(10.0), MinValueValidator(0.0)], verbose_name='امتیاز imdb')
    imdb_link = models.URLField(blank=True, verbose_name='لینک(ارجاع به  imdb)')
    description = models.TextField(max_length=700, blank=True, verbose_name='درباره')
    baner = models.ImageField(upload_to=folder_finder, help_text='480px * 720px', verbose_name='عکس فیلم')
    trailer = models.URLField(blank=True, verbose_name='تریلر')
    director = models.ForeignKey(Agents, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='کارگردان')
    geners = models.ManyToManyField(Geners, verbose_name='ژانر ها')
    dislikes = models.ManyToManyField(User, blank=True, verbose_name='دیس لایک')
    release_date = models.DateTimeField(blank=True, null=True, verbose_name='زمان پخش')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ساخت')
    quality_types = (('Cam', 'پرده سینما'), ('TS', 'تی اس'), ('SD', 'SD'), ('HD', 'HD'), ('FHD', 'Full HD'), ('2K', '2K'), ('4K', '4K'), ('8K', '8K'))
    quality = models.CharField(max_length=3, choices=quality_types, blank=True, verbose_name='کیفیت')
    # Keyword = models

    # point = models.DecimalField(
    #                             max_digits=4,
    #                             decimal_places=2,
    #                             validators=[
    #                                 MaxValueValidator(10.0,),
    #                                 MinValueValidator(0.0)
    #                                 ],
    #                             verbose_name='امتیاز imdb'
    #                             )


    class Meta:
        abstract = True

    def get_absolute_url(self):
        media_type = self.__class__.__name__.lower()
        return reverse(f'media:{media_type}-details', kwargs={'slug': self.slug})

    def get_bookmark_url(self):
        return reverse('media:toggle-bookmark-media', kwargs={'media_type': self.__class__.__name__.lower(), 'slug': self.slug})

    def __str__(self):
        return self.name


class DownloadLink(models.Model):
    quality = models.CharField(max_length=150, verbose_name='کیفیت')
    link = models.URLField(verbose_name='لینک دانلود مستقیم')
    size = models.BigIntegerField(blank=True, null=True, verbose_name='اندازه')
    is_subtitle = models.BooleanField(default=True, verbose_name='زیرنویس')
    subtitle_types = (('nosub', 'بدون زیرنویس'), ('subsoft', 'subsoft'),)
    subtitle_type = models.CharField(max_length=150, default='nosub', choices=subtitle_types, verbose_name='نوع زیرنویس')
    is_persian_sound = models.BooleanField(verbose_name='صدای فارسی')

    class Meta:
        verbose_name = 'لینک دانلود'
        verbose_name_plural = 'لینک های دانلود'
        ordering = ['id']


    def __str__(self):
        return f'{self.quality}: {self.id}'


class Movie(BaseMedia):
    duration = models.TimeField(blank=True, null=True, verbose_name='زمان')
    links = models.ManyToManyField(DownloadLink, verbose_name='لینک های دانلود')
    related_movies = models.ManyToManyField('self', blank=True, verbose_name='فیلم های مشابه')
    stars = models.ManyToManyField(Agents, blank=True, related_name='movie_stars', verbose_name='ستارگان')
    likes = models.ManyToManyField(User, blank=True, related_name='movie_likes', verbose_name='لایک ها')


    class Meta:
        verbose_name = 'سینمایی'
        verbose_name_plural = 'سینمایی ها'
        ordering = ['year_create', 'release_date']


    def __str__(self):
        return f'{self.persian_name}: {self.id}'


class CommentManage(models.Manager):
    def all_accepted(self):
        return self.filter(accepted=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    time = models.DateTimeField(auto_now_add=True, verbose_name='زمان')
    message = models.TextField(verbose_name='متن پیام')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='ایدی کامنت والد')
    media_types = (('serial', 'سریال'), ('movie', 'فیلم'))
    media_type = models.CharField(max_length=6, choices=media_types, verbose_name='نوع مدیا')
    media_id = models.IntegerField(verbose_name='ایدی فیلم/سریال')
    accepted = models.BooleanField(default=False, verbose_name='تایید شده')
    objects = CommentManage()

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'
        ordering = ['time']


    def __str__(self):
        return self.user.__str__()


class Episode(models.Model):
    name = models.CharField(max_length=200, verbose_name='قسمت')
    baner = models.ImageField(upload_to=folder_finder, verbose_name='عکس')
    time = models.TimeField(blank=True, verbose_name='زمان این قسمت')
    links = models.ManyToManyField(DownloadLink, verbose_name='لینک ها')

    class Meta:
        verbose_name = 'قسمت'
        verbose_name_plural = 'قسمت ها'
        ordering = ['id']

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=150, verbose_name='نام')
    episodes = models.ManyToManyField(Episode, verbose_name='قسمت ها')
    status_types = (('creating', 'درحال تولید'),('completed', 'تکمیل شده'), ('canceled', 'کنسل شده'))
    status = models.CharField(max_length=150, choices=status_types, verbose_name='وضعیت')

    class Meta:
        verbose_name = 'فصل'
        verbose_name_plural = 'فصل ها'
        ordering = ['id']


    def __str__(self):
        return self.name


class Serial(BaseMedia):
    sections = models.ManyToManyField(Section, blank=True, verbose_name='فصل ها')
    last_episod = models.CharField(max_length=200, verbose_name='آخرین قسمت')
    related_serials = models.ManyToManyField('self', blank=True, verbose_name='سریال های مشابه')
    stars = models.ManyToManyField(Agents, blank=True, related_name='serial_stars', verbose_name='ستارگان')
    likes = models.ManyToManyField(User, blank=True, related_name='serial_likes', verbose_name='لایک ها')


    class Meta:
        verbose_name = 'سریال'
        verbose_name_plural = 'سریال ها'
        ordering = ['persian_name']


    def __str__(self):
        return f'{self.persian_name}: {self.id}'


class MediaBookmark(models.Model):
    media_types = (('movie', 'فیلم'), ('serial', 'سریال'))
    media_type = models.CharField(max_length=6, choices=media_types, verbose_name='فلیم/سریال')
    media_id = models.IntegerField(verbose_name='ایدی مدیا')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name='کاربر')

    class Meta:
        verbose_name = 'میدیای ذخیره شده'
        verbose_name_plural = 'مدیا های ذخیره شده'
        ordering = ['id']

    def get_media_object(self):
        try:
            return Movie.objects.get(id=self.media_id) if self.media_type == 'movie' else Serial.objects.get(id=self.media_id)
        except:
            pass

    def __str__(self):
        return self.get_media_object().__str__()


# Can use Content-type application.
class MainPageCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name='موضوع')
    all_media = models.ManyToManyField(MediaBookmark, help_text='فقط 10 تای اول نمایش داده میشه', verbose_name='مدیا ها')
    more_category_link = models.URLField(verbose_name='لینک مدیا های بیشتر')
    style_display_types = (('not-scroll', 'بدون اسکرول'), ('scroll', 'با اسکرول'))
    style_display = models.CharField(max_length=10, choices=style_display_types, verbose_name='نوع نمایش دسته بندی')

    class Meta:
        verbose_name = 'دسته بندی صفحه اصلی'
        verbose_name_plural = 'دسته بندی های صفحه اصلی'
        ordering = ['id']

    def get_book_limited(self):
        return self.all_media.all()[:10]

    def __str__(self):
        return '{}:{}'.format(self.title, self.all_media.count())


class MainPageCarousel(models.Model):
    title = models.CharField(max_length=150, verbose_name='توضیح کوتاه')
    media_types = (('movie', 'سینمایی'), ('serial', 'سریال'))
    media_type = models.CharField(max_length=6, choices=media_types, verbose_name='نوع مدیا')
    media_id = models.PositiveIntegerField(verbose_name='مدیا آی دی')
    background_image = models.ImageField(verbose_name='عکس بک گراند', help_text='مستطیلی')

    class Meta:
        verbose_name = 'مدیا کاروسل صفحه خانه'
        verbose_name_plural = 'مدیا های کاروسل صفحه خانه'
        ordering = ['id']

    def get_media_object(self):
        try:
            return Movie.objects.get(id=self.media_id) if self.media_type == 'movie' else Serial.objects.get(id=self.media_id)
        except:
            pass

    def __str__(self):
        return self.title


class ContactUs(models.Model):
    name = models.CharField(max_length=150, verbose_name='')
    email = models.EmailField(verbose_name='')
    subject = models.CharField(max_length=300, verbose_name='')
    message = models.TextField(verbose_name='')

    class Meta:
        verbose_name = 'پیام تماس با ما'
        verbose_name_plural = 'پیام های تماس با ما'

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=150, verbose_name='نام')
    role = models.CharField(max_length=150, verbose_name='سمت')
    picture = models.ImageField(upload_to='images', verbose_name='عکس')
    social_facebook = models.URLField(verbose_name='ادرس فیسبوک')
    social_instagram = models.URLField(verbose_name='ادرس اینستاگرام')
    social_linkedin = models.URLField(verbose_name='ادرس لینکدین')
    social_github = models.URLField(verbose_name='ادرس گیت هاب')

    class Meta:
        verbose_name = 'عضو تیم'
        verbose_name_plural = 'اعضای تیم'

    def __str__(self):
        return self.name
