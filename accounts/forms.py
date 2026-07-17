from django import forms
from .models import CustomUser

# 1. فورم تسجيل المستخدم بطريقة المواقع العالمية 🌟 (بقى كما هو بالضبط بدون أي مساس)
class UserRegisterForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'الاسم الكامل (مثال: أحمد )'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'البريد الإلكتروني'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'رقم الهاتف'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'كلمة المرور'}))

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# 2. فورم تسجيل الشركة 🏢 (تم إضافة المحافظة والـ GPS مع الحفاظ على الحقول القديمة)
class CompanyRegisterForm(forms.ModelForm):
    company_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'اسم الشركة'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'البريد الإلكتروني للشركة'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'رقم هاتف الشركة'}))
    
    # --- الإضافات الجديدة الخاصة بالموقع ---
    governorate = forms.ChoiceField(
        choices=CustomUser.GOVERNORATE_CHOICES, 
        widget=forms.Select(attrs={'class': 'custom-select', 'style': 'width: 100%; padding: 10px; border-radius: 8px; background: #111e30; color: #fff; border: 1px solid #34495e; margin-bottom: 20px; font-family: "Cairo";'})
    )
    gps_coordinates = forms.CharField(
        required=False, 
        widget=forms.HiddenInput(attrs={'id': 'id_gps_coordinates'})
    )
    # ----------------------------------------

    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'العنوان التفصيلي (اختياري)'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'كلمة مرور الشركة'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'وصف مختصر عن الشركة (اختياري)'}))
    logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'custom-file', 'title': 'تحميل شعار الشركة'}))
    commercial_license = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file'})
    )
    
    class Meta:
        model = CustomUser
        # تم إضافة الحقول الجديدة هنا مع الحفاظ على الحقول القديمة
        fields = ['company_name', 'email', 'phone', 'governorate', 'address', 'password', 'description', 'logo', 'commercial_license', 'gps_coordinates']

    def save(self, commit=True):
        user = super().save(commit=False)
        # نعتمد الإيميل كـ username للسهولة (إذا كنت مسويها سابقاً بالفيو، احذف هالدالة)
        user.username = self.cleaned_data["email"] 
        user.user_type = 'company'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user