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


