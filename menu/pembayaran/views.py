import datetime
import babel.dates
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404,get_list_or_404
from .models import Tarif, Transaksi,Diskon
from config import midtrans
import uuid
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse,HttpResponse,HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
import json
import xlwt
from django.db.models import Q
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO
from reportlab.lib.pagesizes import A4
import babel
import logging
from django.http import Http404
import pytz
from core.utils.decorator import admin_pemateri_required,admin_required
from django.utils import timezone
from .forms import TarifForm,DiskonForm
from menu.utils.pagination import pagination_queryset
from menu.utils.encode_url import decode_id
from django.urls import reverse
import csv

MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS

@login_required(login_url='user:masuk')
def pembayaran(request):
    if request.user.role=="pemateri":
        return redirect("menu:menu")
    try:
        transaksi_obj = Transaksi.objects.get(user=request.user)
        if transaksi_obj.layanan_pembayaran == 'gopay':
            return redirect("menu:invoice-gopay", id_transaksi=transaksi_obj.id_transaksi)
        else:
            return redirect("menu:invoice", id_transaksi=transaksi_obj.id_transaksi)
    except Transaksi.DoesNotExist:
        if request.user.role == "admin":
            return redirect("menu:pembayaran-menu")
    diskon = request.POST.get('diskon', '')
    if request.method == "POST":
        tarif_obj = Tarif.get_tarif_is_used()
        harga = 0 if tarif_obj is None else tarif_obj.harga
        try:
            diskon_obj=Diskon.objects.get(diskon_code__exact=str(diskon))
            persentase_diskon =diskon_obj.persentase_diskon
            if datetime.date.today() > diskon_obj.kedaluwarsa:
                diskon_harga = 0
                is_valid_diskon = False
                messages.error(request,"diskon kedaluwarsa")
            else:
                is_valid_diskon = True
                diskon_harga=(persentase_diskon/100)*harga
                messages.success(request,"diskon berhasil digunakan")
            context = {
                'title': 'menu pembayaran',
                'harga': int(harga-diskon_harga),
                'is_valid_diskon':is_valid_diskon,
                "diskon_code":diskon_obj.diskon_code
            }
            return render(request, 'pembayaran/pembayaran.html', context)
        except Diskon.DoesNotExist:
            messages.error(request,"diskon kode invalid")
            

    tarif_obj = Tarif.get_tarif_is_used()
    harga = 0 if tarif_obj is None else tarif_obj.harga
    context = {
        'title': 'menu pembayaran',
        'harga': harga,
        "diskon_code":diskon,
    }
    return render(request, 'pembayaran/pembayaran.html', context)



