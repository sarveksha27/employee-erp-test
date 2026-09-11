# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import os
from io import BytesIO
from typing import Literal
from PIL import Image
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

import frappe
from frappe.translate import print_language
from frappe.www.printview import validate_print_permission


@frappe.whitelist(allow_guest=True)
def download_pdf(
	doctype: str,
	name: str,
	format=None,
	doc=None,
	no_letterhead=0,
	language=None,
	letterhead=None,
	pdf_generator: Literal["wkhtmltopdf", "chrome"] | None = None,
):
	"""
	Overridden download_pdf method that:
	1. Renders the clean PDF using the customized print format.
	2. Applies the full-page letterhead stationery initially as the background (100% unsqueezed A4),
	   and prints all data directly over the image.
	3. Stitches attached external PDFs/images for Vendor Purchase Orders.
	"""
	if pdf_generator is None:
		pdf_generator = "wkhtmltopdf"

	doc = doc or frappe.get_doc(doctype, name)
	validate_print_permission(doc)

	with print_language(language):
		pdf_file = frappe.get_print(
			doctype,
			name,
			format,
			doc=doc,
			as_pdf=True,
			letterhead=letterhead,
			no_letterhead=no_letterhead,
			pdf_generator=pdf_generator,
			pdf_options={"print-media-type": ""},
		)

	# 1. Apply full-page stationery image as background with data overlaid
	if not no_letterhead:
		try:
			pdf_file = apply_stationery_background(doc, doctype, pdf_file)
		except Exception as e:
			frappe.log_error(
				title=f"Stationery Background Error: {name}",
				message=f"Error applying background for {name}: {str(e)}\n\n{frappe.get_traceback()}",
				reference_doctype=doctype,
				reference_name=name,
			)

	# 2. If Vendor Purchase Order, append any external quotation/inspection attachments
	if doctype == "Vendor Purchase Order":
		try:
			pdf_file = merge_po_attachments(doc, pdf_file)
		except Exception as e:
			frappe.log_error(
				title=f"PDF Merge System Error: {name}",
				message=f"Unhandled error while merging attachments for {name}: {str(e)}\n\n{frappe.get_traceback()}",
				reference_doctype=doctype,
				reference_name=name,
			)

	frappe.local.response.filename = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
	frappe.local.response.filecontent = pdf_file
	frappe.local.response.type = "pdf"


def get_letterhead_image_path(doctype: str, doc) -> str | None:
	"""
	Resolves the disk file path of the full-page stationery image for the document.
	"""
	lh_img = None
	if doctype == "Proforma Invoice":
		lh_name = "India (Sarveksha Realty)"
		if frappe.db.exists("Letter Head", lh_name):
			lh_img = frappe.db.get_value("Letter Head", lh_name, "image")
		if not lh_img:
			lh_img = "/files/letterhead_sri_india.png"
	elif doctype == "Vendor Purchase Order":
		lh_name = getattr(doc, "letter_head", None)
		if not lh_name and getattr(doc, "company", None):
			lh_name = frappe.db.get_value("Company", doc.company, "default_letter_head")
		if not lh_name:
			lh_name = frappe.db.get_value("Letter Head", {"disabled": 0, "is_default": 1}, "name")
		if lh_name and frappe.db.exists("Letter Head", lh_name):
			lh_img = frappe.db.get_value("Letter Head", lh_name, "image")
	else:
		lh_name = getattr(doc, "letter_head", None)
		if not lh_name and getattr(doc, "company", None):
			lh_name = frappe.db.get_value("Company", doc.company, "default_letter_head")
		if lh_name and frappe.db.exists("Letter Head", lh_name):
			lh_img = frappe.db.get_value("Letter Head", lh_name, "image")

	if not lh_img:
		return None

	clean_url = lh_img.lstrip("/")
	paths_to_try = [
		frappe.get_site_path("public", clean_url),
		frappe.get_site_path(clean_url),
		frappe.get_site_path("public", "files", os.path.basename(clean_url)),
		os.path.join(frappe.get_site_path(), "public", clean_url),
		os.path.join(frappe.get_site_path(), clean_url),
	]
	for p in paths_to_try:
		if os.path.exists(p):
			return p

	return None


