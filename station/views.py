from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Station, Band, OTPCode
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import random
import string

# Create your views here.

def menu_view(request):
    return render(request, 'station/menu.html')

def queries_view(request):
    return render(request, 'station/queries.html')

def simple_password_reset(request):
    """Απλό σύστημα επαναφοράς κωδικού"""
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        
        try:
            # Δημιουργούμε νέο χρήστη με γνωστό κωδικό
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if not created:
                # Αν ο χρήστης υπάρχει, αλλάζουμε τον κωδικό
                user.set_password('reset123')
                user.save()
            
            messages.success(request, f'Ο κωδικός για τον χρήστη "{username}" έχει αλλάξει σε: reset123')
            return redirect('/admin/login/')
            
        except Exception as e:
            messages.error(request, f'Σφάλμα: {str(e)}')
    
    return render(request, 'admin/simple_password_reset.html')

def generate_otp():
    """Δημιουργία 6ψήφιου OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user, otp_code):
    """Αποστολή OTP μέσω email"""
    subject = 'Επαναφορά Κωδικού - OTP'
    message = f'''
    Γεια σας {user.username},
    
    Έχετε ζητήσει επαναφορά κωδικού για το λογαριασμό σας.
    
    Ο κωδικός OTP σας είναι: {otp_code}
    
    Αυτός ο κωδικός ισχύει για {getattr(settings, 'OTP_EXPIRY_MINUTES', 10)} λεπτά.
    
    Αν δεν ζητήσατε εσείς αυτή την επαναφορά, παρακαλώ αγνοήστε αυτό το email.
    
    Με εκτίμηση,
    Η ομάδα διαχείρισης
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Σφάλμα αποστολής email: {e}")
        return False

def otp_password_reset(request):
    """View για την αρχική σελίδα επαναφοράς κωδικού με OTP"""
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        
        try:
            # Εύρεση χρήστη
            user = User.objects.get(username=username, email=email)
            
            # Δημιουργία OTP
            otp_code = generate_otp()
            
            # Αποθήκευση OTP στη βάση
            OTPCode.objects.create(user=user, otp_code=otp_code)
            
            # Αποστολή email
            if send_otp_email(user, otp_code):
                messages.success(request, f'Ο κωδικός OTP έχει σταλεί στο email: {email}')
                return redirect('otp_verify', user_id=user.id)
            else:
                messages.error(request, 'Σφάλμα στην αποστολή του OTP. Παρακαλώ δοκιμάστε ξανά.')
                
        except User.DoesNotExist:
            messages.error(request, 'Δεν βρέθηκε χρήστης με αυτό το username και email.')
        except Exception as e:
            messages.error(request, f'Σφάλμα: {str(e)}')
    
    return render(request, 'admin/otp_password_reset.html', {'title': 'Επαναφορά Κωδικού με OTP'})

def otp_verify(request, user_id):
    """View για την επαλήθευση OTP"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Μη έγκυρος χρήστης.')
        return redirect('otp_password_reset')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Έλεγχος passwords αν ταιριάζουν
        if new_password != confirm_password:
            messages.error(request, 'Οι κωδικοί δεν ταιριάζουν.')
            return render(request, 'admin/otp_verify.html', {'user': user, 'title': 'Επαλήθευση OTP'})
        
        # Έλεγχος αν το OTP είναι έγκυρο
        try:
            otp_obj = OTPCode.objects.filter(
                user=user,
                otp_code=otp_code,
                is_used=False
            ).latest('created_at')
            
            if otp_obj.is_expired():
                messages.error(request, 'Ο κωδικός OTP έχει λήξει.')
                return render(request, 'admin/otp_verify.html', {'user': user, 'title': 'Επαλήθευση OTP'})
            
            # Ενημέρωση κωδικού
            user.set_password(new_password)
            user.save()
            
            # Σήμανση OTP ως χρησιμοποιημένο
            otp_obj.is_used = True
            otp_obj.save()
            
            messages.success(request, 'Ο κωδικός σας έχει αλλάξει επιτυχώς!')
            return redirect('/admin/login/')
            
        except OTPCode.DoesNotExist:
            messages.error(request, 'Μη έγκυρος κωδικός OTP.')
    
    return render(request, 'admin/otp_verify.html', {'user': user, 'title': 'Επαλήθευση OTP'})

def get_modulation_type(entry):
    if entry.AM:
        return 'AM'
    elif entry.FM:
        return 'FM'
    elif entry.USB:
        return 'USB'
    elif entry.LSB:
        return 'LSB'
    elif entry.SSB:
        return 'SSB'
    elif entry.CW:
        return 'CW'
    return '-'

