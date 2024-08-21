from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_402_PAYMENT_REQUIRED, HTTP_409_CONFLICT

from users.models import Subscription, Balance, CustomUser
from courses.models import Course

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


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        """
        Если пользователь является студентом этого курса, то он может только просматривать курс.
        Админу же доступны все методы. Если появляется ошибка `AttributeError`, то пользователь 
        не аутентифицирован.
        """
        try:
            return (CustomUser.objects.filter(pk=request.user.pk).first().is_student(view.kwargs['course_id']) and request.method in SAFE_METHODS) or request.user.is_staff
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
    

class ReadOnlyOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
