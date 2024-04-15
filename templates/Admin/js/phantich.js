document.addEventListener('DOMContentLoaded', function () {
        // Fetch predicted consumption from the server
        fetch('/read_data_admin')
            .then(response => response.text())  // Response sẽ là một chuỗi HTML
            .then(html => {
                // Update the content of a container div with the received HTML
                document.getElementById('predictionContainer').innerHTML = html;
            })
            .catch(error => console.error('Error:', error));
    });

function displayData(data) {
    // Lấy đối tượng container từ DOM
    const dataContainer = document.getElementById('data-container');

    // Tạo một bảng để hiển thị dữ liệu
    const table = document.createElement('table');
    table.border = '1';

    // Tạo hàng tiêu đề
    const headerRow = table.insertRow();
    for (const key in data[0]) {
        const headerCell = headerRow.insertCell();
        headerCell.textContent = key;
    }

    // Thêm dữ liệu vào bảng
    data.forEach(item => {
        const row = table.insertRow();
        for (const key in item) {
            const cell = row.insertCell();
            cell.textContent = item[key];
        }
    });

    // Thêm bảng vào container
    dataContainer.appendChild(table);
}
// Lấy giá trị của biến predicted_consume từ Python và gán vào thẻ span
var predictedConsume = {{ predicted_consume }};
document.getElementById('predictedValue').innerText = predictedConsume;

 function displayPredictions(predictions) {
            // Hiển thị dự đoán trong một phần tử HTML có id là 'predictions'
            var predictionsElement = document.getElementById('predictions');

            // Xóa nội dung cũ (nếu có)
            predictionsElement.innerHTML = '';

            // Tạo danh sách (ul) để chứa các mục (li)
            var listElement = document.createElement('ul');

            // Duyệt qua từng dự đoán và thêm vào danh sách
            for (var i = 0; i < predictions.length; i++) {
                var listItem = document.createElement('li');
                listItem.textContent = 'Month ' + (i + 1) + ': ' + predictions[i];
                listElement.appendChild(listItem);
            }

            // Thêm danh sách vào phần tử hiển thị dự đoán
            predictionsElement.appendChild(listElement);
        }
 document.addEventListener("DOMContentLoaded", function() {
    // Lấy tất cả các ô "xóa"
    var deleteCells = document.querySelectorAll(".delete-cell");

    // Gắn sự kiện click cho từng ô "xóa"
    deleteCells.forEach(function(cell) {
        cell.addEventListener("click", function() {
            // Lấy dòng cha (tr) của ô "xóa"
            var row = this.parentNode;
            // Xóa dòng
            row.parentNode.removeChild(row);
        });
    });
});


