from django.test import TestCase
from django.utils import timezone
from django.contrib.gis.geos import Point
from datetime import timedelta
import time

from place.models import Place


class CreatedUpdatedModelTest(TestCase):
    """
    Test case for verifying the functionality of CreatedUpdatedModel.
    
    These tests ensure that the created_at and updated_at fields are
    automatically set and updated as expected.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create a test place
        self.test_place = Place.objects.create(
            name="Test Place",
            location=Point(14.4378, 50.0755),  # Example coordinates for Prague
            google_maps_url="https://maps.google.com/?q=50.0755,14.4378",
            website="https://example.com",
            type=Place.PlaceType.PLAYGROUND
        )
    
    def test_timestamps_created_on_new_object(self):
        """Test that timestamps are automatically set when creating a new object."""
        # Get the current time for comparison
        now = timezone.now()
        
        # Verify that created_at and updated_at are set
        self.assertIsNotNone(self.test_place.created_at)
        self.assertIsNotNone(self.test_place.updated_at)
        
        # Verify that timestamps are recent (within the last minute)
        self.assertLess(now - self.test_place.created_at, timedelta(minutes=1))
        self.assertLess(now - self.test_place.updated_at, timedelta(minutes=1))
        
        # Verify that created_at and updated_at are initially very close
        # Using a small delta for comparison instead of exact equality
        self.assertAlmostEqual(
            self.test_place.created_at.timestamp(),
            self.test_place.updated_at.timestamp(),
            delta=0.1,  # Allow a small difference (100ms)
            msg="created_at and updated_at should be very close when object is first created"
        )
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at is automatically updated when saving an object."""
        # Store the original timestamps
        original_created_at = self.test_place.created_at
        original_updated_at = self.test_place.updated_at
        
        # Wait a short time to ensure timestamps will be different
        time.sleep(0.1)
        
        # Update the place
        self.test_place.name = "Updated Test Place"
        self.test_place.save()
        
        # Refresh from database to get updated values
        self.test_place.refresh_from_db()
        
        # Verify that created_at hasn't changed
        self.assertEqual(
            original_created_at,
            self.test_place.created_at,
            "created_at should not change when object is updated"
        )
        
        # Verify that updated_at has changed
        self.assertGreater(
            self.test_place.updated_at,
            original_updated_at,
            "updated_at should change when object is updated"
        )
