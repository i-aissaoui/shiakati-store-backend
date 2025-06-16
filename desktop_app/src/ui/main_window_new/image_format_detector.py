"""
Image format detector for API responses to help with debugging.
"""

def describe_image_response(images_data):
    """
    Analyze an image response from the API and provide a detailed description.
    
    Args:
        images_data: The response from the API (could be dict, list, or other format)
        
    Returns:
        str: A human-readable description of the format
    """
    if images_data is None:
        return "Response is None (no data)"
    
    response_type = type(images_data).__name__
    
    if isinstance(images_data, dict):
        keys = list(images_data.keys())
        description = f"Dictionary with {len(keys)} keys: {keys}"
        
        # Analyze images key if present
        if 'images' in images_data:
            images_list = images_data.get('images', [])
            description += f"\n- 'images' key contains {len(images_list)} items"
            
            # Check first few images
            if images_list:
                sample_size = min(3, len(images_list))
                description += f"\n- First {sample_size} images:"
                for i in range(sample_size):
                    if i < len(images_list):
                        image = images_list[i]
                        if isinstance(image, str):
                            description += f"\n  - Item {i}: string URL: {image[:50]}..."
                        else:
                            description += f"\n  - Item {i}: {type(image).__name__}"
            
        # Analyze main_image if present
        if 'main_image' in images_data:
            main_image = images_data.get('main_image')
            if main_image:
                description += f"\n- 'main_image' is present: {main_image[:50]}..."
            else:
                description += "\n- 'main_image' is empty or null"
                
    elif isinstance(images_data, list):
        description = f"List with {len(images_data)} items"
        
        # Check the first few items
        if images_data:
            sample_size = min(3, len(images_data))
            description += f"\n- First {sample_size} items:"
            
            for i in range(sample_size):
                if i < len(images_data):
                    item = images_data[i]
                    if isinstance(item, str):
                        description += f"\n  - Item {i}: string URL: {item[:50]}..."
                    elif isinstance(item, dict):
                        item_keys = list(item.keys())
                        description += f"\n  - Item {i}: dictionary with keys {item_keys}"
                    else:
                        description += f"\n  - Item {i}: {type(item).__name__}"
    else:
        description = f"Unexpected type: {response_type}"
        
    return f"Response Format: {response_type}\n{description}"
