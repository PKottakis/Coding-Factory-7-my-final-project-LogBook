from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

# Create your models here.

class Band(models.Model):
    band = models.FloatField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Μπάντα'
        verbose_name_plural = 'Μπάντες'

    def __str__(self):
        return f"{self.band}m"

class Station(models.Model):
    band = models.ForeignKey(Band, on_delete=models.CASCADE,  related_name="Station", verbose_name='Μπάντα')
    Frequency = models.CharField(max_length=12, verbose_name='Συχνότητα')
    Callsign_Station = models.CharField(max_length=20, verbose_name='Callsign/Σταθμός')
    AM = models.BooleanField(default=False, verbose_name='AM')
    FM = models.BooleanField(default=False, verbose_name='FM')
    USB = models.BooleanField(default=False, verbose_name='USB')
    LSB = models.BooleanField(default=False, verbose_name='LSB')
    SSB = models.BooleanField(default=False, verbose_name='SSB')
    CW = models.BooleanField(default=False, verbose_name='CW')
    Analog = models.BooleanField(default=False, verbose_name='Analog')
    Digital = models.BooleanField(default=False, verbose_name='Digital')
    C4FM = models.BooleanField(default=False, verbose_name='C4FM')
    DMR = models.BooleanField(default=False, verbose_name='DMR')
    DSTAR = models.BooleanField(default=False, verbose_name='DSTAR')
    FAX = models.BooleanField(default=False, verbose_name='FAX')
    FSK31 = models.BooleanField(default=False, verbose_name='FSK31')
    FT4 = models.BooleanField(default=False, verbose_name='FT4')
    FT8 = models.BooleanField(default=False, verbose_name='FT8')
    JT65 = models.BooleanField(default=False, verbose_name='JT65')
    JT9 = models.BooleanField(default=False, verbose_name='JT9')
    RTTY = models.BooleanField(default=False, verbose_name='RTTY')
    SSTV = models.BooleanField(default=False, verbose_name='SSTV')
    RSV = models.CharField(max_length=3, verbose_name='RSV')
    TRS = models.CharField(max_length=3, blank=True, null=True, verbose_name='TRS')
    Date = models.DateField(verbose_name='Ημερομηνία')
    Time = models.TimeField(verbose_name='Ώρα')

    class Meta:
        verbose_name = 'Σταθμός'
        verbose_name_plural = 'Σταθμοί'

    def clean(self):
        super().clean()
        
        # Validation για Frequency format
        if self.Frequency:
            # Αφαιρούμε τα κενά και όλες τις τελείες για validation
            freq_clean = self.Frequency.strip().replace('.', '')
            
            # Ελέγχουμε αν περιέχει μόνο αριθμούς
            if not freq_clean.isdigit():
                raise ValidationError('Η συχνότητα πρέπει να περιέχει μόνο αριθμούς (χωρίς τελείες ή κενά).')
        
        # Validation για Analog/Digital
        if self.Analog and self.Digital:
            raise ValidationError('Δεν μπορείτε να επιλέξετε και Analog και Digital ταυτόχρονα. Επιλέξτε μόνο το ένα.')
        if not self.Analog and not self.Digital:
            raise ValidationError('Πρέπει να επιλέξετε είτε Analog είτε Digital.')
        
        # Validation για Modulation types
        modulation_types = [self.AM, self.FM, self.USB, self.LSB, self.SSB, self.CW]
        if sum(modulation_types) == 0:
            raise ValidationError('Πρέπει να επιλέξετε τουλάχιστον έναν τύπο modulation (AM, FM, USB, LSB, SSB ή CW).')
        if sum(modulation_types) > 1:
            raise ValidationError('Δεν μπορείτε να επιλέξετε περισσότερους από έναν τύπο modulation ταυτόχρονα.')
        
        # Validation για Decoding types - μόνο αν είναι Digital
        if self.Digital:
            decoding_types = [self.C4FM, self.DMR, self.DSTAR, self.FAX, self.FSK31, self.FT4, self.FT8, self.JT65, self.JT9, self.RTTY, self.SSTV]
            if sum(decoding_types) == 0:
                raise ValidationError('Πρέπει να επιλέξετε τουλάχιστον έναν τύπο decoding όταν είναι Digital.')
            if sum(decoding_types) > 1:
                raise ValidationError('Δεν μπορείτε να επιλέξετε περισσότερους από έναν τύπο decoding ταυτόχρονα.')
        
        # Αν είναι Analog, βεβαιωθείτε ότι δεν επιλέγεται κανένας decoding
        if self.Analog:
            decoding_types = [self.C4FM, self.DMR, self.DSTAR, self.FAX, self.FSK31, self.FT4, self.FT8, self.JT65, self.JT9, self.RTTY, self.SSTV]
            if any(decoding_types):
                raise ValidationError('Δεν μπορείτε να επιλέξετε decoding types όταν είναι Analog.')

    def save(self, *args, **kwargs):
        # Μορφοποίηση Frequency πριν το save
        if self.Frequency:
            # Αφαιρούμε τα κενά και όλες τις τελείες
            freq_clean = self.Frequency.strip().replace('.', '')
            
            # Προσθέτουμε αυτόματα τις τελείες για διαχώριση χιλιάδων (μέχρι 2 τελείες)
            if len(freq_clean) >= 3:
                # Από το τέλος, κάθε 3 ψηφία προσθέτουμε τελεία (μέχρι 2)
                formatted_freq = ''
                dot_count = 0
                for i in range(len(freq_clean)):
                    if i > 0 and (len(freq_clean) - i) % 3 == 0 and dot_count < 2:
                        formatted_freq += '.'
                        dot_count += 1
                    formatted_freq += freq_clean[i]
                
                # Ενημερώνουμε το πεδίο με τη μορφοποιημένη τιμή
                self.Frequency = formatted_freq
            else:
                self.Frequency = freq_clean
        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Callsign_Station

class OTPCode(models.Model):
    """Model για την αποθήκευση OTP codes"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        from django.conf import settings
        
        expiry_time = self.created_at + timedelta(minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 10))
        return timezone.now() > expiry_time
    
    class Meta:
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
    
