# Тестовое задание Django/Backend

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

Проект представляет собой площадку для размещения онлайн-курсов с набором уроков. Доступ к урокам предоставляется после покупки курса (подписки). Внутри курса студенты автоматически распределяются по группам.

Перед тем, как приступить к выполнению задания, советуем изучить документацию, которая поможет в выполнении заданий:

1. https://docs.djangoproject.com/en/4.2/intro/tutorial01/
2. https://docs.djangoproject.com/en/4.2/topics/db/models/
3. https://docs.djangoproject.com/en/4.2/topics/db/queries/
4. https://docs.djangoproject.com/en/4.2/ref/models/querysets/
5. https://docs.djangoproject.com/en/4.2/topics/signals/
6. https://www.django-rest-framework.org/tutorial/quickstart/
7. https://www.django-rest-framework.org/api-guide/viewsets/
8. https://www.django-rest-framework.org/api-guide/serializers/

# Построение системы для обучения

Суть задания заключается в проверке знаний построения связей в БД и умении правильно строить запросы без ошибок N+1.

### Построение архитектуры(5 баллов)

В этом задании у нас есть 4 бизнес-задачи на хранение:

1. Создать сущность продукта. У продукта должен быть создатель этого продукта(автор/преподаватель). Название продукта, дата и время старта, стоимость. **(0,5 балла)**  
**_Done_**
```
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
```
2. Определить, каким образом мы будем понимать, что у пользователя(клиент/студент) есть доступ к продукту. 
**(2 балла)**   
**_Done_**  
>_У пользователя есть доступ к продукту, если у него есть подписка на этот курс, то есть существует запись в таблиц `Subscription`, где `course` - ссылка на курс, `user` - ссылка на этого пользователя. Для этого есть метод в модели `CustomUser` - `is_student(self, course: Course)`, который проверяет, является ли пользователь студентом определенного курса._
3. Создать сущность урока. Урок может принадлежать только одному продукту. В уроке должна быть базовая информация: название, ссылка на видео. **(0,5 балла)**  
**_Done_**
```
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
```
4. Создать сущность баланса пользователя. Баланс пользователя не может быть ниже 0, баланс пользователя при создании пользователя равен 1000 бонусов. Бонусы могут начислять только через админку или посредством `REST-апи` с правами `is_staff=True`. **(2 балла)**  
**_Done_** 

Сущность баланса:
```
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
```
`ViewSet` баланса:
```
class BalancesViewset(viewsets.ModelViewSet):
    """Баланс и Бонусы."""
 
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = (permissions.IsAdminUser,)
    http_method_names = ["get", "head", "options", "patch"]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BalanceSerializer
        return ChangeBalanceSerializer
```
>! Чтобы изменить баланс, надо отправить PATCH запрос на адрес `api/v1/balances/{id баланса}` и передать параметр `amount`. Это может делать только админ.

### Реализация базового сценария оплат (11 баллов)

В этом пункте потребуется использовать выполненную вами в прошлом задании архитектуру:

1. Реализовать API на список продуктов, доступных для покупки(доступных к покупке = они еще не куплены пользователем и у них есть флаг доступности), которое бы включало в себя основную информацию о продукте и количество уроков, которые принадлежат продукту. **(2 балла)**
>_Для этого в сериализаторе `CourseSerializer` есть поле `is_bought`, которое проверяет, является ли пользователь, запрашивающий курсы, студентом конкретного курса. `True` - является, `False` - нет._
2. Реализовать API оплаты продукты за бонусы. Назовем его …/pay/ **(3 балла)**  
**_Done_**  

`View`:
```
    @action(methods=['get'], detail=True, permission_classes=(permissions.IsAuthenticated,))
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""
        response = make_payment(request.user, pk)
        return response
```
`make_payment`:
```
def make_payment(user: CustomUser, cid: int):
    target_course = Course.objects.filter(pk=cid).first()
    target_balance = user.balance
    if not user.is_student(target_course.pk):  # Проверка, что курс еще не куплен пользователем
        if target_balance.amount >= target_course.price:  # Проверка, что баланс пользователя больше или равен стоимости курса
            target_balance.reduce_bonuses(target_course.price)
            new_sub = Subscription(student=user, course=target_course) # Если все условия прошли, то создаем новую запись
            new_sub.save()                                             # в таблице подписок
            return Response(data={'detail' : 'success'}, status=HTTP_200_OK)
        else:
            return Response(data={'detail' : 'insufficient funds'}, status=HTTP_402_PAYMENT_REQUIRED)
    else:
        return Response(data={'detail' : 'course already bought'}, status=HTTP_409_CONFLICT)
```
3. По факту оплаты и списания бонусов с баланса пользователя должен быть открыт доступ к курсу. **(2 балла)**  
**_Done_**
> _Создаем новую запись `Subscription`_
4. После того, как доступ к курсу открыт, пользователя необходимо **равномерно** распределить в одну из 10 групп студентов. **(4 балла)**  
**_Done_**  
```
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
```

### Результат выполнения:

1. Выполненная архитектура на базе данных SQLite с использованием Django.
2. Реализованные API на базе готовой архитектуры.

### Мы ожидаем:

Ссылка на публичный репозиторий в GitHub с выполненным проектом.

**Нельзя форкать репозиторий. Используйте git clone.**

