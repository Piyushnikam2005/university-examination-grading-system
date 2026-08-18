from django.urls import path

from . import views


urlpatterns = [

    # Exam
    path(
        "exam/create/",
        views.create_exam,
        name="create_exam"
    ),

    path(
        "exam/success/",
        views.exam_success,
        name="exam_success"
    ),

    # Enter grades
    path(
        "grades/enter/<int:exam_id>/",
        views.enter_grades,
        name="enter_grades"
    ),

    # CSV
    path(
        "grades/download/<int:exam_id>/",
        views.download_grade_csv,
        name="download_grade_csv"
    ),

    path(
        "grades/upload/<int:exam_id>/",
        views.upload_grade_csv,
        name="upload_grade_csv"
    ),

    # Grade summary
    path(
        "grades/summary/<int:exam_id>/",
        views.grade_summary,
        name="grade_summary"
    ),

    # Student report
    path(
        "grades/student/<int:student_id>/",
        views.student_report,
        name="student_report"
    ),
]