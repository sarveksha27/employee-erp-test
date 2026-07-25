// Copyright (c) 2026, Umesh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment", {
	// refresh(frm) {
	// }
});

frappe.listview_settings["Equipment"] = {
	onload: function (listview) {
		// Add a search bar at the top of the Equipment list
		const search_html = `
			<div id="equipment-search-bar" style="
				padding: 10px 0 6px 0;
				display: flex;
				align-items: center;
				gap: 8px;
			">
				<div style="
					position: relative;
					flex: 1;
					max-width: 420px;
				">
					<span style="
						position: absolute;
						left: 10px;
						top: 50%;
						transform: translateY(-50%);
						color: #8d8d8d;
						pointer-events: none;
					">
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
							fill="none" stroke="currentColor" stroke-width="2.5"
							stroke-linecap="round" stroke-linejoin="round">
							<circle cx="11" cy="11" r="8"></circle>
							<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
						</svg>
					</span>
					<input
						id="equipment-quick-search"
						type="text"
						placeholder="Search by name, HSN code or category…"
						style="
							width: 100%;
							padding: 7px 12px 7px 32px;
							border: 1px solid #d1d8dd;
							border-radius: 6px;
							font-size: 13px;
							outline: none;
							background: #fff;
							color: #333;
							box-sizing: border-box;
							transition: border-color 0.15s;
						"
					/>
				</div>
			</div>
		`;

		// Insert the search bar before the list content
		listview.$page.find(".layout-main-section-wrapper").prepend(search_html);

		// Focus styling
		const input = document.getElementById("equipment-quick-search");
		if (input) {
			input.addEventListener("focus", () => {
				input.style.borderColor = "#5e64ff";
				input.style.boxShadow = "0 0 0 2px rgba(94,100,255,0.15)";
			});
			input.addEventListener("blur", () => {
				input.style.borderColor = "#d1d8dd";
				input.style.boxShadow = "none";
			});
			// Real-time filter using Frappe list filter
			input.addEventListener("input", frappe.utils.debounce(function () {
				const val = this.value.trim();
				listview.filter_area.add([
					["Equipment", "equipment_name", "like", `%${val}%`, false]
				]);
				// Remove old quick-search filters and re-apply
				listview.filter_area.filter_list.filters = listview.filter_area.filter_list.filters.filter(
					f => f.fieldname !== "equipment_name" && f.fieldname !== "hsn_code"
				);
				if (val) {
					// Use server-side OR search via frappe list filters
					listview.filter_area.add([
						["Equipment", "equipment_name", "like", `%${val}%`]
					]);
				} else {
					listview.filter_area.clear_filters();
				}
				listview.refresh();
			}, 400));
		}
	}
};
