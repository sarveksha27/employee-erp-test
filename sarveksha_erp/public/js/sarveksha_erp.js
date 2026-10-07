frappe.provide("sarveksha_erp");

(function () {
	const APP_VERSION = (frappe.boot && frappe.boot.versions && frappe.boot.versions.sarveksha_erp) || "1.1.2";
	const VERSION_TEXT = "v" + APP_VERSION;

	function renderNavbarVersion() {
		// 1. Desktop Navbar (Desktop home screen)
		const $desktopNavbar = $(".desktop-navbar, header.navbar-container, header.navbar").first();
		if ($desktopNavbar.length && !$("#sarveksha-navbar-version").length) {
			const badgeHtml = `
				<div id="sarveksha-navbar-version" class="sarveksha-navbar-version-badge" title="Sarveksha ERP ${VERSION_TEXT}">
					<span class="badge-version">${VERSION_TEXT}</span>
				</div>
			`;
			const $navbarHome = $desktopNavbar.find(".navbar-home");
			if ($navbarHome.length) {
				$navbarHome.after(badgeHtml);
			} else {
				$desktopNavbar.prepend(badgeHtml);
			}
		}

		// 2. Page Head Top Bar (Active page/doctype/workspace header)
		const $pageHead = $(".page-head:visible");
		if ($pageHead.length && !$pageHead.find(".sarveksha-pagehead-version-badge").length) {
			const $titleArea = $pageHead.find(".title-area, .page-title");
			if ($titleArea.length) {
				$titleArea.append(`
					<span class="sarveksha-pagehead-version-badge" title="Sarveksha ERP ${VERSION_TEXT}">
						<span class="badge-version">${VERSION_TEXT}</span>
					</span>
				`);
			}
		}
	}

	function renderSidebarVersion() {
		const $sidebarBottom = $(".body-sidebar-bottom");
		if (!$sidebarBottom.length) return;

		// Check if already rendered
		if ($("#sarveksha-sidebar-version").length) return;

		// Locate the user section at the bottom of the sidebar
		const $userDropdown = $sidebarBottom.find(".dropdown-navbar-user");
		const $userButton = $sidebarBottom.find(".sidebar-user-button");
		const $target = $userDropdown.length ? $userDropdown : ($userButton.length ? $userButton.parent() : null);

		if ($target && $target.length) {
			const sidebarBadgeHtml = `
				<div id="sarveksha-sidebar-version" class="sarveksha-sidebar-version-container">
					<div class="sarveksha-version-inner" title="Sarveksha ERP ${VERSION_TEXT}">
						<span class="sarveksha-app-name">Sarveksha ERP</span>
						<span class="sarveksha-app-version">${VERSION_TEXT}</span>
					</div>
				</div>
			`;
			// Insert directly above the user details
			$target.before(sidebarBadgeHtml);
		}
	}

	function updateVersionIndicators() {
		renderNavbarVersion();
		renderSidebarVersion();
	}

	// Initial hooks
	$(document).ready(function () {
		updateVersionIndicators();
		setTimeout(updateVersionIndicators, 300);
		setTimeout(updateVersionIndicators, 1000);
	});

	$(document).on("toolbar_setup page-change", function () {
		updateVersionIndicators();
	});

	if (window.frappe && frappe.router) {
		frappe.router.on("change", function () {
			setTimeout(updateVersionIndicators, 150);
		});
	}

	// Guard for dynamic SPA re-renders and lazy DOM mounting
	setInterval(function () {
		if (!$("#sarveksha-sidebar-version").length || !$("#sarveksha-navbar-version").length) {
			updateVersionIndicators();
		}
	}, 1500);
})();