@login_required(login_url='user:masuk')
def buat_pesanan(request):
    if request.method == "POST":

        try:
            transaksi_obj = Transaksi.objects.get(user=request.user)
            return redirect("menu:pembayaran")
        except Transaksi.DoesNotExist:
            pass
        
        diskon_code = request.POST['layanan_pembayaran']
        diskon_code = str(diskon_code).split(" ")
        diskon_code = str(diskon_code[1])
        try:
            diskon_objs = Diskon.objects.all()
            diskon_codes =[]
            for i in diskon_objs:
                diskon_codes.append(i.diskon_code)
            if diskon_code != "":
                if diskon_code not in diskon_codes:
                    messages.error(request,"bad request")
                    return redirect("menu:pembayaran")
        except Diskon.DoesNotExist:
            pass
        
        tarif_obj = Tarif.get_tarif_is_used()
        harga = 0 if tarif_obj is None else tarif_obj.harga
        try:
            diskon_obj =  Diskon.objects.get(diskon_code__exact=diskon_code)
            persentase_diskon = diskon_obj.persentase_diskon
            diskon_harga = (persentase_diskon/100)*harga
        except Diskon.DoesNotExist:
            diskon_harga= 0

        layanan_pembayaran = request.POST['layanan_pembayaran']
        layanan_pembayaran = str(layanan_pembayaran).split(" ")
        layanan_pembayaran = layanan_pembayaran[0].lower()
        domain             = request.META['HTTP_HOST']
        
        if layanan_pembayaran not in ["bri", 'bni', 'gopay']:
            return redirect("menu:pembayaran")
        
        if layanan_pembayaran in ['bri','bni']:
            params ={
                "payment_type": "bank_transfer",
                "transaction_details": {
                    "order_id": str(uuid.uuid4()),
                    "gross_amount": harga-diskon_harga,
                },
                "bank_transfer": {
                    "bank": layanan_pembayaran,
                },
                "custom_expiry": {
                    "expiry_duration": 3,
                    "unit": "days"
                },
            }
        elif layanan_pembayaran == 'gopay':
            params = {
                "payment_type": "gopay",
                "transaction_details": {
                    "order_id":str(uuid.uuid4()),
                    "gross_amount": harga-diskon_harga,
                },
                "item_details": [
                    {
                    "id": tarif_obj.id_tarif,
                    "price": harga-diskon_harga,
                    "quantity":1,
                    "name":tarif_obj.subject
                    }
                ],
                "customer_details": {
                    "email":request.user.email
                },
                "gopay": {
                    "enable_callback": True,
                    "callback_url": f"https://{domain}/menu/pembayaran/",
                },
                "custom_expiry": {
                "expiry_duration": 1,
                "unit": "days"
                },
            }
        try:
            resp = MIDTRANS_CORE.charge(parameters=params)
        except Exception as e:
            return HttpResponseServerError(str(f"error : {e}"))
        
        if resp:
            try:
                if layanan_pembayaran == "gopay":
                    resp_harga = resp.get("gross_amount")
                    resp_harga = str(resp_harga).split(".")
                    resp_harga = int(resp_harga[0])

                    transaksi_obj = Transaksi.objects.create(
                        user=request.user,
                        tarif=tarif_obj,
                        harga = resp_harga,
                        id_transaksi=str(resp.get('transaction_id')),
                        transaksi_status=resp.get('transaction_status'),
                        layanan_pembayaran=resp.get("payment_type"),
                        transaction_time=resp.get('transaction_time'),
                        expiry_time=resp.get('expiry_time'),
                        qrcode_link =resp.get("actions")[0]["url"],
                        deep_link_redirect=resp.get("actions")[1]["url"],
                    )
                    transaksi_obj.save()
                else:
                    resp_harga = resp.get("gross_amount")
                    resp_harga = str(resp_harga).split(".")
                    resp_harga = int(resp_harga[0])
                    transaksi_obj = Transaksi.objects.create(
                        user=request.user,
                        tarif=tarif_obj,
                        harga = resp_harga,
                        id_transaksi=str(resp.get('transaction_id')),
                        transaksi_status=resp.get('transaction_status'),
                        va_number=resp.get('va_numbers')[0]['va_number'],
                        layanan_pembayaran=resp.get('va_numbers')[0]['bank'],
                        transaction_time=resp.get('transaction_time'),
                        expiry_time=resp.get('expiry_time'),
                    )
                    transaksi_obj.save()
            except Exception as e:
                # return redirect("menu:pembayaran")
                return HttpResponse(str(e))
            if layanan_pembayaran == "gopay":
                return redirect("menu:invoice-gopay", id_transaksi=str(resp.get('transaction_id')))
            else:
                return redirect("menu:invoice", id_transaksi=str(resp.get('transaction_id')))
    
    return redirect("menu:pembayaran")

