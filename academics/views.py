from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

import csv

from .forms import ExamForm
from .models import Exam, Grade, Student


# ============================================================
# V2 - EXAM SCHEDULING
# ============================================================

def create_exam(request):

    if request.method == "POST":
        form = ExamForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("exam_success")

    else:
        form = ExamForm()

    return render(
        request,
        "exams/create_exam.html",
        {"form": form}
    )


def exam_success(request):

    return render(
        request,
        "exams/exam_success.html"
    )


# ============================================================
# V3 - MANUAL GRADE ENTRY
# ============================================================

def enter_grades(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)

    students = (
        exam.subject.department.students
        .filter(semester=exam.subject.semester)
        .order_by("roll_number")
    )

    if request.method == "POST":

        saved_count = 0
        error_count = 0

        for student in students:

            marks = request.POST.get(
                f"marks_{student.id}",
                ""
            ).strip()

            # Empty marks are ignored
            if marks == "":
                continue

            try:
                marks = int(marks)

            except (ValueError, TypeError):

                messages.error(
                    request,
                    f"Invalid marks for {student.name}."
                )

                error_count += 1
                continue

            if marks < 0 or marks > 100:

                messages.error(
                    request,
                    f"Marks for {student.name} "
                    f"must be between 0 and 100."
                )

                error_count += 1
                continue

            Grade.objects.update_or_create(
                student=student,
                exam=exam,
                defaults={
                    "marks": marks
                }
            )

            saved_count += 1

        if saved_count > 0:

            messages.success(
                request,
                f"{saved_count} grade(s) saved successfully."
            )

        if error_count > 0:

            messages.warning(
                request,
                f"{error_count} grade(s) could not be saved."
            )

        return redirect(
            "enter_grades",
            exam_id=exam.id
        )

    return render(
        request,
        "grades/enter_grades.html",
        {
            "exam": exam,
            "students": students,
        }
    )


# ============================================================
# V4 - DOWNLOAD CSV TEMPLATE
# ============================================================

def download_grade_csv(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)

    students = (
        exam.subject.department.students
        .filter(semester=exam.subject.semester)
        .order_by("roll_number")
    )

    response = HttpResponse(
        content_type="text/csv"
    )

    filename = (
        f"grade_roster_{exam.subject.code}.csv"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "roll_number",
        "student_name",
        "marks"
    ])

    for student in students:

        writer.writerow([
            student.roll_number,
            student.name,
            ""
        ])

    return response


# ============================================================
# V4 - UPLOAD CSV
# ============================================================

