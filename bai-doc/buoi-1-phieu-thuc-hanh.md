# Buổi 1 (04/11) - Page Object Model - Phiếu thực hành

Làm theo cặp: một bạn gõ (driver), một bạn đọc phiếu và soát luật (navigator). Xong mỗi bài thì đổi vai.

Mục tiêu cuối buổi: mọi test trong `tests/buoi1/test_b1_pom.py` chuyển từ đỏ sang xanh.

## 0. Mở máy và chuẩn bị (trước khi bắt đầu)

1. Mở VS Code, chọn **File > Open Folder**, mở thư mục `toolshop-practice` của em (repo em đã tạo từ template và clone về ở nhà).
2. Mở terminal trong VS Code (**Terminal > New Terminal**) và bật môi trường ảo:

   ```powershell
   .venv\Scripts\activate          # Windows
   ```

   ```bash
   source .venv/bin/activate       # macOS / Linux
   ```

   Bật đúng thì đầu dòng lệnh có chữ `(.venv)`.
3. Mở trình duyệt vào https://practicesoftwaretesting.com, bấm F12 để mở DevTools. Bấm chuột phải vào một phần tử, chọn **Inspect** để xem thuộc tính `data-test` của nó.

Buổi này em làm việc với các file sau:

| File | Vai trò |
|---|---|
| `tests/buoi1/test_b1_spaghetti.py` | 4 test "mì ống" viết sẵn, chạy được, nhưng locator lặp khắp nơi. **Chỉ đọc, không sửa** |
| `pages/base_page.py` | Phần chung của mọi trang, có sẵn, đọc để hiểu |
| `pages/home_page.py` | Trang chủ: tìm kiếm, sắp xếp, mở sản phẩm |
| `pages/product_page.py` | Trang chi tiết sản phẩm |
| `pages/cart_page.py` | Trang giỏ hàng |
| `pages/login_page.py` | Trang đăng nhập |
| `tests/buoi1/test_b1_pom.py` | Bài B1.1 - B1.7, mỗi bài một hàm test. Đây là 4 test mì ống viết lại bằng page object, cộng thêm vài bài mới |

Trong `pages/`, chỗ nào em cần viết đều có dòng `# TODO B1.x`. Hàm chưa viết có dòng `raise NotImplementedError("B1.x")`: viết xong thì xoá dòng đó.

### Ba luật (cũng là luật chấm đồ án)

1. Không có locator (`get_by_...`, `locator(...)`) trong file test. Locator chỉ nằm trong `pages/`.
2. Không có `expect` hay `assert` trong `pages/`. Kiểm tra chỉ nằm trong file test.
3. Không dùng `time.sleep()` hay `wait_for_timeout()`.

Tự kiểm tra luật bất cứ lúc nào (cả 3 lệnh phải không in ra gì):

```bash
grep -rn "get_by_\|locator(" tests/buoi1/test_b1_pom.py
grep -rn "expect(\|assert " pages/
grep -rn "sleep\|wait_for_timeout" tests pages
```

Windows PowerShell không có `grep`, dùng `Select-String`. Ví dụ lệnh thứ hai: `Select-String -Path pages\*.py -Pattern "expect\(|assert "`.

### Đọc kết quả pytest

| Em thấy | Nghĩa là |
|---|---|
| `1 passed` | Bài đã xanh |
| `NotImplementedError: B1.3` | Chưa viết hàm có TODO B1.3 trong `pages/` |
| `AssertionError` hoặc `Locator expected to ...` | Code chạy được nhưng kết quả sai. Đọc dòng bắt đầu bằng `E` để biết mong đợi gì, nhận được gì |
| `TimeoutError` | Không tìm thấy phần tử, thường do gõ sai tên `data-test` |
| `strict mode violation ... resolved to 9 elements` | Locator trúng nhiều phần tử. Dùng `.first`, `.nth(i)` hoặc `.filter(...)` |
| `'NoneType' object has no attribute ...` | Một hàm trong `pages/` quên `return` |

Muốn xem trình duyệt chạy chậm từng bước: thêm `--headed --slowmo 300` vào cuối lệnh pytest.

### Bảng data-test của Toolshop (kiểm tra ngày 02/11/2026)