@login_required(login_url="user:masuk")
def invoice_gopay(request,id_transaksi):
    try:
        transaksi_obj = Transaksi.objects.get(
            id_transaksi=id_transaksi, user=request.user)
    except Transaksi.DoesNotExist:
        return redirect("menu:pembayaran")
    try:
        transaksi_obj = Transaksi.objects.get(user=request.user,transaksi_status="settlement")
        if transaksi_obj:
            context = {
                'vn': transaksi_obj.va_number,
                'harga':transaksi_obj.harga,
                'layanan_pembayaran': transaksi_obj.layanan_pembayaran,
                'id_transaksi': transaksi_obj.id_transaksi,
                'status_transaksi': midtrans.PAYMENT_STATUS[transaksi_obj.transaksi_status],
                'expiry_time': transaksi_obj.expiry_time,
                'qr_code':transaksi_obj.qrcode_link,
                'deep_link_redirect':transaksi_obj.deep_link_redirect,

            }
            return render(request, 'pembayaran/invoice-gopay.html', context)
    except Transaksi.DoesNotExist:
        pass
       
        
    resp = MIDTRANS_CORE.transactions.status(id_transaksi)
    resp_harga = resp.get("gross_amount")
    resp_harga = str(resp_harga).split(".")
    resp_harga = int(resp_harga[0])

    if resp.get('transaction_status') == "cancel":
        return redirect("menu:pembayaran")
    
    if resp.get('transaction_status') == "settlement":
        transaksi_obj.transaksi_status = resp.get(
            'transaction_status')
        transaksi_obj.save()

    elif resp.get('transaction_status') == "expire":
        transaksi_obj.transaksi_status = resp.get(
            'transaction_status')
        transaksi_obj.save()
    else:
        transaksi_obj.transaksi_status = resp.get(
            'transaction_status')
        transaksi_obj.save()
    
    context = {
        'harga':resp_harga,
        'layanan_pembayaran': resp.get("payment_type"),
        'id_transaksi': str(resp.get('transaction_id')),
        'status_transaksi': PAYMENT_STATUS[resp.get('transaction_status')],
        'expiry_time': resp.get('expiry_time'),
        'qr_code':transaksi_obj.qrcode_link,
        'deep_link_redirect':transaksi_obj.deep_link_redirect,
    }
    return render(request, 'pembayaran/invoice-gopay.html', context)



@login_required(login_url='user:masuk')
def invoice(request, id_transaksi):
    try:
        transaksi_obj = Transaksi.objects.get(
            id_transaksi=id_transaksi, user=request.user)
    except Transaksi.DoesNotExist:
        return redirect("menu:pembayaran")
    try:
        transaksi_obj = Transaksi.objects.get(user=request.user,transaksi_status="settlement")
        if transaksi_obj:
            context = {
                'vn': transaksi_obj.va_number,
                'harga':transaksi_obj.harga,
                'bank': transaksi_obj.layanan_pembayaran,
                'id_transaksi': transaksi_obj.id_transaksi,
                'status_transaksi': midtrans.PAYMENT_STATUS[transaksi_obj.transaksi_status],
                'expiry_time': transaksi_obj.expiry_time,

            }
            return render(request, 'pembayaran/invoice.html', context)
    except Transaksi.DoesNotExist:
        pass
    resp = MIDTRANS_CORE.transactions.status(id_transaksi)
    resp_harga = resp.get("gross_amount")
    resp_harga = str(resp_harga).split(".")
    resp_harga = int(resp_harga[0])
    if resp.get('transaction_status') == "cancel":
        return redirect("menu:pembayaran")
    if resp.get('transaction_status') == "settlement":
        transaksi_obj.transaksi_status = resp.get(
            'transaction_status')
        transaksi_obj.save()

    elif resp.get('transaction_status') == "expire":
        transaksi_obj.transaksi_status = resp.get(
            'transaction_status')
        transaksi_obj.save()
    else:
        transaksi_obj.transaksi_status = resp.get(
            'transaction_status')
        transaksi_obj.save()
    context = {
        'vn': resp.get('va_numbers')[0]['va_number'],
        'harga':resp_harga,
        'bank': resp.get('va_numbers')[0]['bank'],
        'id_transaksi': str(resp.get('transaction_id')),
        'status_transaksi': PAYMENT_STATUS[resp.get('transaction_status')],
        'expiry_time': resp.get('expiry_time'),

    }
    return render(request, 'pembayaran/invoice.html', context)