## Если вы все сделали, но хотите еще, то можете реализовать API для отображения статистики по продуктам. 
Необходимо отобразить список всех продуктов на платформе, к каждому продукту приложить информацию:

1. Количество учеников занимающихся на продукте.  
**_Done_**
2. На сколько % заполнены группы? (среднее значение по количеству участников в группах от максимального значения у
частников в группе, где максимальное = 30).  
**_Done_**
3. Процент приобретения продукта (рассчитывается исходя из количества полученных доступов к продукту деленное на общее количество пользователей на платформе).  
**_Done_**

**Код доп. задания:**
```
class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)
    is_bought = serializers.SerializerMethodField(read_only=True)

    def get_lessons_count(self, obj) -> int:
        """Количество уроков в курсе."""
        return obj.lessons.count()

    def get_students_count(self, obj) -> int:
        """Общее количество студентов на курсе."""
        amount = Subscription.objects.filter(course=obj.pk).count()
        return amount
    
    def get_groups_filled_percent(self, obj) -> int:
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        try:
            average = obj.groups.annotate(students=Count('users')).aggregate(Avg('students'))
            return (average['students__avg'] / 30) * 100
        except:
            return 0.0
     
    def get_demand_course_percent(self, obj) -> int:
        """Процент приобретения курса."""
        users = CustomUser.objects.all().count()
        return (self.get_students_count(obj) / users) * 100

    def get_is_bought(self, obj) -> bool:
        """Определяет, куплен ли курс пользователем"""
        target_user = CustomUser.objects.filter(pk=self.context['request'].user.pk).first()
        return target_user.is_student(obj.pk)

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons',
            'lessons_count',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
            'is_bought'
        )
```

## Доп. задание
### __Реализуйте следующее API__

<details><summary> GET: http://127.0.0.1:8000/api/v1/courses/  - показать список всех курсов.
</summary>

    200 OK:
    ```
    [
        {
            "id": 3,
            "author": "Михаил Потапов",
            "title": "Backend developer",
            "start_date": "2024-03-03T12:00:00Z",
            "price": "150000",
            "lessons_count": 0,
            "lessons": [],
            "demand_course_percent": 0,
            "students_count": 0,
            "groups_filled_percent": 0
        },
        {
            "id": 2,
            "author": "Михаил Потапов",
            "title": "Python developer",
            "start_date": "2024-03-03T12:00:00Z",
            "price": "120000",
            "lessons_count": 3,
            "lessons": [
                {
                    "title": "Урок №1"
                },
                {
                    "title": "Урок №2"
                },
                {
                    "title": "Урок №3"
                }
            ],
            "demand_course_percent": 84,
            "students_count": 10,
            "groups_filled_percent": 83
        },
        {
            "id": 1,
            "author": "Иван Петров",
            "title": "Онлайн курс",
            "start_date": "2024-03-03T12:00:00Z",
            "price": "56000",
            "lessons_count": 3,
            "lessons": [
                {
                    "title": "Урок №1"
                },
                {
                    "title": "Урок №2"
                },
                {
                    "title": "Урок №3"
                }
            ],
            "demand_course_percent": 7,
            "students_count": 1,
            "groups_filled_percent": 10
        }
    ]
    ```
</details>


<details><summary> GET: http://127.0.0.1:8000/api/v1/courses/2/groups/  - показать список групп определенного курса.</summary> 

    200 OK:
    ```
    [
        {
            "title": "Группа №3",
            "course": "Python developer",
            "students": [
                {
                    "first_name": "Иван",
                    "last_name": "Грозный",
                    "email": "user9@user.com"
                },
                {
                    "first_name": "Корней",
                    "last_name": "Чуковский",
                    "email": "user8@user.com"
                },
                {
                    "first_name": "Максим",
                    "last_name": "Горький",
                    "email": "user7@user.com"
                }
            ]
        },
        {
            "title": "Группа №2",
            "course": "Python developer",
            "students": [
                {
                    "first_name": "Ольга",
                    "last_name": "Иванова",
                    "email": "user6@user.com"
                },
                {
                    "first_name": "Саша",
                    "last_name": "Иванов",
                    "email": "user5@user.com"
                },
                {
                    "first_name": "Дмитрий",
                    "last_name": "Иванов",
                    "email": "user4@user.com"
                }
            ]
        },
        {
            "title": "Группа №1",
            "course": "Python developer",
            "students": [
                {
                    "first_name": "Андрей",
                    "last_name": "Петров",
                    "email": "user10@user.com"
                },
                {
                    "first_name": "Олег",
                    "last_name": "Петров",
                    "email": "user3@user.com"
                },
                {
                    "first_name": "Сергей",
                    "last_name": "Петров",
                    "email": "user2@user.com"
                },
                {
                    "first_name": "Иван",
                    "last_name": "Петров",
                    "email": "user@user.com"
                }
            ]
        }
    ]
    ```
</details>

**_Done_**

### __Технологии__
* [Python 3.10.12](https://www.python.org/doc/)
* [Django 4.2.10](https://docs.djangoproject.com/en/4.2/)
* [Django REST Framework  3.14.0](https://www.django-rest-framework.org/)
* [Djoser  2.2.0](https://djoser.readthedocs.io/en/latest/getting_started.html)
