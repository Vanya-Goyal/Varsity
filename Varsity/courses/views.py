from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Course
from django.db.models import Q
from .forms import CourseForm 

def course_list(request):
    courses = Course.objects.all()
    query = request.GET.get('q')
    sort_by = request.GET.get('sort')
    category = request.GET.get('category')

    if query:
        courses = courses.filter(title__icontains=query)
    if category:
        courses = courses.filter(category__iexact=category)

    if sort_by == 'price_asc':
        courses = courses.order_by('price')
    elif sort_by == 'price_desc':
        courses = courses.order_by('-price')

    paginator = Paginator(courses, 6)  # 6 per page
    page = request.GET.get('page')
    courses = paginator.get_page(page)

    categories = Course.objects.values_list('category', flat=True).distinct()

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
        "sort_by": sort_by
    })
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})

@login_required
def buy_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user not in course.students.all():
        course.students.add(request.user)
    return render(request, 'courses/payment_success.html', {'course': course})

# Check if user is instructor (customize based on your User model)
def is_instructor(user):
    return user.is_authenticated or user.role == 'instructor'

# Instructor Dashboard View
@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor_dashboard.html', {'courses': courses})

# Create Course
@login_required
def add_course(request):
    if request.user.role != 'instructor' and not request.user.is_superuser:
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('courses:instructor_dashboard')
    else:
        form = CourseForm()

    return render(request, 'courses/add_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.instructor != request.user and not request.user.is_superuser:
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:instructor_dashboard')
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})

# Delete Course
@login_required
@user_passes_test(is_instructor)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:instructor_dashboard')
    return render(request, 'courses/confirm_delete.html', {'course': course})