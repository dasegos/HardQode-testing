from django.contrib.auth.models import AbstractUser
from django.db import models

from courses.models import Course, Group

class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    groups = models.ManyToManyField(Group,
        verbose_name='Группы',
        related_name='users',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()
    
    def is_student(self, course: Course) -> bool:
        '''Проверка, является ли пользователь студентов определенного курса.'''
        if Subscription.objects.filter(student=self, course=course).first():
            return True
        return False


class Balance(models.Model):
    """Модель баланса пользователя."""

    amount = models.PositiveIntegerField(
        default=1000,                    
        verbose_name='Бонусы'
    )
    user = models.OneToOneField(CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Студент'
    )

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)

    def add_bonuses(self, bonuses):
        self.amount += bonuses

    def reduce_bonuses(self, bonuses):
        self.amount -= bonuses


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    student = models.ForeignKey(CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Студент'
    )
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    active_since = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Активна с'
    )

    def __str__(self) -> str:
        return f'{self.student} - {self.course.title}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
