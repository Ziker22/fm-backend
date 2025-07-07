import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from scraping.models import ScrapedPlace, ScrapedPost


class Command(BaseCommand):
    help = 'Imports data from a JSONL file into the database'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, help='Type of the data source')
        parser.add_argument('name', type=str, help='Name of the file (without extension)')

    def handle(self, *args, **options):
        data_type = options['type']
        file_name = options['name']

        # Construct the path to the JSONL file
        file_path = os.path.join('scraping', 'raw_files', data_type, f"{file_name}.jsonl")

        if not os.path.exists(file_path):
            raise CommandError(f"File {file_path} does not exist")

        self.stdout.write(self.style.SUCCESS(f"Importing data from {file_path}"))

        # Counter for statistics
        processed_posts = 0
        processed_places = 0
        skipped = 0
        duplicates = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    # Parse the JSON line
                    data = json.loads(line.strip())

                    # Check if places key is missing or places array is empty
                    if 'places' not in data or not data['places']:
                        skipped += 1
                        continue

                    # Check if a post with the same third_party_id already exists
                    third_party_id = str(data.get('id', ''))
                    existing_post = ScrapedPost.objects.filter(third_party_id=third_party_id).first()

                    if existing_post:
                        post = existing_post
                        duplicates += 1
                    else:
                        # Create a new ScrapedPost
                        post = ScrapedPost(
                            third_party_id=third_party_id,
                            third_party_type=data_type,
                            title=data.get('title', ''),
                            content=data.get('perex', ''),
                            comments=data.get('comments', []),
                            probability=data.get('probability', 0.0),
                        )
                        post.save()
                        processed_posts += 1

                    # Process all places in the data
                    for place_data in data['places']:
                        # Create ScrapedPlace associated with the post
                        place = ScrapedPlace(
                            name=place_data.get('name', ''),
                            types=place_data.get('types', []),
                            post=post
                        )
                        place.save()
                        processed_places += 1

            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported {processed_posts} posts with {processed_places} places. "
                f"Skipped {skipped} records. Found {duplicates} duplicate posts."
            ))

        except Exception as e:
            raise CommandError(f"Error importing data: {str(e)}")