@login_required(login_url='user:masuk')
def batalkan_pesanan(request, id_transaksi):
    try:
        resp_status = MIDTRANS_CORE.transactions.status(id_transaksi)
        if resp_status.get('transaction_status') == "settlement":
            return redirect("menu:invoice", id_transaksi=id_transaksi)
        try:
            MIDTRANS_CORE.transactions.cancel(id_transaksi)
            transaksi_obj = Transaksi.objects.get(id_transaksi=id_transaksi)
            transaksi_obj.delete()
            return redirect("menu:pembayaran")
        except Exception:
            transaksi_obj = Transaksi.objects.get(id_transaksi=id_transaksi)
            transaksi_obj.delete()
            return redirect("menu:pembayaran")

    except Exception as e:
        raise Http404()

# siapa sih yang meminta req ke endpoint ini? jika ip address -> unique,
@csrf_exempt
def notifikasi_midtrans_handler(request):
    import ipaddress
    logger = logging.getLogger('django')

    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip is None:
        ip = request.META.get('REMOTE_ADDR')
    whitelist_ip = [
        # prod_ip
        '103.208.23.0/24',
        '103.208.23.6/32',
        '103.127.16.0/23',
        '103.127.17.6/32',
        '34.87.92.33/32',
        '34.87.59.67/32',
        "35.186.147.251/32",
        "34.87.157.231/32",
        "13.228.166.126/32",
        "52.220.80.5/32",
        "3.1.123.95/32",
        "108.136.204.114/32",
        "108.136.34.95/32",
        "108.137.159.245/32",
        "108.137.135.225/32",
        "16.78.53.66/32",
        "43.218.2.230/32",
        "16.78.88.149/32",
        "16.78.85.64/32",
        "16.78.69.49/32",
        "16.78.98.130/32",
        "16.78.9.40/32",
        "43.218.223.26/32",

        # sandboxip
        '34.101.68.130/32',  
        '34.101.92.69/32',

    ]
    
    if request.method == "GET":
        return render(request, '404.html',status=404)
    ip_obj = ipaddress.ip_address(ip)

    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        logger.info(f"Invalid IP address: {ip}")
        return JsonResponse({}, status=400)
    
    allowed = any(ip_obj in ipaddress.ip_network(allowed_range) for allowed_range in whitelist_ip)
    if not allowed:
        logger.info(f"Access denied for IP: {ip}")
        return JsonResponse({}, status=400)
    
    logger.info(f"Access accept for IP: {ip}")
    data = json.loads(request.body)
    id_transaksi = data['transaction_id']
    transaction_status = data['transaction_status']

    # MIDTRANS_CORE.transactions.notification(data)
    channel_layer = get_channel_layer()

    try:
        transaksi_obj = Transaksi.objects.get(id_transaksi=id_transaksi)
    except Transaksi.DoesNotExist:
        return JsonResponse({}, status=200)

    if transaction_status == 'settlement':
        if transaksi_obj:
            transaksi_obj.transaksi_status = transaction_status
            transaksi_obj.save()
        data = {
            'type': 'status_transaksi',
            "resp": PAYMENT_STATUS[data['transaction_status']]
        }
        async_to_sync(channel_layer.group_send)(id_transaksi, data)

    elif transaction_status == 'expire':
        if transaksi_obj:
            transaksi_obj.transaksi_status = transaction_status
            transaksi_obj.save()
        data = {
            'type': 'status_transaksi',
            "resp": PAYMENT_STATUS[data['transaction_status']]
        }
        async_to_sync(channel_layer.group_send)(id_transaksi, data)

    elif transaction_status == 'pending':
        if transaksi_obj:
            transaksi_obj.transaksi_status = transaction_status
            transaksi_obj.save()
        data = {
            'type': 'status_transaksi',
            "resp": PAYMENT_STATUS[data['transaction_status']]
        }
        async_to_sync(channel_layer.group_send)(id_transaksi, data)

    return JsonResponse({}, status=200)


