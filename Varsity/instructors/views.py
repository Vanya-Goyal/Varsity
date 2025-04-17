# instructors/views.py

from django.shortcuts import render, get_object_or_404
from courses.models import Course
from django.contrib.auth.decorators import login_required
from dsa_assignments.models import DSAAssignment
@login_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'instructors/dashboard.html', {'courses': courses})


@login_required
def manage_assignments(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    assignments = DSAAssignment.objects.filter(course=course)
    return render(request, 'instructors/manage_assignments.html', {
        'course': course,
        'assignments': assignments
    })