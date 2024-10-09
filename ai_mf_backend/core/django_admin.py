from django.contrib import admin
from models.v1.database.user import (
    Gender, MaritalStatus, Occupation, UserPersonalDetails, UserContactInfo, UserOTP, 
    
)
from models.v1.database.financial_details import (
    AnnualIncome, MonthlySavingCapacity, 
    InvestmentAmountPerYear,UserFinancialDetails

)
from models.v1.database.questions import ( Section, Question, Response, UserResponse, ConditionalQuestion
)

from ai_mf_backend.models.v1.database.user_authentication import (
    UserLogs,
    UserManagement,
)
 
@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('gender', 'add_date', 'update_date')
    search_fields = ('gender',)
    ordering = ('gender',)


@admin.register(MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'add_date', 'update_date')
    search_fields = ('status',)
    ordering = ('status',)


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ('occupation', 'add_date', 'update_date')
    search_fields = ('occupation',)
    ordering = ('occupation',)


@admin.register(AnnualIncome)
class AnnualIncomeAdmin(admin.ModelAdmin):
    list_display = ('income_category', 'add_date', 'update_date')
    search_fields = ('income_category',)
    ordering = ('income_category',)


@admin.register(MonthlySavingCapacity)
class MonthlySavingCapacityAdmin(admin.ModelAdmin):
    list_display = ('saving_category', 'add_date', 'update_date')
    search_fields = ('saving_category',)
    ordering = ('saving_category',)


@admin.register(InvestmentAmountPerYear)
class InvestmentAmountPerYearAdmin(admin.ModelAdmin):
    list_display = ('investment_amount_per_year', 'add_date', 'update_date')
    search_fields = ('investment_amount_per_year',)
    ordering = ('investment_amount_per_year',)


@admin.register(UserPersonalDetails)
class UserPersonalDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth', 'gender', 'marital_status', 'add_date', 'update_date')
    search_fields = ('name',)
    list_filter = ('gender', 'marital_status')
    ordering = ('name',)


@admin.register(UserContactInfo)
class UserContactInfoAdmin(admin.ModelAdmin):
    list_display = ('email', 'mobile_number', 'add_date', 'update_date')
    search_fields = ('email', 'mobile_number')
    ordering = ('email',)


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'otp_valid', 'add_date', 'update_date')
    search_fields = ('user__email', 'otp')
    ordering = ('-add_date',)


@admin.register(UserFinancialDetails)
class UserFinancialDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'occupation', 'annual_income', 'monthly_saving_capacity', 'investment_amount_per_year', 'add_date', 'update_date')
    search_fields = ('user__email',)
    list_filter = ('occupation', 'annual_income', 'monthly_saving_capacity', 'investment_amount_per_year')
    ordering = ('user',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'add_date', 'update_date')
    search_fields = ('section_name',)
    ordering = ('section_name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('section', 'question', 'add_date', 'update_date')
    search_fields = ('question',)
    list_filter = ('section',)
    ordering = ('section',)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'section', 'response', 'add_date', 'update_date')
    search_fields = ('response',)
    list_filter = ('section', 'question')
    ordering = ('question',)


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'response', 'section', 'add_date', 'update_date')
    search_fields = ('user__email', 'question__question')
    list_filter = ('section', 'question')
    ordering = ('user',)


@admin.register(ConditionalQuestion)
class ConditionalQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'dependent_question', 'condition', 'visibility', 'add_date', 'update_date')
    search_fields = ('question__question', 'dependent_question__question')
    list_filter = ('visibility',)
    ordering = ('question',)


@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'last_access', 'action')
    search_fields = ('user__email', 'device_type', 'action')
    list_filter = ('action', 'device_type')
    ordering = ('-last_access',)


@admin.register(UserManagement)
class UserManagementAdmin(admin.ModelAdmin):
    list_display = ("mobile_number", "email", "created_at")
    search_fields = ("email", "mobile_number")
    list_filter = ("updated_at",)
    ordering = ("-created_at",)
