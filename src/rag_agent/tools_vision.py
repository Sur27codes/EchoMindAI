"""
Vision Tools for Image Analysis.
"""
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Lazy load model to avoid startup costs if not used
_processor = None
_model = None

def load_vision_model():
    global _processor, _model
    if _model is None:
        try:
            print("Loading BLIP Vision Model (this may take a moment)...")
            # Use base model for speed on CPU
            model_id = "Salesforce/blip-image-captioning-base"
            _processor = BlipProcessor.from_pretrained(model_id)
            _model = BlipForConditionalGeneration.from_pretrained(model_id)
        except Exception as e:
            print(f"Error loading vision model: {e}")
            raise e

def describe_image(image_path: str) -> str:
    """
    Generate a detailed caption for an image file.
    Args:
        image_path: Absolute path to the image file.
    """
    try:
        load_vision_model()
        
        raw_image = Image.open(image_path).convert('RGB')
        
        # Unconditional image captioning
        inputs = _processor(raw_image, return_tensors="pt")
        
        out = _model.generate(**inputs, max_new_tokens=50)
        caption = _processor.decode(out[0], skip_special_tokens=True)
        
        return caption
    except Exception as e:
        return f"Error describing image: {e}"
