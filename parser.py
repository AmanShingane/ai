import fitz
import os
import re
from PIL import Image

_reader = None


def get_ocr_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


def clean_text(text: str) -> str:
    """
    Clean extracted text.
    """

    text = re.sub(r"\s+", " ", text)
    text = text.replace("\x00", "")

    return text.strip()


def extract_text(pdf_path: str) -> str:
    """
    Extract text from PDF.
    """

    doc = fitz.open(pdf_path)

    full_text = []

    for page in doc:
        text = page.get_text()

        if text:
            full_text.append(text)

    doc.close()

    return clean_text("\n".join(full_text))


def extract_images(
    pdf_path: str,
    output_dir: str = "images"
):
    """
    Extract all images from PDF.
    """

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    image_paths = []

    for page_index in range(len(doc)):

        page = doc[page_index]

        image_list = page.get_images(full=True)

        for image_index, img in enumerate(image_list):

            xref = img[0]

            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]

            ext = base_image["ext"]

            image_name = (
                f"page_{page_index+1}"
                f"_img_{image_index+1}.{ext}"
            )

            image_path = os.path.join(
                output_dir,
                image_name
            )

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)

    doc.close()

    return image_paths


def perform_ocr(image_path: str) -> str:
    """
    OCR on extracted image.
    """
    reader = get_ocr_reader()
    results = reader.readtext(image_path)

    text = " ".join(
        [result[1] for result in results]
    )

    return clean_text(text)


def extract_ocr_from_images(
    image_paths
):
    """
    OCR all images.
    """

    ocr_text = []

    for image_path in image_paths:

        try:
            text = perform_ocr(image_path)

            if text.strip():
                ocr_text.append(text)

        except Exception:
            continue

    return "\n".join(ocr_text)


def parse_pdf(pdf_path):
    """
    Complete PDF parsing.
    """

    text = extract_text(pdf_path)

    images = extract_images(pdf_path)

    # Optimization: Only run OCR on images if native text extraction is empty or too short.
    if len(text.strip()) > 150:
        ocr_text = "(OCR skipped as native text was successfully extracted)"
    else:
        ocr_text = extract_ocr_from_images(images)

    combined_text = f"""
    PDF TEXT:
    {text}

    OCR TEXT:
    {ocr_text}
    """

    return {
        "text": combined_text,
        "images": images
    }


if __name__ == "__main__":

    result = parse_pdf("sample.pdf")

    print(result["text"][:1000])

    print(
        f"Images Extracted: {len(result['images'])}"
    )