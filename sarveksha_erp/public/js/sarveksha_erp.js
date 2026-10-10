frappe.provide("sarveksha_erp");

(function () {
	// Ensure version badges are removed from DOM
	function cleanVersionBadges() {
		$(
			"#sarveksha-navbar-version, .sarveksha-navbar-version-badge, .sarveksha-pagehead-version-badge, #sarveksha-sidebar-version, .sarveksha-sidebar-version-container"
		).remove();
	}

	$(document).ready(cleanVersionBadges);
	$(document).on("toolbar_setup page-change", cleanVersionBadges);
	if (window.frappe && frappe.router) {
		frappe.router.on("change", cleanVersionBadges);
	}
})();
