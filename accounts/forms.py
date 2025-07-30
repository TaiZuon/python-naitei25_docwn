from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from constants import (
    MIN_PASSWORD_LENGTH,
    MIN_TEXTAREA_ROWS
)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Mật khẩu'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu')
        }),
        min_length=MIN_PASSWORD_LENGTH,
        help_text=_(f'Mật khẩu phải có ít nhất 8 ký tự')
    )
    confirm_password = forms.CharField(
        label=_('Xác nhận mật khẩu'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập lại mật khẩu')
        })
    )
    captcha = ReCaptchaField(
        label='',
        widget=ReCaptchaV2Checkbox
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nhập tên đăng nhập')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nhập địa chỉ email')
            }),
        }
        labels = {
            'username': _('Tên đăng nhập'),
            'email': _('Địa chỉ email'),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Tên đăng nhập đã tồn tại.'))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Email đã được sử dụng.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError(_('Mật khẩu không khớp.'))
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập địa chỉ email'),
            'autofocus': True,
            'id': 'id_email'
        })
    )
    password = forms.CharField(
        label=_('Mật khẩu'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu'),
            'id': 'id_password'
        })
    )
    captcha = ReCaptchaField(
        label='',
        widget=ReCaptchaV2Checkbox
    )
    remember_me = forms.BooleanField(
        label=_('Ghi nhớ đăng nhập'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_remember_me'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise ValidationError(_('Email hoặc mật khẩu không đúng.'))
            except User.DoesNotExist:
                raise ValidationError(_('Email hoặc mật khẩu không đúng.'))
        
        return cleaned_data


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label=_('Mật khẩu hiện tại'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu hiện tại')
        })
    )
    new_password = forms.CharField(
        label=_('Mật khẩu mới'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu mới')
        }),
        min_length=MIN_PASSWORD_LENGTH,
        help_text=_(f'Mật khẩu phải có ít nhất 8 ký tự')
    )
    confirm_password = forms.CharField(
        label=_('Xác nhận mật khẩu mới'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập lại mật khẩu mới')
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError(_('Mật khẩu hiện tại không đúng.'))
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError(_('Mật khẩu mới không khớp.'))
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name',
            'gender',
            'birthday',
            'avatar',
            'description',
            'interest',
            'is_locked',
        ]
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': MIN_TEXTAREA_ROWS}),
            'interest': forms.Textarea(attrs={'rows': MIN_TEXTAREA_ROWS}),
        }
        labels = {
            'display_name': _('Tên hiển thị'),
            'gender': _('Giới tính'),
            'birthday': _('Ngày sinh'),
            'avatar': _('Ảnh đại diện'),
            'description': _('Mô tả bản thân'),
            'interest': _('Sở thích'),
            'is_locked': _('Ẩn hồ sơ'),
        }
