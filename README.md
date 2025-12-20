# Memgraph LTDT - Mô phỏng Thuật toán Đồ thị

Dự án này là một ứng dụng web mô phỏng và trực quan hóa các thuật toán lý thuyết đồ thị (Graph Theory). Ứng dụng sử dụng **Memgraph** làm cơ sở dữ liệu đồ thị nền tảng và **Streamlit** để xây dựng giao diện tương tác người dùng.

## Giới thiệu

Memgraph LTDT cho phép người dùng:
- Xây dựng đồ thị (thêm đỉnh, thêm cạnh) thông qua giao diện trực quan.
- Lưu trữ dữ liệu đồ thị bền vững vào Memgraph Database.
- Chạy và mô phỏng các thuật toán đồ thị phổ biến.
- Trực quan hóa kết quả thuật toán ngay trên giao diện web.

## Các Chức Năng Chính

1.  **Quản lý Đồ thị:**
    - Thêm/Xóa đỉnh và cạnh.
    - Reset dữ liệu đồ thị hoặc xóa toàn bộ database.
    - Tự động đồng bộ dữ liệu giữa giao diện và Memgraph.

2.  **Thuật Toán Hỗ Trợ:**
    - **BFS (Breadth-First Search):** Duyệt đồ thị theo chiều rộng.
    - **DFS (Depth-First Search):** Duyệt đồ thị theo chiều sâu.
    - **Dijkstra:** Tìm đường đi ngắn nhất (trọng số không âm).
    - **Bellman-Ford:** Tìm đường đi ngắn nhất (xử lý cạnh trọng số âm).

3.  **Trực Quan Hóa:**
    - Hiển thị đồ thị dưới dạng mạng lưới tương tác (Interactive Network).
    - Tô màu và đánh dấu kết quả đường đi của các thuật toán.

## Yêu Cầu Hệ Thống

Để chạy dự án này dễ dàng nhất, bạn cần cài đặt:
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Bao gồm Docker Compose).

## Hướng Dẫn Cài Đặt và Chạy (Khuyên dùng)

Dự án đã được tích hợp sẵn Docker Compose để bạn có thể chạy toàn bộ hệ thống chỉ với một lệnh duy nhất.

### Bước 1: Khởi động ứng dụng

Mở terminal (Command Prompt/PowerShell trên Windows hoặc Terminal trên MacOS/Linux) tại thư mục gốc của dự án và chạy lệnh:

```bash
docker-compose up -d --build
```

**Lệnh này sẽ:**
1.  Tải và khởi chạy container **Memgraph** (Database).
2.  Xây dựng và khởi chạy container **Streamlit App** (Ứng dụng web).
3.  Kết nối hai dịch vụ với nhau.

### Bước 2: Truy cập ứng dụng

Sau khi các container đã khởi chạy thành công, bạn có thể truy cập:

- **Ứng dụng Mô Phỏng (Streamlit):** [http://localhost:8501](http://localhost:8501)
- **Giao diện quản lý Memgraph Lab (Optional):** [http://localhost:3000](http://localhost:3000) (Để xem dữ liệu trực tiếp trong DB nếu cần).

### Bước 3: Dừng ứng dụng

Để dừng các container, chạy lệnh:

```bash
docker-compose down
```

---
## Cấu Trúc Thư Mục

- `app.py`: File chính chạy ứng dụng Streamlit.
- `algorithms/`: Chứa cài đặt các thuật toán (BFS, DFS, Dijkstra, ...).
- `services/`: Các service xử lý logic kết nối Database và Graph.
- `ui/`: Các thành phần giao diện và visualization.
- `docker-compose.yml`: Cấu hình Docker cho toàn bộ dự án.