@login_required(login_url='user:masuk')
def laporan_invoice(request):
    try:
        transaksi_obj = Transaksi.objects.get(user=request.user)
    except Transaksi.DoesNotExist:
        return redirect("menu:pembayaran")
    # Data invoice
    waktu_transaksi = timezone.localtime(transaksi_obj.transaction_time)
    data = {
        'title': 'Bimbingan belajar banua',
        'date': babel.dates.format_date(datetime.date.today(),locale="id"),
        'invoice_number': f'#{str(transaksi_obj.id_transaksi)}',
        'price': transaksi_obj.harga,
        'status': midtrans.PAYMENT_STATUS[transaksi_obj.transaksi_status],
        'virtual_number': transaksi_obj.va_number,
        'layanan_pembayaran': str(transaksi_obj.layanan_pembayaran).upper(),
        'waktu_transaksi':waktu_transaksi.strftime("%d-%m-%Y %H:%M WIB"),
        'note': '*Invoice ini sah diterbitkan langsung oleh pihak bimbingan belajar banua'
    }
    # Ukuran kertas setengah dari A4
    half_A4 = (A4[0], A4[1] / 2)

    # Buat objek BytesIO untuk menampung data PDF di memori
    buffer = BytesIO()

    # Buat objek canvas dengan buffer sebagai output dan ukuran kertas setengah A4
    p = canvas.Canvas(buffer, pagesize=half_A4)
    p.setTitle("Invoice - Bimbingan Belajar Banua")
    width, height = half_A4

    p.setFont("Helvetica", 10)
    p.drawString(15 * cm, height - 1 * cm, f"Tanggal Dicetak: {data['date']}")
    # Header
    # p.setFillColor(color_header_footer)
    # p.rect(0, height - 2 * cm, width, 2 * cm, stroke=0, fill=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(1 * cm, height - 2.9 * cm, data['title'])

    # Date and Invoice Label
    p.setFillColor(colors.black)
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(width - 10 * cm, height - 2.7 * cm, "Invoice")
    p.setFont("Helvetica", 12)
    p.drawString(width - 10 * cm, height - 3.2 * cm, data['invoice_number'])

    # Garis pemisah
    p.setStrokeColor(colors.black)
    p.line(1 * cm, height - 3.9 * cm, width - 1 * cm, height - 3.9 * cm)

    # Detail invoice
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2 * cm, height - 5 * cm, "Detail Pembayaran")
    p.setFont("Helvetica", 12)
    p.drawString(2 * cm, height - 6 * cm, f"Layanan Pembayaran: {data['layanan_pembayaran']}")#5.2
    if data['virtual_number']:
        p.drawString(2 * cm, height - 7 * cm, f"Virtual number: {data['virtual_number']}")#5.9
        p.drawString(2 * cm, height - 8 * cm, f"Status: {data['status']}")#6.6
        p.drawString(2 * cm, height - 9 * cm, f"Waktu Transaksi: {data['waktu_transaksi']}")#6.6
        
        
        p.setStrokeColor(colors.black)
        p.line(1 * cm, height - 11 * cm, width - 1 * cm, height - 11 * cm)

        p.setFont("Helvetica-Bold", 14)
        p.drawString(2 * cm, height - 12 * cm, f"Total Harga: Rp. {data['price']}")#8

        # Footer
        # p.setFillColor(color_header_footer)
        # p.rect(0, 0, width, 2 * cm, stroke=0, fill=1)
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 10)
        p.drawString(2 * cm, 1.5 * cm, data['note'])
    else:
        p.drawString(2 * cm, height - 7 * cm, f"Status: {data['status']}")#6.6
        p.drawString(2 * cm, height - 8 * cm, f"Waktu Transaksi: {data['waktu_transaksi']}")#6.6
        
        
        p.setStrokeColor(colors.black)
        p.line(1 * cm, height - 11 * cm, width - 1 * cm, height - 11 * cm)

        p.setFont("Helvetica-Bold", 14)
        p.drawString(2 * cm, height - 12 * cm, f"Total Harga: Rp. {data['price']}")#8

        # Footer
        # p.setFillColor(color_header_footer)
        # p.rect(0, 0, width, 2 * cm, stroke=0, fill=1)
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 10)
        p.drawString(2 * cm, 1.5 * cm, data['note'])

    # Selesaikan PDF
    p.showPage()
    p.save()

    # Pindahkan pointer buffer ke awal
    buffer.seek(0)

    # Buat HttpResponse dengan tipe konten 'application/pdf'
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response

@login_required(login_url='user:masuk')
@admin_required
def menu_pembayaran(request):
    return render(request, 'pembayaran/menu_pembayaran.html')

