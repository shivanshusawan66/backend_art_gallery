from django.db import models
from user import UserContactInfo
class Section(models.Model):
    section_name = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "section"
    
    def __str__(self):
        return self.section_name


class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question"
    
    def __str__(self):
        return self.question


class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    response = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "response"
    
    def __str__(self):
        return self.response

class ConditionalQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='main_question')
    dependent_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='dependent_question')
    condition = models.ForeignKey(Response, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conditional_question"

    def __str__(self):
        return f"Conditional visibility for {self.dependent_question.question} based on {self.question.question}"


class UserResponse(models.Model):
    user = models.ForeignKey(UserContactInfo, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_response"
    
    def __str__(self):
        return f"Response by {self.user.name} for {self.question.question}"