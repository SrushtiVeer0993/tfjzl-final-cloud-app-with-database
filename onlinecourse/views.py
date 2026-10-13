from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Course, Lesson, Enrollment, Question, Choice, Submission


def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    
    # Get user enrollment
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    # Create submission
    submission = Submission.objects.create(enrollment=enrollment)
    
    # Process selected choices
    selected_choice_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            selected_choice_ids.append(int(value))
            choice = get_object_or_404(Choice, pk=int(value))
            submission.choices.add(choice)
            
    submission.save()
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    total_score = 0
    grade = 0
    
    for question in course.question_set.all():
        total_score += question.grade
        if question.is_get_score(selected_ids):
            grade += question.grade
            
    context['course'] = course
    context['submission'] = submission
    context['selected_ids'] = selected_ids
    context['grade'] = grade
    context['total_score'] = total_score
    context['percentage'] = int((grade / total_score) * 100) if total_score > 0 else 0
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
