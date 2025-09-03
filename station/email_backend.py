"""
Custom Email Backend για να χειριστεί το SSL πρόβλημα με Python 3.13
"""
import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

class CustomEmailBackend(SMTPBackend):
    def open(self):
        """Override το open method για να χειριστεί το SSL context"""
        if self.connection is None:
            # Δημιουργία SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Δημιουργία connection με το custom SSL context
            import smtplib
            self.connection = smtplib.SMTP(self.host, self.port)
            self.connection.starttls(context=ssl_context)
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
        
        return self.connection
