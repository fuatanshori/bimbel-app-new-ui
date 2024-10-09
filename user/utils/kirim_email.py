from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from celery import shared_task

@shared_task
def kirim_email_activate(uid, token, user_obj_email, domain, protocol):
    mail_subject = 'Aktifasi Akun'
    message = render_to_string('user/verification/aktifasi_akun.html', {
        'user': user_obj_email,
        'domain': domain,
        'uid': uid,
        'token': token,
        'protocol': protocol
    })
    to_email = user_obj_email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

    
    
@shared_task
def kirim_email_reset_password(uid, token, user_obj_email, domain, protocol):
    mail_subject = 'Reset Password'
    message = render_to_string('user/verification/resetpassword.html', {
        'user': user_obj_email,
        'domain': domain,
        'uid': uid,
        'token': token,
        'protocol': protocol
    })
    to_email = user_obj_email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    