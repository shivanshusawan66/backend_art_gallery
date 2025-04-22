from django.db import models
from pgvector.django import VectorField
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database import SoftDeleteModel


class Section(SoftDeleteModel):
    section = models.CharField(max_length=100, unique=True)
    initial_section_weight = models.FloatField(default=0.0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

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
    initial_question_weight = models.FloatField(default=0.0)
    visibility_question = models.CharField(max_length=50)

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
    position = models.PositiveIntegerField(default=0.0)
    response_weight = models.FloatField(default=0.0)
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



class QuestionWeightsPerUser(SoftDeleteModel):
    user_id = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True
    )
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, blank=True
    )
    weight = models.FloatField(default=0.0)


class SectionWeightsPerUser(SoftDeleteModel):
    user_id = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    embedding = VectorField(dimensions=7)
