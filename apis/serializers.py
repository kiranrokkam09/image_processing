import os
import re
import csv
from django.conf import settings
from .models import CSVUpload
from rest_framework import serializers

class CSVUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)  # Accept file input

    class Meta:
        model = CSVUpload
        fields = ["id", "file", "file_name", "file_path", "status", "uploaded_at","webhook_url"]
        read_only_fields = ["id", "file_name", "file_path", "status", "uploaded_at"]
    
        def validate_file(self, file):

            required_columns = ["S. No.", "Product Name", "Input Image Urls"]

            # Read file content and validate CSV format
            try:
                decoded_file = file.read().decode("utf-8").splitlines()
                csv_reader = csv.reader(decoded_file)
                headers = next(csv_reader)  # Read header row

                if headers != required_columns:
                    raise serializers.ValidationError("CSV format is incorrect. Expected columns: S. No., Product Name, Input Image Urls")

                # Validate each row
                for row in csv_reader:
                    if len(row) != 3:
                        raise serializers.ValidationError("Each row must have exactly 3 columns.")

                    # Validate Serial Number (should be a number)
                    if not row[0].strip().isdigit():
                        raise serializers.ValidationError(f"Invalid Serial Number: {row[0]}")

                    # Validate Image URLs
                    urls = row[2].split(", ")
                    for url in urls:
                        if not re.match(r"https?://[^\s]+", url):
                            raise serializers.ValidationError(f"Invalid URL found: {url}")

            except Exception as e:
                raise serializers.ValidationError(f"Error reading CSV file: {str(e)}")

            # Reset file pointer after reading
            file.seek(0)
            return file

    def create(self, validated_data):
        uploaded_file = validated_data.pop("file")  # Extract file from request
        file_name = uploaded_file.name
        file_path = os.path.join("uploads/csv_files", file_name)  # Define storage path
        webhook_url = validated_data.get("webhook_url", None)

        # Ensure the directory exists
        full_dir_path = os.path.join(settings.MEDIA_ROOT, "uploads/csv_files")
        os.makedirs(full_dir_path, exist_ok=True)

        # Save file to media folder manually
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        with open(full_file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        # Save record in database
        csv_record = CSVUpload.objects.create(
            file_name=file_name,
            file_path=file_path,
            webhook_url=webhook_url,
            status="Pending",
        )
        return csv_record


class CSVStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVUpload
        fields = ["id", "file_name", "status", "uploaded_at", "completed_at","webhook_url"]
