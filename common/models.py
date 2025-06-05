from django.db import models


class CreatedUpdatedModel(models.Model):
    """
    Abstract base model that automatically tracks creation and update timestamps.
    
    This model provides two fields:
    - created_at: Automatically set when the object is first created
    - updated_at: Automatically updated whenever the object is saved
    
    To use this model, simply inherit from it in your model classes:
    
    class YourModel(CreatedUpdatedModel):
        # Your fields here
        pass
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
