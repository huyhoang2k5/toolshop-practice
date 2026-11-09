# Sprint 1 của đồ án (hạn: đầu buổi 11/11)

Sprint 1 dựng khung repo đồ án của nhóm và 4 test smoke đầu tiên. Đầu buổi 11/11, mỗi nhóm chiếu repo 1 phút.

Cần nộp đủ 4 việc:

1. Repo nhóm công khai, đủ thành viên, nhánh `main` chỉ nhận Pull Request.
2. Khung kiểm thử chép từ repo thực hành: `conftest.py`, `pytest.ini`, `requirements.txt`, `.gitignore`, `.env.example`, thư mục `pages/`.
3. 4 test smoke dùng page object, `pytest -m smoke` xanh.
4. PR #1 có một bạn khác trong nhóm review rồi mới merge.

Làm theo các bước dưới đây, theo thứ tự.

## Bước 1. Lấy bài giải buổi 1 về repo thực hành (5 phút)

Để `pages/` đủ các hàm đã làm trên lớp. Trong thư mục repo thực hành của em (repo tạo từ template):

```bash
git remote add lop https://github.com/jameboykks/toolshop-practice.git   # chỉ làm lần đầu
git fetch lop
git checkout lop/bai-giai -- pages tests/buoi1/test_b1_pom.py
git commit -m "Take the session 1 reference solution"
pytest tests/buoi1                                                        # 13 passed
```

Bản em tự làm vẫn còn trong lịch sử commit. Muốn so trước khi lấy: `git diff HEAD lop/bai-giai -- pages`.

## Bước 2. Một bạn tạo repo nhóm (10 phút)

Trưởng nhóm làm:

1. GitHub, nút **New** (tạo repo mới). Đặt tên `toolshop-automation-<tên nhóm>`, chọn **Public**, tích **Add a README file** (để nhánh `main` có sẵn), bấm **Create repository**.
2. Thêm thành viên: **Settings** → **Collaborators** → **Add people**, nhập tên GitHub từng bạn. Các bạn mở email (hoặc https://github.com/notifications) bấm **Accept invitation**.
3. Bảo vệ `main`: **Settings** → **Branches** → **Add classic branch protection rule**.
   - **Branch name pattern:** `main`
   - Tích **Require a pull request before merging**, ở dòng **Require approvals** chọn `1`.
   - Bấm **Create**.

Từ giờ không ai đẩy thẳng lên `main` được, kể cả trưởng nhóm. Mọi thay đổi đi qua Pull Request.

## Bước 3. Chép khung kiểm thử sang repo nhóm (10 phút)

Một bạn clone repo nhóm về máy, tạo nhánh mới:

```bash
git clone https://github.com/<trưởng-nhóm>/toolshop-automation-<tên nhóm>.git
cd toolshop-automation-<tên nhóm>
git checkout -b feature/<tên-em>-sprint1
```

Chép từ repo thực hành sang (giữ nguyên tên và vị trí):

| Chép | Để làm gì |
|---|---|
| `conftest.py` | Đọc `.env`, đặt `data-test` cho `get_by_test_id`, các fixture dùng chung |
| `pytest.ini` | Khai báo marker `smoke`, `ui`, `api`... |
| `requirements.txt` | Danh sách thư viện, cùng phiên bản với repo thực hành |
| `.gitignore` | Không đẩy `.env`, `.venv/`, cache lên GitHub |
| `.env.example` | Mẫu cấu hình URL |
| `pages/` (cả thư mục) | Các page object: BasePage, HomePage, ProductPage, CartPage, LoginPage, ContactPage, AccountPage |

Rồi tạo `.env` và môi trường:

```bash
cp .env.example .env                      # Windows: copy .env.example .env
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Thiếu `.env` thì pytest báo `BASE_URL is not set. Copy .env.example to .env`. File `.env` không được đẩy lên GitHub (`.gitignore` đã chặn).

## Bước 4. Viết 4 test smoke (30 - 45 phút)

Tạo file `tests/ui/test_smoke.py`. Viết 4 test sau, mỗi test gắn `@pytest.mark.smoke` và có docstring 3 dòng (mục tiêu, điều kiện, kết quả mong đợi):

| # | Test | Các bước | Kết quả mong đợi | Gợi ý |
|---|---|---|---|---|
| 1 | Tìm kiếm | Mở trang chủ, tìm `pliers` | Mọi tên sản phẩm hiện ra đều chứa chữ "pliers" | Giống B1.1 |
| 2 | Thêm vào giỏ | Mở sản phẩm "Claw Hammer", thêm với số lượng 3 | Badge giỏ hàng trên menu hiện `3` | Giống B1.3 |
| 3 | Đăng nhập sai | Đăng nhập bằng email **không tồn tại** và mật khẩu bất kỳ | Hiện "Invalid email or password", URL vẫn kết thúc bằng `/auth/login` | Giống B1.5 |
| 4 | Form liên hệ trống | Mở trang Contact, không điền gì, bấm Send | Hiện "Subject is required" và "Message is required" | Dùng `ContactPage` có sẵn trong `pages/contact_page.py` |

Ba test đầu viết lại từ bài B1.1, B1.3, B1.5 trên lớp. Test 4 là test mới: đọc `pages/contact_page.py` để biết có những locator và hàm nào.

Không dùng tài khoản mẫu `customer@practicesoftwaretesting.com` cho test đăng nhập sai: Toolshop khoá tài khoản sau 3 lần sai, cả lớp sẽ không đăng nhập được.

Chạy:

```bash
pytest -m smoke                       # 4 passed
pytest -m smoke --headed --slowmo 300 # xem trình duyệt chạy
```

Kiểm tra luật (3 lệnh đều phải **không in ra gì**):

```bash
grep -rn "get_by_\|locator(" tests/
grep -rn "expect(\|assert " pages/
grep -rn "sleep\|wait_for_timeout" tests pages
```

Windows PowerShell không có `grep`, dùng 3 lệnh này thay thế:

```powershell
Select-String -Path tests\ui\*.py -Pattern "get_by_|locator\("
Select-String -Path pages\*.py -Pattern "expect\(|assert "
Select-String -Path tests\ui\*.py,pages\*.py -Pattern "sleep|wait_for_timeout"
```

## Bước 5. Pull Request #1 (15 phút)

```bash
git add conftest.py pytest.ini requirements.txt .gitignore .env.example pages tests
git status                            # KHÔNG được thấy .env trong danh sách
git commit -m "Add test framework and 4 smoke tests"
git push -u origin feature/<tên-em>-sprint1
```

Trên GitHub:

1. Bấm **Compare & pull request**. Tiêu đề: `Sprint 1: framework and smoke tests`. Mô tả: kết quả `pytest -m smoke` (chép dòng `4 passed`). Bên phải chọn **Reviewers** là một bạn trong nhóm. Bấm **Create pull request**.
2. Bạn review mở tab **Files changed**, đọc theo 4 câu:
   - Test có locator nào không? (phải không có)
   - `pages/` có `expect` hay `assert` không? (phải không có)
   - Có `sleep` không? (phải không có)
   - Test nào thiếu docstring 3 dòng?

   Có góp ý thì bấm dấu `+` cạnh dòng code để ghi. Ổn thì **Review changes** → **Approve** → **Submit review**.
3. Người mở PR bấm **Merge pull request**.

Người mở PR không tự Approve được PR của mình; đó là lý do cần một bạn khác.

## Nghiệm thu đầu buổi 11/11 (mỗi nhóm 1 phút)

Một bạn chiếu màn hình:

1. **Settings** → **Branches**: có luật cho `main`.
2. Tab **Pull requests** → **Closed**: PR #1 đã merge, có dấu Approved của bạn khác.
3. Terminal: `pytest -m smoke` → `4 passed`.

Kẹt ở bước nào: chụp màn hình lỗi (cả lệnh đã gõ) gửi lên nhóm lớp.