def create_a4_stationery_page(img_path: str) -> PageObject | None:
	"""
	Converts a high-resolution full-page letterhead stationery image (PNG, JPEG)
	into an exact standard A4 PDF page (595.28 x 841.89 pt) without squeezing, distortion,
	or PyPDF clipping artifacts.
	"""
	if not img_path or not os.path.exists(img_path):
		return None
	try:
		src_img = Image.open(img_path).convert("RGB")
		dpi_x = (src_img.width / A4_WIDTH) * 72.0
		dpi_y = (src_img.height / A4_HEIGHT) * 72.0
		dpi = (dpi_x + dpi_y) / 2.0
		buf = BytesIO()
		src_img.save(buf, format="PDF", resolution=dpi)
		buf.seek(0)
		reader = PdfReader(buf)
		page = reader.pages[0]
		page.mediabox.lower_left = (0, 0)
		page.mediabox.upper_right = (A4_WIDTH, A4_HEIGHT)
		return page
	except Exception as e:
		frappe.log_error(
			title="Stationery Background Generation Error",
			message=f"Failed creating stationery page from {img_path}: {str(e)}",
		)
		return None


def apply_stationery_background(doc, doctype: str, pdf_bytes: bytes) -> bytes:
	"""
	Stamps the full-page stationery background image under each page of the generated PDF document.
	The content (tables, text, numbers) is printed directly over the stationery background with 100%
	transparency, ensuring no white card or rectangle obscures the letterhead.
	"""
	img_path = get_letterhead_image_path(doctype, doc)
	if not img_path:
		return pdf_bytes

	try:
		reader = PdfReader(BytesIO(pdf_bytes))
		writer = PdfWriter()

		for page in reader.pages:
			norm_content = normalize_page_to_a4(page)
			bg_page = create_a4_stationery_page(img_path)
			if bg_page:
				canvas = PageObject.create_blank_page(width=A4_WIDTH, height=A4_HEIGHT)
				canvas.merge_page(bg_page)
				canvas.merge_page(norm_content)
				writer.add_page(canvas)
			else:
				writer.add_page(norm_content)

		out = BytesIO()
		writer.write(out)
		return out.getvalue()
	except Exception as e:
		frappe.log_error(
			title=f"Stationery Background Overlay Error ({getattr(doc, 'name', 'Document')})",
			message=f"Failed overlaying stationery background: {str(e)}\n\n{frappe.get_traceback()}",
			reference_doctype=doctype,
			reference_name=getattr(doc, "name", str(doc)),
		)
		return pdf_bytes


def get_file_bytes_from_url_or_doc(file_url: str, file_doc=None) -> bytes:
	"""
	Retrieves raw binary bytes for a file, checking File document methods first,
	and falling back to disk path resolution for form-field attached files.
	"""
	if file_doc:
		try:
			full_path = file_doc.get_full_path()
			if full_path and os.path.exists(full_path):
				with open(full_path, "rb") as f:
					return f.read()
		except Exception:
			pass
		try:
			content = file_doc.get_content()
			if content:
				return content.encode("utf-8") if isinstance(content, str) else content
		except Exception:
			pass

	if file_url:
		clean_url = file_url.lstrip("/")
		paths_to_try = [
			frappe.get_site_path(clean_url),
			frappe.get_site_path("public", clean_url),
			frappe.get_site_path("private", clean_url),
		]
		if clean_url.startswith("private/files/"):
			paths_to_try.append(frappe.get_site_path("private", "files", clean_url[14:]))
		elif clean_url.startswith("files/"):
			paths_to_try.append(frappe.get_site_path("public", "files", clean_url[6:]))

		for p in paths_to_try:
			if os.path.exists(p):
				try:
					with open(p, "rb") as f:
						return f.read()
				except Exception:
					pass

	return b""