def get_decoding_type(entry):
    if entry.C4FM:
        return 'C4FM'
    elif entry.DMR:
        return 'DMR'
    elif entry.DSTAR:
        return 'DSTAR'
    elif entry.FAX:
        return 'FAX'
    elif entry.FSK31:
        return 'FSK31'
    elif entry.FT4:
        return 'FT4'
    elif entry.FT8:
        return 'FT8'
    elif entry.JT65:
        return 'JT65'
    elif entry.JT9:
        return 'JT9'
    elif entry.RTTY:
        return 'RTTY'
    elif entry.SSTV:
        return 'SSTV'
    return '-'

def analog_entries(request):
    page = int(request.GET.get('page', 1))
    per_page = 14
    entries = Station.objects.filter(Analog=True)
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def digital_entries(request):
    page = int(request.GET.get('page', 1))
    per_page = 14
    entries = Station.objects.filter(Digital=True)
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
            'Decoding': get_decoding_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def bands_list(request):
    bands = Band.objects.all().order_by('band')
    data = [str(b.band) for b in bands]
    return JsonResponse({'bands': data})

def band_entries(request):
    band_value = request.GET.get('band')
    page = int(request.GET.get('page', 1))
    per_page = 14
    entries = Station.objects.filter(band__band=band_value)
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
            'Decoding': get_decoding_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def modulation_entries(request):
    modulation = request.GET.get('modulation')
    page = int(request.GET.get('page', 1))
    per_page = 14
    # Mapping modulation string to field name
    modulation_map = {
        'AM': 'AM',
        'FM': 'FM',
        'USB': 'USB',
        'LSB': 'LSB',
        'SSB': 'SSB',
        'CW': 'CW',
    }
    field = modulation_map.get(modulation)
    if not field:
        return JsonResponse({'results': [], 'has_next': False, 'has_previous': False, 'page': 1, 'num_pages': 1})
    filter_kwargs = {f'{field}': True}
    entries = Station.objects.filter(**filter_kwargs)
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
            'Decoding': get_decoding_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def decoding_entries(request):
    decoding = request.GET.get('decoding')
    page = int(request.GET.get('page', 1))
    per_page = 14
    decoding_fields = [
        'C4FM', 'DMR', 'DSTAR', 'FAX', 'FSK31', 'FT4', 'FT8', 'JT65', 'JT9', 'RTTY', 'SSTV'
    ]
    if decoding not in decoding_fields:
        return JsonResponse({'results': [], 'has_next': False, 'has_previous': False, 'page': 1, 'num_pages': 1})
    filter_kwargs = {f'{decoding}': True}
    entries = Station.objects.filter(**filter_kwargs)
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
            'Decoding': get_decoding_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def callsign_entries(request):
    callsign = request.GET.get('callsign', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = 14
    
    # Αφαίρεση wildcards και ειδικών χαρακτήρων
    clean_callsign = callsign.replace('*', '').replace('%', '').strip()
    
    if len(clean_callsign) < 2:
        return JsonResponse({'results': [], 'has_next': False, 'has_previous': False, 'page': 1, 'num_pages': 1})
    
    # Αν το αρχικό callsign περιείχε wildcard, χρησιμοποιούμε istartswith
    # Αν δεν περιείχε wildcard, χρησιμοποιούμε iexact για ακριβή αντιστοίχιση
    if '*' in callsign or '%' in callsign:
        entries = Station.objects.filter(Callsign_Station__istartswith=clean_callsign)
    else:
        # Αναζήτηση με wildcard - χρησιμοποιούμε icontains για να βρίσκει το callsign οπουδήποτε
        entries = Station.objects.filter(Callsign_Station__icontains=clean_callsign)
    
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
            'Decoding': get_decoding_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def date_entries(request):
    date = request.GET.get('date', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = 15
    if not date:
        return JsonResponse({'results': [], 'has_next': False, 'has_previous': False, 'page': 1, 'num_pages': 1})
    entries = Station.objects.filter(Date=date)
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)
    data = [
        {
            'id': entry.id,
            'Callsign_Station': entry.Callsign_Station,
            'Frequency': entry.Frequency,
            'band': str(entry.band),
            'Date': entry.Date.strftime('%d/%m/%Y'),
            'Time': entry.Time.strftime('%H:%M'),
            'Modulation': get_modulation_type(entry),
            'Decoding': get_decoding_type(entry),
        }
        for entry in page_obj
    ]
    return JsonResponse({
        'results': data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

@csrf_exempt
def auto_logout(request):
    """Αυτόματο logout endpoint"""
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({'status': 'logged_out'})

def database_backup(request):
    """View για backup της βάσης δεδομένων"""
    import os
    import shutil
    from django.conf import settings
    from django.http import JsonResponse
    from datetime import datetime
    
    try:
        # Δημιουργία backup στον φάκελο Downloads του χρήστη (Windows compatible)
        if os.name == 'nt':  # Windows
            downloads_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
        else:  # Linux/Mac
            downloads_dir = os.path.expanduser("~/Downloads")
            
        if not os.path.exists(downloads_dir):
            # Fallback σε άλλο φάκελο αν δεν υπάρχει Downloads
            if os.name == 'nt':  # Windows
                downloads_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
            else:
                downloads_dir = os.path.expanduser("~/Desktop")
                
            if not os.path.exists(downloads_dir):
                downloads_dir = os.path.join(settings.BASE_DIR, 'backups')
                if not os.path.exists(downloads_dir):
                    os.makedirs(downloads_dir)
        
        # Δημιουργία όνομα αρχείου με timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_path = os.path.join(downloads_dir, backup_filename)
        
        # Αντιγραφή της βάσης
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        shutil.copy2(db_path, backup_path)
        
        return JsonResponse({
            'success': True,
            'message': f'Backup δημιουργήθηκε επιτυχώς στον φάκελο Downloads: {backup_filename}',
            'filename': backup_filename,
            'path': backup_path
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Σφάλμα κατά το backup: {str(e)}'
        })

def database_restore(request):
    """View για restore της βάσης δεδομένων"""
    import os
    import shutil
    from django.conf import settings
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            backup_filename = data.get('filename')
            
            if not backup_filename:
                return JsonResponse({
                    'success': False,
                    'message': 'Δεν δόθηκε όνομα αρχείου backup'
                })
            
            # Αναζήτηση backup αρχείου στον φάκελο Downloads
            if os.name == 'nt':  # Windows
                downloads_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
            else:  # Linux/Mac
                downloads_dir = os.path.expanduser("~/Downloads")
                
            backup_path = os.path.join(downloads_dir, backup_filename)
            
            # Έλεγχος αν το αρχείο backup υπάρχει
            if not os.path.exists(backup_path):
                return JsonResponse({
                    'success': False,
                    'message': f'Το αρχείο backup {backup_filename} δεν βρέθηκε στον φάκελο Downloads'
                })
            
            # Δημιουργία backup της τρέχουσας βάσης πριν το restore
            current_db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Δημιουργία safety backup στον φάκελο Downloads
            safety_backup = os.path.join(downloads_dir, f'safety_backup_{timestamp}.sqlite3')
            shutil.copy2(current_db_path, safety_backup)
            
            # Restore της βάσης
            shutil.copy2(backup_path, current_db_path)
            
            return JsonResponse({
                'success': True,
                'message': f'Restore ολοκληρώθηκε επιτυχώς από το {backup_filename}. Safety backup δημιουργήθηκε στον φάκελο Downloads: safety_backup_{timestamp}.sqlite3',
                'safety_backup': f'safety_backup_{timestamp}.sqlite3'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Σφάλμα κατά το restore: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Μη έγκυρη μέθοδος'
    })

def get_backup_files(request):
    """View για λήψη λίστας των διαθέσιμων backup αρχείων"""
    import os
    from django.conf import settings
    from django.http import JsonResponse
    
    try:
        # Αναζήτηση backup αρχείων στον φάκελο Downloads (Windows compatible)
        if os.name == 'nt':  # Windows
            downloads_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
        else:  # Linux/Mac
            downloads_dir = os.path.expanduser("~/Downloads")
            
        if not os.path.exists(downloads_dir):
            return JsonResponse({'files': []})
        
        backup_files = []
        for filename in os.listdir(downloads_dir):
            if filename.endswith('.sqlite3') and filename.startswith('db_backup_'):
                file_path = os.path.join(downloads_dir, filename)
                file_size = os.path.getsize(file_path)
                file_date = datetime.fromtimestamp(os.path.getctime(file_path))
                
                backup_files.append({
                    'filename': filename,
                    'size': file_size,
                    'date': file_date.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Ταξινόμηση κατά ημερομηνία (πιο πρόσφατο πρώτο)
        backup_files.sort(key=lambda x: x['date'], reverse=True)
        
        return JsonResponse({'files': backup_files})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Σφάλμα κατά τη λήψη λίστας backup: {str(e)}'
        })
