from django.db import models
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database import SoftDeleteModel


class Section(SoftDeleteModel):
    section = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    section_score = models.FloatField(default=1.0)
    class Meta:
        db_table = "section"
        verbose_name = "Section"
        verbose_name_plural = "Section"

    def __str__(self):
        return self.section


class Question(SoftDeleteModel):
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, blank=True
    )
    question = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    question_score = models.FloatField(default=1.0)
    base_weight = models.FloatField(default=5.0)
    initial_weight=models.PositiveIntegerField(default=1)
    class Meta:
        db_table = "question"
        verbose_name = "Question"
        verbose_name_plural = "Question"

    def __str__(self):
        return self.question


class Allowed_Response(SoftDeleteModel):
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True
    )
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, blank=True
    )
    response = models.CharField(max_length=500)
    position = models.PositiveIntegerField(null=True, blank=True,default=0)
    weight_per_option = models.FloatField(default=0.0)
    option_score = models.FloatField(default=1.0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "allowed_response"
        verbose_name = "Allowed Response"
        verbose_name_plural = "Allowed Response"

    def __str__(self):
        return self.response


class ConditionalQuestion(SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_question",
    )
    dependent_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_question",
    )
    response = models.ForeignKey(
        Allowed_Response, on_delete=models.SET_NULL, null=True, blank=True
    )
    visibility = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conditional_question"
        verbose_name = "Conditional Question"
        verbose_name_plural = "Conditional Question"

    def __str__(self):
        return f"Conditional visibility for {self.dependent_question.question} based on {self.question.question}"


class UserResponse(SoftDeleteModel):
    user_id = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    question_id = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True
    )
    response_id = models.ForeignKey(
        Allowed_Response, on_delete=models.SET_NULL, null=True, blank=True
    )
    section_id = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, blank=True
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_response"
        verbose_name = "User Response"
        verbose_name_plural = "User Response"

    def __str__(self):
        return f"Response by {self.user_id} for {self.question_id.question}"