def convert_image_to_a4_pdf(content: bytes) -> bytes:
	"""
	Converts raw image bytes (PNG, JPG, WEBP, BMP) into a clean, standard A4 PDF page (595 x 842 pt).
	Resizes and centers the image proportionally within A4 margins so it renders clearly in all PDF viewers.
	"""
	src_img = Image.open(BytesIO(content))
	if src_img.mode != "RGB":
		src_img = src_img.convert("RGB")

	target_w, target_h = 1240, 1754
	margin = 40

	canvas = Image.new("RGB", (target_w, target_h), "white")

	avail_w = target_w - (margin * 2)
	avail_h = target_h - (margin * 2)

	src_w, src_h = src_img.size
	scale = min(avail_w / src_w, avail_h / src_h)
	new_w = max(1, int(src_w * scale))
	new_h = max(1, int(src_h * scale))

	resized_img = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

	pos_x = margin + (avail_w - new_w) // 2
	pos_y = margin + (avail_h - new_h) // 2

	canvas.paste(resized_img, (pos_x, pos_y))

	buf = BytesIO()
	canvas.save(buf, format="PDF", resolution=150.0)
	buf.seek(0)
	return buf.getvalue()


A4_WIDTH = 595.28
A4_HEIGHT = 841.89


def normalize_page_to_a4(page: PageObject) -> PageObject:
	"""
	Ensures every page has identical A4 size (595.28 x 841.89 pt).
	Scales and centers content if the source page has different dimensions.
	"""
	try:
		src_width = float(page.mediabox.width)
		src_height = float(page.mediabox.height)
	except Exception:
		return page

	# Check if page is already A4 portrait within 1.5 point tolerance
	if abs(src_width - A4_WIDTH) <= 1.5 and abs(src_height - A4_HEIGHT) <= 1.5:
		return page

	scale = min(A4_WIDTH / max(src_width, 1), A4_HEIGHT / max(src_height, 1))
	new_w = src_width * scale
	new_h = src_height * scale

	tx = (A4_WIDTH - new_w) / 2.0
	ty = (A4_HEIGHT - new_h) / 2.0

	a4_page = PageObject.create_blank_page(width=A4_WIDTH, height=A4_HEIGHT)
	transform = Transformation().scale(scale).translate(tx=tx, ty=ty)
	page.add_transformation(transform)
	a4_page.merge_page(page)
	return a4_page


def get_all_attached_files(doc) -> list[tuple[str, str, bytes]]:
	"""
	Retrieves all attached files (filename, file_url, content) linked to a Vendor Purchase Order.
	Aggregates from sidebar attachments, form attachment fields, and child table quotation PDFs.
	"""
	discovered = []
	seen_urls = set()

	# 1. Sidebar attachments (File doctype)
	sidebar_files = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": "Vendor Purchase Order",
			"attached_to_name": doc.name,
		},
		fields=["name", "file_name", "file_url"],
		order_by="creation asc",
	)
	for sf in sidebar_files:
		if sf.file_url and sf.file_url not in seen_urls:
			try:
				fdoc = frappe.get_doc("File", sf.name)
				content = get_file_bytes_from_url_or_doc(fdoc.file_url, fdoc)
				if content:
					discovered.append((fdoc.file_name or os.path.basename(sf.file_url), sf.file_url, content))
					seen_urls.add(sf.file_url)
			except Exception:
				pass

	# 2. Form attachment fields on Vendor Purchase Order
	attachment_fieldnames = [
		"quotation_comparison_sheet",
		"invoice_doc",
		"shipping_bill",
		"bill_of_lading",
		"packing_list",
		"commercial_invoice",
		"certificate_of_origin",
		"inspection_report",
		"insurance_doc",
		"cfa_doc",
		"attachments",
	]

	for fieldname in attachment_fieldnames:
		val = getattr(doc, fieldname, None)
		if val and isinstance(val, str) and val not in seen_urls:
			content = get_file_bytes_from_url_or_doc(val)
			if content:
				file_name = os.path.basename(val)
				discovered.append((file_name, val, content))
				seen_urls.add(val)

	# 3. Child table quotation PDFs
	if hasattr(doc, "quotations") and doc.quotations:
		for q in doc.quotations:
			q_pdf = getattr(q, "quotation_pdf", None)
			if q_pdf and isinstance(q_pdf, str) and q_pdf not in seen_urls:
				content = get_file_bytes_from_url_or_doc(q_pdf)
				if content:
					file_name = os.path.basename(q_pdf)
					discovered.append((file_name, q_pdf, content))
					seen_urls.add(q_pdf)

	return discovered


