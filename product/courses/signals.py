from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count
from users.models import Subscription, CustomUser, Balance
from .models import Group, Course
from users.models import CustomUser
from django.utils import timezone

"""
Учитываем, что при такой логике распределения студентов
в группе может оказаться 1 студент. Чтобы такого не было, 
нужно ввести некий "минимум", начиная с которого группа 
"может существовать". Еще стоит ввести доп. поле в модель
`Group`, например, `is_active`, которое бы определяло, активна 
ли на данный момент группа (достаточно ли в ней студентов).
Тогда бы добавление студентов в группы можно было бы реализовать 
немного по-другому, например дать преимущество "неактивным группам", 
чтобы, при их наличии, новые студенты добавлялись туда. Или вообще 
расформировывать "неактивные" группы. Также в таком случае необходимо
решить: "Что делать, если курс начался, а какая-то группа так и
недобрала студентов?". В общем, здесь нужна еще доп. информация.

Но так как в задании не было дано условия, что группа с одним
студентом существовать не может, то решение этого и не предполагает.
"""

def regather(course: Course):
    groups = course.groups.all()
    subs = Subscription.objects.filter(course=course.pk).select_related('student')
    students = list()
    for sub in subs:
        students.append(sub.student)
    middle = subs.count() // groups.count()
    for group in groups:
        group.users.clear()  # Очищаем группы чтобы предотвратить дубли 
        for student in students[:middle]:
            student.groups.add(group)
        students = students[middle:]
    if students:  # Так как кол-во студентов может не поровну делится на кол-во групп, то могут остаться лишние студенты
        for student, group in zip(students, groups):
            student.groups.add(group)

@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    Если есть свободные группы (те, в которых меньше 30), то добавляем нового
    студента в самую "пустую" из них, так, чтобы кол-во человек не отличалось 
    больше, чем на единицу.
    Если пустых групп нет и курс еще не начался, то нужно создать новую и пересобрать студентов заново,
    чтобы в каждой группе их было примерно поровну.
    """
    if created:
        user = CustomUser.objects.filter(pk=instance.student.pk).first()
        groups = Group.objects.annotate(students=Count('users')).filter(course=instance.course.pk, students__lt=30).order_by('students')
        if groups or instance.course.start_date <= timezone.now():
            # Если есть свободная группа или курс уже начался и группы нельзя пересобрать,
            # то добавляем пользователя в самую пустую из них
            user.groups.add(groups[0])
        else:  # Если все группы заняты, то создаем новую
            new_group = Group(course=instance.course)
            new_group.save()
            regather(instance.course)
            user.groups.add(new_group)

@receiver(post_delete, sender=Subscription)
def post_delete_subscription(sender, instance: Subscription, **kwargs): 
    """
    Удаление пользователя из группы после отмены подписки.
    """
    user = CustomUser.objects.filter(pk=instance.student.pk).first()
    target_group = user.groups.filter(course=instance.course.pk)
    user.groups.remove(target_group.first().pk)
    # regather(instance.course)  # Пересобираем группы курса при удалении пользователя - необязательно

@receiver(post_save, sender=CustomUser)
def post_save_user(sender, instance: CustomUser, created, **kwargs):
    """
    Добавление новому (!) пользователю баланса.
    """
    if created:
        new_balance = Balance(user=instance)
        new_balance.save()
