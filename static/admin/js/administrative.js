document.addEventListener("DOMContentLoaded", function () {
  const provinceSelect = document.getElementById("id_province");
  const districtSelect = document.getElementById("id_district");
  const wardSelect = document.getElementById("id_ward");

  let initialDistrictId = districtSelect?.value;
  let initialWardId = wardSelect?.value;

  // Hàm để tạo request AJAX
  function fetchData(url, params) {
    const queryString = new URLSearchParams(params).toString();
    return fetch(`${url}?${queryString}`).then((response) => response.json());
  }

  // Xử lý khi thay đổi tỉnh/thành phố
  provinceSelect.addEventListener("change", function () {
    const provinceId = this.value;
    if (provinceId) {
      // Xóa các option hiện có
      districtSelect.innerHTML = '<option value="">---------</option>';
      wardSelect.innerHTML = '<option value="">---------</option>';

      // Gọi API lấy danh sách quận/huyện
      fetchData("/api/v1/location/adminitrative/district", {
        province_id: provinceId,
      }).then((data) => {
        const districts = data?.data || [];

        // Thêm các option mới
        districts.forEach((district) => {
          const option = document.createElement("option");
          option.value = district.id;
          option.textContent = district.title;
          districtSelect.appendChild(option);
        });

        // Khôi phục giá trị ban đầu nếu có
        if (initialDistrictId) {
          districtSelect.value = initialDistrictId;
          districtSelect.dispatchEvent(new Event("change", { bubbles: true }));
          initialDistrictId = null;
        }
      });
    }
  });

  // Xử lý khi thay đổi quận/huyện
  districtSelect.addEventListener("change", function () {
    const districtId = this.value;
    if (districtId) {
      // Xóa các option hiện có
      wardSelect.innerHTML = '<option value="">---------</option>';

      // Gọi API lấy danh sách phường/xã
      fetchData("/api/v1/location/adminitrative/ward", {
        district_id: districtId,
      }).then((data) => {
        const wards = data?.data || [];

        // Thêm các option mới
        wards.forEach((ward) => {
          const option = document.createElement("option");
          option.value = ward.id;
          option.textContent = ward.title;
          wardSelect.appendChild(option);
        });

        // Khôi phục giá trị ban đầu nếu có
        if (initialWardId) {
          wardSelect.value = initialWardId;
          initialWardId = null;
        }
      });
    }
  });

  // Kích hoạt sự kiện change ban đầu nếu đã có sẵn tỉnh/thành phố
  if (provinceSelect.value) {
    provinceSelect.dispatchEvent(new Event("change", { bubbles: true }));
  }
});