| Trang | data-test |
|---|---|
| Trang chủ | `search-query`, `search-submit`, `search-reset`, `search-caption`, `search-result-count`, `search_completed`, `no-results`, `sort`, `sorting_completed`, `product-name`, `product-price`, `pagination-next` |
| Chi tiết sản phẩm | `product-name` (tiêu đề h1), `unit-price`, `quantity`, `increase-quantity`, `decrease-quantity`, `add-to-cart`, `add-to-favorites` |
| Giỏ hàng `/checkout` | `product-title`, `product-quantity`, `product-price`, `line-price`, `cart-total`, `continue-shopping`, `proceed-1` |
| Đăng nhập `/auth/login` | `email`, `password`, `login-submit`, `login-error`, `email-error`, `password-error` |
| Header (mọi trang) | `nav-home`, `nav-contact`, `nav-sign-in`, `nav-cart`, `cart-quantity`, `nav-menu` |

Thông báo nổi (toast) không có data-test: `BasePage` đã có sẵn `self.toast = page.get_by_role("alert")`.

Cần tìm thêm phần tử: chạy `playwright codegen https://practicesoftwaretesting.com`, bấm vào phần tử trên trang, Playwright tự gợi ý locator.

---

## B1.0 - Đếm chỗ phải sửa (cả lớp, 5 phút)

**Mở file** `tests/buoi1/test_b1_spaghetti.py`. File có 4 test viết kiểu "mì ống": test nào cũng tự gọi `page.get_by_test_id(...)` trực tiếp.

| Test | Làm gì |
|---|---|
| `test_spaghetti_search_pliers` | Mở trang chủ, tìm "pliers", kiểm tra mọi sản phẩm hiện ra đều có chữ pliers |
| `test_spaghetti_add_two_hammers` | Mở "Claw Hammer", đặt số lượng 2, thêm vào giỏ, kiểm tra số trên biểu tượng giỏ là 2 |
| `test_spaghetti_search_then_open_first_product` | Tìm "saw", mở sản phẩm đầu tiên, kiểm tra trang chi tiết đúng tên sản phẩm đó |
| `test_spaghetti_login_wrong_password` | Đăng nhập bằng email không tồn tại, kiểm tra thông báo "Invalid email or password" |

**Chạy:**

```bash
python tools/doctor.py
pytest tests/buoi1/test_b1_spaghetti.py
grep -c "product-name" tests/buoi1/test_b1_spaghetti.py
```

Windows PowerShell thay lệnh cuối bằng: `(Select-String -Path tests\buoi1\test_b1_spaghetti.py -Pattern "product-name").Count`

**Kết quả đúng:**
- doctor in dòng cuối "Máy đã sẵn sàng".
- pytest in `4 passed`.
- Lệnh đếm in `11`. Trong đó 2 dòng nằm ở phần chú thích đầu file, **9 dòng là code**.

**Câu hỏi:** giả sử ngày mai Toolshop đổi `data-test="product-name"` thành `data-test="product-title"`. Em phải sửa bao nhiêu dòng code để 4 test chạy lại? Ghi con số ra giấy, cuối buổi (B1.8) đếm lại.

## B1.1 - HomePage.search() (làm cùng giảng viên, 10 phút)

**Mở file** `pages/home_page.py`, tìm dòng `# TODO B1.1`.

**Làm từng bước:**

1. Trong `__init__`, ngay dưới dòng TODO B1.1, thêm 4 locator:

   ```python
   self.search_button = page.get_by_test_id("search-submit")
   self.search_caption = page.get_by_test_id("search-caption")
   self.search_completed = page.get_by_test_id("search_completed")
   self.product_names = page.get_by_test_id("product-name")
   ```

2. Viết hàm `search()`, thay cho dòng `raise NotImplementedError("B1.1")`:

   ```python
   def search(self, keyword: str):
       self.search_box.fill(keyword)
       self.search_button.click()
       return self
   ```

3. Mở `tests/buoi1/test_b1_pom.py`, đọc test `test_b1_1_...`. Test này viết sẵn rồi, chỉ chờ page object của em.

**Chạy:** `pytest tests/buoi1 -k b1_1 --headed --slowmo 300`

**Đạt khi:** `1 passed`.

Vì sao `search()` phải `return self`: để viết được trên một dòng `HomePage(page).open().search("pliers")`.

## B1.2 - Không có kết quả (10 phút)

**Mở file** `pages/home_page.py` (tìm `# TODO B1.2`) và `tests/buoi1/test_b1_pom.py` (hàm `test_b1_2_...`).

**Làm từng bước:**

1. Thêm locator `self.no_results` cho phần tử `data-test="no-results"`.
2. Trong test, xoá dòng `raise NotImplementedError`, rồi viết:
   - mở trang chủ, tìm `zzz-no-such-tool`;
   - kiểm tra `home.no_results` có chữ `There are no products found.`;
   - kiểm tra số sản phẩm hiện ra là 0.

**Chạy:** `pytest tests/buoi1 -k b1_2`

**Đạt khi:** `1 passed`.

<details><summary>Gợi ý</summary>

