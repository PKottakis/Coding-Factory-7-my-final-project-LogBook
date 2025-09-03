from django.contrib import admin
from django import forms
from .models import Band, Station
from django.contrib.auth.models import Group, User # Added for unregistering Group
from django.contrib.auth.admin import UserAdmin

class StationAdminForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = '__all__'

    class Media:
        js = ('admin/js/station_admin.js',)
        css = {
            'all': ('admin/css/station_admin.css',)
        }

class StationAdmin(admin.ModelAdmin):
    form = StationAdminForm
    list_display = ['Callsign_Station', 'Frequency', 'Date', 'Time', 'get_modulation_type', 'Analog', 'Digital', 'get_decoding_type']
    list_filter = ['Date', 'Analog', 'Digital', 'band']
    search_fields = ['Callsign_Station', 'Frequency']
    
    change_list_template = 'admin/station/station/change_list.html'
    change_form_template = 'admin/station/station/change_form.html'
    
    def changelist_view(self, request, extra_context=None):
        # Ενεργοποίηση του "show counts" ως default
        if '_facets' not in request.GET:
            # Αν δεν υπάρχει το _facets parameter, το προσθέτουμε
            get_params = request.GET.copy()
            get_params['_facets'] = '1'
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('admin:station_station_changelist') + '?' + get_params.urlencode())
        
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('band', 'Frequency', 'Callsign_Station')
        }),
        ('Modulation', {
            'fields': (('AM', 'FM', 'USB', 'LSB', 'SSB', 'CW'),),
            'classes': ('wide', 'modulation-fieldset')
        }),
        ('Type', {
            'fields': (('Analog', 'Digital'),),
            'classes': ('wide', 'signaltype-fieldset')
        }),
        ('Decoding Types', {
            'fields': (('C4FM', 'DMR', 'DSTAR', 'FAX', 'FSK31', 'FT4', 'FT8', 'JT65', 'JT9', 'RTTY', 'SSTV'),),
            'classes': ('wide', 'decoding-fieldset')
        }),
        ('Receive - Transmit', {
            'fields': (('RSV', 'TRS'),),
            'classes': ('wide', 'rx-tx-fieldset')
        }),
        ('Date & Time', {
            'fields': (('Date', 'Time'),)
        }),
    )
    
    def get_modulation_type(self, obj):
        if obj.AM:
            return 'AM'
        elif obj.FM:
            return 'FM'
        elif obj.USB:
            return 'USB'
        elif obj.LSB:
            return 'LSB'
        elif obj.SSB:
            return 'SSB'
        elif obj.CW:
            return 'CW'
        return '-'
    get_modulation_type.short_description = 'Modulation'

    def get_decoding_type(self, obj):
        if obj.C4FM:
            return 'C4FM'
        elif obj.DMR:
            return 'DMR'
        elif obj.DSTAR:
            return 'DSTAR'
        elif obj.FAX:
            return 'FAX'
        elif obj.FSK31:
            return 'FSK31'
        elif obj.FT4:
            return 'FT4'
        elif obj.FT8:
            return 'FT8'
        elif obj.JT65:
            return 'JT65'
        elif obj.JT9:
            return 'JT9'
        elif obj.RTTY:
            return 'RTTY'
        elif obj.SSTV:
            return 'SSTV'
        return '-'
    get_decoding_type.short_description = 'Decoding Type'

class BandAdmin(admin.ModelAdmin):
    list_display = ['band', 'active', 'get_station_count']
    list_filter = ['active']
    search_fields = ['band']
    ordering = ['band']
    
    change_list_template = 'admin/station/band/change_list.html'
    change_form_template = 'admin/station/band/change_form.html'
    
    fieldsets = (
        ('Πληροφορίες Μπάντας', {
            'fields': ('band', 'active'),
            'description': 'Εισάγετε τις πληροφορίες της μπάντας'
        }),
    )
    
    def get_station_count(self, obj):
        return obj.Station.count()
    get_station_count.short_description = 'Αριθμός Σταθμών'

# Register 
admin.site.register(Band, BandAdmin)
admin.site.register(Station, StationAdmin)

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    
    change_list_template = 'admin/auth/user/change_list.html'
    change_form_template = 'admin/auth/user/change_form.html'
    
    fieldsets = (
        ('Πληροφορίες Χρήστη', {
            'fields': ('username', 'password')
        }),
        ('Προσωπικές Πληροφορίες', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Δικαιώματα', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Σημαντικές ημερομηνίες', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        ('Πληροφορίες Χρήστη', {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Προσωπικές Πληροφορίες', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Δικαιώματα', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Αν είναι προσθήκη νέου χρήστη
            form.base_fields['email'].required = True
        return form

# Αφαίρεση του Group από το admin
admin.site.unregister(Group)
admin.site.unregister(User)

# Εγγραφή του custom User admin
admin.site.register(User, CustomUserAdmin)

# Αλλαγή τίτλου διαχειριστικού
admin.site.site_header = 'Σελίδα διαχείρισης'
admin.site.site_title = 'Σελίδα διαχείρισης'
# admin.site.index_title = 'Καλώς ήρθατε'

# Ρύθμιση για το custom login template
admin.site.login_template = 'admin/login.html'