def merge_po_attachments(doc, base_pdf_bytes: bytes) -> bytes:
	"""
	Stitches attached PDF files and image attachments (PNG, JPEG, WEBP, BMP) directly to the main PO PDF document.
	Defensively logs any damaged or unsupported files to Frappe Error Log without crashing execution.
	"""
	pdf_writer = PdfWriter()

	# 1. Append primary Vendor Purchase Order PDF (normalized to standard A4)
	try:
		base_reader = PdfReader(BytesIO(base_pdf_bytes))
		for p in base_reader.pages:
			pdf_writer.add_page(normalize_page_to_a4(p))
	except Exception as e:
		frappe.log_error(
			title=f"PDF Merge: Invalid Base PO PDF ({doc.name})",
			message=f"Failed reading base PO PDF bytes: {str(e)}\n\n{frappe.get_traceback()}",
			reference_doctype="Vendor Purchase Order",
			reference_name=doc.name,
		)
		return base_pdf_bytes

	# 2. Retrieve all attached files (Sidebar + Form Fields + Quotation PDFs)
	attached_files = get_all_attached_files(doc)

	for fname, file_url, content in attached_files:
		filename = fname.lower()

		# Process PDF Attachments via native pypdf append
		if filename.endswith(".pdf"):
			try:
				reader = PdfReader(BytesIO(content))
				if len(reader.pages) == 0:
					raise ValueError("Attached PDF file has no pages.")
				for p in reader.pages:
					pdf_writer.add_page(normalize_page_to_a4(p))
			except Exception as e:
				frappe.log_error(
					title=f"PDF Merge Error: Damaged PDF Attachment ({fname})",
					message=f"Error reading/stitching attached PDF {fname} ({file_url}): {str(e)}\n\n{frappe.get_traceback()}",
					reference_doctype="Vendor Purchase Order",
					reference_name=doc.name,
				)

		# Process Image Attachments (PNG, JPG, JPEG, WEBP, BMP)
		elif filename.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
			try:
				img_pdf_bytes = convert_image_to_a4_pdf(content)
				img_reader = PdfReader(BytesIO(img_pdf_bytes))
				for p in img_reader.pages:
					pdf_writer.add_page(normalize_page_to_a4(p))
			except Exception as e:
				frappe.log_error(
					title=f"PDF Merge Error: Corrupted Image Attachment ({fname})",
					message=f"Error converting attached image {fname} ({file_url}) to PDF: {str(e)}\n\n{frappe.get_traceback()}",
					reference_doctype="Vendor Purchase Order",
					reference_name=doc.name,
				)

		# Process Unsupported File Types (.txt, .doc, corrupted files)
		else:
			frappe.log_error(
				title=f"PDF Merge Warning: Unsupported Attachment Format ({fname})",
				message=f"File {fname} ({file_url}) attached to {doc.name} is an unsupported format for PDF merging and was safely skipped.",
				reference_doctype="Vendor Purchase Order",
				reference_name=doc.name,
			)

	output_io = BytesIO()
	pdf_writer.write(output_io)
	return output_io.getvalue()
