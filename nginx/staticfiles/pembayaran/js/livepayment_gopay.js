var statusTransaksi = document.getElementById("status_transaksi");
var expiryTime = document.getElementById("expirytime");
const transStatusElement = document.getElementById('trans-status');
const status_trans = transStatusElement.getAttribute('data-status');
const transDataElement = document.getElementById('trans-data');
const id_transaksi = transDataElement.getAttribute('data-id');

if (status_trans === "Belum Dibayar"){
    var btnStatus = document.querySelector('#btn_status');
    var qrCode = document.querySelector('#qrcode');
    var btnBayar = document.getElementById("btn_bayar")
    var btnStatusInvoice = document.getElementById("btn_status_invoice")
}
var modul = document.querySelector('#modul');
var ujian = document.querySelector('#ujian');
var nilai = document.querySelector('#nilai');
var laporan = document.querySelector('#laporan');

const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
var socket = new WebSocket(`${protocol}${window.location.host}/ws/pembayaran/${id_transaksi}/`);

socket.onopen = function(event) {
    console.log('Koneksi WebSocket dibuka');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data === 'Telah Dibayar'){
        if (status_trans === "Belum Dibayar"){
            btnStatus.style.display='none';
            qrCode.remove()
            btnBayar.style.display='none'; 
        }
        statusTransaksi.textContent = data;
        modul.style.display='block';
        ujian.style.display='block';
        nilai.style.display='block';   
        laporan.style.display='block';   
        
        socket.onclose();   
    }
    else if (data === 'Pembayaran Melebihi Batas Waktu'){
        statusTransaksi.textContent = data;
        btnStatusInvoice.style.display='none';
        btnStatus.textContent = 'Lakukan Pembayaran Lagi';
        qrCode.remove()
        btnBayar.style.display='none'; 
        socket.onclose();       
    }
};
socket.onerror = function(error) {
    console.error('Kesalahan koneksi WebSocket:', error);
};
socket.onclose = function(event) {
    console.log('Koneksi WebSocket ditutup');
};