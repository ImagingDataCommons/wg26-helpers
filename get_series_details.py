"""
Given a public DICOM endpoint, generate the list of all series
to help finding content
"""


import csv
from dicomweb_client.api import DICOMwebClient

# Replace this with your DICOMweb base URL (no authentication)
#DICOMWEB_URL = 'https://dicomwebproxy.app/dicomWeb'
DICOMWEB_URL = 'https://ihe.j4care.com:18443/dcm4chee-arc/aets/DCM4CHEE/rs'

# Initialize DICOMweb client
client = DICOMwebClient(url=DICOMWEB_URL)

# Prepare CSV output
csv_filename = 'dicom_instances.csv'
fieldnames = ['PatientName', 'StudyInstanceUID', 'SeriesInstanceUID', 'Modality', 'Manufacturer']

with open(csv_filename, mode='w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Search for all studies
    studies = client.search_for_studies()
    for study in studies:
        study_uid = study.get('0020000D', {}).get('Value', [None])[0]
        if not study_uid:
            continue

        # Search for all series in the study
        series_list = client.search_for_series(study_instance_uid=study_uid)
        for series in series_list:
            series_uid = series.get('0020000E', {}).get('Value', [None])[0]
            if not series_uid:
                continue

            # Search for all instances in the series
            instances = client.search_for_instances(study_instance_uid=study_uid, series_instance_uid=series_uid)

            for instance in instances:
                instance_uid = instance.get('00080018', {}).get('Value', [None])[0]                
                metadata= client.retrieve_instance_metadata(study_instance_uid=study_uid, series_instance_uid=series_uid, sop_instance_uid=instance_uid)
                modality = metadata.get('00080060', {}).get('Value', [None])[0]
                manufacturer = metadata.get('00080070', {}).get('Value', [None])[0]
                patient_name = metadata.get('00100010', {}).get('Value', [None])[0]

                # Extract required fields with DICOM tags
                # 00080060: Modality, 00080070: Manufacturer

                writer.writerow({
                    'PatientName': patient_name,
                    'StudyInstanceUID': study_uid,
                    'SeriesInstanceUID': series_uid,
                    'Modality': modality,
                    'Manufacturer': manufacturer
                })

                break

print(f"CSV file '{csv_filename}' generated successfully.")

