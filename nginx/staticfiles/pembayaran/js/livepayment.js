var statusTransaksi = document.getElementById("status_transaksi");
var expiryTime = document.getElementById("expirytime");
'{% if status_transaksi == "Belum Dibayar" %}'
var btnStatus = document.querySelector('#btn_status');
var btnStatusInvoice = document.getElementById("btn_status_invoice")
'{% endif %}'
var modul = document.querySelector('#modul');
var ujian = document.querySelector('#ujian');
var nilai = document.querySelector('#nilai');
var quizBtn = document.getElementById('quiz');
const transDataElement = document.getElementById('trans-data');
const id_transaksi = transDataElement.getAttribute('data-id');
var socket = new WebSocket('wss://'+ window.location.host +'/ws/pembayaran/'+id_transaksi+"/");

socket.onopen = function(event) {
    console.log('Koneksi WebSocket dibuka');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data === 'Telah Dibayar'){
        '{% if status_transaksi == "Belum Dibayar" %}'
        btnStatus.style.display='none';
        '{% endif %}'

        statusTransaksi.textContent = `Status : ${data}`;
        modul.style.display='block';
        ujian.style.display='block';
        nilai.style.display='block';    
        socket.onclose();   
    }
    else if (data === 'Pembayaran Melebihi Batas Waktu'){
        statusTransaksi.textContent = `Status : ${data}`;
        btnStatusInvoice.style.display='none'
        btnStatus.textContent = 'Lakukan Pembayaran Lagi';
        socket.onclose();       
    }
};
socket.onerror = function(error) {
    console.error('Kesalahan koneksi WebSocket:', error);
};
socket.onclose = function(event) {
    console.log('Koneksi WebSocket ditutup');
};