- Kiểm tra chữ: `expect(home.no_results).to_have_text("There are no products found.")`.
- Kiểm tra số lượng: `expect(home.product_names).to_have_count(0)`. Hàm này tự chờ. Đừng viết `assert home.product_names.count() == 0`: nó đếm ngay lập tức, có thể đếm nhầm danh sách cũ.

</details>

## B1.3 - ProductPage (15 phút)

**Mở file** `pages/product_page.py` (TODO B1.3), `pages/home_page.py` (hàm `open_product`) và test `test_b1_3_...`.

**Làm từng bước:**

1. Trong `ProductPage.__init__`, thêm 4 locator: `name`, `unit_price`, `quantity`, `add_to_cart_button`. Tên data-test tra trong bảng ở phần 0.
2. Viết `ProductPage.add_to_cart(quantity)`: nếu `quantity` khác 1 thì điền ô số lượng, bấm nút thêm vào giỏ, `return self`.
3. Viết `HomePage.open_product(name)`: bấm vào thẻ sản phẩm đúng tên đó, trả về `ProductPage(self.page)`.
4. Viết test: mở "Claw Hammer", thêm số lượng 3, kiểm tra toast có chữ `Product added to shopping cart` và số trên biểu tượng giỏ là `3`.

**Chạy:** `pytest tests/buoi1 -k b1_3`

**Đạt khi:** `1 passed`.

<details><summary>Gợi ý</summary>

- Điền ô số lượng: `self.quantity.fill(str(quantity))`.
- Trong `open_product`, dùng hàm có sẵn: `self.product_card(name).first.click()`. Hàm này khớp đúng nguyên tên, nên "Pliers" không mở nhầm "Combination Pliers".
- Toast: `expect(product.toast).to_contain_text("Product added to shopping cart")`.
- Biểu tượng giỏ: `expect(product.cart_quantity).to_have_text("3")`. `cart_quantity` có sẵn trong `BasePage`.

</details>

**Bẫy:** sản phẩm thân thiện môi trường có chữ `ECO` nằm ngay trong tiêu đề (ví dụ "Wood Saw ECO"). Kiểm tra tên bằng `to_have_text("Wood Saw")` sẽ đỏ, dùng `to_contain_text`.

## B1.4 - CartPage và phép tính (15 phút)

**Mở file** `pages/cart_page.py` (TODO B1.4), `pages/product_page.py` (hàm `price`) và test `test_b1_4_...`.

**Làm từng bước:**

1. Trong `CartPage.__init__`, thêm locator `product_titles`, `quantities`, `line_prices`, `total`.
2. Viết `line_totals()`: lấy chữ của mọi `line_prices`, đổi sang số bằng hàm `money()` có sẵn ở đầu file.
3. Viết `total_value()`: đổi chữ của `total` sang số.
4. Viết `ProductPage.price()`: đổi chữ của `unit_price` sang số.
5. Viết test:
   - mở "Combination Pliers", **đọc đơn giá trước** khi thêm;
   - thêm số lượng 2, chờ số trên biểu tượng giỏ là `2`;
   - mở giỏ hàng bằng `go_to_cart()`;
   - kiểm tra giá của dòng bằng đơn giá x 2, và tổng bằng cộng các dòng.

**Chạy:** `pytest tests/buoi1 -k b1_4`

**Đạt khi:** `1 passed`.

<details><summary>Gợi ý</summary>

- Lấy chữ của nhiều phần tử: `self.line_prices.all_inner_texts()`. Một phần tử: `self.total.inner_text()`.
- So sánh số thực bằng `pytest.approx`: `assert cart.line_totals() == [pytest.approx(unit * 2)]`. So bằng `==` có thể sai vì `14.15 * 2` ra `28.299999...`.
- Phải chờ biểu tượng giỏ là `2` rồi mới mở giỏ. Mở sớm quá thì giỏ còn trống.

</details>

## B1.5 - LoginPage (10 phút)

**Mở file** `pages/login_page.py` (TODO B1.5) và 2 test `test_b1_5_...`.

**Làm từng bước:**

1. Thêm locator `email`, `password`, `submit_button`, `error`, `email_error`, `password_error`.
2. Viết `login(email, password)`: điền 2 ô, bấm nút, `return self`.
3. Test sai mật khẩu: mở trang bằng `LoginPage(page).open()`, đăng nhập bằng `nobody-here@example.com` và một mật khẩu bất kỳ. Kiểm tra `error` có chữ `Invalid email or password` và URL vẫn kết thúc bằng `/auth/login`.
4. Test để trống: bấm nút đăng nhập khi chưa điền gì. Kiểm tra `email_error` có chữ `Email is required`, `password_error` có chữ `Password is required`.

