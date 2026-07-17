from django import forms
from .models import CompletedProject, SolarPackage,CompanyProfile
from django.contrib.auth import get_user_model

User = get_user_model()

# [1] فورم إدارة المشاريع المنجزة (بدون تغيير)
class ProjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields['package_reference'].queryset = SolarPackage.objects.filter(company=company)

    class Meta:
        model = CompletedProject
        fields = [
            'package_reference',
            'title',
            'description',
            'main_image',
            'location',
            'customer_feedback',
            'completion_date',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'package_reference': forms.Select(attrs={'class': 'form-control'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

# [2] فورمة تعديل بيانات اليوزر (تم حذف حقل العنوان القديم وبقت المحافظة والـ GPS) ✨
class UserUpdateForm(forms.ModelForm):
    governorate = forms.ChoiceField(
        choices=User.GOVERNORATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control custom-select-settings'})
    )
    gps_coordinates = forms.CharField(
        required=False, 
        widget=forms.HiddenInput(attrs={'id': 'id_gps_coordinates'})
    )

    class Meta:
        model = User
        fields = ['company_name', 'logo', 'governorate', 'gps_coordinates']

# [3] فورمة تعديل بيانات البروفايل (بدون تغيير)
class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['cover_image', 'about_us', 'support_phone', 'whatsapp_number', 'working_hours']
        widgets = {
            'about_us': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'تكلم عن شركتك، خبراتكم، والضمانات التي تقدمونها...'}),
            'support_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXXXXXXXX'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXXXXXXXX'}),
            'working_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: من 9 صباحاً إلى 5 مساءً - الجمعة عطلة'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }