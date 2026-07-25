// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment", {
	// refresh(frm) {
	// }
});

frappe.listview_settings["Equipment"] = {
	onload: function (listview) {
		// Prevent duplicate search bars if navigated back
		if (document.getElementById("eq-name-search")) return;

		const search_html = `
			<div id="eq-name-search" style="
				padding: 8px 0 4px 0;
				display: flex;
				align-items: center;
				gap: 8px;
			">
				<div style="position: relative; width: 360px;">
					<svg style="
						position: absolute; left: 10px; top: 50%;
						transform: translateY(-50%);
						color: #8d8d8d; pointer-events: none;
					" xmlns="http://www.w3.org/2000/svg" width="14" height="14"
					viewBox="0 0 24 24" fill="none" stroke="currentColor"
					stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="11" cy="11" r="8"></circle>
						<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
					</svg>
					<input
						id="eq-name-search-input"
						type="text"
						placeholder="Search by equipment name…"
						style="
							width: 100%; padding: 7px 32px 7px 32px;
							border: 1px solid #d1d8dd; border-radius: 6px;
							font-size: 13px; outline: none; background: #fff;
							color: #333; box-sizing: border-box;
							transition: border-color 0.15s, box-shadow 0.15s;
						"
					/>
					<span id="eq-name-search-clear" style="
						display: none; position: absolute; right: 10px; top: 50%;
						transform: translateY(-50%); cursor: pointer;
						color: #999; font-size: 16px; line-height: 1;
					">&times;</span>
				</div>
			</div>
		`;

		listview.$page.find(".layout-main-section-wrapper").prepend(search_html);

		const input = document.getElementById("eq-name-search-input");
		const clearBtn = document.getElementById("eq-name-search-clear");

		if (!input) return;

		// Focus / blur styling
		input.addEventListener("focus", () => {
			input.style.borderColor = "#5e64ff";
			input.style.boxShadow = "0 0 0 2px rgba(94,100,255,0.12)";
		});
		input.addEventListener("blur", () => {
			input.style.borderColor = "#d1d8dd";
			input.style.boxShadow = "none";
		});

		// Clear button
		clearBtn.addEventListener("click", () => {
			input.value = "";
			clearBtn.style.display = "none";
			applyFilter("");
			input.focus();
		});

		// Debounced filter on input
		input.addEventListener("input", frappe.utils.debounce(function () {
			const val = this.value.trim();
			clearBtn.style.display = val ? "block" : "none";
			applyFilter(val);
		}, 350));

		function applyFilter(val) {
			// Remove any existing equipment_name filter set by this search bar
			const existing = listview.filter_area.filter_list.get_filters();
			existing.forEach(f => {
				if (f.get_value && f.fieldname === "equipment_name") {
					f.remove();
				}
			});

			if (val) {
				listview.filter_area.add([
					["Equipment", "equipment_name", "like", "%" + val + "%"]
				]);
			}
			listview.refresh();
		}
	}
};
