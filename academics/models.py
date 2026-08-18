from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================================================
# V1 - ACADEMIC STRUCTURE
# ============================================================

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Semester {self.number}"


class Professor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="professors"
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    roll_number = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="students"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="students"
    )

    def __str__(self):
        return f"{self.roll_number} - {self.name}"


class Subject(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    credits = models.PositiveIntegerField()

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    professor = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subjects"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================================
# V2 - EXAM SCHEDULING
# ============================================================

class Room(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - Capacity: {self.capacity}"


class Exam(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    exam_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="exams"
    )

    def __str__(self):
        return f"{self.subject.code} - {self.exam_date}"


# ============================================================
# V3 - GRADE INGESTION
# ============================================================

class Grade(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    marks = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "exam"],
                name="unique_student_exam_grade"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks}"
    