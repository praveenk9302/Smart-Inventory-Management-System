document.addEventListener("DOMContentLoaded", () => {

    const scanBtn = document.getElementById("scanBtn");
    const modal = document.getElementById("scanModal");
    const scanner = document.getElementById("scanner");
    const closeBtn = document.getElementById("closeScan");

    const productName = document.getElementById("productName");
    const productStock = document.getElementById("productStock");
    const scanStatus = document.getElementById("scanStatus");

    let isScanning = false;

    if (!scanBtn) return;

    // ---------------- OPEN SCANNER ----------------
    scanBtn.addEventListener("click", () => {

        modal.style.display = "flex";

        productName.textContent = "-";
        productStock.textContent = "-";
        scanStatus.textContent = "";
        scanStatus.className = "";

        if (isScanning) return;

        Quagga.init({
            inputStream: {
                type: "LiveStream",
                target: scanner,
                constraints: { facingMode: "environment" }
            },
            decoder: {
                readers: ["code_128_reader", "ean_reader", "ean_8_reader"]
            }
        }, err => {
            if (err) {
                scanStatus.textContent = "❌ Camera error";
                scanStatus.className = "error";
                return;
            }
            Quagga.start();
            isScanning = true;
        });
    });

    // ---------------- BARCODE DETECTED ----------------
    Quagga.onDetected(data => {

        if (!isScanning) return;
        isScanning = false;

        const barcode = data.codeResult.code;
        Quagga.stop();

        scanStatus.textContent = "⏳ Updating product...";

        fetch("/scan-barcode/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ barcode })
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {
                productName.textContent = data.name;
                productStock.textContent = data.stock;
                scanStatus.textContent = "✅ Product updated";
                scanStatus.className = "success";
            } else {
                scanStatus.textContent = "❌ " + data.message;
                scanStatus.className = "error";
            }

            setTimeout(() => modal.style.display = "none", 1500);
        })
        .catch(() => {
            scanStatus.textContent = "❌ Server error";
            scanStatus.className = "error";
        });
    });

    // ---------------- CLOSE MODAL ----------------
    closeBtn.addEventListener("click", () => {
        if (isScanning) {
            Quagga.stop();
            isScanning = false;
        }
        modal.style.display = "none";
    });
});

// ---------------- CSRF ----------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