def upload_grade_csv(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":

        csv_file = request.FILES.get("csv_file")

        if not csv_file:

            messages.error(
                request,
                "Please select a CSV file."
            )

            return redirect(
                "upload_grade_csv",
                exam_id=exam.id
            )

        if not csv_file.name.lower().endswith(".csv"):

            messages.error(
                request,
                "Only CSV files are allowed."
            )

            return redirect(
                "upload_grade_csv",
                exam_id=exam.id
            )

        try:

            file_data = csv_file.read().decode(
                "utf-8-sig"
            )

            reader = csv.DictReader(
                file_data.splitlines()
            )

            required_columns = {
                "roll_number",
                "student_name",
                "marks"
            }

            actual_columns = set(
                reader.fieldnames or []
            )

            if not required_columns.issubset(
                actual_columns
            ):

                messages.error(
                    request,
                    "Invalid CSV format. "
                    "Required columns: "
                    "roll_number, student_name, marks"
                )

                return redirect(
                    "upload_grade_csv",
                    exam_id=exam.id
                )

            students = (
                exam.subject.department.students
                .filter(semester=exam.subject.semester)
            )

            success_count = 0
            error_count = 0

            for row_number, row in enumerate(
                reader,
                start=2
            ):

                roll_number = (
                    row.get("roll_number") or ""
                ).strip()

                student_name = (
                    row.get("student_name") or ""
                ).strip()

                marks_value = (
                    row.get("marks") or ""
                ).strip()

                # Completely empty row
                if not roll_number and not marks_value:
                    continue

                # Roll number missing
                if not roll_number:

                    messages.error(
                        request,
                        f"Row {row_number}: "
                        f"Roll number is required."
                    )

                    error_count += 1
                    continue

                # Marks missing
                if not marks_value:

                    messages.error(
                        request,
                        f"Row {row_number}: "
                        f"Marks are required for "
                        f"{roll_number}."
                    )

                    error_count += 1
                    continue

                # Find student
                try:

                    student = students.get(
                        roll_number=roll_number
                    )

                except Student.DoesNotExist:

                    messages.error(
                        request,
                        f"Row {row_number}: "
                        f"Student with roll number "
                        f"{roll_number} not found."
                    )

                    error_count += 1
                    continue

                # Optional name verification
                if (
                    student_name
                    and student.name.strip().lower()
                    != student_name.lower()
                ):

                    messages.warning(
                        request,
                        f"Row {row_number}: "
                        f"Student name does not match "
                        f"roll number {roll_number}."
                    )

                # Convert marks
                try:

                    marks = int(marks_value)

                except (ValueError, TypeError):

                    messages.error(
                        request,
                        f"Row {row_number}: "
                        f"Invalid marks for "
                        f"{roll_number}."
                    )

                    error_count += 1
                    continue

                # Marks validation
                if marks < 0 or marks > 100:

                    messages.error(
                        request,
                        f"Row {row_number}: "
                        f"Marks must be between "
                        f"0 and 100."
                    )

                    error_count += 1
                    continue

                # Save / update grade
                Grade.objects.update_or_create(
                    student=student,
                    exam=exam,
                    defaults={
                        "marks": marks
                    }
                )

                success_count += 1

            if success_count > 0:

                messages.success(
                    request,
                    f"{success_count} grade(s) "
                    f"uploaded successfully."
                )

            if error_count > 0:

                messages.warning(
                    request,
                    f"{error_count} row(s) "
                    f"could not be uploaded."
                )

            return redirect(
                "upload_grade_csv",
                exam_id=exam.id
            )

        except UnicodeDecodeError:

            messages.error(
                request,
                "Could not read the CSV file. "
                "Please save the file as UTF-8 CSV."
            )

            return redirect(
                "upload_grade_csv",
                exam_id=exam.id
            )

        except Exception as e:

            messages.error(
                request,
                f"Error processing CSV: {e}"
            )

            return redirect(
                "upload_grade_csv",
                exam_id=exam.id
            )

    return render(
        request,
        "grades/upload_grades.html",
        {
            "exam": exam
        }
    )


# ============================================================
# V4 - GRADE SUMMARY
# ============================================================

def grade_summary(request, exam_id):

    exam = get_object_or_404(
        Exam,
        id=exam_id
    )

    grades = (
        Grade.objects
        .filter(exam=exam)
        .select_related("student")
        .order_by("student__roll_number")
    )

    total_students = grades.count()

    passed_students = grades.filter(
        marks__gte=40
    ).count()

    failed_students = grades.filter(
        marks__lt=40
    ).count()

    average_marks = 0

    if total_students > 0:

        total_marks = sum(
            grade.marks
            for grade in grades
        )

        average_marks = round(
            total_marks / total_students,
            2
        )

    return render(
        request,
        "grades/grade_summary.html",
        {
            "exam": exam,
            "grades": grades,
            "total_students": total_students,
            "passed_students": passed_students,
            "failed_students": failed_students,
            "average_marks": average_marks,
        }
    )


# ============================================================
# V5 - GRADE POINT
# ============================================================

def get_grade_point(marks):

    if marks >= 90:
        return 10, "A+"

    elif marks >= 80:
        return 9, "A"

    elif marks >= 70:
        return 8, "B+"

    elif marks >= 60:
        return 7, "B"

    elif marks >= 50:
        return 6, "C"

    elif marks >= 40:
        return 5, "D"

    else:
        return 0, "F"


# ============================================================
# V5 - STUDENT REPORT CARD
# ============================================================

def student_report(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    grades = (
        Grade.objects
        .filter(student=student)
        .select_related(
            "exam",
            "exam__subject"
        )
        .order_by(
            "exam__subject__semester__number",
            "exam__subject__code"
        )
    )

    report_data = []

    total_credits = 0
    total_weighted_points = 0

    for grade in grades:

        subject = grade.exam.subject

        grade_point, letter_grade = (
            get_grade_point(grade.marks)
        )

        credits = subject.credits

        weighted_points = (
            grade_point * credits
        )

        total_credits += credits
        total_weighted_points += (
            weighted_points
        )

        report_data.append({

            "subject": subject,

            "exam": grade.exam,

            "marks": grade.marks,

            "credits": credits,

            "grade_point": grade_point,

            "letter_grade": letter_grade,

            "result": (
                "PASS"
                if grade.marks >= 40
                else "FAIL"
            ),

        })

    if total_credits > 0:

        cgpa = round(
            total_weighted_points /
            total_credits,
            2
        )

    else:

        cgpa = 0

    return render(
        request,
        "grades/student_report.html",
        {
            "student": student,
            "report_data": report_data,
            "total_credits": total_credits,
            "cgpa": cgpa,
        }
    )