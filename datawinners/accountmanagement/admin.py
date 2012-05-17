# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from forms import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import OrganizationSetting, SMSC, PaymentDetails, MessageTracker, Organization, NGOUserProfile, OutgoingNumberSetting
from mangrove.utils.types import is_empty, is_not_empty
from datawinners.countrytotrialnumbermapping.models import Country, Network

admin.site.disable_action('delete_selected')

class DatawinnerAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

class OrganizationSettingAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'organization_id', 'type', 'payment_details', 'activation_date')
    fields = ('sms_tel_number', 'outgoing_number')

    def organization_name(self, obj):
        return obj.organization.name

    def organization_id(self, obj):
        return obj.organization.org_id

    def payment_details(self, obj):
        organization = obj.organization
        payment_details = PaymentDetails.objects.filter(organization = organization)
        if not is_empty(payment_details):
            return payment_details[0].preferred_payment

        return "--"

    def type(self, obj):
        return 'Trial' if obj.organization.in_trial_mode else 'Paid'

    def activation_date(self, obj):
        return obj.organization.active_date if obj.organization.active_date is not None else '--'


class MessageTrackerAdmin(DatawinnerAdmin):
    list_display = ("organization_name", "month", "incoming_messages", "outgoing_messages", "total_messages")

    def organization_name(self, obj):
        return obj.organization.name

    def month(self, obj):
        return obj.month

    def incoming_messages(self, obj):
        return obj.incoming_sms_count

    def outgoing_messages(self, obj):
        return obj.outgoing_sms_count

    def total_messages(self, obj):
        return obj.incoming_sms_count + obj.outgoing_sms_count


class OrganizationAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'complete_address', 'office_phone', 'website', 'paid', 'active_date','admin_name','admin_email','admin_mobile_number','admin_office_phone')

    def organization_name(self, obj):
        return obj.name

    def paid(self, obj):
        return "No" if obj.in_trial_mode else "Yes"

    def _get_ngo_admin(self, organization):
        user_profiles = NGOUserProfile.objects.filter(org_id=organization.org_id)
        admin_users = [x.user for x in user_profiles if x.user.groups.filter(name="NGO Admins")]
        #right now there is only one ngo admin
        return admin_users[0] if is_not_empty(admin_users) else NullAdmin()

    def admin_email(self, obj):
        return self._get_ngo_admin(obj).email

    def admin_office_phone(self, obj):
        admin_user = self._get_ngo_admin(obj)
        return admin_user.get_profile().office_phone

    def admin_mobile_number(self, obj):
        admin_user = self._get_ngo_admin(obj)
        return admin_user.get_profile().mobile_phone

    def admin_name(self, obj):
        admin_user = self._get_ngo_admin(obj)
        return self._get_full_name(admin_user)

    def complete_address(self, obj):
        complete_address = [obj.address, obj.addressline2, obj.city, obj.zipcode, obj.state, obj.country_name()]
        return ", ".join([element for element in complete_address if is_not_empty(element)])

    def _get_full_name(self,user):
        return user.first_name + ' ' + user.last_name


class NullAdmin:
    def __init__(self):
        self.email=''
        self.mobile_phone=''
        self.office_phone=''
        self.first_name=''
        self.last_name=''

    def get_profile(self):
        return self

class CountryAdmin(admin.ModelAdmin):
    ordering = ('country_name_en',)
    list_display = ('country_name_en','country_code')

class NetworkAdmin(admin.ModelAdmin):
    ordering = ('network_name',)
    list_display = ('network_name','trial_sms_number', 'country_name')
    filter_horizontal = ['country']

    def country_name(self,obj):
        return ' ,'.join([country.country_name for country in obj.country.all()])

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'email' in cleaned_data:
            username = cleaned_data.get('email').strip()
            if not len(username):
                raise forms.ValidationError("This email address is required")
            existing_users_with_username = User.objects.filter(username=username)
            if existing_users_with_username.count() > 0 and existing_users_with_username[0] != self.instance:
                raise forms.ValidationError("This email address is already in use. Please supply a different email address")
            cleaned_data['email'] = username
        return cleaned_data

class NgoUserAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'country', 'organization_id','admin_name','admin_email')
    fields = ('email', )
    form = UserAdminForm

    def organization_name(self, obj):
        profile = obj.get_profile()
        return Organization.objects.get(org_id=profile.org_id).name

    def country(self, obj):
        return (Organization.objects.get(org_id=obj.get_profile().org_id)).country_name()

    def organization_id(self, obj):
        return obj.get_profile().org_id

    def admin_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def admin_email(self, obj):
        return obj.email

    def queryset(self, request):
        qs = super(NgoUserAdmin, self).queryset(request)
        return qs.filter(groups = Group.objects.filter(name="NGO Admins"))

    def save_model(self, request, obj, form, change):
        username = form.cleaned_data['email']
        obj.username = username
        obj.email = username
        obj.save()

admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.register(OrganizationSetting, OrganizationSettingAdmin)
admin.site.register(OutgoingNumberSetting,admin.ModelAdmin)
admin.site.register(SMSC,admin.ModelAdmin)
admin.site.register(MessageTracker, MessageTrackerAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(User, NgoUserAdmin)