@login_required(login_url='user:masuk')
@admin_required
def pembayaran_admin_list(request):
    if request.user.role != "admin":
        raise Http404
    cari_transaksi=request.GET.get('cari_transaksi', None)
    if cari_transaksi:
        transaksi_objs=Transaksi.objects.filter(
            Q(user__email__icontains=cari_transaksi)|
            Q(va_number__iexact=cari_transaksi)
        )
    else:
        transaksi_objs=Transaksi.objects.all()
    context = {
        "transaksi_objs": transaksi_objs,
    }
    # return redirect("menu:mapel-modul")
    return render(request, 'pembayaran/pembayaran_admin.html',context)

@login_required(login_url='user:masuk')
@admin_required
def tarif(request):
    tarif_form = TarifForm()
    amount_perpage=5
    custom_range,tarif_objs = pagination_queryset(request,Tarif.objects.all(),amount_perpage)
    context={
    "tarif_form":tarif_form, 
    "custom_range":custom_range,
    "tarif_objs":tarif_objs
    }
    return render(request,"pembayaran/tarif.html",context)

@login_required(login_url='user:masuk')
@admin_required
def delete_tarif(request,id_tarif):
    pk = decode_id(id_tarif)
    tarif_objs = get_list_or_404(Tarif)
    tarif_obj = get_object_or_404(Tarif,pk=pk)
    if len(tarif_objs)>1:
        tarif_obj.delete()
        messages.success(request,"berhasil dihapus")
        page = request.GET.get('page') 
        return redirect(f"{reverse('menu:tarif')}?page={page}")
    else:
        messages.error(request,"Tarif tidak boleh dihapus. sisakan 1 tarif")
        page = request.GET.get('page') 
        return redirect(f"{reverse('menu:tarif')}?page={page}")

@login_required(login_url='user:masuk')
@admin_required
def add_tarif(request):
    if request.method == "POST":
        tarif_form = TarifForm(request.POST)
        if tarif_form.is_valid():
            tarif_form.save()
            messages.success(request, "Tarif berhasil di tambahkan.")
            return redirect('menu:tarif')
        else:
            error_messages = []
            for field, errors in tarif_form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")    
            messages.error(request, " | ".join(error_messages))
            return redirect('menu:tarif')
    raise Http404
    
    
@login_required(login_url='user:masuk')
@admin_required 
def edit_tarif(request, id_tarif):
    if request.method == "POST":
        pk = decode_id(id_tarif)
        tarif_obj = get_object_or_404(Tarif, pk=pk)
        tarif_form = TarifForm(request.POST, instance=tarif_obj)
        if tarif_form.is_valid():
            tarif_form.save()
            messages.success(request, "Tarif berhasil diedit.")
            page = request.GET.get('page') 
            return redirect(f"{reverse('menu:tarif')}?page={page}")
        else:
            error_messages = []
            for field, errors in tarif_form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, " | ".join(error_messages))
            page = request.GET.get('page') 
            return redirect(f"{reverse('menu:tarif')}?page={page}")
    raise Http404


@login_required(login_url='user:masuk')
@admin_required
def diskon(request,id_tarif):
    pk =decode_id(id_tarif)
    diskon_form = DiskonForm()
    amount_perpage=5
    try:
        custom_range,diskon_objs = pagination_queryset(request,Diskon.objects.filter(tarif__pk=pk),amount_perpage)
    except Diskon.DoesNotExist:
        diskon_objs = None
    
    context={
        "diskon_objs":diskon_objs,
        "diskon_form":diskon_form,
        "id_tarif":id_tarif,
        "custom_range":custom_range,
    }
    return render(request,"pembayaran/diskon.html",context)

