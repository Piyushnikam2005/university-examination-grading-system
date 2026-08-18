from django import forms
from django.db.models import Q

from .models import Exam


class ExamForm(forms.ModelForm):

    class Meta:
        model = Exam

        fields = [
            "subject",
            "exam_date",
            "start_time",
            "end_time",
            "room",
        ]

        widgets = {
            "exam_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date"
                }
            ),

            "start_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time"
                }
            ),

            "end_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["exam_date"].input_formats = ["%Y-%m-%d"]
        self.fields["start_time"].input_formats = ["%H:%M"]
        self.fields["end_time"].input_formats = ["%H:%M"]

    def clean(self):

        cleaned_data = super().clean()

        subject = cleaned_data.get("subject")
        room = cleaned_data.get("room")
        exam_date = cleaned_data.get("exam_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # --------------------------------------------------
        # 1. Check Start Time and End Time
        # --------------------------------------------------

        if start_time and end_time:

            if start_time >= end_time:

                raise forms.ValidationError(
                    "Start time must be earlier than end time."
                )

        # --------------------------------------------------
        # 2. Check Room Capacity
        # --------------------------------------------------

        if room and subject:

            student_count = subject.department.students.filter(
                semester=subject.semester
            ).count()

            if student_count > room.capacity:

                raise forms.ValidationError(
                    f"Cannot schedule exam. "
                    f"Room capacity is {room.capacity}, "
                    f"but {student_count} students are enrolled."
                )

        # --------------------------------------------------
        # 3. Check Room Time Conflict
        # --------------------------------------------------

        if room and exam_date and start_time and end_time:

            conflicting_exams = Exam.objects.filter(
                room=room,
                exam_date=exam_date
            ).filter(
                Q(start_time__lt=end_time) &
                Q(end_time__gt=start_time)
            )

            # If editing an existing exam,
            # don't compare the exam with itself.
            if self.instance.pk:

                conflicting_exams = conflicting_exams.exclude(
                    pk=self.instance.pk
                )

            if conflicting_exams.exists():

                raise forms.ValidationError(
                    f"The room '{room.name}' is already booked "
                    f"for another exam during this time."
                )

        return cleaned_data