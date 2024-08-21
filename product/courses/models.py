from django.db import models

class Course(models.Model):
    """Модель продукта - курса."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=250,
        verbose_name='URL'
    )
    author = models.CharField(
        max_length=250,
        verbose_name='Автор',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса'
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена'
    )
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',) 


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=250,
        verbose_name='URL'
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )
    course = models.ForeignKey(Course, 
        on_delete=models.CASCADE, 
        related_name='lessons',
        verbose_name='Курс'
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""

    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='Курс'
    )

    @property
    def students_amount(self):
        return self.users.count()

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)