**Chạy:** `pytest tests/buoi1 -k b1_5`

**Đạt khi:** `2 passed`.

<details><summary>Gợi ý</summary>

- Kiểm tra URL: `expect(page).to_have_url(re.compile(r"/auth/login$"))`.
- Test để trống không cần hàm `login()`, chỉ cần `login_page.submit_button.click()`.

</details>

**Quan trọng:** không bao giờ thử mật khẩu sai trên `customer@practicesoftwaretesting.com` hay các tài khoản mẫu khác. Toolshop khoá tài khoản sau 3 lần đăng nhập sai, và cả lớp đang dùng chung các tài khoản này.

## B1.6 - Chuỗi page object (5 phút)

**Làm:** thêm locator `continue_shopping` vào `CartPage`. Viết test bằng một chuỗi:

```python
cart = HomePage(page).open().open_product("Hammer").add_to_cart().go_to_cart()
```

Kiểm tra giỏ có sản phẩm "Hammer", bấm `cart.continue_shopping`, rồi kiểm tra lưới sản phẩm ở trang chủ hiện lại.

**Chạy:** `pytest tests/buoi1 -k b1_6`

**Đạt khi:** `1 passed`.

Chuỗi này chạy được vì mỗi hàm trả về page object của trang tiếp theo: `open()` trả về HomePage, `open_product()` trả về ProductPage, `go_to_cart()` trả về CartPage.

## B1.7 - Thử thách: sắp xếp theo giá (10 phút)

**Làm từng bước:**

1. Thêm 3 locator vào HomePage: `sort_select` (data-test `sort`), `sorting_completed` (data-test `sorting_completed`), `product_prices` (data-test `product-price`).
2. Viết `sort_by(value)`: chọn giá trị trong ô sắp xếp, `return self`.
3. Test đã có `@pytest.mark.parametrize` cho 2 chiều `price,asc` và `price,desc`. Sau khi sắp xếp, chờ `home.sorting_completed` hiện ra, đọc giá bằng hàm có sẵn `home.prices()`, so với `sorted(...)`.

**Chạy:** `pytest tests/buoi1 -k b1_7`

**Đạt khi:** `2 passed`.

<details><summary>Gợi ý</summary>

- Chọn trong ô select: `self.sort_select.select_option(value)`.
- Chờ: `expect(home.sorting_completed).to_be_visible()`. Đọc giá ngay sau khi chọn thì có thể đọc danh sách cũ. Đây là nguyên nhân flaky hay gặp nhất, học kỹ ở buổi 4.
- Chiều giảm dần: `sorted(prices, reverse=True)`.

</details>

## B1.8 - Change request (cả lớp, 5 phút cuối)

Đếm lại: nếu `product-name` đổi tên, với page object em phải sửa mấy dòng?

```bash
grep -rn "product-name" pages/ tests/buoi1/test_b1_pom.py
```

**Kết quả đúng:** 2 dòng, đều nằm trong `pages/` (HomePage và ProductPage), 0 dòng trong test. So với 9 dòng ở B1.0. Đây cũng là câu trả lời cho câu vấn đáp "Nếu website đổi toàn bộ CSS class, nhóm phải sửa bao nhiêu chỗ?".

Kiểm tra cuối buổi:

```bash
pytest tests/buoi1
```

Tất cả xanh, và 3 lệnh kiểm tra luật ở phần 0 không in ra gì.

---

## Bài về nhà = Sprint 1 đồ án (nghiệm thu đầu buổi 11/11)

Hướng dẫn từng bước: `docs/sprint-1.md` trong repo lớp.

1. Repo đồ án công khai, đủ thành viên, nhánh `main` được bảo vệ (bắt buộc Pull Request, 1 approval).
2. Chép `conftest.py`, `pytest.ini`, `requirements.txt`, `.gitignore`, `.env.example`, `pages/` từ repo thực hành sang (đã có sẵn ContactPage).
3. 4 test smoke dùng page object trong `tests/ui/test_smoke.py`, `pytest -m smoke` xanh:
   1. Tìm `pliers`: mọi tên sản phẩm chứa "pliers".
   2. Mở "Claw Hammer", thêm số lượng 3: badge giỏ hàng hiện `3`.
   3. Đăng nhập bằng email không tồn tại: "Invalid email or password", URL vẫn là `/auth/login`.
   4. Bấm Send ở form Liên hệ để trống: "Subject is required" và "Message is required".
4. PR #1 có người khác review và merge.

Trước khi nộp: 3 lệnh kiểm tra luật ở phần 0 đều không in ra gì.
