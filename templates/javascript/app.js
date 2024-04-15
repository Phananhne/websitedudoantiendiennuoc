function uploadImage() {
    const fileInput = document.getElementById('fileInput');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');

    if (!fileInput.files.length) {
        alert("Vui lòng chọn một ảnh hóa đơn trước khi tải lên.");
        return;
    }

    loadingDiv.style.display = "block"; // Hiển thị spinner

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('http://127.0.0.1:8000/upload-bill/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = "none"; // Ẩn spinner
        // Xử lý và hiển thị dữ liệu như trước
        const tableBody = document.getElementById('resultTable').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = "";

        for (let key in data.text) {
            if (data.text.hasOwnProperty(key)) {
                let row = tableBody.insertRow();
                let cell1 = row.insertCell(0);
                let cell2 = row.insertCell(1);
                cell1.textContent = key;
                cell2.textContent = data.text[key];
            }
        }
    })
    .catch(error => {
        console.error("Có lỗi xảy ra:", error);
        loadingDiv.style.display = "none"; // Ẩn spinner khi có lỗi
    });
}

