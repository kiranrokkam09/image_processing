import os
import requests
import csv
from io import BytesIO
from PIL import Image
from celery import shared_task
from django.conf import settings
from .models import CSVUpload
from django.utils.timezone import now

@shared_task
def process_images(csv_id):
    """Download, compress, and save images asynchronously"""
    try:
        csv_record = CSVUpload.objects.get(id=csv_id)
        input_file_path = os.path.join(settings.MEDIA_ROOT, csv_record.file_path)
        input_file_path = os.path.abspath(input_file_path)

        # Read Input CSV File
        with open(input_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()[1:]  # Skip header row

        # Prepare Output CSV Path
        output_file_path = f"processed_csv/{csv_record.file_name}"
        full_output_path = os.path.join(settings.MEDIA_ROOT, output_file_path)
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

        # Open output CSV and write header
        with open(full_output_path, "w", encoding="utf-8") as output_file:
            output_file.write("S. No.,Product Name,Input Image Urls,Output Image Urls\n")

        # Process each row and write to output immediately
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) < 3:
                continue  # Skip invalid rows

            product_name = parts[1]
            image_urls = parts[2:]
            processed_urls = []
            original_urls = []
            
            for i, url in enumerate(image_urls):
                url = url.strip().strip('"').strip("'")

                original_urls.append(url)

                response = requests.get(url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))

                    # Ensure valid filename
                    filename = os.path.basename(url)
                    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):  
                        filename += ".jpg"

                    output_path = f"processed_images/{i}_{product_name}_{filename}"
                    full_output_image_path = os.path.join(settings.MEDIA_ROOT, output_path)
                    os.makedirs(os.path.dirname(full_output_image_path), exist_ok=True)

                    img.save(full_output_image_path, quality=50)  # Reduce quality to 50%
                    processed_urls.append(f"{settings.MEDIA_URL}{output_path}")

            # Append processed row to output file
            with open(full_output_path, "a", encoding="utf-8") as op_file:
                op_file.write(f"{parts[0]},{product_name},{','.join(original_urls)},{' '.join(processed_urls)}\n")

        # Update status in the database
        csv_record.status = "Completed"
        csv_record.file_path = output_file_path
        csv_record.completed_at = now()
        csv_record.save()

        # Trigger webhook if available
        if csv_record.webhook_url:
            webhook_data = {
                "request_id": csv_id,
                "status": "Completed",
                "processed_csv": f"{settings.MEDIA_URL}{output_file_path}"
            }
            requests.post(csv_record.webhook_url, json=webhook_data)
    
    except Exception as e:
        csv_record.status = "Failed"
        csv_record.save()
        raise e