@login_required(login_url='user:masuk')
@admin_required
def add_diskon(request, id_tarif):
    pk= decode_id(id_tarif)
    tarif_obj = get_object_or_404(Tarif, pk=pk)
    if request.method == "POST":
        diskon_form = DiskonForm(request.POST)
        
        if diskon_form.is_valid():
            # Gunakan .save(commit=False) agar bisa menambahkan tarif sebelum menyimpan
            diskon_obj = diskon_form.save(commit=False)
            diskon_obj.tarif = tarif_obj  # Menambahkan objek tarif yang terkait
            diskon_obj.save()  # Simpan objek diskon
            messages.success(request, "Selamat, Diskon berhasil ditambahkan")
            return redirect("menu:diskon",id_tarif=id_tarif)
        else:
            print("not a valid")
            error_messages = []
            for _, errors in diskon_form.errors.items():
                for error in errors:
                    error_messages.append(f"{error}")
            messages.error(request, " | ".join(error_messages))
            return redirect("menu:diskon",id_tarif=id_tarif)

@login_required(login_url='user:masuk')
@admin_required
def delete_diskon(request,id_tarif,id_diskon):
    pk = decode_id(id_diskon)
    diskon_obj = get_object_or_404(Diskon,pk=pk)
    diskon_obj.delete()
    messages.success(request,"berhasil di hapus")
    page = request.GET.get('page') 
    return redirect(f"{reverse('menu:diskon', kwargs={'id_tarif': id_tarif})}?page={page}")

@login_required(login_url='user:masuk')
@admin_required
def edit_diskon(request,id_tarif,id_diskon):
    if request.method == "POST":
        diskon_obj = get_object_or_404(Diskon, pk=id_diskon)
        diskon_form = DiskonForm(request.POST, instance=diskon_obj)
        if diskon_form.is_valid():
            diskon_form.save()
            messages.success(request, "Diskon berhasil diedit.")
            page = request.GET.get('page') 
            return redirect(f"{reverse('menu:diskon', kwargs={'id_tarif': id_tarif})}?page={page}")
        else:
            error_messages = []
            for field, errors in diskon_form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, " | ".join(error_messages))
            page = request.GET.get('page') 
            return redirect(f"{reverse('menu:diskon', kwargs={'id_tarif': id_tarif})}?page={page}")
    raise Http404

@login_required(login_url='user:masuk')
@admin_pemateri_required
def export_transaksi_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaksi_report.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
        'ID Transaksi', 'User', 'Tarif', 'Harga', 'Transaksi Status',
        'VA Number', 'Layanan Pembayaran', 'Transaction Time',
        'QRCode Link', 'Deep Link Redirect', 'Expiry Time', 'Updated At'
    ])

    # Fetch data from the Transaksi model
    transaksi_list = Transaksi.objects.all()

    # Write data rows
    for transaksi in transaksi_list:
        writer.writerow([
            transaksi.id_transaksi,
            transaksi.user.full_name,  # Adjust this if you want a different user field
            transaksi.tarif,  # Assuming the Tarif model has a __str__ method
            transaksi.harga,
            transaksi.transaksi_status,
            transaksi.va_number,
            transaksi.layanan_pembayaran,
            transaksi.transaction_time,
            transaksi.qrcode_link,
            transaksi.deep_link_redirect,
            transaksi.expiry_time,
            transaksi.updated_at,
        ])

    return response

@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    date = datetime.datetime.now(pytz.timezone('Asia/Makassar')).strftime("%H:%M:%S_%m/%b/%Y")
    response['Content-Disposition'] = f'attachment; filename="laporan_rekap_transaksi_{date}.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Rekap Transaksi')

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    ws.write_merge(0, 0, 0, 6, 'Laporan Rekap Transaksi/Pembayaran', font_style)
    
    columns = ['id_transaksi', 'email', 'nama', 'tarif', 'va number', 'layanan_pembayaran', 'status transaksi']

    row_num = 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Transaksi.objects.all().values_list('id_transaksi', 'user__email', 'user__full_name', 'harga', "va_number", 'layanan_pembayaran', 'transaksi_status')
    
    for row in rows:
        row_num += 1
        converted_row = list(row)
        
        converted_row[0] = str(row[0])
        
        converted_row[-1] = midtrans.PAYMENT_STATUS[row[-1]]
        
        for col_num in range(len(converted_row)):
            ws.write(row_num, col_num, converted_row[col_num], font_style)
    
    wb.save(response)
    return response